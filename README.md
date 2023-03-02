# AI - Trading cryptocurrencies - Binance
Trading crypto using artificial intelligence. Exchange : Binance

Getting started :

# Create account on https://www.quantconnect.com/login
Request an ID & API key by email

pip install -r requirements.txt

# To init a project
lean init
lean create-project trading-crypto-ai 

# to update code on the cloud
lean cloud push 

# To backtest the strategy & open results in the server
lean cloud backtest trading-crypto-ai --open
