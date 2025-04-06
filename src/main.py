import os
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import (Message, MessageMediaPhoto, MessageEntityItalic, MessageEntityMention, MessageEntityMentionName, MessageEntityTextUrl, MessageEntityUrl)
import json
from datetime import datetime
from config import settings

# Функция для скачивания только фото
def download_photo(message: Message, folder_path: str):
    if message and message.media:
        # Проверяем, является ли медиа фото
        if isinstance(message.media, MessageMediaPhoto):
            file_path = client.download_media(
                message.media, 
                file=f"{folder_path}/media/{message.id}.jpg")
            
            print(f"Фото сохранено в: {file_path}")
        else:
            print(f"Сообщение {message.id} содержит не фото, пропускаем.")
    else:
        print(f"Сообщение {message.id} не найдено или не содержит медиа.")
        
def parse_message(message: Message):
    result = {
        'id': message.id,
        'date': message.date.isoformat(),
        'text': message.message,
        'views': message.views,
        'forwards': message.forwards,
        'media': None,
        'entities': []
    }

    # Парсинг медиа
    if message.media:
        if hasattr(message.media, 'photo'):
            photo = message.media.photo
            sizes = []
            for size in photo.sizes:
                size_info = {'type': size.type}
                if hasattr(size, 'w'):
                    size_info.update({'w': size.w, 'h': size.h})
                sizes.append(size_info)
            
            result['media'] = {
                'type': 'photo',
                'id': photo.id,
                'sizes': sizes
            }

    # Парсинг entities
    if message.entities:  # Добавляем проверку на наличие entities
        for entity in message.entities:
            if isinstance(entity, MessageEntityMention):
                result['entities'].append({
                    'type': 'mention',
                    'offset': entity.offset,
                    'length': entity.length,
                    'mention': message.message[entity.offset:entity.offset+entity.length]
                })
            elif isinstance(entity, (MessageEntityUrl, MessageEntityTextUrl)):
                link_info = {
                    'type': 'url' if isinstance(entity, MessageEntityUrl) else 'text_url',
                    'offset': entity.offset,
                    'length': entity.length
                }
                if isinstance(entity, MessageEntityTextUrl):
                    link_info['url'] = entity.url
                result['entities'].append(link_info)

    return result

client = TelegramClient('session_name', settings.API_ID, settings.API_HASH)
client.start(settings.PHONE)

if not client.is_user_authorized():
    client.send_code_request(settings.PHONE)
    client.sign_in(settings.PHONE, input('Введите код: '))


try:
    dialog_name = next(dialog.name for dialog in client.iter_dialogs() if dialog.id == int(settings.CHANNEL_USERNAME))
    folder_path = os.path.join(settings.BASE_PATH, 'chats', dialog_name)
    os.makedirs(folder_path, exist_ok=True )  # Создаёт папку, если её нет
    os.makedirs(os.path.join(folder_path, 'media'), exist_ok=True)
except StopIteration:
    dialog_name = None  # Или другое значение по умолчанию
    print(f"Канал с ID {settings.CHANNEL_USERNAME} не найден среди диалогов.")

try:
    channel = client.get_entity(settings.CHANNEL_USERNAME)
except ValueError:
    channel = client.get_entity(int(settings.CHANNEL_USERNAME))

all_messages = []
offset_id = 0
limit = 10

try:
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
            
        for message in history.messages:
            
            all_messages.append(parse_message(message))
            download_photo(message, folder_path)
        
        offset_id = history.messages[-1].id
        print(f'Скачано {len(all_messages)} сообщений...')

except KeyboardInterrupt:
    print("\nСохранение данных перед выходом...")

finally:
    with open(f'{settings.BASE_PATH}/chats/{dialog_name}/messages.json', 'w', encoding='utf-8') as f:
        json.dump(all_messages, f, ensure_ascii=False, indent=4, 
                 default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o))
    
    print(f'Сохранено {len(all_messages)} сообщений.')
    client.disconnect()