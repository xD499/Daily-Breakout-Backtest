import pandas as pd

pair = pd.read_csv("Historical Klines/BTCUSDT 1D.csv")[::-1].reset_index(drop=True)
pair.drop(columns=pair.columns.difference(['Date', 'Open', 'High', 'Low', 'Close']), inplace=True)

open_price = pd.to_numeric(pair['Open'])
high_price = pd.to_numeric(pair['High'])
low_price = pd.to_numeric(pair['Low'])
close_price = pd.to_numeric(pair['Close'])
date = pd.to_datetime(pair['Date'], unit='ms')


def input_float(msg, minval, maxval):
    while True:
        inp = input(msg)
        try:
            inp = float(inp)
        except ValueError:
            print("! Please enter a number.")
            continue

        if inp < minval:
            print(f"! Please enter a number >= {minval}")
            continue
        elif inp > maxval:
            print(f"! Please enter a number <= {maxval}")
            continue

        break

    return inp


entry_offset = input_float("Enter the offset for entries (Percent): ", 0.1, 100) / 100
stop_offset = input_float("Enter a stop size (Percent): ", 0.1, 100) / 100
target_offset = input_float("Enter a target size (Percent): ", 0.1, 100) / 100

long_entries = round(high_price * (entry_offset + 1), 2)
long_stops = round(long_entries * (1 - stop_offset), 2)
long_targets = round(long_entries + (target_offset + 1), 2)

short_entries = round(low_price * (1 - entry_offset), 2)
short_stops = round(short_entries * (stop_offset + 1), 2)
short_targets = round(short_entries * (1 - target_offset), 2)

for i in range(1, len(close_price) - 1):
    if high_price[i] > long_entries[i + 1]:
        print(f"High: {high_price[i]}  "
              f"Date of high: {date[i]} "
              f"Entry: {long_entries[i + 1]} "
              f"High that based Entry: {high_price[i + 1]} "
              f"Date of entry: {date[i + 1]} ✓")
    else:
        print(f"High: {high_price[i]}  "
              f"Date of high: {date[i]} "
              f"Entry: {long_entries[i + 1]} "
              f"High that based Entry: {high_price[i + 1]} "
              f"Date of entry: {date[i + 1]} X")

