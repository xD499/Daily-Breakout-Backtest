import pandas as pd
import datetime as dt

pair_daily = pd.read_csv("Historical Klines/BTCUSDT 1D.csv")[::-1].reset_index(drop=True)
pair_minute = pd.read_csv("Historical Klines/BTCUSDT 1M.csv", index_col=0)[::-1].reset_index(drop=True)
pair_daily.drop(columns=pair_daily.columns.difference(['Date', 'Open', 'High', 'Low', 'Close']), inplace=True)

open_price = pd.to_numeric(pair_daily['Open'])
high_price = pd.to_numeric(pair_daily['High'])
low_price = pd.to_numeric(pair_daily['Low'])
close_price = pd.to_numeric(pair_daily['Close'])
date = pd.to_datetime(pair_daily['Date'], unit='ms')


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

confirmed_entries = pd.DataFrame(columns=['Date of Entry', 'Entry State'])

for i in range(1, len(close_price) - 1):
    if high_price[i] > long_entries[i + 1]:
        confirmed_entries.loc[i, 'Date of Entry'] = pd.to_datetime(date[i])
        confirmed_entries.loc[i, 'Entry State'] = True
    else:
        confirmed_entries.loc[i, 'Date of Entry'] = pd.to_datetime(date[i])
        confirmed_entries.loc[i, 'Entry State'] = False

confirmed_entry_dates = pd.to_datetime(confirmed_entries['Date of Entry']).dt.date.unique()
pair_minute['Date'] = pd.to_datetime(pair_minute['Date']).dt.date
filtered_minute_data = pair_minute[pair_minute['Date'].isin(confirmed_entry_dates)].reset_index(drop=True)
print(filtered_minute_data)
