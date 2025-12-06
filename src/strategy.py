import pandas as pd
import pytz
from datetime import datetime

class Fibonacci:
    def __init__(self, configSession, configData):
        self.configSession = configSession
        self.configData = configData
        self.timezone = pytz.timezone(configSession["trading"]["timezone"])

        self.df = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
        
        self.anchor = None
        self.lastDate = None
        self.pivot = None
        self.level05 = None
        self.spikeLock = False

    def get_current_date(self):
        return datetime.now(self.timezone).date()
    
    async def daily_history(self, client):
        # In case of power outage
        timeNow = datetime.now(self.timezone)
        startOfTheDay = timeNow.replace(hour=0, minute=0, second=0, microsecond=0)
        startTs = int(startOfTheDay.astimezone(pytz.UTC).timestamp() * 1000)

        klines = await client.futures_klines(
                symbol=self.configSession["trading"]["pair"],
                interval=self.configSession["trading"]["interval"],
                startTime=startTs
        )

        if not klines:
            print("Not found")
            return
        self.lastDate = timeNow.date()

        for k in klines:
            newRow = {
                    "date": pd.to_datetime(k[0], unit="ms").tz_localize("UTC").tz_convert(self.timezone),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5])
                    }
            newDf = pd.DataFrame([newRow])
            if self.df.empty:
                self.df = newDf
            else:
                self.df = pd.concat([self.df, newDf], ignore_index=True)
            self.process_logic(newRow)

    def check_new_day(self):
        currentDate = self.get_current_date()
        if self.lastDate != currentDate:
            print("New Day")

            self.df = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
            
            self.anchor = None
            self.pivot = None
            self.level05 = None
            self.spikeLock = False
            
            self.lastDate = currentDate
            
            return True
        return False

    def cal_fibs(self):
        if self.anchor is None or self.level05 is None:
            return

        distance = self.anchor - self.level05
        self.pivot = self.level05 - distance
        
        print(f"FIBS: 1: {self.anchor:.3f} | 0.5: {self.level05:.3f} | 0.0 (est.): {self.pivot:.3f}")

    def update_data(self, kline):
        self.check_new_day()
        k = kline['k']
        currentTime = pd.to_datetime(k['t'], unit="ms").tz_localize("UTC").tz_convert(self.timezone)
        newRow = {
            "date": currentTime,
            "open": float(k['o']),
            "high": float(k['h']),
            "low": float(k['l']),
            "close": float(k['c']),
            "volume": float(k['v'])
        }
        
        if self.df.empty:
            self.df = pd.DataFrame([newRow])
        else:
            lastTime = self.df.iloc[-1]["date"]
            if currentTime == lastTime:
                self.df.iloc[-1] = newRow.values()
            else:
                self.df = pd.concat([self.df, pd.DataFrame([newRow])], ignore_index=True)
        
        self.process_logic(newRow)

    def process_logic(self, newRow):
        dayHigh = self.df["high"].max()
        dayLow = self.df["low"].min()
        dayHighIdx = self.df["high"].idxmax()
        dayLowIdx = self.df["low"].idxmin()

        currentVol = newRow["volume"]
        dayMaxVol = self.df["volume"].max()
       
        isSpike = False
        if len(self.df) > 5:
            isSpike = (currentVol >= dayMaxVol)

        # Downtrend
        if dayHighIdx < dayLowIdx:
            self.anchor = dayHigh

            if isSpike:
                print("Spotted max vol downtrend")
                self.level05 = newRow["open"]
                self.spikeLock = True
            elif not self.spikeLock:
                # Trailing Support
                if self.level05 is None or newRow["close"] < self.level05:
                        # Add deviation later !!!!!!!!!!
                    self.level05 = newRow["close"]
        # Uptrend
        elif dayHighIdx > dayLowIdx:
            self.anchor = dayLow
            
            if isSpike:
                print("Spotted max vol uptrend")
                self.level05 = newRow["open"]
                self.spikeLock = True
            elif not self.spikeLock:
                if self.level05 is None or newRow["close"] > self.level05:
                    # Add deviation pls!!!
                    self.level05 = newRow["close"]

        self.cal_fibs()
