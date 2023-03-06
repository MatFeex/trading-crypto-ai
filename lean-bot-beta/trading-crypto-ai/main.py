from AlgorithmImports import *
from keras.models import Sequential
import json
import numpy as np


class SmoothSkyBlueMosquito(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 1, 1)  # Set Start Date
        self.SetEndDate(2020, 1, 1)  # Set Start Date
        
        # Get model
        model_key = 'bitcoin_price_predictor'
        if self.ObjectStore.ContainsKey(model_key):
            model_str = self.ObjectStore.Read(model_key)
            config = json.loads(model_str)['config']
            self.model = Sequential.from_config(config)

        self.SetCash(100000)  # Set Strategy Cash
        self.SetBrokerageModel(BrokerageName.Bitfinex, AccountType.Margin)  # Crypto brokerage
        self.symbol = self.AddCrypto("BTCUSD", Resolution.Daily).Symbol
        self.SetBenchmark(self.symbol) # to compare the strategy with just holding bitcoin


    def OnData(self, data):
        if self.GetPrediction() == "Bullish":  self.SetHoldings(self.symbol, 1)
        else: self.SetHoldings(self.symbol, -0.5)
    
    def GetPrediction(self):

        # instead of history requests, use rolling window for more efficiency
        df = self.History(self.symbol, 40).loc[self.symbol]
        df_change = df[["close", "open", "high", "low", "volume"]].pct_change().dropna()
        model_input = []

        # turn history into right input format for model
        for index, row in df_change.tail(30).iterrows(): model_input.append(np.array(row))
        model_input = np.array([model_input])
        if round(self.model.predict(model_input)[0][0]) == 1: return "Bullish"
        else: return "Bearish"
