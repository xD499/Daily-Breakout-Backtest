import pandas as pd
from binance.client import Client


def main():
    pair, timeframe, starting_date = 'BTCUSDT', '1h', '12 june 2022'
    info = Client().get_historical_klines(pair, timeframe, starting_date)
    print("Download Complete")

    dl_data = pd.DataFrame(info, columns=['Timestamp', 'Open', 'High', 'Low',
                                          'Close', 'Volume', 'Close Time',
                                          'Quote AV', 'Trades', 'TB Base AV',
                                          'TB Quote AV', 'Ignore']
                           )

    data = dl_data.loc[:, ['Timestamp', 'Open', 'High', 'Low', 'Close']]
    data.set_index(data['Timestamp'], inplace=True)
    data.index = pd.to_datetime(data.index, unit='ms')

    del data['Timestamp']

    data['Open'] = pd.to_numeric(data['Open'])
    data['High'] = pd.to_numeric(data['High'])
    data['Low'] = pd.to_numeric(data['Low'])
    data['Close'] = pd.to_numeric(data['Close'])

    data.to_csv('Historical Klines/BTCUSDT 1H.csv')

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    print(data)


if __name__ == '__main__':
    main()
