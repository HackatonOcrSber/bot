import asyncio
import os
import queue
import urllib

from aiogram import Bot
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils import executor

from config import BOT_TOKEN
from worker import RecognizeThread
from worker import send_ready_images

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(bot)
task_queue = queue.Queue()

start_steps = 300
step_of_steps = 200
end_steps = 1500
iter_crop = 70


@dp.message_handler(commands=['start', 'help'])
async def some_handler(message: types.Message):
    print("!!!!!")
    start_message = 'Привет! Это бот, который Илья Анищенко нагло спиздил из интернетов. \n' \
                    'Ты картинку суй, да, я тебе текст с нее проинтерпретирую)'
    await message.answer(start_message)


@dp.message_handler(content_types=['photo'], state='*')
async def handle_docs_photo(message):
    print("!@#$!@#!$")
    document_id = message['photo'][-1].file_id
    file_id = message['photo'][-1].file_unique_id

    file_info = await bot.get_file(document_id)
    filename, file_extension = os.path.splitext(file_info.file_path)
    image_name = os.path.join('photos', file_id + file_extension)
    urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}', image_name)
    # recognize_thread.iter += iter_crop
    task_queue.put((image_name, message.chat.id, start_steps, True))
    await message.answer('Врум врум, ищем текст, по ожиданию: ' +
                         recognize_thread.get_waiting_time() + '\n')

if __name__ == '__main__':
    recognize_thread = RecognizeThread(task_queue)
    recognize_thread.daemon = True
    recognize_thread.start()

    loop = asyncio.get_event_loop()
    loop.create_task(send_ready_images(recognize_thread.ready_queue, bot))

    executor.start_polling(dp, loop=loop)
