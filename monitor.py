import os
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

# Config
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SOURCE_PHONE = os.getenv('SOURCE_PHONE')
TARGET_ACCOUNT = os.getenv('TARGET_ACCOUNT')
KEYWORDS = [k.strip().lower() for k in os.getenv('KEYWORDS').split(',')]
IGNORE_CHATS = [int(c.strip()) for c in os.getenv('IGNORE_CHATS', '').split(',') if c]

# Setting up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

client = TelegramClient('session', API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    # Skipping your messages and ignored chats
    if event.message.out or (event.chat_id in IGNORE_CHATS):
        return

    # Checking the text of the message
    msg_text = event.message.text or ""
    if event.message.media and not msg_text:
        msg_text = event.message.caption or ""

    # Keyword Search
    if any(keyword in msg_text.lower() for keyword in KEYWORDS):
        try:
            await client.forward_messages(TARGET_ACCOUNT, event.message)
            logger.info(f"Message forwarded from {event.chat_id}: {msg_text[:50]}...")
        except Exception as e:
            logger.error(f"Error: {e}")

async def main():
    await client.start(phone=SOURCE_PHONE)
    logger.info("Monitoring start...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
