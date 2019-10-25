#!/usr/bin/env python


import asyncio
import websockets
MAX_DECIBEL_FILE_PATH = get_path(BASE_DIR, 'decibel_data/max_decibel.txt')  
async def hello(websocket, path):
    value = await websocket.recv()
    print(value)
    try:
        f = open(MAX_DECIBEL_FILE_PATHpath, 'w')
    except IOError as e:
        print(e)
    else:
        f.write(value)
        f.close()

start_server = websockets.serve(hello, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
