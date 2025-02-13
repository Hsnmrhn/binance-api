from binance.client import Client
import pandas as pd
import time
from datetime import datetime
import os

client = Client(None, None)

def fetch_and_save_price():
    price = client.get_symbol_ticker(symbol="BTCUSDT")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    data = {
        'timestamp': [timestamp],
        'price': [float(price['price'])]
    }
    
    df = pd.DataFrame(data)
    
    if os.path.exists('/data/prices.csv'):
        df.to_csv('/data/prices.csv', mode='a', header=False, index=False)
    else:
        df.to_csv('/data/prices.csv', index=False)

while True:
    try:
        fetch_and_save_price()
        time.sleep(300)  # 5 dakika bekle
    except Exception as e:
        print(f"Hata oluştu: {e}")
        time.sleep(10)