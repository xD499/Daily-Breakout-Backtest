import pandas as pd




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


def process_minutes(minute_data):
    filtered_minutes_ohlcd = zip(minute_data['Open'], minute_data['High'],
                                 minute_data['Low'], minute_data['Close'],
                                 minute_data['Date'], minute_data['Entry Price'],
                                 minute_data['Stop Price'], minute_data['Take Profit Price'])
    for minute_open, minute_high, minute_low, minute_close, minute_date, entry, stop, take_profit in filtered_minutes_ohlcd:
        if minute_high >= entry:
            print(f"Entry Date: {minute_date}")
            print(f"Entry Price: {entry}")
            print(f"Stop Price: {stop}")
            print(f"TP Price: {take_profit}")
            print("")
            break


def main():
    pair_daily = pd.read_csv("Historical Klines/BTCUSDT 1D.csv")[::-1].reset_index(drop=True)
    pair_minute = pd.read_csv("Historical Klines/BTCUSDT 1M.csv", index_col=0)[::-1].reset_index(drop=True)
    pair_daily.drop(columns=pair_daily.columns.difference(['Date', 'Open', 'High', 'Low', 'Close']), inplace=True)

    open_price = pd.to_numeric(pair_daily['Open'])
    high_price = pd.to_numeric(pair_daily['High'])
    low_price = pd.to_numeric(pair_daily['Low'])
    close_price = pd.to_numeric(pair_daily['Close'])
    date = pd.to_datetime(pair_daily['Date'], unit='ms')

    entry_offset = input_float("Enter the offset for entries (Percent): ", 0.1, 100) / 100
    stop_offset = input_float("Enter a stop size (Percent): ", 0.1, 100) / 100
    target_offset = input_float("Enter a target size (Percent): ", 0.1, 100) / 100

    long_entries = round(high_price * (entry_offset + 1), 2)
    long_stops = round(long_entries * (1 - stop_offset), 2)
    long_targets = round(long_entries + (target_offset + 1), 2)

    short_entries = round(low_price * (1 - entry_offset), 2)
    short_stops = round(short_entries * (stop_offset + 1), 2)
    short_targets = round(short_entries * (1 - target_offset), 2)

    confirmed_entries = pd.DataFrame(columns=['Date of Long Entry', 'Long Entry State',
                                              'Long Entry Price', 'Long Stop Price', 'Long Take Profit Price'
                                              'Date of Short Entry', 'Short Entry State',
                                              'Short Entry Price', 'Short Stop Price', 'Short Take Profit Price']
                                     )

    for i in range(1, len(close_price) - 1):
        if high_price[i] > long_entries[i + 1]:
            confirmed_entries.loc[i, 'Date of Long Entry'] = pd.to_datetime(date[i])
            confirmed_entries.loc[i, 'Long Entry State'] = True
            confirmed_entries.loc[i, 'Long Entry Price'] = long_entries[i + 1]
            confirmed_entries.loc[i, 'Long Stop Price'] = long_stops[i + 1]
            confirmed_entries.loc[i, 'Long Take Profit Price'] = long_targets[i + 1]
        else:
            confirmed_entries.loc[i, 'Date of Long Entry'] = pd.to_datetime(date[i])
            confirmed_entries.loc[i, 'Long Entry State'] = False
            confirmed_entries.loc[i, 'Long Entry Price'] = long_entries[i + 1]
            confirmed_entries.loc[i, 'Long Stop Price'] = None
            confirmed_entries.loc[i, 'Long Take Profit Price'] = None

        if low_price[i] < short_entries[i + 1]:
            confirmed_entries.loc[i, 'Date of Short Entry'] = pd.to_datetime(date[i])
            confirmed_entries.loc[i, 'Short Entry State'] = True
            confirmed_entries.loc[i, 'Short Entry Price'] = short_entries[i + 1]
            confirmed_entries.loc[i, 'Short Stop Price'] = short_stops[i + 1]
            confirmed_entries.loc[i, 'Short Take Profit Price'] = short_targets[i + 1]
        else:
            confirmed_entries.loc[i, 'Date of Short Entry'] = pd.to_datetime(date[i])
            confirmed_entries.loc[i, 'Short Entry State'] = False
            confirmed_entries.loc[i, 'Short Entry Price'] = short_entries[i + 1]
            confirmed_entries.loc[i, 'Short Stop Price'] = None
            confirmed_entries.loc[i, 'Short Take Profit Price'] = None

    confirmed_long_dates = pd.to_datetime(
        confirmed_entries[confirmed_entries['Long Entry State']]
        ['Date of Long Entry']
    ).reset_index(drop=True)

    confirmed_long_prices = pd.to_numeric(
        confirmed_entries[confirmed_entries['Long Entry State']]
        ['Long Entry Price']
    ).reset_index(drop=True)

    confirmed_long_stop_prices = pd.to_numeric(
        confirmed_entries[confirmed_entries['Long Entry State']]
        ['Long Stop Price']
    ).reset_index(drop=True)

    confirmed_long_take_profit_prices = pd.to_numeric(
        confirmed_entries[confirmed_entries['Long Entry State']]
        ['Long Take Profit Price']
    ).reset_index(drop=True)

    confirmed_long_strdates = pd.DataFrame({'Date': confirmed_long_dates})
    confirmed_long_strdates['YMD'] = confirmed_long_strdates['Date'].dt.strftime('%Y-%m-%d')

    minute_dates = pd.to_datetime(pair_minute['Date'])
    minute_strdates = pd.DataFrame({'Date': minute_dates})
    minute_strdates['YMD'] = minute_strdates['Date'].dt.strftime('%Y-%m-%d')

    for i in reversed(range(len(confirmed_long_strdates))):
        current_day = confirmed_long_strdates.iloc[i]['YMD']
        entry_price = confirmed_long_prices[i]
        stop_price = confirmed_long_stop_prices[i]
        take_profit_price = confirmed_long_take_profit_prices[i]
        filtered_minutes = pair_minute[minute_strdates['YMD'] == current_day][::-1].reset_index(drop=True)
        filtered_minutes['Entry Price'] = entry_price
        filtered_minutes['Stop Price'] = stop_price
        filtered_minutes['Take Profit Price'] = take_profit_price
        process_minutes(filtered_minutes)


if __name__ == '__main__':
    main()
