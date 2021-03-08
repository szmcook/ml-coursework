#### IMPORTS ####
import pandas as pd # for data manipulation and .describe()

#### READ IN DATA ####
cov = pd.read_csv("datasets/latestdata.csv") # original (can be switched out for smaller or outcome to run quicker)

# Inspect data
# print(cov.count()) # print(cov["sex"].describe() # also good

#### SELECT ONLY THE RELEVANT COLUMNS ####
# Interesting problems which don't have quite enough data
# fields = ["age", "sex", "outcome", "date_admission_hospital", "date_onset_symptoms", "country"] # 228 rows
# fields = ["outcome", "date_admission_hospital", "date_onset_symptoms"] # 234 rows
# fields = ["outcome", "date_admission_hospital", "date_confirmation"] # 262 rows
# fields = ["outcome", "date_confirmation", "date_onset_symptoms"] # 3505 rows

# Identify the columns required for the problem
fields = ["outcome", "age", "sex", "date_confirmation", "date_onset_symptoms", "country"] # 3493 rows - mostly from the phillipines
# Without the dates - worth having a look into
# fields = ["outcome", "country", "age", "sex"] # 33599 rows

# Select these columns from the dataset
dataset = cov[fields]


#### DATA CLEANING ####
 
# Drop the rows which are missing information
dataset = dataset.dropna(subset=fields)

# Store the set for future use
dataset.to_csv("datasets/dataset1.csv")
# Load the dataset if not doing the earlier steps
dataset = pd.read_csv('datasets/dataset1.csv')


# The outcome column contains a lot of different variations on three values.
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

# Drop the unnamed column
dataset = dataset.drop(columns=['Unnamed: 0'])

# Calculate the time that patients were waiting and store this in a new column (replacing the previous dates)
gaps = []
from datetime import date, datetime, timedelta
for i in range(len(dataset['date_confirmation'])):
    dataset['date_confirmation'][i] = datetime.strptime(dataset['date_confirmation'][i], r'%d.%m.%Y')
    dataset['date_onset_symptoms'][i] = datetime.strptime(dataset['date_onset_symptoms'][i], r'%d.%m.%Y')
    gaps.append(dataset['date_confirmation'][i] - dataset['date_onset_symptoms'][i])

dataset['days_waiting'] = gaps
dataset = dataset.drop(columns=['date_confirmation', 'date_onset_symptoms'])

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
features['days_waiting'] = features['days_waiting'].dt.days

# Use one hot encoding for the age and the country # TODO IS THERE A BETTER WAY OF ENCODING THESE?
countries_df = pd.get_dummies(features['country'])
age_df = pd.get_dummies(features['age'])
features = pd.concat([features, countries_df, age_df], axis=1)
features = features.drop(columns=['country', 'age'])

# Encode the labels with integers
labels = labels.replace({
    'died':0,
    'hospitalized':1,
    'recovered':2
})


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


# Import and fit a Support Vector Machine
from sklearn import svm
clf = svm.SVC()
clf.fit(X_train, y_train)

# TODO train 2 more types of model - naive bayes and logistic regression?

#### MODEL EVALUATION
print(clf.predict([ person_encode(22, 1, 'Japan', '80-89') ]))

