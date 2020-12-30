import numpy as np
import pandas as pd
import yfinance as yf
import pandas_datareader as pdr
import datetime as dt
import matplotlib.pyplot as plt

#Get the Stock Price 
ticker = 'SPY'
current = dt.datetime.now()
start_year = 2018
start_month = 1
start_day = 1

start = dt.datetime(start_year, start_month, start_day)
df = pdr.get_data_yahoo(ticker, start, current)
df

#### Take the current row and comparing it to the one before that.
#Check if the difference is positive or negative

delta = df['Adj Close'].diff(1) #Delta = difference --> taking current row and comparing it to the previous

# Get rid of non number values
delta.dropna(inplace = True)

# Save all positive and negative movements 
positive = delta.copy()
negative = delta.copy()

#Cut off data that is not positive
positive[positive < 0] = 0 # positve values stay the same but negative values have value of zero
negative[negative > 0] = 0 # either have zero or negative value

#Set RSI days(Common amount of days)
days = 14

avg_gain = positive.rolling(window = days).mean() # taking past 14 days and calculating the mean
avg_loss = abs(negative.rolling(window = days).mean()) # absolute difference which becomes positive number

rel_strength = avg_gain / avg_loss
rsi = 100.0 - (100.0 / (1.0 + rel_strength)) #formula for the RSI

combined = pd.DataFrame() #empty data frame
combined['Adj Close'] = df['Adj Close'] 
combined['rsi'] = rsi # will get a bunch of values bc the data is using rolling function and will add below first chart

#First plot for Adj Close of Ticker

plt.figure(figsize=(12.5, 8))
axis1 = plt.subplot(211)
axis1.plot(combined.index, combined['Adj Close'], color ='white')
axis1.set_title('Adjusted Close Price', color = 'white')
axis1.grid(True, color = 'white')
axis1.set_axisbelow(True)
axis1.set_facecolor('black')
axis1.figure.set_facecolor('black')
axis1.tick_params(axis = 'x', colors = 'white')
axis1.tick_params(axis = 'y', colors = 'white')

#Second plot is RSI data and RSI lines

axis2 = plt.subplot(212, sharex = axis1)
axis2.plot(combined.index, combined['rsi'], color = 'white') 
axis2.axhline(0, linestyle = '--', alpha = 1, color = 'red')
axis2.axhline(10, linestyle = '--', alpha = 1, color = 'blue')
axis2.axhline(20, linestyle = '--', alpha = 1, color = 'yellow')
axis2.axhline(30, linestyle = '--', alpha = 1, color = 'green')
axis2.axhline(70, linestyle = '--', alpha = 1, color = 'green')
axis2.axhline(80, linestyle = '--', alpha = 1, color = 'yellow')
axis2.axhline(90, linestyle = '--', alpha = 1, color = 'blue')
axis2.axhline(100, linestyle = '--', alpha = 1, color = 'red')

axis2.set_title('RSI Value')
axis2.grid(False)
axis2.set_axisbelow(True)
axis2.set_facecolor('black')
axis2.tick_params(axis = 'x', colors = 'white')
axis2.tick_params(axis = 'y', colors = 'white')

plt.show()

#Initialize the coloums types we need 
df['Long Tomorrow'] = np.nan
df['Buy Signal'] = np.nan
df['Sell Signal'] = np.nan
df['Buy RSI'] = np.nan
df['Sell RSI'] = np.nan
df['Strategy'] = np.nan

#Create buy and sell indicators for RSI plot
for x in range(15,len(df)):
    if ((combined['rsi'][x] <= 30) & (combined['rsi'][x-1]>30)):
        df['Long Tomorrow'][x] = True
    elif ((df['Long Tomorrow'][x-1] == True) & (combined['rsi'][x] <= 70)):
        df['Long Tomorrow'][x] = True
    else:
        df['Long Tomorrow'][x] = False
    
    if ((df['Long Tomorrow'][x] == True) & (df['Long Tomorrow'][x-1] == False)):
        df['Buy Signal'][x] = df['Adj Close'][x]
        df['Buy RSI'][x] = combined['rsi'][x]
    
    if ((df['Long Tomorrow'][x] == False) & (df['Long Tomorrow'][x-1] == True)):
        df['Sell Signal'][x] = df['Adj Close'][x]
        df['Sell RSI'][x] = combined['rsi'][x]
        
df['Strategy'][15] = df['Adj Close'][15]

for x in range(16, len(df)):
    if df ['Long Tomorrow'][x-1] == True:
        df['Strategy'][x] = df['Strategy'][x-1] * (df['Adj Close'][x] / df['Adj Close'][x-1])
    else:
        df['Strategy'][x] = df['Strategy'][x-1]

df

#First plot for Adj Close of Ticker

plt.figure(figsize=(12.5, 8))
axis1 = plt.subplot(211)
axis1.plot(combined.index, combined['Adj Close'], color ='white')
axis1.set_title('Adjusted Close Price', color = 'white')
axis1.grid(True, color = 'white')
axis1.set_axisbelow(True)
axis1.set_facecolor('black')
axis1.figure.set_facecolor('black')
axis1.tick_params(axis = 'x', colors = 'white')
axis1.tick_params(axis = 'y', colors = 'white')

#Second plot is RSI data and RSI lines

axis2 = plt.subplot(212, sharex = axis1)
axis2.plot(combined.index, combined['rsi'], color = 'grey') 
axis2.axhline(0, linestyle = '--', alpha = 0.5, color = 'red')
axis2.axhline(10, linestyle = '--', alpha = 0.5, color = 'blue')
axis2.axhline(20, linestyle = '--', alpha = 0.5, color = 'yellow')
axis2.axhline(30, linestyle = '--', alpha = 0.5, color = 'green')
axis2.axhline(70, linestyle = '--', alpha = 0.5, color = 'green')
axis2.axhline(80, linestyle = '--', alpha = 0.5, color = 'yellow')
axis2.axhline(90, linestyle = '--', alpha = 0.5, color = 'blue')
axis2.axhline(100, linestyle = '--', alpha = 0.5, color = 'red')

axis2.set_title('RSI Value')
axis2.grid(False)
axis2.set_axisbelow(True)
axis2.set_facecolor('black')
axis2.tick_params(axis = 'x', colors = 'white')
axis2.tick_params(axis = 'y', colors = 'white')

axis2.scatter(df.index, df['Buy RSI'], label = 'Buy', marker = '^', color = 'green')
axis2.scatter(df.index, df['Sell RSI'], label = 'Sell', marker = 'v', color = 'red')
axis2.plot(combined['rsi'], alpha = 1)
plt.show()

#How many Buy Signal trades did we make?
trade_count = df['Buy Signal'].count()

#Was algorithm profitable?
average_profit = ((df['Strategy'][-1]/df['Strategy'][15])**(1/trade_count))-1
avgP = average_profit.round(4)

print('This algorithm concurred', trade_count,'trades.')
print('The average profit per trade was',avgP*100,'%.')
