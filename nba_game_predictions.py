# -*- coding: utf-8 -*-
"""NBA_Game_Predictions.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1imdWXercHiQmuQ5LJmCBbWh8CPA_V77m

Imports
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn.metrics as metrics
import seaborn as sns

from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier, AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier, Perceptron



"""Tune Hyperparameters

The following code references http://www.davidsbatista.net/blog/2018/02/23/model_optimization/
"""

class EstimatorSelectionHelper:

    def __init__(self, models, params):
        if not set(models.keys()).issubset(set(params.keys())):
            missing_params = list(set(models.keys()) - set(params.keys()))
            raise ValueError("Some estimators are missing parameters: %s" % missing_params)
        self.models = models
        self.params = params
        self.keys = models.keys()
        self.grid_searches = {}

    def fit(self, X, y, cv=3, n_jobs=3, verbose=1, scoring=None, refit=False):
        for key in self.keys:
            print("Running GridSearchCV for %s." % key)
            model = self.models[key]
            params = self.params[key]
            gs = GridSearchCV(model, params, cv=cv, n_jobs=n_jobs,
                              verbose=verbose, scoring=scoring, refit=refit,
                              return_train_score=True)
            gs.fit(X,y)
            self.grid_searches[key] = gs    

    def f1(self, sort_by='mean_f1', name = 'f1', k=None):
        def row(key, scores, params):
            d = {
                'estimator': key,
                'mean_f1': np.mean(scores),
            }
            return pd.Series({**d, **params})

        rows = []
        params = self.grid_searches[k].cv_results_['params']
        scores = []
        for i in range(self.grid_searches[k].cv):
            key = "split{}_test_f1".format(i)
            r = self.grid_searches[k].cv_results_[key]        
            scores.append(r.reshape(len(params),1))

        all_scores = np.hstack(scores)
        for p, s in zip(params,all_scores):
            rows.append((row(k, s, p)))

        df = pd.concat(rows, axis=1).T.sort_values([sort_by], ascending=False)

        columns = ['estimator', 'mean_f1']
        columns = ['estimator'] + [c for c in df.columns if c not in columns] + ['mean_f1'] 
        # print("F1", df[columns])

        return df[columns]

    def accuracy(self, sort_by='mean_accuracy', name = 'accuracy', k=None):
        def row(key, scores, params):
            d = {
                'estimator': key,
                'mean_accuracy': np.mean(scores),
            }
            return pd.Series({**d, **params})

        rows = []
        params = self.grid_searches[k].cv_results_['params']
        scores = []
        for i in range(self.grid_searches[k].cv):
            key = "split{}_test_accuracy".format(i)
            r = self.grid_searches[k].cv_results_[key]        
            scores.append(r.reshape(len(params),1))

        all_scores = np.hstack(scores)
        for p, s in zip(params,all_scores):
            rows.append((row(k, s, p)))

        df = pd.concat(rows, axis=1).T.sort_values([sort_by], ascending=False)

        columns = ['estimator', 'mean_accuracy']
        columns = ['estimator'] + [c for c in df.columns if c not in columns] + ['mean_accuracy'] 
        # print("Accuracy", df[columns])

        return df[columns]

    def recall(self, sort_by='mean_recall', name = 'recall', k=None):
        def row(key, scores, params):
            d = {
                'estimator': key,
                'mean_recall': np.mean(scores),
            }
            return pd.Series({**d, **params})

        rows = []
        params = self.grid_searches[k].cv_results_['params']
        scores = []
        for i in range(self.grid_searches[k].cv):
            key = "split{}_test_recall".format(i)
            r = self.grid_searches[k].cv_results_[key]        
            scores.append(r.reshape(len(params),1))

        all_scores = np.hstack(scores)
        for p, s in zip(params,all_scores):
            rows.append((row(k, s, p)))

        df = pd.concat(rows, axis=1).T.sort_values([sort_by], ascending=False)

        columns = ['estimator', 'mean_recall']
        columns = ['estimator'] + [c for c in df.columns if c not in columns] + ['mean_recall'] 
        # print("Recall", df[columns])
        return df[columns]

    def precision(self, sort_by='mean_precision', name = 'precision', k=None):
        def row(key, scores, params):
            d = {
                'estimator': key,
                'mean_precision': np.mean(scores),
            }
            return pd.Series({**d, **params})

        rows = []
        params = self.grid_searches[k].cv_results_['params']
        scores = []
        for i in range(self.grid_searches[k].cv):
            key = "split{}_test_precision".format(i)
            r = self.grid_searches[k].cv_results_[key]        
            scores.append(r.reshape(len(params),1))

        all_scores = np.hstack(scores)
        for p, s in zip(params,all_scores):
            rows.append((row(k, s, p)))

        df = pd.concat(rows, axis=1).T.sort_values([sort_by], ascending=False)

        columns = ['estimator', 'mean_precision']
        columns = ['estimator'] + [c for c in df.columns if c not in columns] + ['mean_precision'] 
        # print ("precision", df[columns])
        return df[columns]

    def score_summary(self, model_name=None):
        f1 = self.f1(k=model_name)
        accuracy = self.accuracy(k=model_name)
        recall = self.recall(k=model_name)
        precision = self.precision(k=model_name)
        df = pd.merge(accuracy, f1)
        df = pd.merge(df, recall)
        df = pd.merge(df, precision)
        return df

models1 = {
    'MLPClassifier': MLPClassifier(activation='relu', max_iter=1000, random_state=18),
    'BaggingClassifier': BaggingClassifier(random_state=18),
    'SVC': SVC(random_state=18)
}

params1 = {
    'MLPClassifier': {'solver': ['adam', 'sgd'], 
                      'learning_rate': ['constant', 'adaptive'], 
                      'alpha': [0.0001, 0.00001, 0.1], 
                      'learning_rate_init': [0.001, 0.0001, .1] },
    'BaggingClassifier': {'n_estimators': [10, 25, 50], 'max_features': [1.0, 2, 4, 6], 'bootstrap': [True, False]},
    'SVC': {'kernel': ['rbf', 'poly'], 'C': [1, 10, 50], 'gamma': ['auto', 0.001, 0.0001]}
}

def tune_params(xtrain, ytrain):
    print ("Tuning Hyperparameters...\n")

    helper1 = EstimatorSelectionHelper(models1, params1)
    helper1.fit(xtrain, ytrain.values.ravel(), scoring=['accuracy', 'f1', 'recall', 'precision'])

    """GridSearchCV Results"""
    print ("")
    print ("Results...\n")
    df_rf = helper1.score_summary(model_name='BaggingClassifier')
    df_rf.sort_values(by=['mean_accuracy'],ascending=False)
    print (df_rf)
    print ("")

    df_svc = helper1.score_summary(model_name='SVC')
    df_svc.sort_values(by=['mean_accuracy'],ascending=False)
    print (df_svc)
    print ("")

    df_nn = helper1.score_summary(model_name='MLPClassifier')
    df_nn.sort_values(by=['mean_accuracy'],ascending=False)
    print (df_nn)
    print ("")

"""Using PCA to plot data and evaluate linear separability

