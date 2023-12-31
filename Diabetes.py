# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19rD3JFJXNDgh2bqedzA2c_aqGlVe8lVE
"""

!pip install lime

pip install matplotlib

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import matplotlib.pyplot as plt
# %matplotlib inline
import seaborn as sns
import numpy as np
## for statistical tests
import scipy
import statsmodels.formula.api as smf
import statsmodels.api as sm
## for machine learning
from sklearn import model_selection, preprocessing, feature_selection, ensemble, linear_model, metrics, decomposition

## for explainer
from lime import lime_tabular

dtf = pd.read_csv('diabetes_data.csv')
dtf.head()

dtf.info()

dtf.describe(include='all')

dtf.nunique()

#Heatmap to show the Categorical , Numerical data and Nan values
def utils_recognize_type(dtf, col, max_cat=20):
    if (dtf[col].dtype == "O") | (dtf[col].nunique() < max_cat):
        return "cat"
    else:
        return "num"

dic_cols = {col:utils_recognize_type(dtf, col, max_cat=20) for col in dtf.columns}
heatmap = dtf.isnull()
for k,v in dic_cols.items():
 if v == "num":
   heatmap[k] = heatmap[k].apply(lambda x: 0.5 if x is False else 1)
 else:
   heatmap[k] = heatmap[k].apply(lambda x: 0 if x is False else 1)
sns.heatmap(heatmap, cbar=False).set_title('Dataset Overview')
plt.show()
print("\033[1;37;40m Categerocial ", "\033[1;30;41m Numeric ", "\033[1;30;47m NaN ")

#this step is to check wether the data is balanced or not .
y = "Diabetes"
ax = dtf[y].value_counts().sort_values().plot(kind="barh")
totals= []
for i in ax.patches:
    totals.append(i.get_width())
total = sum(totals)
for i in ax.patches:
     ax.text(i.get_width()+.3, i.get_y()+.20,
     str(round((i.get_width()/total)*100, 2))+'%',
     fontsize=10, color='black')
ax.grid(axis="x")
plt.suptitle(y, fontsize=20)
plt.show()

## this gragh show how many male and female smokers and non smokers have diabetes .. it shows also that the diabetes percentage is balanced .
# Data is balanced
dtf["Smoker"] = dtf["Smoker"].apply(lambda x: str(x)[0])
## Plot contingency table
cont_table = pd.crosstab(index=dtf["Smoker"],
             columns=dtf["Sex"], values=dtf["Diabetes"], aggfunc="sum")
sns.heatmap(cont_table, annot=True, cmap="YlGnBu", fmt='.0f',
            linewidths=.5).set_title(
            'Smokers (filter: Y)' )



#to show the distribution of the age in the Data set and also to recognize the outliers values .
x = "Age"
fig, ax = plt.subplots(nrows=1, ncols=2,  sharex=False, sharey=False)
fig.suptitle(x, fontsize=20)
### distribution
ax[0].title.set_text('distribution')
variable = dtf[x].fillna(dtf[x].mean())
breaks = np.quantile(variable, q=np.linspace(0, 1, 11))
variable = variable[ (variable > breaks[0]) & (variable <
                    breaks[10]) ]
sns.distplot(variable, hist=True, kde=True, kde_kws={"shade": True}, ax=ax[0])
des = dtf[x].describe()
ax[0].axvline(des["25%"], ls='--')
ax[0].axvline(des["mean"], ls='--')
ax[0].axvline(des["75%"], ls='--')
ax[0].grid(True)
des = round(des, 2).apply(lambda x: str(x))
box = '\n'.join(("min: "+des["min"], "25%: "+des["25%"], "mean: "+des["mean"], "75%: "+des["75%"], "max: "+des["max"]))
ax[0].text(0.95, 0.95, box, transform=ax[0].transAxes, fontsize=10, va='top', ha="right", bbox=dict(boxstyle='round', facecolor='white', alpha=1))
### boxplot
ax[1].title.set_text('outliers (log scale)')
tmp_dtf = pd.DataFrame(dtf[x])
tmp_dtf[x] = np.log(tmp_dtf[x])
tmp_dtf.boxplot(column=x, ax=ax[1])
plt.show()
# we can conclude that we need to remove the values under age 1.5

#Heat map for showing correlations.
sns.heatmap(dtf.corr(),cmap='rainbow', annot=True)

#the Density Graph show how many people have diabetes as every age
#Box plot to distinguish the ages where people have more diabetes and where they don not have .
y = "Diabetes"
cat, num = "Diabetes", "Age"
fig, ax = plt.subplots(nrows=1, ncols=3,  sharex=False, sharey=False)
fig.suptitle(x+"   vs   "+y, fontsize=20)

### distribution
ax[0].title.set_text('density')
for i in dtf[cat].unique():
    sns.distplot(dtf[dtf[cat]==i][num], hist=False, label=i, ax=ax[0])
ax[0].grid(True)
### stacked
ax[1].title.set_text('bins')
breaks = np.quantile(dtf[num], q=np.linspace(0,1,11))
tmp = dtf.groupby([cat, pd.cut(dtf[num], breaks, duplicates='drop')]).size().unstack().T
tmp = tmp[dtf[cat].unique()]
tmp["tot"] = tmp.sum(axis=1)
for col in tmp.drop("tot", axis=1).columns:
     tmp[col] = tmp[col] / tmp["tot"]
tmp.drop("tot", axis=1).plot(kind='bar', stacked=True, ax=ax[1], legend=False, grid=True)
### boxplot
ax[2].title.set_text('outliers')
sns.catplot(x=cat, y=num, data=dtf, kind="box", ax=ax[2])
ax[2].grid(True)
plt.show()

#we can conclude that the people in range Age10 is more subjected to become diabetes Patients .

x = "Age"
fig, ax = plt.subplots(nrows=1, ncols=2,  sharex=False, sharey=False)
fig.suptitle(x, fontsize=20)
### distribution
ax[0].title.set_text('distribution')
variable = dtf[x].fillna(dtf[x].mean())
breaks = np.quantile(variable, q=np.linspace(0, 1, 11))
variable = variable[ (variable > breaks[0]) & (variable <
                    breaks[10]) ]
sns.distplot(variable, hist=True, kde=True, kde_kws={"shade": True}, ax=ax[0])
des = dtf[x].describe()
ax[0].axvline(des["25%"], ls='--')
ax[0].axvline(des["mean"], ls='--')
ax[0].axvline(des["75%"], ls='--')
ax[0].grid(True)
des = round(des, 2).apply(lambda x: str(x))
box = '\n'.join(("min: "+des["min"], "25%: "+des["25%"], "mean: "+des["mean"], "75%: "+des["75%"], "max: "+des["max"]))
ax[0].text(0.95, 0.95, box, transform=ax[0].transAxes, fontsize=10, va='top', ha="right", bbox=dict(boxstyle='round', facecolor='white', alpha=1))
### boxplot
ax[1].title.set_text('outliers (log scale)')
tmp_dtf = pd.DataFrame(dtf[x])
tmp_dtf[x] = np.log(tmp_dtf[x])
tmp_dtf.boxplot(column=x, ax=ax[1])
plt.show()

#this is to check if the BMI od the data set is balanced or not .
sns.distplot(dtf['BMI'])

# to make sure that the dataset tends to have General Health Issues.
sns.distplot(dtf['GenHlth'])

# to make sure that the dataset tends to have Mental Health Issues
sns.distplot(dtf['MentHlth'])

# to make sure that the dataset tends to have Phy Health Issues
sns.distplot(dtf['PhysHlth'])

"""# Neuer Abschnitt"""

