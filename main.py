import pandas as pd
from backtest_utilities import load_data, input_float, calculate_trade_values, process_minutes


def main():
    pair_daily = load_data("Historical Klines/BTCUSDT 1D.csv")
    pair_minute = load_data("Historical Klines/BTCUSDT 1M.csv")

    if pair_daily is None or pair_minute is None:
        return
    pair_daily.drop(columns=pair_daily.columns.difference(['Date', 'Open', 'High', 'Low', 'Close']), inplace=True)

    open_price = pd.to_numeric(pair_daily['Open'])
    high_price = pd.to_numeric(pair_daily['High'])
    low_price = pd.to_numeric(pair_daily['Low'])
    close_price = pd.to_numeric(pair_daily['Close'])
    date = pd.to_datetime(pair_daily['Date'], unit='ms')

    entry_offset = input_float("Enter the offset for entries (Percent): ", 0.1, 100) / 100
    stop_offset = input_float("Enter a stop size (Percent): ", 0.1, 100) / 100
    target_offset = input_float("Enter a target size (Percent): ", 0.1, 100) / 100

    long_entries, long_stops, long_targets = calculate_trade_values(high_price, entry_offset, stop_offset, target_offset, "Long")
    short_entries, short_stops, short_targets = calculate_trade_values(low_price, entry_offset, stop_offset, target_offset, "Short")

    confirmed_entries = pd.DataFrame(columns=['Date of Long Entry', 'Long Entry State',
                                              'Long Entry Price', 'Long Stop Price', 'Long Take Profit Price'
                                                                                     'Date of Short Entry',
                                              'Short Entry State',
                                              'Short Entry Price', 'Short Stop Price', 'Short Take Profit Price']
                                     )

    for i in range(1, len(close_price) - 1):
        confirmed_entries.loc[i, 'Date of Long Entry'] = pd.to_datetime(date[i])
        confirmed_entries.loc[i, 'Long Entry Price'] = long_entries[i + 1]
        confirmed_entries.loc[i, 'Long Entry State'] = high_price[i] > long_entries[i + 1]
        confirmed_entries.loc[i, 'Long Stop Price'] = long_stops[i + 1] if high_price[i] > long_entries[i + 1] else None
        confirmed_entries.loc[i, 'Long Take Profit Price'] = long_targets[i + 1] if high_price[i] > long_entries[i + 1] else None

        confirmed_entries.loc[i, 'Date of Short Entry'] = pd.to_datetime(date[i])
        confirmed_entries.loc[i, 'Short Entry Price'] = short_entries[i + 1]
        confirmed_entries.loc[i, 'Short Entry State'] = low_price[i] < short_entries[i + 1]
        confirmed_entries.loc[i, 'Short Stop Price'] = short_stops[i + 1] if low_price[i] < short_entries[i + 1] else None
        confirmed_entries.loc[i, 'Short Take Profit Price'] = short_targets[i + 1] if low_price[i] < short_entries[i + 1] else None

    confirmed_long_dates = pd.to_datetime(confirmed_entries[confirmed_entries['Long Entry State']]['Date of Long Entry']).reset_index(drop=True)
    confirmed_long_prices = pd.to_numeric(confirmed_entries[confirmed_entries['Long Entry State']]['Long Entry Price']).reset_index(drop=True)
    confirmed_long_stop_prices = pd.to_numeric(confirmed_entries[confirmed_entries['Long Entry State']]['Long Stop Price']).reset_index(drop=True)
    confirmed_long_take_profit_prices = pd.to_numeric(confirmed_entries[confirmed_entries['Long Entry State']]['Long Take Profit Price']).reset_index(drop=True)

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
        filtered_minutes['Direction'] = "Long"
        process_minutes(filtered_minutes)


if __name__ == '__main__':
    main()
