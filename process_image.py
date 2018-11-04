import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from .models import get_or_create, Response, ResponseType
from . import db

import requests
import datetime

def get_weather():
    #reston ID == 4781530
    response = requests.get('http://api.openweathermap.org/data/2.5/weather?id=4781530&APPID=844269118cfd1233e896c26cc113fddc')
    forecasts = []
    responses = {
        'rain': "Wear a rain coat! It is forecasted to rain today!",
        'drizzle': "Wear a rain coat! It is forecasted to rain today!",
        'snow': "Don't forget your snow boots! We are forecasted for snowflakes!",
        'clear': "Don't forget your sunglasses! Stay stylin in the sun!",
        'partly cloudy': "Don't forget your sunglasses! Stay stylin in the sun!",
        'clouds': "Keep your head up and don't let the cloudy weather get to you."
    }
    if response.status_code == 200:
        response_type = get_or_create(db.session, ResponseType, **{'name': 'weather'})[0]
        forecasts = [forecast['main'] for forecast in response.json()['weather']]
        response__kwargs = {'response': responses[forecasts[0].lower()],
                            'type_id': response_type.id,
                            #'time': datetime.datetime.now
                            }
        new_resp = get_or_create(db.session, Response, **response__kwargs)[0]
    return response.status_code


def send_image(image_bytes, elapsed):
    # img = Image.open(image_bytes)
    # draw = ImageDraw.Draw(img)
    # # font = ImageFont.truetype("arial.ttf", 14)
    # # draw.text((0, 220), "This is a test11", (255, 255, 0), font=font)
    # # draw = ImageDraw.Draw(img)
    # img.save(f"frame_{elapsed}.jpeg")
    # print("in image")
    check_weather = get_weather()