The following code references https://towardsdatascience.com/pca-using-python-scikit-learn-e653f8989e60
"""

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.mplot3d import Axes3D  


def pca_plot(dfGames):

    print ("Plotting data...\n")

    features = ['W_PCT', 'REB', 'TOV', 'PLUS_MINUS', 'OFF_RATING', 'DEF_RATING', 'TS_PCT']

    # Separating out the features
    x = dfGames.loc[:, features].values

    # Separating out the target
    y = dfGames.loc[:,['Result']].values

    x = StandardScaler().fit_transform(x)

    principalComponents = PCA(n_components=2).fit_transform(x)
    principalDf = pd.DataFrame(data = principalComponents
                 , columns = ['principal component 1', 'principal component 2'])
    finalDf = pd.concat([principalDf, dfGames[['Result']]], axis = 1)

    fig = plt.figure(figsize = (8,8))
    ax = fig.add_subplot(1,1,1) 
    ax.set_xlabel('Principal Component 1', fontsize = 15)
    ax.set_ylabel('Principal Component 2', fontsize = 15)
    ax.set_title('PCA of NBA Games Data', fontsize = 20)
    targets = [0, 1]
    colors = ['r','b']
    for target, color in zip(targets,colors):
        indicesToKeep = finalDf['Result'] == target
        ax.scatter(finalDf.loc[indicesToKeep, 'principal component 1']
                   , finalDf.loc[indicesToKeep, 'principal component 2']
                   , c = color
                   , s = 50)
    ax.legend(targets)
    ax.grid()

    principalComponents = PCA(n_components=3).fit_transform(x)
    principalDf = pd.DataFrame(data = principalComponents
                 , columns = ['principal component 1', 'principal component 2', 'principal component 3'])
    finalDf = pd.concat([principalDf, dfGames[['Result']]], axis = 1)

    fig = plt.figure(figsize = (8,8))
    ax = fig.add_subplot(111, projection='3d') 
    ax.set_xlabel('Principal Component 1', fontsize = 15)
    ax.set_ylabel('Principal Component 2', fontsize = 15)
    ax.set_zlabel('Principal Component 3', fontsize = 15)
    ax.set_title('PCA of NBA Games Data', fontsize = 20)
    targets = [0, 1]
    colors = ['r','b']
    for target, color in zip(targets,colors):
        indicesToKeep = finalDf['Result'] == target
        ax.scatter(finalDf.loc[indicesToKeep, 'principal component 1']
                   , finalDf.loc[indicesToKeep, 'principal component 2']
                   , finalDf.loc[indicesToKeep, 'principal component 3']
                   , c = color
                   , s = 50)
    ax.legend(targets)
    ax.grid()
    plt.show()

def run_linear_classifiers(xtrain, ytrain):
    """A single perceptron basically finds the decision boundary given samples and labels. It learns a series of weights that are used in a linear combination of the inputs. This value is then processed by the activation function and produces an binary classification. Due to the nature of this classifier, it can only classify linearly separable data (XOR problem). 

    http://www.ece.utep.edu/research/webfuzzy/docs/kk-thesis/kk-thesis-html/node19.html
    """
    print ("Running linear classifiers...\n")

    single = Perceptron(random_state=18)
    single.fit(xtrain, ytrain.values.ravel())
    print ("Single Perceptron Score:", single.score(xtrain, ytrain))
    print ("")

    """SVM's with linear kernel tries to separate the data with a soft margin that maximizes the distance between two sides. Making C large wil allow close to 0 misclassifications. If the model separates the training data close to 100%, then it's linearly separable. 

    https://medium.com/@xmauryvrockx/how-to-check-for-linear-separability-13c177ae5a6e
    """

    lin = SVC(C=2**8, kernel='linear', random_state=18)
    lin.fit(xtrain, ytrain.values.ravel())
    print ("SVC linear Score:", lin.score(xtrain, ytrain))
    print ("")

"""Create models

