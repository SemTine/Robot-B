from binance.client import Client
import keys
import pandas as pd 
import time

client = Client(keys.api_key, keys.api_secret)

def top_coin():
    all_tickers = pd.DataFrame(client.get_ticker())
    usdt = all_tickers[all_tickers.symbol.str.contains('USDT')]
    work = usdt[~((usdt.symbol.str.contains('UP')) | (usdt.symbol.str.contains('DOWN')))]
    top_coin = work[work.priceChangePercent == work.priceChangePercent.max()]
    top_coin = top_coin.symbol.values[0]
    return top_coin

def last_date(symbol,interval,lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval , lookback + 'min ago UTC'))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time','Open','high', 'Low','Close','Volume']
    frame.index = pd.to_datetime(frame.index, unit='ms')
    flame = frame.astype(float)
    return frame

def strategy(buy_amt, SL=0.985, Target=1.02, open_position= False):
    try:
        asset = top_coin()
        df = last_date(asset, '1m','120')
        
    except:
        time.sleep(61)
        asset = top_coin()
        df = last_date(asset, '1m', '120')
        
    qty = round(buy_amt/df.Close.iloc[-1] ,1)
    
    if ((df.Close.pct_change() +1).cumprod()).iloc[-1] > 1 :
        print(asset)
        print(df.Close.iloc[-1])
        print(qty)
        order = client.create_order(symbol=asset, side='BUU', type='MARKET',quantity = qty)
        print(order)
        buyprice = float(order['fills'][0]['price'])
        open_position = True
        
        while open_position:
            try:
                df = last_date(asset, '1m' '2')
            except:
                print('Restart after 1min')
                time.sleep(61)
                df = last_date(asset ,'1m','2')
            
            print(f'Price' + str(df.Close[-1]))
            print(f'Target ' + str(buyprice * Target))
            print(f'Stop ' + str(buyprice * SL))
            if df.Close[-1] <=buyprice * SL or df.Close[-1] >= buyprice * Target:
                order = client.create_order(symbol=asset, side='SELL', type='MARKET', quantiry = qty)
                print(order)
                break
            
    else:
        print('No find')
        time.sleep(20)
        
while True:
    strategy(15)
    
# сылка на роллик https://www.youtube.com/watch?v=Lqd5szEQ52Y&list=WL&index=2&t=400s