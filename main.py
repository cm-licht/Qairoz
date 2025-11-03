import ccxt
from datetime import datetime
import plotly.graph_objects as go

def main():
    binance = ccxt.binance()
    tradingPair = 'BTC/USDT'

    candles = binance.fetch_ohlcv(tradingPair, '1h')

    dates = []
    openData = []
    highData = []
    lowData = []
    closeData = []

    for candle in candles:
        dates.append(datetime.fromtimestamp(candle[0] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f'))
        openData.append(candle[1])
        highData.append(candle[2])
        lowData.append(candle[3])
        closeData.append(candle[4])

    fig = go.Figure(data=[go.Candlestick(x=dates, open=openData, high=highData, low=lowData, close=closeData)])
    fig.show()

if __name__ == "__main__":
    main()