import asyncio
from binance import AsyncClient, BinanceSocketManager
from src.strategy import Fibonacci
from src.telegram import Notifier
from src.utils import load_config
from src.visualizer import Visualizer

"""
    Todo list:
        1. Add deviation in 0.5 level + fix plan
        2. Add notification when cross 0.236 level with proper market structure (export .png/.jpg to telegram)
        
        4. Store database
        5. After eveything is aligned, execute trade at 0 and record to database + image
        6. Reload too fast, increase interval
        7. ...
        !!! FUTURE PLAN !!!
        Add higher time frame observer + 1/5/30 mins time frame ? maybe ? 
"""

# def test(configPath):
#     notifier = Notifier(configPath)
#
#     success = notifier.send("Beep Boop")
#
#     if success:
#         print("Success")
#     else:
#         print("Fail")

async def main():
    try:
        configSession = load_config("config/configSession.json")
        configData = load_config("config/config.json")
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    session = Fibonacci(configSession, configData)
    viz = Visualizer(configSession["trading"]["pair"])

    apiKey = configData["binance"]["api_key"]
    apiSecret = configData["binance"]["api_secret"]

    client = await AsyncClient.create(apiKey, apiSecret)
    await session.daily_history(client)
    viz.update_chart(session.df, session.anchor, session.level05, session.pivot)
    bm = BinanceSocketManager(client)

    pair = configSession["trading"]["pair"]
    interval = configSession["trading"]["interval"]
    ts = bm.kline_futures_socket(pair, interval=interval)

    print(f"Starting connection for {pair}")

    async with ts as tscm:
        while True:
            res = await tscm.recv()
            if res:
                session.update_data(res)

                viz.update_chart(session.df, session.anchor, session.level05, session.pivot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by user.")
