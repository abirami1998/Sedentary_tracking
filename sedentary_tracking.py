# -*- coding: utf-8 -*-
"""Sedentary_tracking.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12DXr8dAGKwoXZpM2CeqIAUqki76o2TV_
"""

import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Flatten,Dense,Dropout,BatchNormalization
from tensorflow.keras.layers import Conv2D,MaxPool2D
from tensorflow.keras.optimizers import Adam
print(tf.__version__)



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler,LabelEncoder

file=open('WISDM_ar_v1.1_raw.txt')
lines=file.readlines()

processedList=[]

for i,line in enumerate(lines):
  try:
    line=line.split(',')
    last=line[5].split(',')[0]
    last=last.strip()
    if last=='':
        break;
    temp=  [line[0],line[1],line[2],line[3],line[4],last]
    processedList.append(temp)
  except:
    print('Error at',i)

columns=['user','activity','time','x','y','z']

data=pd.DataFrame(data=processedList,columns=columns)
data.head()

data.shape

data.info()

data.isnull().sum()

data['activity'].value_counts()

#To avoid overfitting, balance the data

data['x']=data['x'].astype('float')
data['y']=data['y'].astype('float')
#data['z']=data['z'].astype('float')

Fs=20

df=data.drop(['user','time'],axis=1).copy()
df.head()

Walking=df[df['activity']=='Walking'].head(3555).copy()
Jogging=df[df['activity']=='Jogging'].head(3555).copy()
Upstairs=df[df['activity']=='Upstairs'].head(3555).copy()
Downstairs=df[df['activity']=='Downstairs'].head(3555).copy()
Sitting=df[df['activity']=='Sitting'].head(3555).copy()
Standing=df[df['activity']=='Standing'].head(3555).copy()

balanced_data=pd.DataFrame()
balanced_data=balanced_data.append([Walking,Jogging,Upstairs,Downstairs,Sitting,Standing])
balanced_data.shape

balanced_data.head()

balanced_data['x']=balanced_data['x'].astype('float')
balanced_data['y']=balanced_data['y'].astype('float')
#balanced_data['z']=balanced_data['z'].astype('float')

from sklearn.preprocessing import LabelEncoder

label=LabelEncoder()
balanced_data['label']=label.fit_transform(balanced_data['activity'])
balanced_data.head()

x=balanced_data[['x','y']]
y=balanced_data['label']

scaler=StandardScaler()
x=scaler.fit_transform(x)

scaled_x=pd.DataFrame(data=x,columns=['x','y'])
scaled_x['label']=y.values

scaled_x

import scipy.stats as stats

Fs=20
frame_size=Fs*4  #80
hop_size=Fs*2

def get_frame(df,frame_size,hop_size):
  N_FEATURES=2

  frames=[]
  labels=[]
  for i in range(0,len(df)-frame_size,hop_size):
    x=df['x'].values[i:i+frame_size]
    y=df['y'].values[i:i+frame_size]

    label=stats.mode(df['label'][i:i+frame_size])[0][0]
    frames.append([x,y])
    labels.append(label)


  frames=np.asarray(frames).reshape(-1,frame_size,N_FEATURES)
  labels=np.asarray(labels)

  return frames,labels

x,y=get_frame(scaled_x,frame_size,hop_size)

x.shape

x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2,random_state=0,stratify=y)

x_test.shape

x_train=x_train.reshape(425,80,2,1)
x_test=x_test.reshape(107,80,2,1)

x_train[0].shape,x_test[0].shape

#MODEL BUILD

model=Sequential()
model.add(Conv2D(16,(2,1),activation='relu',input_shape=x_train[0].shape))
model.add(Dropout(0.1))

model.add(Conv2D(32,(2,1),activation='relu'))
model.add(Dropout(0.2))

model.add(Flatten())
model.add(Dense(64,activation='relu'))
model.add(Dropout(0.5))

model.add(Dense(6,activation='softmax'))

model.compile(optimizer=Adam(learning_rate=0.001),loss='sparse_categorical_crossentropy',metrics=['accuracy'])

history=model.fit(x_train,y_train,epochs=35,validation_data=(x_test,y_test),verbose=1)

model.save_weights('model.py')

final=model.save('Final_model(1).h5')

model.predict_classes(x_test[:6])

y_test[:6]

score=model.evaluate(x_test,y_test)

def plot_learningCurve(history,epochs):
  epoch_range=range(1,epochs+1)
  plt.plot(epoch_range,history.history['accuracy'])
  plt.plot(epoch_range,history.history['val_accuracy'],scalex=0.5)
  plt.title('Model Accuracy')
  plt.ylabel('Accuracy')
  plt.xlabel('Epochs')
  plt.legend([ 'train','Val'],loc='upper left')
  plt.show

plot_learningCurve(history,35)

#Confusion Matrix

from mlxtend.plotting import plot_confusion_matrix
from sklearn.metrics import confusion_matrix

y_pred=model.predict_classes(x_test)

y_pred

mat=confusion_matrix(y_test,y_pred)
plot_confusion_matrix(conf_mat=mat,show_normed=True,figsize=(7,7))