#to show how many smokers and non smokers have diabetes
cat, num = "Diabetes", "Age"
model = smf.ols(num+' ~ '+cat, data=dtf).fit()
table = sm.stats.anova_lm(model)
p = table["PR(>F)"][0]
coeff, p = None, round(p, 3)
conclusion = "Correlated" if p < 0.05 else "Non-Correlated"
print("Anova F: the variables are", conclusion, "(p-value: "+str(p)+")")

x, y = "Smoker", "Diabetes"
fig, ax = plt.subplots(nrows=1, ncols=2,  sharex=False, sharey=False)
fig.suptitle(x+"   vs   "+y, fontsize=20)
### count
ax[0].title.set_text('count')
order = dtf.groupby(x)[y].count().index.tolist()
sns.catplot(x=x, hue=y, data=dtf, kind='count', order=order, ax=ax[0])
ax[0].grid(True)
### percentage
ax[1].title.set_text('percentage')
a = dtf.groupby(x)[y].count().reset_index()
a = a.rename(colomns={y:"tot"})
b = dtf.groupby([x,y])[y].count()
b = b.rename(colomns={y:0}).reset_index()
b = b.merge(a, how="left")
b["%"] = b[0] / b["tot"] *100
sns.barplot(x=x, y="%", hue=y, data=b,
            ax=ax[1]).get_legend().remove()
