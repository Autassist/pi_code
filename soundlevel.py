#!/usr/bin/env python
import os, errno
import pyaudio
import spl_lib as spl
from scipy.signal import lfilter
import numpy
import wave
import subprocess
import sys
import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)
gpio.setup(18, gpio.OUT)

noise_limit = 50

''' The following is similar to a basic CD quality
   When CHUNK size is 4096 it routinely throws an IOError.
   When it is set to 8192 it doesn't.
   IOError happens due to the small CHUNK size

   What is CHUNK? Let's say CHUNK = 4096
   math.pow(2, 12) => RATE / CHUNK = 100ms = 0.1 sec
'''
CHUNKS = [4096, 9600]  # Use what you need
CHUNK = CHUNKS[1]  # rate/chunk=50ms=0.05sec
FORMAT = pyaudio.paInt16  # 16 bit
CHANNEL = 1  # 1 means mono. If stereo, put 2

'''
update your mic rate
'''
RATES = [44300, 48000]
RATE = RATES[1]

NUMERATOR, DENOMINATOR = spl.A_weighting(RATE)  # A weighting using scientific python library, converting frequencies to DB


def get_path(base, tail, head=''):
    return os.path.join(base, tail) if head == '' else get_path(head, get_path(base, tail)[1:])


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SINGLE_DECIBEL_FILE_PATH = get_path(BASE_DIR, 'decibel_data/single_decibel.txt')
MAX_DECIBEL_FILE_PATH = get_path(BASE_DIR,
                                 'decibel_data/max_decibel.txt')  # update path this txt file contains max value for db we will update this value from android app

'''
Listen to mic
'''

pa = pyaudio.PyAudio()   #creating a pyaudio object

stream = pa.open(format=FORMAT,
                 channels=CHANNEL,
                 rate=RATE,
                 input=True,
                 frames_per_buffer=CHUNK)    #creating a pyaudio stream


def is_meaningful(old, new):
    return abs(old - new) > 3


def update_text(path, content):
    try:
        f = open(path, 'w')
    except IOError as e:
        print(e)
    else:
        f.write(content)
        f.close()


def click(id):
    driver.find_element_by_id(id).click()


# def open_html(path):MAX_DECIBEL_FILE_PATH
#    driver.get(path)

def update_max_if_new_is_larger_than_max(new, max): # backup function.
    print("update_max_if_new_is_larger_than_max called")
    if new > max:
        print("greater than max db")
        gpio.output(18, gpio.HIGH)  # led on
        # call(["amixer", "-D", "pulse", "sset", "Master", "10%-"])    # decrease the volume by 10 %
        # stream.stop_stream()               # stop stream
        # stream.close()
        # p.terminate()

    else:
        gpio.output(18, gpio.LOW)  # led off
        data = wf.readframes(CHUNK)
        stream.write(data)  # play stream


def read_max_value(path):
    try:
        f = open(path, 'w')
    except IOError as e:
        print(e)
    else:
        value = f.read()
        f.close()
        return value


def listen(old=0, error_count=0, min_decibel=100, max_decibel=0):
    print("Listening")
    while True:
        try:
            block = stream.read(CHUNK)
        except IOError as e:
            error_count += 1
            print(" (%d) Error recording: %s" % (error_count, e))
        else:

            decoded_block = numpy.fromstring(block, 'Int16')
            y = lfilter(NUMERATOR, DENOMINATOR, decoded_block)
            new_decibel = 20 * numpy.log10(spl.rms_flat(y))  #root mean squared of the sound array recorded.
            if is_meaningful(old, new_decibel):
                print('A-weighted: {:+.2f} dB'.format(new_decibel))
                # max_value=read_max_value(MAX_DECIBEL_FILE_PATH)              # edith value in this text file
                # update_max_if_new_is_larger_than_max(new_decibel, max_value)
                try:
                    f = open('/home/pi/Desktop/Soundmeter/decibel_data/max_decibel.txt', 'r')
                except IOError as e:
                    print(e)
                else:
                    value2 = f.read()
                    f.close()
                    print(value2)
                try:
                    noise_limit = int(value2)
                except:
                    noise_limit = 50
                    print("invalid limit")

                if new_decibel > noise_limit:
                    gpio.output(18, gpio.HIGH)
                    print("Higher than limit")
                else:
                    gpio.output(18, gpio.LOW)
                    print("Lower than limit")

    stream.stop_stream()
    stream.close()
    pa.terminate()


if __name__ == '__main__':
    listen()
