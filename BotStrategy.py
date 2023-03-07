import pandas as pd
from binance import Client
from datetime import datetime
import numpy as np
import os

import pytz
from MachineLearning import engine, MachineLearning
from binance.helpers import round_step_size


symbol = "BTCBUSD"

# --- GET THE PREDICTION FOR TODAY ---
ml = MachineLearning()
shouldInvest = ml.getPrediction()


class BotStrategy:

    def addTrade(self, side, price,quantity,profit,closed_at,created_at) -> None:
        if closed_at == 'NA' : closed_at = created_at
        try :
            sql_query = \
                """
                INSERT INTO bot_trade (id,side,price,quantity,amount,profit,created_at,closed_at,user_id)
                VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            values = (side,float(price),quantity,"%.4f" %(float(price)*quantity),profit,created_at,closed_at,self.user_id)
            self.read_query(sql_query,values)
        except Exception as error : print(f"[{datetime.utcnow()}]  ADD TRADE ERROR - user id {self.user_id} - : {error}")

    def getBuyInfo(self) -> float:

        # GET SYMBOL QUANTITY
        info = self.client.get_symbol_info(symbol=symbol)
        lotSize = float([i for i in info['filters'] if i['filterType'] == 'LOT_SIZE'][0]['minQty'])
        quantity = round((round(self.cash / self.getMostRecentPrice() / lotSize) * lotSize), 7)
        return round_step_size(quantity,8)

    def buyOrder(self):
        try :
            # add a line to logs
            print(f"[{datetime.utcnow()}]  BUY ORDER - user {self.user_id}")

            # FIRST BUY ORDER
            quantity = self.getBuyInfo()
            buyOrder = self.client.order_market_buy(symbol="BTCBUSD", quantity = quantity)
            
            if buyOrder['fills']:
                buyOrderPrice = buyOrder['fills'][0]['price']
                # UPDATE TradesDatabase
                self.addTrade('BUY',buyOrderPrice,quantity,0,'NA',pd.Timestamp(buyOrder['transactTime'],unit='ms',tzinfo=pytz.UTC))

        except Exception as error : print(f"[{datetime.utcnow()}]  BUY ORDER error - user {self.user_id} : {error}")

    def updateTradeDate(self,id,closeDate) -> None:
        try :
            sql_query = "UPDATE bot_trade SET closed_at = %s WHERE id = %s"
            values = (closeDate,id)
            self.read_query(sql_query,values)
        except Exception as error : print(f"[{datetime.utcnow()}]  UPDATE TRADE DATE error : {error}")

    def sellOrder(self):
        print(f"[{datetime.utcnow()}]  SELL SESSION - bot id {self.bot_id} (session {self.currentSession}) : {symbol}")
        try :
            previousBuyQuantity = self.latest_trade.quantity
            previousBuyAmount = self.latest_trade.amount
            sellOrder = self.client.order_market_sell(symbol=symbol, quantity = previousBuyQuantity)  # EX SELL : {'symbol': 'BTCUSDT', 'orderId': 11780057473, 'orderListId': -1, 'clientOrderId': '8Hl1wOIB79OvUFKpHBfFpW', 'transactTime': 1658437986625, 'price': '0.00000000', 'origQty': '0.00240000', 'executedQty': '0.00240000', 'cummulativeQuoteQty': '55.43064000', 'active': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'SELL', 'fills': [{'price': '23096.10000000', 'qty': '0.00240000', 'commission': '0.00000000', 'commissionAsset': 'BNB', 'tradeId': 1504113799}]} # IF ERROR : binance.#exceptions.BinanceAPI#exception: APIError(code=-2010): Account has insufficient balance for requested action.

            if sellOrder['fills']:

                sellOrderPrice = float(sellOrder['fills'][0]['price'])
                sellOrderQty = previousBuyQuantity
                profit = (sellOrderPrice * sellOrderQty) - previousBuyAmount
                sellOrderDate = pd.Timestamp(sellOrder['transactTime'],unit='ms',tzinfo=pytz.UTC)

                self.updateTradeDate(self.latest_trade.id,sellOrderDate) # -> UPDATE TradesDatabase (previous trade - closed_at)

                # ADD NEW SELL ORDER
                self.addTrade('SELL',sellOrderPrice,sellOrderQty,profit,sellOrderDate,sellOrderDate)

        except Exception as error : print(f"[{datetime.utcnow()}] SELL ORDER error - user {self.user_id}: {error}")

    def __init__(self, user_id:int) -> None:
        
        self.user_id = user_id

        # --- GET USER ---
        self.user = pd.read_sql_table('bot_user', engine , index_col='id').query('id == @user_id')
        api_key = self.user.api_key.values[0]
        api_secret = self.user.api_secret.values[0]
        self.client = Client(api_key,api_secret)

        # --- get lastest trade ---
        self.latest_trade = pd.read_sql("bot_trade",engine).query("user_id == @user_id").sort_values('created_at').iloc[-1]

        if shouldInvest :
            if not self.latest_trade or self.latest_trade.side == 'SELL' : 
                self.buyOrder() # invest in BTC
        elif self.latest_trade.side == 'BUY' : 
            self.sellOrder() # close the open position to sell


users_id = pd.read_sql("bot_user",engine).query('active == True')['id'].tolist()

# --> BOT STRATEGY : Apply strategy for all active bots (eg. if active is True) 
for i in range(len(users_id)): BotStrategy(users_id[i])