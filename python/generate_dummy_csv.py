import pandas as pd
import numpy as np

rows = []
price = 1.1000
for i in range(3000):  # 3000 bars for enough history
    high = price + np.random.uniform(0, 0.0005)
    low = price - np.random.uniform(0, 0.0005)
    close = low + np.random.uniform(0, high - low)
    open_price = price
    rows.append([f"2025-10-07 00:{i//60:02d}:{i%60:02d}", open_price, high, low, close, np.random.randint(100, 200)])
    price = close

df = pd.DataFrame(rows, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
df.to_csv("EURUSD_1min.csv", index=False)
print("Dummy EURUSD CSV generated successfully.")
