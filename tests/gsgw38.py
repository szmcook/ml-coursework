#### IMPORTS ####
import pandas as pd # for data manipulation and .describe()

# #### READ IN DATA ####
# cov = pd.read_csv("datasets/latestdata.csv") # original (can be switched out for smaller or outcome to run quicker)

# # Inspect data
# # print(cov.count()) # print(cov["sex"].describe() # also good

# #### SELECT ONLY THE RELEVANT COLUMNS ####
# # Interesting problems which don't have quite enough data
# # fields = ["age", "sex", "outcome", "date_admission_hospital", "date_onset_symptoms", "country"] # 228 rows
# # fields = ["outcome", "date_admission_hospital", "date_onset_symptoms"] # 234 rows
# # fields = ["outcome", "date_admission_hospital", "date_confirmation"] # 262 rows
# # fields = ["outcome", "date_confirmation", "date_onset_symptoms"] # 3505 rows

# # Identify the columns required for the problem
# fields = ["outcome", "age", "sex", "date_confirmation", "date_onset_symptoms", "country"] # 3493 rows - mostly from the phillipines
# # Without the dates - worth having a look into
# # fields = ["outcome", "country", "age", "sex"] # 33599 rows

# # Select these columns from the dataset
# dataset = cov[fields]


# #### DATA CLEANING ####
 
# # Drop the rows which are missing information
# dataset = dataset.dropna(subset=fields)

# # Store the set for future use
# dataset.to_csv("datasets/dataset1.csv")
# # Load the dataset if not doing the earlier steps
dataset = pd.read_csv('datasets/dataset1.csv')
# Drop the unnamed column
dataset = dataset.drop(columns=['Unnamed: 0'])

# The outcome column contains a lot of different variations on three values.
dataset = dataset.replace(to_replace={'outcome': {
    'death':0,
    'Deceased':0,
    'dead':0,
    'stable':1,
    'treated in an intensive care unit (14.02.2020)':1, # drop
    'Symptoms only improved with cough. Currently hospitalized for follow-up.':1, # drop
    'severe':0,        # drop these
    'Hospitalized':0,
    'discharge':1,
    'discharged':1,
    'Discharged':1,
    'Alive':1,
    }})

# The ages are a mixture of numbers and ranges so we tidy these too
dataset = dataset.replace(to_replace={'age': {
    '^[0-9]$':'0-9',
    '1[0-9][.-]*[0-9]{0,2}':'10-19',
    '2[0-9][.-]*[0-9]{0,2}':'20-29',
    '3[0-9][.-]*[0-9]{0,2}':'30-39',
    '4[0-9][.-]*[0-9]{0,2}':'40-49',
    '5[0-9][.-]*[0-9]{0,2}':'50-59',
    '6[0-9][.-]*[0-9]{0,2}':'60-69',
    '7[0-9][.-]*[0-9]{0,2}':'70-79',
    '8[0-9][.-]*[0-9]{0,2}':'80-89',
    '9[0-9][.-]*[0-9]{0,2}':'90-99',
    }}, regex=True)


# Calculate the time that patients were waiting and store this in a new column (replacing the previous dates)
gaps = []
from datetime import date, datetime, timedelta
for i in range(len(dataset['date_confirmation'])):
    dataset['date_confirmation'][i] = datetime.strptime(dataset['date_confirmation'][i], r'%d.%m.%Y')
    dataset['date_onset_symptoms'][i] = datetime.strptime(dataset['date_onset_symptoms'][i], r'%d.%m.%Y')
    gaps.append(dataset['date_confirmation'][i] - dataset['date_onset_symptoms'][i])

dataset['days_waiting'] = gaps
dataset = dataset.drop(columns=['date_confirmation', 'date_onset_symptoms'])
dataset['days_waiting'] = dataset['days_waiting'].dt.days
dataset = dataset[dataset['days_waiting'] >= 0]

# Save the cleaned up dataset for future use
dataset.to_csv('datasets/dataset1_clean.csv')

#### DATA PREPARATION ####
# Split the data into features and labels
features = dataset[['days_waiting', 'age', 'sex', 'country']]
labels = dataset['outcome']

