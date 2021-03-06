# -*- coding: utf-8 -*-
"""Keras Course.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-wtFvQf_QQAfdUI99oBq4EU88RFpfVWz
"""

import numpy as np
from random import randint
from sklearn.utils import shuffle
from sklearn.preprocessing import MinMaxScaler
import os

if not os.path.isdir('Properties_philly_Kraggle_v2.csv'):
  print(os.listdir("/content"))

# philly_properties = np.genfromtxt('Properties_philly_Kraggle_v2.csv', delimiter=',')

"""Read in table to Pandas Dataframe"""

import pandas as pd
# df=pd.read_csv('Properties_philly_Kraggle_v2.csv', sep=',')
df=pd.read_csv('Properties_philly_Kraggle_v2.csv', sep=',', index_col=False)
df.dropna(inplace=True)
df.reset_index()
df.values

"""Remove last index of n/a data"""

# Fix index after dropna
df = df[:-1]

"""Drop columns that are not needed"""

df.drop(['Address', 'Opening Bid', 'Book/Writ', 'OPA', 'Ward', 'Sheriff Cost', 'Advertising', 'Other', 'Record Deed', 'Zillow Estimate', 'Sale Date', 'Zillow Address', 'Attorney', 'Seller', 'Buyer'], axis=1, inplace=True)

"""Rename oddly formatted columns"""

df.rename(columns={'finished \n(SqFt)':'SqFt', 
                   'Sale Price/bid price': 'Sale Price', 
                   'Zillow Address': 'Address', 
                   ' bedrooms ': 'bedrooms', 
                   ' Avg Walk&Transit score  ': 'Avg Walk&Transit score',
                   ' Violent Crime Rate ': 'Violent Crime Rate',
                   ' School Score  ': 'School Score',
                   ' bathrooms ': 'bathrooms'}, inplace=True)

df.columns

"""## Analyze Sale Prices
And classify data into quantiles
"""

prices = df['Sale Price']
# prices.values
prices = prices.to_numpy()
prices_int = []
for price in prices:
  prices_int.append(int(price[1:].replace(',', '')))
prices = np.array(prices_int)
prices[1]

import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = [17.50, 13.50]
plt.rcParams["figure.autolayout"] = True

prices_index = np.array(list(range(prices.size)))

plt.title("Graph of Sale Price Data")
plt.plot(prices_index, prices, color="green")

plt.show()

quartile_0 = min(prices) 
quartile_1 = np.quantile(prices, .25)
quartile_2 = np.quantile(prices, .50)
quartile_3 = np.quantile(prices, .75)
quartile_4 = max(prices)
print(quartile_0, quartile_1, quartile_2, quartile_3, quartile_4)

Sales_price_category = []
for price in prices:
  if price < quartile_1:
    Sales_price_category.append(float(0))
  elif price < quartile_2:
    Sales_price_category.append(float(1))
  elif price < quartile_3:
    Sales_price_category.append(float(2))
  else:
    Sales_price_category.append(float(3))
Sales_price_category[-10:]

df['Sales Price Category'] = Sales_price_category
df.drop(columns=['Sale Price'], inplace=True)
df[-10:]

"""## Pre process data for the Nerual Network"""

# df.drop(columns=['Address', 'Attorney', 'Seller', 'Buyer'], inplace=True)

PropType = df['PropType']
prop_types = set()
for prop in PropType:
  prop_types.add(prop)
prop_types = list(prop_types)
new_prop = list()
for prop in PropType:
  new_prop.append(float(prop_types.index(prop)))
df['PropType'] = new_prop

"""Account for errror fields in the tables"""

df = df[df['bathrooms'] != ' -   ']
df = df[df['bedrooms'] != ' -   ']
df = df[df['Avg Walk&Transit score'] != ' -   ']
df = df[df['Violent Crime Rate'] != ' -   ']
df = df[df['School Score'] != ' -   ']
df = df.astype({'bathrooms': float, 'bedrooms': float})

for column_name in ['Rent Estimate', 'taxAssessment', 'Average comps']:
  new_col = list()
  for cell in df[column_name]:
    new_col.append(float(cell.replace(',', '')))
  df[column_name] = new_col

df.dtypes

df = df.sample(frac = 1)
train_samples = df[:500].drop(columns=['Sales Price Category'])
train_labels = df[:500]['Sales Price Category']
test_samples = df[500:].drop(columns=['Sales Price Category'])
test_labels = df[500:]['Sales Price Category']

train_samples

train_samples = train_samples.to_numpy()
train_labels = train_labels.to_numpy()
test_samples = test_samples.to_numpy()
test_labels = test_labels.to_numpy()

train_samples.dtype

"""## Building the neural network model"""

model = None

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import categorical_crossentropy

model = Sequential([
    Dense(units=16, input_shape=(14,), activation='relu'),
    Dense(units=32, activation='relu'),
    Dense(units=4, activation='softmax')
])

model.summary()

model.compile(optimizer=Adam(learning_rate=0.0001),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy']
)

model.fit(x=train_samples,
          y=train_labels, validation_split=0.1,
          batch_size=10,
          epochs=200,
          shuffle=True,
          verbose=2
)

predictions = model.predict(x=test_samples, batch_size=10, verbose=1)

for i in predictions:
    print(i)

rounded_predictions = np.argmax(predictions, axis=-1)

for i in rounded_predictions:
    print(i)

"""# Confusion Matrix"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
from sklearn.metrics import confusion_matrix
import itertools
import matplotlib.pyplot as plt

cm = confusion_matrix(y_true=test_labels, y_pred=rounded_predictions)

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

cm_plot_labels = ['quartile 1','quartile 2', 'quartile 3', 'quartile 4']
plot_confusion_matrix(cm=cm, classes=cm_plot_labels, title='Confusion Matrix')

"""# Analysis of the confusion Matrix

It would appear that the house prices that are hardest to predict for the model are the Level 2/4 ones -- not the worst but not good.
This is partly a result of the distribution of the data into 4 arbitrary categories. However it is clear that the model can predict the cheapest and most expensive houses with some ease.

"""