ax[1].grid(True)
plt.show()

#removing the outliers
# Define the column name and the threshold(awel change )

age = 'Age'
threshold = 1.5

# Filter the dataset and keep only the rows where the column value is greater than or equal to the threshold
dtf = dtf[dtf[age] >= threshold]
dtf.info()

dtf.columns

"""Data Preprocessing# Droping CholCheck COLUMN & Romving all Nan Values"""

dtf=dtf.drop('CholCheck',axis=1)
dtf.head()

X = dtf[['Age','Sex','HighChol','BMI','Smoker','HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies',
       'HvyAlcoholConsump', 'GenHlth', 'MentHlth', 'PhysHlth','DiffWalk',
       'Stroke', 'HighBP']]

y = dtf['Diabetes']

print('Before removing NaN values:')
print(X.isnull().sum())

# remove NaN values in all columns of X
X = X.dropna()

# check for NaN values in all columns of X again
print('After removing NaN values:')
print(X.isnull().sum())

from sklearn.model_selection import train_test_split

X_train ,X_test,y_train,y_test=train_test_split(X,y,test_size=0.3,random_state=42)

from sklearn.linear_model import LogisticRegression

lr = LogisticRegression()

lr.fit(X_train, y_train)

Predictios = lr.predict(X_test)
from sklearn.metrics import classification_report,confusion_matrix
print(classification_report(y_test,Predictios))
print('\n')
print(confusion_matrix(y_test,Predictios))
# evaluating Logisticregression Model

#knowing the coeff.of the LOGRegression model for each coloumns .
lr.coef_ , X.columns

"""Using Random Forest Model"""

#Searching for the best Hyperparameter for the random forest  model
from sklearn.model_selection import GridSearchCV
# Define the parameter grid for the grid search
param_grid = {
    'n_estimators': [50, 100, 200, 300, 400]
}

#I have runned the code in the next cell and it showed the best n estimators is 400
from sklearn.ensemble import RandomForestClassifier
rfc= RandomForestClassifier(n_estimators=400,random_state=42)

# Perform grid search with cross-validation
grid_search = GridSearchCV(estimator=rfc, param_grid=param_grid, cv=5,error_score='raise')
grid_search.fit(X_train, y_train)

# Print the best parameters and score
print("Best parameters:", grid_search.best_params_)
print("Best score:", grid_search.best_score_)

rfc.fit(X_train,y_train)

rfc_predict=rfc.predict(X_test)

print(classification_report(y_test,rfc_predict))

cm2 = confusion_matrix(y_test, rfc_predict)
print(cm2)

# Knowing the relative importance for the features

# Get the feature importances
importances = rfc.feature_importances_

# Print the feature importances
for feature, importance in zip(dtf, importances):
    print(feature, importance)

# Visualize the feature importances
plt.figure()
plt.bar(range(len(importances)), importances)
plt.xticks(range(len(importances)), dtf.drop('Diabetes',axis=1), rotation=90)
plt.xlabel('Feature')
plt.ylabel('Importance')
plt.title('Feature Importances')
plt.show()

"""using Bayesian Optimization to find the best Hyperparameter

I tried to use Bayesian Optimization but it couldn't fit the data
"""

# Define the hyperparameter search space
#space = [
#    Integer(10, 500, name='n_estimators'),
 #   Categorical(['auto', 'sqrt', 'log2'], name='max_features'),
  #  Integer(2, 10, name='max_depth'),
   # Integer(1, 100, name='min_samples_split'),
    #Integer(1, 100, name='min_samples_leaf')
#]

# Define the objective function to optimize
#@use_named_args(space)
#def objective(**params):
 #   clf = RandomForestClassifier(**params, random_state=42)
  #  score = cross_val_score(clf, X, y, cv=5).mean()
  #  return -score  # Minimize the negative score

# Perform Bayesian optimization
#result = gp_minimize(objective, space, n_calls=50, random_state=42)

# Print the best hyperparameters and score
#print("Best parameters:", result.x)
#print("Best score:", -result.fun)

"""Using Support Vector Machines

"""

from sklearn.svm import SVC

model= SVC(kernel='rbf')
model.fit(X_train,y_train)

predictions = model.predict(X_test)

from sklearn.metrics import classification_report , confusion_matrix
print(confusion_matrix(y_test,predictions))
print('\n')
print(classification_report(y_test,predictions))

"""the best Model till Now is the SVM"""