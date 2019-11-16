import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from .models import get_or_create, Response, ResponseType
from . import db

from multiprocessing import Process, Queue, Pool
import requests
import datetime
from .image_processing.store_face_name import store
from .image_processing.analyze_faces import analyze

def get_weather():
    #reston ID == 4781530
    try:
        response = requests.get('http://api.openweathermap.org/data/2.5/weather?id=4781530&APPID=844269118cfd1233e896c26cc113fddc')
    except:
        return
    forecasts = []
    responses = {
        'rain': "Wear a rain coat! It is forecasted to rain today!",
        'drizzle': "Wear a rain coat! It is forecasted to rain today!",
        'snow': "Don't forget your snow boots! We are forecasted for snowflakes!",
        'clear': "Don't forget your sunglasses! Stay stylin in the sun!",
        'partly cloudy': "Don't forget your sunglasses! Stay stylin in the sun!",
        'clouds': "Keep your head up and don't let the cloudy weather get to you.",
        'mist': "Misty, very misty."
    }
    if response.status_code == 200:
        response_type = get_or_create(db.session, ResponseType, **{'name': 'weather'})[0]
        forecasts = [forecast['main'] for forecast in response.json()['weather']]
        if responses.get(forecasts[0].lower(), False):
            response__kwargs = {'response': responses[forecasts[0].lower()],
                                'type_id': response_type.id,
                                 'time': datetime.datetime.now()
                                }
            new_resp = get_or_create(db.session, Response, **response__kwargs)[0]
    return response.status_code


def process_image(images, em_face):
    #get_weather()
    #analysis = analyze(images)

    #consuecutive clicks of analyze require each analysis to be on it's own process
    # with Pool(processes=4) as pool:
    #     analysis = pool.apply_async(analyze, (images,))
    # q = Queue()
    # send = Process(target=analyze, args=(q,images))
    # send.start()
    # analysis = q.get()
    # send.join()
    analysis = analyze(images, em_face)
    if not analysis:
        return False
    responses = {
        'neutral': "You're too neutral today. Don't be a plain jane.",
        'sad': "Don't be sad. Cheer up. The day will get better!",
        'happy': "YAYYY Stay happy!",
        'fear': "Have you seen a ghost? There's nothing to fear.",
        'disgust': "Did you drink some expired milk? Wash down the disgust with water.",
        'angry': "Whoa, you're angry! HULK SMASH!",
        'surprise': "SURPRISE!"
    }
    for name, emotion in analysis.items():
        response_type = get_or_create(db.session, ResponseType, **{'name': emotion})[0]
        response__kwargs = {'response': f'Hey {name}! {responses[emotion.lower()]}',
                            'type_id': response_type.id,
                            'time': datetime.datetime.now()
                            }
        new_resp = get_or_create(db.session, Response, **response__kwargs)[0]
    return True


def train_image(image_bytes):
    return store(image_bytes)


