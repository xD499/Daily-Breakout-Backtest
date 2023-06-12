import pandas as pd
from pandas import DataFrame


def load_data(file_path: str):
    try:
        data = pd.read_csv(file_path)[::-1].reset_index(drop=True)
        return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None


def input_float(msg: str, minval: float, maxval: float):
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


def calculate_trade_values(price: float, entry_offset: float, stop_offset: float, target_offset: float, direction: str):
    entry_price = 0.0
    stop_price = 0.0
    target_price = 0.0

    if direction == "Long":
        entry_price = round(price * (1 + entry_offset), 2)
        stop_price = round(entry_price * (1 - stop_offset), 2)
        target_price = round(entry_price * (1 + target_offset), 2)
    elif direction == "Short":
        entry_price = round(price * (1 - entry_offset), 2)
        stop_price = round(entry_price * (1 + stop_offset), 2)
        target_price = round(entry_price * (1 - target_offset), 2)

    return entry_price, stop_price, target_price


def is_closed(row: DataFrame):
    if row['Low'] <= row['Stop Price']:
        print("Trade Stopped")
        print(f"Stop Date: {row['Date']}")
        print(f"Stop Price: {row['Stop Price']}")
        print("")
        return "stopped"

    if row['High'] >= row['Take Profit Price']:
        print("Trade Profited!")
        print(f"Take Profit Date: {row['Date']}")
        print(f"Take Profit Price: {row['Take Profit Price']}")
        print("")
        return "profited"

    return "Day End Exit"


def process_entry(direction: str, minute_date: str, entry_price: float, stop_price: float, take_profit_price: float) -> None:
    print(direction)
    print(f"Entry Date: {minute_date}")
    print(f"Entry Price: {entry_price}")
    print(f"Stop Price: {stop_price}")
    print(f"TP Price: {take_profit_price}")
    print("")


def process_exit(data: DataFrame, start_index: int, stop_offset: float, target_offset: float):
    for index, row in data.iterrows():
        pnl = 0.0
        if index <= start_index:
            continue
        result = is_closed(row)
        if result == "stopped":
            pnl = -abs(stop_offset * 1000)
        elif result == "profited":
            pnl = abs(target_offset * 1000)
        elif result == "Day End Exit":
            pnl = 404
        return pnl


def exit_not_found(pnl, minute_data, entry):
    if pnl != 404:
        pnl = pnl
        return pnl
    else:
        pnl = ((minute_data.loc[1439, 'Close'] - entry) / entry) * 100
        print(f"No Exit Found: {minute_data.loc[1439, 'Close']}")
        print(f"Date: {minute_data.loc[1439, 'Date']}")
        return pnl


def process_minutes(minute_data: DataFrame):
    minute_data_zip = zip(
        minute_data.index, minute_data['Open'], minute_data['High'],
        minute_data['Low'], minute_data['Close'], minute_data['Date'],
        minute_data['Entry Price'], minute_data['Stop Price'],
        minute_data['Take Profit Price'], minute_data['Direction'],
        minute_data['Stop Offset'], minute_data['Target Offset']
    )
    for minute_index, minute_open, minute_high, minute_low, minute_close, minute_date, entry, stop, take_profit, direction, stop_offset, target_offset in minute_data_zip:
        if minute_high >= entry:
            entry_index = minute_index
            process_entry(direction, minute_date, entry, stop, take_profit)
            pnl = process_exit(minute_data, entry_index, stop_offset, target_offset)
            pnl = exit_not_found(pnl, minute_data, entry)
            return pnl


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

    confirmed_entries = pd.DataFrame(columns=['Date of Long Entry', 'Long Entry State', 'Long Entry Price', 'Long Stop Price', 'Long Take Profit Price',
                                              'Date of Short Entry', 'Short Entry State', 'Short Entry Price', 'Short Stop Price', 'Short Take Profit Price'])

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

    pnl = 0.0
    # for i in reversed(range(len(confirmed_long_strdates))):
    #     current_day = confirmed_long_strdates.iloc[i]['YMD']
    #     entry_price = confirmed_long_prices[i]
    #     stop_price = confirmed_long_stop_prices[i]
    #     take_profit_price = confirmed_long_take_profit_prices[i]
    #     filtered_minutes = pair_minute[minute_strdates['YMD'] == current_day][::-1].reset_index(drop=True)
    #     filtered_minutes['Entry Price'] = entry_price
    #     filtered_minutes['Stop Price'] = stop_price
    #     filtered_minutes['Take Profit Price'] = take_profit_price
    #     filtered_minutes['Direction'] = "Long"
    #     filtered_minutes['Stop Offset'] = stop_offset
    #     filtered_minutes['Target Offset'] = target_offset
    #     pnl += process_minutes(filtered_minutes)
    #     print(f"PNL: {pnl}%\n")
    

if __name__ == '__main__':
    main()
