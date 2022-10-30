import os
import sys

sys.path.append('face-alignment')
sys.path.append('Stylegan3')
import asyncio
import queue
from dataclasses import dataclass
from threading import Thread

# import torch
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
# from face_aligner import align_image
# from face_aligner import get_detector
# from PIL import Image

import numpy as np

# import dnnlib
# import legacy
# import predict
# from blend_models import blend
# from metrics.metric_utils import get_feature_detector

start_steps = 300
step_of_steps = 200
end_steps = 1500
iter_crop = 70


@dataclass
class Task:
    chat_id: str
    image_path: str
    steps: int
    cnt_faces: int
    crop: bool


# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


async def send_ready_images(ready_queue, bot):
    while True:
        if ready_queue.qsize():
            (path, pred_str), task = ready_queue.get()
            print("$%^$%^", path, task)
            print('sending photo to {}'.format(task.chat_id))
            markup = InlineKeyboardMarkup()
            #     markup.row_width = 1
            #     markup.add(
            #         InlineKeyboardButton('Пойдет', callback_data='yes|' + task.image_path),
            #         InlineKeyboardButton('Доработать',
            #                              callback_data='do|' + str(task.steps + step_of_steps) + '|' + task.image_path),
            #     )

            with open(path, 'rb') as f:
                await bot.send_photo(
                    chat_id=task.chat_id,
                    photo=f,
                    caption=f"я вижу тут слово {pred_str}",
                    reply_markup=markup
                )
            # os.remove(path)
        else:
            await asyncio.sleep(0.1)


class RecognizeThread(Thread):

    def __init__(self, task_queue):
        Thread.__init__(self)
        self.task_queue = task_queue
        self.ready_queue = queue.Queue()

        print('LOADING MODELS')

        # вот тут загрузка модели

        print('MODELS LOADED')

    def predict(self, task: Task):
        image_path = task.image_path

        #     faces = self.align_face_on_image(image_path)
        #     if faces:
        #         for face in faces:
        #             save_path = image_path[:image_path.rfind('.')] + f'{task.cnt_faces:03d}' + '.png'
        #             task.cnt_faces += 1
        #             face.save(save_path)
        pred_str = 'kek1'

        self.ready_queue.put(((image_path, pred_str), task))

    def get_waiting_time(self):
        time = 10
        return f"{str(time)} секунд"

    def run(self) -> None:
        while True:
            image_path, chat_id, steps, crop = self.task_queue.get()
            print("!!!", image_path, chat_id, steps, crop)
            self.predict(Task(chat_id=chat_id, image_path=image_path, steps=steps, cnt_faces=0, crop=crop))
