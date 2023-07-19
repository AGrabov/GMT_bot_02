# TGnotify.py

from aiogram import Bot

class TG_Notifier:
    def __init__(self, token, chat_id):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_message(self, text):
        await self.bot.send_message(chat_id=self.chat_id, text=text)

    async def send_trade_notification(self, trade):
        text = f"Trade executed:\n{trade}"
        await self.send_message(text)

    async def send_daily_summary(self, summary):
        text = f"Daily summary:\n{summary}"
        await self.send_message(text)

    async def send_error_notification(self, error):
        text = f"An error occurred:\n{error}"
        await self.send_message(text)

    async def close(self):
        await self.bot.close()