# One encode the features as integers
features = features.replace(to_replace={'sex': {
    'male':0,
    'female':1
}})


# Use one hot encoding for the age and the country # TODO IS THERE A BETTER WAY OF ENCODING THESE?
countries_df = pd.get_dummies(features['country'])
age_df = pd.get_dummies(features['age'])
features = pd.concat([features, countries_df, age_df], axis=1)
features = features.drop(columns=['country', 'age'])


def person_encode(days_waiting, sex, country, age):
    '''Function to encode the features of a person in the form used for the model'''
    array = [days_waiting]
    if sex == 'male':
        array.append(0)
    else:
        array.append(1)

    countries = ['Angola', 'Brazil', 'Cabo Verde', 'Canada', 'Central African Republic', 'China', 'France', 'Gabon', 'Gambia', 'Germany', 'India', 'Japan', 'Nepal', 'Philippines', 'Romania', 'Singapore', 'South Korea', 'Vietnam']
    array.extend([int(c == country) for c in countries])

    ages = ['0-9', '0.20-29', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99']
    array.extend([int(a == age) for a in ages])
    return array


#### MODEL TRAINING ####
# It may be necessary to sample the dataset to ensure a more balanced set of recovered/vs died results
# Split the data into training and testing
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.1, random_state=0)

# print(labels.value_counts())

# Import and fit a Support Vector Machine
from sklearn import svm
svm_classifier = svm.SVC(gamma='auto')
# In problems where it is desired to give more importance
# to certain classes or certain individual samples, 
# the parameters class_weight and sample_weight can be used.
# parameter class_weight goes in the fit method. 
# It???s a dictionary of the form {class_label : value}
# where value is a floating point number > 0 
# that sets the parameter C of class class_label to 
# C * value.
svm_classifier.fit(X_train, y_train)

# Immport and fit a logistic regression model
from sklearn import linear_model
LR_classifier = linear_model.LogisticRegression(solver='lbfgs', multi_class='multinomial', max_iter=1000)
# There are five solvers that can be used to obtain the weights
LR_classifier.fit(X_train, y_train)

# Import and fit a decision tree
from sklearn import tree
tree_classifier = tree.DecisionTreeClassifier()
tree_classifier.fit(X_train, y_train)

# Import and fit a naive bayes model
from sklearn.naive_bayes import MultinomialNB
nb_classifier = MultinomialNB()
nb_classifier.fit(X_train, y_train)

# import and fit an XGboost model
import xgboost as xgb
xgb_classifier = xgb.XGBClassifier(use_label_encoder=False)
xgb_classifier.fit(X_train, y_train)


#### MODEL EVALUATION ####
svm_predictions = svm_classifier.predict(X_test)
LR_predictions = LR_classifier.predict(X_test)
tree_predictions = tree_classifier.predict(X_test)
nb_predictions = nb_classifier.predict(X_test)
xgb_predictions = xgb_classifier.predict(X_test)

from sklearn import metrics
svm_accuracy = metrics.accuracy_score(y_test, svm_predictions)
LR_accuracy = metrics.accuracy_score(y_test, LR_predictions)
tree_accuracy = metrics.accuracy_score(y_test, tree_predictions)
# random forest
nb_accuracy = metrics.accuracy_score(y_test, nb_predictions)
xgb_accuracy = metrics.accuracy_score(y_test, xgb_predictions)

print(f'SVM score: {svm_accuracy}\nLR score: {LR_accuracy}\nTree score: {tree_accuracy}\nNaive Bayes score: {nb_accuracy}\nXGB score: {xgb_accuracy}')

print(f'Classification report for svm (remember 0:died, 1:hospitalised, 2:recovered (0.805)): \n{metrics.classification_report(y_test, svm_predictions)}')
# These scores are all around the 80% mark.
# I'd like to know what the true and false positive rates are (precision = % of Positives that are correct and recall = % of negatives that are found)
# I think it'll be necessary to adjust the sampling or reweight the inputs
# get rid of hospitalised - they probably recovered
# reweight the died class: for every entry repeat 4 times
# make a few plots such as age/country and days waiting
# Should I be doing k-fold validation? Do I have enough data for that?
# There are also several model parameters that could be tuned