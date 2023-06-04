import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from backtesting.test import EURUSD
from itertools import zip_longest
import pandas as pd

pair = EURUSD.reset_index().rename(columns={'index': 'Date'})[::-1]

o = pair['Open']
h = pair['High']
l = pair['Low']
c = pair['Close']
d = pair['Date']

mintick = 0.00001


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


entry_offset = input_float("Enter the offset for entries (Pips): ", 1, 3)
stop_offset = input_float("Enter a stop size (Pips): ", 1, 5)
target_offset = input_float("Enter a target size (Pips): ", 1, 10)

long_entries = h + (entry_offset * 10 * mintick)
long_stops = long_entries - (stop_offset * 10 * mintick)
long_targets = long_entries + (target_offset * 10 * mintick)

short_entries = l - (entry_offset * 10 * mintick)
short_stops = short_entries + (stop_offset * 10 * mintick)
short_targets = short_entries - (target_offset * 10 * mintick)

previous_long_entry = None
previous_short_entry = None

for i in range(1, len(c)):
    if h[i] > long_entries[i - 1]:
        print(f"High: {h[i]}  Date of high: {d[i]} Entry: {long_entries[i - 1]} High that based Entry: {h[i - 1]} Date of entry: {d[i - 1]} ✓")
    else:
        print(f"High: {h[i]}  Date of high: {d[i]} Entry: {long_entries[i - 1]} High that based Entry: {h[i - 1]} Date of entry: {d[i - 1]} X")

