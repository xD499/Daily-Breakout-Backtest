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


def is_win(row: DataFrame):
    if row['Low'] <= row['Stop Price']:
        print("Trade Stopped")
        print(f"Stop Date: {row['Date']}")
        print(f"Stop Price: {row['Stop Price']}")
        print("")
        return True

    if row['High'] >= row['Take Profit Price']:
        print("Trade Profited!")
        print(f"Take Profit Date: {row['Date']}")
        print(f"Take Profit Price: {row['Take Profit Price']}")
        print("")
        return True

    return False


def process_entry(direction: str, minute_date: str, entry_price: float, stop_price: float, take_profit_price: float) -> None:
    print(direction)
    print(f"Entry Date: {minute_date}")
    print(f"Entry Price: {entry_price}")
    print(f"Stop Price: {stop_price}")
    print(f"TP Price: {take_profit_price}")
    print("")


def process_exit(data: DataFrame, start_index: int) -> None:
    for index, row in data.iterrows():
        if index <= start_index:
            continue
        if is_win(row):
            break


def get_offset_values(entry_price: float, stop_price: float, take_profit_price: float):
    stop_offset_percent = abs(((entry_price - stop_price) / stop_price) * 100)
    take_profit_offset_percent = abs(((entry_price - take_profit_price) / take_profit_price) * 100)
    return stop_offset_percent, take_profit_offset_percent


def process_minutes(minute_data: DataFrame) -> None:
    minute_data_zip = zip(
        minute_data.index, minute_data['Open'], minute_data['High'],
        minute_data['Low'], minute_data['Close'], minute_data['Date'],
        minute_data['Entry Price'], minute_data['Stop Price'],
        minute_data['Take Profit Price'], minute_data['Direction']
    )

    for minute_index, minute_open, minute_high, minute_low, minute_close, minute_date, entry, stop, take_profit, direction in minute_data_zip:
        if minute_high >= entry:
            entry_index = minute_index
            process_entry(direction, minute_date, entry, stop, take_profit)
            process_exit(minute_data, entry_index)
            break