The following code references http://www.davidsbatista.net/blog/2018/02/23/model_optimization/
"""

def scores(model, xtrain, ytrain, xtest, ytest):
    
    model.fit(xtrain, ytrain.values.ravel())
    y_pred = model.predict(xtest)
    
    # print("Accuracy score: %.3f" % metrics.accuracy_score(ytest, y_pred))
    # print("Recall: %.3f" % metrics.recall_score(ytest, y_pred))
    # print("Precision: %.3f" % metrics.precision_score(ytest, y_pred))
    # print("F1: %.3f" % metrics.f1_score(ytest, y_pred))
    
    # proba = model.predict_proba(xtest)
    # print("Log loss: %.3f" % metrics.log_loss(ytest, proba))

    # pos_prob = proba[:, 1]
    # print("Area under ROC curve: %.3f" % metrics.roc_auc_score(ytest, pos_prob))
    
    cv = cross_val_score(model, xtest, ytest.values.ravel(), cv = 3, scoring = 'accuracy')
    print("Accuracy (cross validation score): %0.3f (+/- %0.3f)" % (cv.mean(), cv.std() * 2))

    cv = cross_val_score(model, xtest, ytest.values.ravel(), cv = 3, scoring = 'f1')
    print("f1 (cross validation score): %0.3f (+/- %0.3f)" % (cv.mean(), cv.std() * 2))

    cv = cross_val_score(model, xtest, ytest.values.ravel(), cv = 3, scoring = 'recall')
    print("recall (cross validation score): %0.3f (+/- %0.3f)" % (cv.mean(), cv.std() * 2))

    cv = cross_val_score(model, xtest, ytest.values.ravel(), cv = 3, scoring = 'precision')
    print("precision (cross validation score): %0.3f (+/- %0.3f)" % (cv.mean(), cv.std() * 2))

    print ("")

    print ("***************************************")

    # confusionMatrix = metrics.confusion_matrix(ytest, y_pred)  # Diagonals tell you correct predictions
    # print (confusionMatrix)
    return y_pred

"""scores() provides mean score and the 95% confidence interval for all metrics

