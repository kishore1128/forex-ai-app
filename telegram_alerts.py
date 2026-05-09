import os
from telegram import Bot

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError("Telegram credentials not set.")

bot = Bot(token=BOT_TOKEN)

def send_alert(message: str):
    """Send a generic text alert via the configured Telegram bot."""
    bot.send_message(
        chat_id=CHAT_ID,
        text=message,
    )

def send_trade_alert(event: dict) -> None:
    """Send a structured trade‑event notification.

    The *event* dict should contain at least:
    - ``symbol``
    - ``action`` (OPEN, CLOSE_SIGNAL, STOP_LOSS, TAKE_PROFIT, SWITCH)
    - ``price``
    - optional ``direction`` and ``reason``
    """
    parts = [f"{event.get('symbol')} | {event.get('action')}"]
    if 'direction' in event:
        parts.append(f"Direction: {event['direction']}")
    if 'price' in event:
        parts.append(f"Price: {event['price']:.5f}")
    if 'reason' in event:
        parts.append(f"Reason: {event['reason']}")
    message = " – ".join(parts)
    send_alert(message)
