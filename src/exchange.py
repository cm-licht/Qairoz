import ccxt
import json
import logging
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Exchange:
    def __init__(self, configPath, apiKeysPath):
        logger.info("Initializing client...")

        with open(configPath, 'r') as file:
            self.config = json.load(file)

        with open(apiKeysPath, 'r') as file:
            self.keys = json.loag(file)

        if 'exchange' in self.config:
            self.exchange_name = self.config['exchange']
        else:
            logger.warning("No exchange was found in config")
            # Add a fallback exchange name in the future
        self.is_testnet = self.config.get('testnet')

        try:
            exchange_class = getattr(ccxt, self.exchange_name)
        except AttributeError:
            logger.error(f"Exchange '{self.exchange_name}' not found")
            raise
            
        self.client = exchange_class({
            'apiKey': self.keys['apiKey'],
            'secret': self.keys['secret'],
        # check out adjustForTimeDifference
        })

        if self.is_testnet:
            try:
                self.client.set_sandbox_mode(True)
            except Exception as error:
                logger.warning("Could not set sandbox mode")
        else:
            logger.info(f"Successfully connected to '{self.exchange_name}'")

        # Fetches open, high, low, close, volume data for symbol
        def fetchOhlcv(self, symbol, timeframe, limit):
            logger.info(f"Fetching {limit} candles for {symbol} on {timeframe} timeframe")
            try:
                data = self.client.fetchOhlcv(symbol, timeframe, limit)
                if not data:
                    logger.warning("No OHLCV data returned")
                    return None
                
                return data
            except Exception as error:
                logger.error(f"{error}")
                return None
