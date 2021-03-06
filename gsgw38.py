# import numpy # for data manipulation
import pandas as pd # for data manipulation and .describe()
# import matplotlib # for visualisation
# import sklearn # for model training


# load the data
# cov = pd.read_csv("latestdata.csv") # original
# cov = pd.read_csv("smaller.csv") # without the irrelevant columns
cov = pd.read_csv("outcome.csv") # only rows with an outcome entry (307382)

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
dataset = cov[fields]
# drop the rows which are missing information
dataset = dataset.dropna(subset=fields)
# store the set
dataset.to_csv("dataset1.csv")

dataset = pd.read_csv('dataset1.csv')

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

dataset.to_csv('dataset1_clean_outcome.csv')