https://scikit-learn.org/dev/modules/cross_validation.html
"""

def confusion_matrix(y_pred, model_name, ytest):
    cm = metrics.confusion_matrix(ytest, y_pred)

    plt.style.use("fivethirtyeight")
    z, ax = plt.subplots()

    sns.heatmap(cm, annot=True, ax = ax, linewidth = 2, fmt='g')

    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")

    z.suptitle("%s Confusion Matrix" % model_name.upper(), weight = 'bold', size = 18, x = .45)
    
    z.text(x = 0, y = -0.08,
        s = '__________________________________________________________',
        fontsize = 14, color = 'grey', horizontalalignment='left')

    z.text(x = 0, y = -.14,
        s = 'Raven Nuega                     ',
        fontsize = 14, fontname = 'Rockwell', color = 'grey', horizontalalignment='left')

    z.savefig('%s_cm.png' % model_name, dpi = 400, bbox_inches = 'tight')
    plt.show()


def run_final_classifiers(xtrain, ytrain, xtest, ytest, df_predictions):

    print ("Running optimized classifiers...\n")

    print ("")
    print ("Random Forest with bagging\n")
    rf = BaggingClassifier(n_estimators=25, max_features=2, bootstrap=True, random_state=18)
    y_rf = scores(rf, xtrain, ytrain, xtest, ytest)

    df_predictions['Prediction'] = y_rf 
    print (df_predictions)
    print ("***************************************")
    print ("")

    confusion_matrix(y_rf, 'rf', ytest)

    print ("Support Vector Classifier\n")
    svc = SVC(C=1, kernel='rbf', gamma='auto', probability=True, random_state=18)
    y_svc = scores(svc, xtrain, ytrain, xtest, ytest)

    df_predictions['Prediction'] = y_svc 
    print (df_predictions)
    print ("***************************************")

    print ("")

    confusion_matrix(y_svc, 'svc', ytest)

    print ("Multi-Layer Perceptron Classifier\n")
    dnn = MLPClassifier(activation='relu', solver='sgd', learning_rate='constant', learning_rate_init=0.001, alpha=0.0001, max_iter=500, random_state=18)
    y_dnn = scores(dnn, xtrain, ytrain, xtest, ytest)

    df_predictions['Prediction'] = y_dnn
    print (df_predictions)
    print ("***************************************")


    confusion_matrix(y_dnn, 'dnn', ytest)

def main(): 

    """Obtain Data"""

    dfGames = pd.read_csv('./COMBINEDgamesWithInfo2016-19.csv')

    dfGames = dfGames.drop(['Unnamed: 0'], axis=1)
    dfGames.columns

    print ("Head of dataset...\n")
    print (dfGames.head())
    print ("")

    """Split Data"""

    train, test = train_test_split(dfGames, test_size = 0.25, random_state = 10)

    xtrain = train[['W_PCT', 'REB', 'TOV', 'PLUS_MINUS', 'OFF_RATING', 'DEF_RATING', 'TS_PCT']]
    ytrain = train[['Result']]

    xtest = test[['W_PCT', 'REB', 'TOV', 'PLUS_MINUS', 'OFF_RATING', 'DEF_RATING', 'TS_PCT']]
    ytest = test[['Result']]

    df_predictions = test.drop(labels=['W_PCT', 'REB', 'TOV', 'PLUS_MINUS', 'OFF_RATING', 'DEF_RATING', 'TS_PCT'], axis=1)


    pca_plot(dfGames)
    run_linear_classifiers(xtrain, ytrain)
    tune_params(xtrain, ytrain)
    run_final_classifiers(xtrain, ytrain, xtest, ytest, df_predictions)


if __name__ == '__main__':
    main()

