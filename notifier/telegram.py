import requests
import logging
import json
import os

logger = logging.getLogger(__name__)

class Notifier:
    def __init__(self, configPath):
        self.token = None
        self.chatId = None
        self.baseUrl = None
        self._load_config(configPath)

    def _load_config(self, configPath):
        if not os.path.exists(configPath):
            logger.warning(f"Config not found at {configPath}.")
            return

        try:
            with open(configPath, 'r') as f:
                config = json.load(f)
                botConfig = config.get('telegram')
                self.token = botConfig.get('token')
                self.chatId = botConfig.get('channelID')

                if self.token and self.chatId:
                    self.baseUrl = f"https://api.telegram.org/bot{self.token}/sendMessage"
                else:
                    logger.warning("Token or chat ID missing in config.")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

    def send(self, message):
        if not self.baseUrl:
            logger.info("Message skipped.")
            return False

        try:
            payload = {
                    "chat_id": self.chatId,
                    "text": message,
                    "parse_mode": "Markdown"
                    }
            response = requests.post(self.baseUrl, json=payload, timeout=5)

            if response.status_code == 200:
                logger.info("Message sent.")
                return True
            else:
                logger.info("Failed to send message.")
                print(response.text)
                return False

        except Exception as e:
            logger.error(f"Error: {e}")
            return False


