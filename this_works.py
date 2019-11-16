import cv2
import sys
import time
import requests
import datetime
import matplotlib.pyplot as plt
import numpy as np
import asyncio
import aiohttp
import socket
from concurrent.futures import ThreadPoolExecutor


# class VideoFeed:
def stream_video_image(gap):
    # Initializes webcam and for a frequency of the <gap_time> sends zip of images to an endpoint
    cap = cv2.VideoCapture(0)
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 25, (1920, 1080))
    start_time = int(round(time.time()))
    while (cap.isOpened()):
        grabbed, frame = cap.read()
        current_time = int(round(time.time()))
        out.write(frame)
        # cv2.imshow('VIDEO', frame)
        if cv2.waitKey(1) and 0xFF == ord('q'):
            break
        seconds = current_time - start_time
        if seconds % gap == 0:
            image_file = "frame-%d.jpeg" % seconds
            cv2.imwrite(image_file, frame)
            yield image_file
    cap.release()
    out.release()
    cv2.destroyAllWindows()


async def get_match(response):
    matched = {}
    for item, match_rate in response['answer'].items():
        if match_rate * 100 > 75:
            matched[item.lower()] = match_rate * 100
    return matched


async def make_graph(results):
    labels = list(results['answer'].keys())

    values = np.asarray(list(results['answer'].values()))
    values = values.astype(float)
    values = values * 100

    fig, ax = plt.subplots()
    y_pos = np.arange(len(labels))

    ax.bar(y_pos, values, align='center', alpha=0.5)
    plt.xticks(y_pos, labels)
    ax.set_ylim(0, 100)

    for i, v in enumerate(values):
        plt.text(i - 0.2, v + 1, str(round(v, 2)) + '%', color='blue', fontsize=14)

    plt.ylabel('Percentage')
    title = 'Image Recognition %s' % (datetime.datetime.now().time())
    plt.title(title)
    file = '%s.png' % title
    plt.savefig(file)
    return plt


async def send_frame(endpoint_uri, file, session=None):
    # async with aiohttp.ClientSession() as session:
    data = {
        'file': open(file, 'rb')}
    async with session.post(endpoint_uri, data=data) as response:
        if response.status == 200:
            json_body = await response.json()
            await make_graph(json_body)
            return await get_match(json_body)


async def bound_fetch(sem, image_file, session):
    # Getter function with semaphore.
    async with sem:
        await send_frame('https://tensorflowwaiter-aserecruitfy19.uscom-central-1.oraclecloud.com/tensorflow',
                         image_file, session)


async def check_image(gap=2, stop_time=5, executor=None):
    # matches = {}
    loop = asyncio.get_event_loop()
    start = int(round(time.time()))
    conn = aiohttp.TCPConnector(
        family=socket.AF_INET,
        ssl=False,
    )
    # create instance of Semaphore
    sem = asyncio.Semaphore(1000)
    async with aiohttp.ClientSession(connector=conn) as session:
        futures = []
        responses = []
        for i, image_file in enumerate(stream_video_image(gap)):

            task = asyncio.ensure_future(
                send_frame('https://tensorflowwaiter-aserecruitfy19.uscom-central-1.oraclecloud.com/tensorflow',
                           image_file, session))
            # futures.append(loop.run_in_executor(executor, send_frame(
            #     'https://tensorflowwaiter-aserecruitfy19.uscom-central-1.oraclecloud.com/tensorflow',
            #     image_file, session), i))
            # loop.run_forever()
            # yield image_file
            # task = asyncio.run(send_frame('https://tensorflowwaiter-aserecruitfy19.uscom-central-1.oraclecloud.com/tensorflow',
            #                        image_file))
            # responses.append(resp)
            futures.append(task)
            if stop_time <= int(round(time.time())) - start:
                break
        # completed, pending = await asyncio.wait(futures)
        # return[t.result() for t in completed]
        responses = await asyncio.gather(*futures)
        # yield responses
        return responses

        # future = [asyncio.ensure_future(check_image(gap=gap, stop_time=stop_time))]
        # matches = loop.run_until_complete(asyncio.wait(future))
        # # matches = loop.run_until_complete(check_image(gap=gap, stop_time=stop_time, loop=loop))
        # # matches = asyncio.run(check_image(gap=gap, stop_time=stop_time))
        # # for resp in check_image(gap=gap, stop_time=stop_time):
        # #     if item and item.lower in resp:
        # #         matches[datetime.datetime.now().time()] = resp
        # #     if not item:
        # #         matches[datetime.datetime.now().time()] = resp
        # yield matches
#
#
# def api_return_gen(gap=10, stop_time=None, item=None):
#     matches = {}
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     future = [asyncio.ensure_future(check_image(gap=gap, stop_time=stop_time))]
#     matches = loop.run_forever()
#     # matches = loop.run_until_complete(check_image(gap=gap, stop_time=stop_time, loop=loop))
#     # matches = asyncio.run(check_image(gap=gap, stop_time=stop_time))
#     # for resp in check_image(gap=gap, stop_time=stop_time):
#     #     if item and item.lower in resp:
#     #         matches[datetime.datetime.now().time()] = resp
#     #     if not item:
#     #         matches[datetime.datetime.now().time()] = resp
#     return matches


# api_return_gen(gap=10, stop_time=40)



####
##FROM MAIN.PY

# async def get_match(response):
#     matched = {}
#     for item, match_rate in response['answer'].items():
#         if match_rate * 100 > 75:
#             matched[item.lower()] = match_rate * 100
#     return matched
#
#
# async def make_graph(results):
#     labels = list(results['answer'].keys())
#
#     values = np.asarray(list(results['answer'].values()))
#     values = values.astype(float)
#     values = values * 100
#
#     fig, ax = plt.subplots()
#     y_pos = np.arange(len(labels))
#
#     ax.bar(y_pos, values, align='center', alpha=0.5)
#     plt.xticks(y_pos, labels)
#     ax.set_ylim(0, 100)
#
#     for i, v in enumerate(values):
#         plt.text(i - 0.2, v + 1, str(round(v, 2)) + '%', color='blue', fontsize=14)
#
#     plt.ylabel('Percentage')
#     title = 'Image Recognition %s' % (datetime.datetime.now().time())
#     plt.title(title)
#     file = '%s.png' % title
#     plt.savefig(file)
#     return plt
#
#
# async def send_frame(endpoint_uri, file):
#     async with aiohttp.ClientSession() as session:
#         data = {
#             'file': open(file, 'rb')}
#         async with session.post(endpoint_uri, data=data) as response:
#             if response.status == 200:
#                 json_body = await response.json()
#                 await make_graph(json_body)
#                 return await get_match(json_body)
#
#
# async def bound_fetch(sem, image_file, session):
#     # Getter function with semaphore.
#     async with sem:
#         await send_frame('https://tensorflowwaiter-aserecruitfy19.uscom-central-1.oraclecloud.com/tensorflow',
#                          image_file, session)
