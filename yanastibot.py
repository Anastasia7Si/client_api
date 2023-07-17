import logging
import os
import random
import requests
import io
from PIL import Image

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater

from dotenv import load_dotenv

load_dotenv()

secret_token = os.getenv('TOKEN')
NASA_API_KEY = os.getenv('NASA_KEY')
ROVER_URL = os.getenv('NASA_URL')
URL = os.getenv('CATS_URL')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def get_new_image():
    try:
        response = requests.get(URL)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)

    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def new_cat(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image())


def say_hi(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text='Привет, я Yabot!')


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/newcat'], ['/cospic']],
                                 resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Посмотри, какого котика я тебе нашёл'.format(name),
        reply_markup=button)
    context.bot.send_photo(chat.id, get_new_image())


def get_mars_image_url_from_nasa():
    sol = random.randint(0, 1722)
    params = {'sol': sol, 'api_key': NASA_API_KEY}
    response = requests.get(ROVER_URL, params=params)
    resp_dict = response.json()
    if 'photos' not in resp_dict:
        raise Exception
    photos = resp_dict['photos']
    return random.choice(photos)['img_src']


def validate_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return image.width >= 1024 and image.height >= 1024


def get_mars_photo_bytes():
    image_url = get_mars_image_url_from_nasa()
    response = requests.get(image_url)
    image_bytes = response.read()
    if validate_image(image_bytes):
        return image_bytes


def comsmos_pic(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_mars_image_url_from_nasa())


def main():
    updater = Updater(token=secret_token)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('newcat', new_cat))
    updater.dispatcher.add_handler(CommandHandler('cospic', comsmos_pic))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
