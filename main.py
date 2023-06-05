import pandas as pd
import os


def input_float(message, min_value, max_value):
    while True:
        user_input = input(message)
        try:
            float_value = float(user_input)
        except ValueError:
            print("! Please enter a number.")
            continue

        if float_value < min_value:
            print(f"! Please enter a number >= {min_value}")
        elif float_value > max_value:
            print(f"! Please enter a number <= {max_value}")
        else:
            return float_value


def calculate_entries(prices, offset):
    return round(prices * offset, 2)


def calculate_stops(entries, offset):
    return round(entries * (1 - offset), 2)


def calculate_targets(entries, offset):
    return round(entries + offset, 2)


def filter_minute_data(minute_data, entry_dates):
    return minute_data[minute_data['Date'].isin(entry_dates)].reset_index(drop=True)


def main():
    pair_daily_path = "Historical Klines/BTCUSDT 1D.csv"
    pair_minute_path = "Historical Klines/BTCUSDT 1M.csv"

    if not (os.path.exists(pair_daily_path) and os.path.exists(pair_minute_path)):
        print("Error: Input file(s) not found.")
        return

    pair_daily = pd.read_csv(pair_daily_path)[::-1].reset_index(drop=True)
    pair_minute = pd.read_csv(pair_minute_path, index_col=0)[::-1].reset_index(drop=True)
    pair_daily.drop(columns=pair_daily.columns.difference(['Date', 'Open', 'High', 'Low', 'Close']), inplace=True)

    open_price = pd.to_numeric(pair_daily['Open'])
    high_price = pd.to_numeric(pair_daily['High'])
    low_price = pd.to_numeric(pair_daily['Low'])
    close_price = pd.to_numeric(pair_daily['Close'])
    date = pd.to_datetime(pair_daily['Date'], unit='ms')

    entry_offset = input_float("Enter the offset for entries (Percent): ", 0.1, 100) / 100
    stop_offset = input_float("Enter a stop size (Percent): ", 0.1, 100) / 100
    target_offset = input_float("Enter a target size (Percent): ", 0.1, 100) / 100

    long_entries = calculate_entries(high_price, entry_offset + 1)
    long_stops = calculate_stops(long_entries, stop_offset)
    long_targets = calculate_targets(long_entries, target_offset + 1)

    short_entries = calculate_entries(low_price, 1 - entry_offset)
    short_stops = calculate_stops(short_entries, stop_offset + 1)
    short_targets = calculate_targets(short_entries, 1 - target_offset)

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
    filtered_minute_data = filter_minute_data(pair_minute, confirmed_entry_dates)
    print(filtered_minute_data)


if __name__ == "__main__":
    main()
