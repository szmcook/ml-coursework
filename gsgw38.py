# import numpy # for data manipulation
import pandas as pd # for data manipulation and .describe()
# import matplotlib # for visualisation
# import sklearn # for model training


# load the data
# cov = pd.read_csv("datasets/latestdata.csv") # original
# cov = pd.read_csv("datasets/smaller.csv") # without the irrelevant columns
# cov = pd.read_csv("datasets/outcome.csv") # only rows with an outcome entry (307382)

# print(cov.count()) # print(cov["sex"].describe() # also good

# Ideally I"d like to do this
fields = ["age", "sex", "outcome", "date_admission_hospital", "date_onset_symptoms", "country"] # 228 rows

# Interesting problems which don't have quite enough data
fields = ["outcome", "date_admission_hospital", "date_onset_symptoms"] # 234 rows
fields = ["outcome", "date_admission_hospital", "date_confirmation"] # 262 rows
fields = ["outcome", "date_confirmation", "date_onset_symptoms"] # 3505 rows


# The problem I intend to solve
fields = ["outcome", "age", "sex", "date_confirmation", "date_onset_symptoms", "country"] # 3493 rows - mostly from the phillipines
# Without the dates - worth having a look into
# fields = ["outcome", "country", "age", "sex"] # 33599 rows

# drop the columns which aren"t in the fields we want
# dataset = cov[fields]
# # drop the rows which are missing information
# dataset = dataset.dropna(subset=fields)
# # store the set
# dataset.to_csv("datasets/dataset1.csv")

dataset = pd.read_csv('datasets/dataset1.csv')

# Data cleaning
# The outcome column contains a lot of dubious information so let's tidy it up.
dataset = dataset.replace(to_replace={'outcome': {
    'death':'died',
    'Deceased':'died',
    'dead':'died',
    'stable':'hospitalized',
    'treated in an intensive care unit (14.02.2020)':'hospitalized', # drop
    'Symptoms only improved with cough. Currently hospitalized for follow-up.':'hospitalized', # drop
    'severe':'hospitalized',        # drop these
    'Hospitalized':'hospitalized',
    'discharge':'recovered',
    'discharged':'recovered',
    'Discharged':'recovered',
    'Alive':'recovered',
    }})

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

dataset['age'].value_counts()

dataset = dataset.drop(columns=['Unnamed: 0'])

gaps = []
from datetime import date, datetime, timedelta
for i in range(len(dataset['date_confirmation'])):
    dataset['date_confirmation'][i] = datetime.strptime(dataset['date_confirmation'][i], r'%d.%m.%Y')
    dataset['date_onset_symptoms'][i] = datetime.strptime(dataset['date_onset_symptoms'][i], r'%d.%m.%Y')
    gaps.append(dataset['date_confirmation'][i] - dataset['date_onset_symptoms'][i])

dataset['days_waiting'] = gaps

dataset = dataset.drop(columns=['date_confirmation', 'date_onset_symptoms'])

dataset.to_csv('datasets/dataset1_clean_outcome.csv')

## encode features as integers
features = dataset[['days_waiting', 'age', 'sex', 'country']]
labels = dataset['outcome']

features = features.replace(to_replace={'sex': {
    'male':0,
    'female':1
}})
features['days_waiting'] = features['days_waiting'].dt.days

## return dataframes
# features.drop(features.loc[features['country'] in ['Angola', 'Gambia', 'South Korea', 'Brazil', 'Canada','Gabon','Romania','Nepal','France','India','Germany','Cabo Verde','Central African Republic']].index, inplace=True)
countries_df = pd.get_dummies(features['country'])
age_df = pd.get_dummies(features['age'])
features = pd.concat([features, countries_df, age_df], axis=1)
features = features.drop(columns=['country', 'age'])

labels = labels.replace({
    'died':0,
    'hospitalized':1,
    'recovered':2
})

print(features.head)

### Model training 

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.1, random_state=0)


from sklearn import svm

clf = svm.SVC()
clf.fit(X_train, y_train)

# print(clf.predict( [[15,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0]] ))

def person_encode(days_waiting, sex, country, age):
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

print(clf.predict([ person_encode(22, 1, 'Japan', '80-89') ]))