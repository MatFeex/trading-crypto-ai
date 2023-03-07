import pandas as pd
from binance import Client
from datetime import datetime
import numpy as np
from sklearn.linear_model import LogisticRegression
from sqlalchemy import create_engine
import os
from env import API_KEY_ADMIN, API_SECRET_ADMIN

engine = create_engine("sqlite:///" + os.getcwd() + "/frontend/database.db")


class MachineLearning:

    def lagReturns(self, df, lags): 
        for i in range(1,lags+1):
            df[f'lag_{i}'] = df['returns'].shift(i)
        return [f'lag_{i}' for i in range(1, lags+1)]
    
    
    def getPrediction(self) -> bool:
        df = self.df

        # "RETURNS" :  the percentage change from previous day (close column considered)
        df['returns'] = df.close.pct_change() # relative price change on the current time frame (1 day)

        # "DIRECTION" : translate returns into binary results
        df['direction'] = np.where(df.returns > 0,1,0) # 1 if positive returns and 0 otherwise

        # "LAGGED RETURNS" : add the n_lags previous returns next to the current one in a dataframe
        features = self.lagReturns(df,2) # add 2 lagged returns
        df.dropna(inplace=True) # drop NaN rows

        # VARIABLES to provide
        x = df[features] # independent variables - dataframe of n lagged returns
        y = df['direction'] # dependent var - dataframe of the directions ( 0 or 1 )

        # Setting up the Machine Learning Model
        self.model = LogisticRegression(class_weight='balanced')
        self.model.fit(x,y) # train the model with corresponding dataset

        # From Machine Learning (Logistic Regression):
        # ----> GET THE PREDICTIONS ---
        df['prediction_LR'] = self.model.predict(x)
        shouldInvest = True if df['prediction_LR'].iloc[-1] == 1 else False

        return shouldInvest


    def getHistoricalData(self, start, end) -> pd.DataFrame :

        data = pd.DataFrame(self.client.get_historical_klines("BTCBUSD", Client.KLINE_INTERVAL_1DAY, str(start), str(end)))

        # format columns name
        data.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume','close_time', 'qav', 'num_trades','taker_base_vol', 'taker_quote_vol', 'ignore']
        data.index = [datetime.fromtimestamp(x/1000.0) for x in data.datetime]

        return data.astype(float)


    def __init__(self):

        # --- init Binance Client API ---
        self.client = Client(API_KEY_ADMIN, API_SECRET_ADMIN)

        # --- get data ---
        start = datetime(2020,1,1)
        end = datetime.utcnow()
        self.df = self.getHistoricalData(start, end)









"""

data = pd.DataFrame(client.get_historical_klines("BTCBUSD", Client.KLINE_INTERVAL_1DAY, str(datetime(2020,1,1)), str(datetime.utcnow())))

#format columns name
data.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume','close_time', 'qav', 'num_trades','taker_base_vol', 'taker_quote_vol', 'ignore']
data.index = [datetime.fromtimestamp(x/1000.0) for x in data.datetime]
df = data.astype(float)

# "RETURNS" :  the percentage change from previous day (close column considered)
df['returns'] = df.close.pct_change() # relative price change on the current time frame 

# "DIRECTION" : translate returns into binary results
df['direction'] = np.where(df.returns > 0,1,0) # 1 if returns > 0 and 0 otherwise

df.direction.value_counts() # check the balance between both sides

# "LAGGED RETURNS" : add the n_lags previous returns next to the current one in a dataframe

def lagReturns(df, lags): 
    for i in range(1,lags+1):
        df[f'lag_{i}'] = df['returns'].shift(i)
    return [f'lag_{i}' for i in range(1, lags+1)]

features = lagReturns(df,2) # add 2 lagged returns
df.dropna(inplace=True) # drop NaN rows

x = df[features] # indep var - dataframe of n lags

y = df['direction'] # dependent var - dataframe of the directions ( 0 or 1 )

# Setting up the Machine Learning Model
model = LogisticRegression(class_weight='balanced')
model.fit(x,y)

# Make the predictions from the logistic regression model
df['prediction_LR'] = model.predict(x)

# The model will show 1 if we should be in the market and 0 if we shouldn't

# This strategy is getting a return if the prediction return 1 because we are in the market
# If the strategy predicted 0, we are not in the market so no returns

df['strategy_returns'] = df['prediction_LR'] * df.returns
df

# Evaluate the performance
# We need to compare the returns from the strategy and the returns from Bitcoin itself
(df[['strategy_returns','returns']] + 1).cumprod()

# RESULTS : great performance 
# BUT - The model is trained on the whole dataset - overfitted model

# To do a realistic backtest, we need to train the model with a prior dataset than the one for backtest
# And check if the model is still outpermorming Bitcoin on newer data

from sklearn.model_selection import train_test_split

# Set indep & dependent variables to train the model AND to backtest
# NB : test_size = 0.3 ==> 30% data used to backtest & 70% ==> train the model
# NB : shuffle = False because we have a time serie - order matter

x_train, x_backtest, y_train, y_backtest = train_test_split(x,y,test_size=0.3, shuffle=False)

model.fit(x_train,y_train) # train the model with corresponding dataset

x_backtest['prediction_LR'] = model.predict(x_backtest)

x_backtest['returns'] = df.returns[x_backtest.index[0]:]
x_backtest['strategy_returns'] = x_backtest['prediction_LR'] * x_backtest.returns


(x_backtest[['strategy_returns','returns']] + 1).cumprod()


"""