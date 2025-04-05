from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import json
from config import settings

# Создаем клиент Telegram
client = TelegramClient('session_name', settings.API_ID, settings.API_HASH)
client.start(settings.PHONE)

if not client.is_user_authorized():
    client.send_code_request(settings.PHONE)
    client.sign_in(settings.PHONE, input('Введите код: '))

# Получаем канал
channel = client.get_entity(settings.CHANNEL_USERNAME)

# Получаем историю сообщений
all_messages = []
offset_id = 0
limit = 100  # Количество сообщений за один запрос
total_messages = 0

while True:
    history = client(GetHistoryRequest(
        peer=channel,
        offset_id=offset_id,
        offset_date=None,
        add_offset=0,
        limit=limit,
        max_id=0,
        min_id=0,
        hash=0
    ))
    if not history.messages:
        break
    messages = history.messages
    for message in messages:
        all_messages.append({
            'id': message.id,
            'date': message.date.isoformat(),
            'text': message.text
        })
    offset_id = messages[-1].id
    total_messages += len(messages)
    print(f'Скачано {total_messages} сообщений...')

# Сохраняем в JSON
with open('channel_messages.json', 'w', encoding='utf-8') as f:
    json.dump(all_messages, f, ensure_ascii=False, indent=4)

print(f'Всего скачано {len(all_messages)} сообщений. Сохранено в channel_messages.json.')
client.disconnect()