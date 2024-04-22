import base64
import os
import random
import time

IMG_PATH = 'media/images/'
MEDIA_ADDR = 'http://localhost:8000/' + IMG_PATH


def get_img_url(img_name):
    return MEDIA_ADDR + img_name


def get_img_path(img_name):
    return IMG_PATH + img_name


def delete_img(img_name):
    path = get_img_path(img_name)
    if os.path.exists(path):
        os.remove(path)


def base64_to_img_name(base64_string):
    image_data = base64.b64decode(base64_string)
    img_name = str(time.time()).replace('.', '') + str(random.randint(0, 100)) + '.jpg'
    image_path = get_img_path(img_name)
    with open(image_path, 'wb') as f:
        f.write(image_data)
    return img_name
