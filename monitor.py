import os
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

# Конфигурация
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SOURCE_PHONE = os.getenv('SOURCE_PHONE')
TARGET_ACCOUNT = os.getenv('TARGET_ACCOUNT')
KEYWORDS = [k.strip().lower() for k in os.getenv('KEYWORDS').split(',')]
IGNORE_CHATS = [int(c.strip()) for c in os.getenv('IGNORE_CHATS', '').split(',') if c]

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

client = TelegramClient('session', API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    # Пропуск своих сообщений и игнорируемых чатов
    if event.message.out or (event.chat_id in IGNORE_CHATS):
        return

    # Проверка текста сообщения
    msg_text = event.message.text or ""
    if event.message.media and not msg_text:
        msg_text = event.message.caption or ""

    # Поиск ключевых слов
    if any(keyword in msg_text.lower() for keyword in KEYWORDS):
        try:
            await client.forward_messages(TARGET_ACCOUNT, event.message)
            logger.info(f"Переслано сообщение из {event.chat_id}: {msg_text[:50]}...")
        except Exception as e:
            logger.error(f"Ошибка: {e}")

async def main():
    await client.start(phone=SOURCE_PHONE)
    logger.info("Мониторинг запущен...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
