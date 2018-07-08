##############################################################################
##                         NALA.PY - MAC RELEASE                            ##
##############################################################################

'''
Nala.py

Author: @Jim Schwoebel
Role: Chief Executive Officer
Git Repo: [TBA]
Script: nala-mac.py 
Version: 0.10
License: Trade secret
Contact: js@neurolex.co 

(C) 2018 NeuroLex Laboratories, Inc.
All rights reserved. 

This version is intended for mac operationg systems only. If you have a different
operation system please use a different distribution.

THIS CODE IS PROTECTED BY UNITED STATES AND INTERNATIONAL LAW. It constitutes
a TRADE SECRET possessed by NeuroLex Laboratories, Inc. If you received this
code base by error, please delete this code immediately and do not read below.
Please do not distribute this code base outside of our company.
'''

##############################################################################
##                           RELEASE NOTES                                  ##
##############################################################################

'''
Nala is a verastile open-source voice assistant to improve the workflow of 
your daily life. Nala uses actions which can be triggered by user voice queries. 

All the user needs to do is say 'hey nala' and it will spark Nala to listen 
and respond to requests.

Nala uses machine learning to parse through user intents. If a request is not 
understood or is an anomaly, a web search is performed to give th user an answer.
'''

##############################################################################
##                          IMPORT STATEMENT                                ##
##############################################################################

# first thing we need to do is get the import statements right.

import ftplib
from ftplib import FTP
import smtplib, os, glob, time, getpass, socket, pyaudio, pygame, wave
import shutil, importlib, geocoder, librosa, json, re, platform, urllib
import requests, random, webbrowser, pickle
from pydub import AudioSegment
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
from datetime import datetime
from sys import byteorder
from array import array
from struct import pack
import soundfile as sf
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import urllib.request
from cryptography.fernet import Fernet
import pyscreenshot as ImageGrab
import pyautogui, cv2, readchar, psutil
import speech_recognition as sr_audio
import pyttsx3 as pyttsx
import soundfile as sf 
import collections, contextlib, sys, wave, webrtcvad, struct
import cv2, itertools, operator
import skvideo.io, skvideo.motion, skvideo.measure
from moviepy.editor import VideoFileClip
from PIL import Image

##############################################################################
##                          GET ENVIRONMENT VARS                            ##
##############################################################################

# be sure to include google application credentials as a .json file 
# referenced in the .bash_profile environment vars.
# e.g. export GOOGLE_APPLICATION_CREDENTIALS='/Users/jimschwoebel/Desktop/appcreds/NLX-infrastructure-b9201d884ea5.json'

##############################################################################
##                          ACTIONS LOADED                                  ##
##############################################################################

hostdir = os.getcwd()
os.chdir(hostdir+'/actions')
listdir=os.listdir()

action_list=list()
for i in range(len(listdir)):
    if listdir[i][-3:]=='.py':
        action_list.append(listdir[i])

os.chdir(hostdir)

##############################################################################
##                           HELPER FUNCTIONS                               ##
##############################################################################

def speaktext(hostdir,text):
    # speak to user from a text sample (tts system)  
    curdir=os.getcwd()
    os.chdir(hostdir+'/actions') 
    os.system("python3 speak.py '%s'"%(str(text)))
    os.chdir(curdir)

def curloc():
    # get current location, limit 1000 requests/day
    r=requests.get('http://ipinfo.io')
    location=r.json()
    return location

def get_date():
    return str(datetime.now())

def record_to_file(path,filename,recordtime):

    # record 3 second voice file 
    CHUNK = 1024 
    FORMAT = pyaudio.paInt16 #paInt8
    CHANNELS = 1 
    RATE = 16000 #sample rate
    RECORD_SECONDS = recordtime
    WAVE_OUTPUT_FILENAME = filename

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK) #buffer

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data) # 2 bytes(16 bits) per channel

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio_sphinx(filename):
    # transcribe the audio (note this is only done if a voice sample)
    r=sr_audio.Recognizer()
    with sr_audio.AudioFile(filename) as source:
        audio = r.record(source) 
    text=r.recognize_sphinx(audio)

    return text

def transcribe_audio_google(filename):
    # transcribe the audio (note this is only done if a voice sample)
    r=sr_audio.Recognizer()
    with sr_audio.AudioFile(filename) as source:
        audio = r.record(source) 
    text=r.recognize_google_cloud(audio)

    return text    

def playbackaudio(filename):
    # takes in a question and a filename to open and plays back the audio
    # file and prints on the screen the question for the user 
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    time.sleep(0.5)
    return "playback completed"

def capture_video(filename, timesplit):
    video=cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    frame_width = int(video.get(3))
    frame_height = int(video.get(4))
    out = cv2.VideoWriter(filename,cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height))

    a=0
    start=time.time()

    while True:
        a=a+1
        check, frame=video.read()
        #print(check)
        #print(frame)
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        out.write(frame)
        #cv2.imshow("frame",gray)
        end=time.time()
        if end-start>timesplit:
            break 
        #print(end-start)

    print(a)
    video.release()
    out.release() 
    cv2.destroyAllWindows()

    return filename 

def cut_faces(modeldir,filename):

    hostdir=os.getcwd()
    capture_video(filename, 10)
    face_cascade = cv2.CascadeClassifier(modeldir+'/data/models/haarcascade_frontalface_default.xml')
    foldername=filename[0:-4]+'_faces'

    try:
        os.mkdir(foldername)
    except:
        shutil.rmtree(foldername)
        os.mkdir(foldername)

    shutil.move(hostdir+'/'+filename, hostdir+'/'+foldername+'/'+filename)
    os.chdir(foldername)

    videodata=skvideo.io.vread(filename)
    frames, rows, cols, channels = videodata.shape
    metadata=skvideo.io.ffprobe(filename)
    frame=videodata[0]
    r,c,ch=frame.shape

    for i in range(0,len(videodata),25):
        #row, col, channels
        skvideo.io.vwrite("output"+str(i)+".png", videodata[i])

    listdir=os.listdir()
    facenums=0

    for i in range(len(listdir)):
        if listdir[i][-4:]=='.png':

            try:

                image_file = listdir[i]

                img = cv2.imread(hostdir+'/'+foldername+'/'+image_file)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                increment=0
                print(len(faces))

                if len(faces) == 0:
                    pass
                else:
                    for (x,y,w,h) in faces:
                        os.chdir(hostdir+'/'+foldername)
                        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                        newimg=img[y:y+h,x:x+w]
                        new_image_file=image_file[0:-4] + '_face_' + str(increment) + '.png'
                        cv2.imwrite(new_image_file, newimg)
                        facenums=facenums+1

            except:
                print('error')

    os.chdir(hostdir+'/'+foldername)
    listdir=os.listdir()
    print(listdir)
    
    for i in range(len(listdir)):
        if listdir[i][-4:]=='.png':
            if listdir[i].find('face') < 0:
                os.remove(listdir[i])

    return facenums

def register_user(action_list, hostdir):

    # hostdir
    os.chdir(hostdir)
    hostdir=os.getcwd()

    # assume default directory is hostdir 
    # if any folders exist delete them
    try:
        os.mkdir(hostdir+'/data/wakewords')
    except:
        shutil.rmtree(hostdir+'/data/wakewords')
        os.mkdir(hostdir+'/data/wakewords')
    try:
        os.mkdir(hostdir+'/data/actions')
    except:
        shutil.rmtree(hostdir+'/data/actions')
        os.mkdir(hostdir+'/data/actions')
    try:
        os.mkdir(hostdir+'/data/queries')
    except:
        shutil.rmtree(hostdir+'/data/queries')
        os.mkdir(hostdir+'/data/queries')
    try:
        os.mkdir(hostdir+'/data/baseline')
    except:
        shutil.rmtree(hostdir+'/data/baseline')
        os.mkdir(hostdir+'/data/baseline')

    os.chdir(hostdir+'/data/baseline')

    # get name from user profile name, if not record it 
    speaktext(hostdir, 'To begin, you must register with us. I have a few quick questions for you. Please type in the answers to the following questions.')
    email=input('what is your email? \n')
    name=input('what is your name (leave blank for %s)? \n'%(getpass.getuser()))
    if name == '':
        name=getpass.getuser()

    speaktext(hostdir, 'Now give us a few seconds to make an account for you.')

    facenums=cut_faces(hostdir, name+'.avi')
    os.chdir(hostdir+'/data/baseline')

    jsonfile=open('settings.json','w')

    data = {
        'alarm': False,
        'alarm time': 8,
        'greeting': True,
        'end': time.time(),
    }
    jsonfile=open('settings.json','w')
    json.dump(data,jsonfile)
    jsonfile.close()

    jsonfile=open('registration.json','w')
    data = {
        'name': name, 
        'email': email,
        'userID': 0,
        'hostdir': os.getcwd(),
        'location': curloc(),
        'rest time': 0.10,
        'facenums': facenums,
        'registration date': get_date(),
        'google tts': 'en-US-Wavenet-C',
        }

    json.dump(data,jsonfile)
    jsonfile.close()

    jsonfile=open('actions.json','w')
    data = {
        'logins': [], # login datetime
        'logouts': [], # logout datetime (last time before login)
        'active session': [],
        'sessions': [],
        'query count': 0,
        'queries': [],
        'noise': [],
        'action count': 0,
        'action log': [], #action, datetime, other stuff 
        'loopnum': 0,
        'available actions': action_list,
    }
    json.dump(data, jsonfile)
    jsonfile.close()

    # store 2 copies in case of deletion
    shutil.copy(os.getcwd()+'/registration.json', hostdir+'/registration.json')
    shutil.copy(os.getcwd()+'/settings.json', hostdir+'/settings.json')
    shutil.copy(os.getcwd()+'/actions.json', hostdir+'/actions.json')

    speaktext(hostdir, 'Thank you, you are now registered.')


def update_database(hostdir,logins,logouts,session,sessions,query_count,queries,noise,action_count,loopnum, alarm, end):

    curdir=os.getcwd()
    os.chdir(hostdir)

    # update only the fields that matter
    data=json.load(open('actions.json'))

    data['logins']=logins
    data['logouts']=logouts
    data['active session']=session
    data['sessions']=sessions
    data['query count']=query_count
    data['queries']=queries
    data['noise']=noise
    data['action count']=action_count
    data['loopnum']=loopnum

    jsonfile=open('actions.json','w')
    json.dump(data,jsonfile)
    jsonfile.close()

    data=json.load(open('settings.json'))

    data['alarm']=alarm
    data['end']=end

    jsonfile=open('settings.json','w')
    json.dump(data,jsonfile)
    jsonfile.close()

    # store backup copy just in case of either database being corrupted 
    os.chdir(hostdir+'/data/baseline')
    os.remove('actions.json')
    os.remove('settings.json')
    shutil.copy(hostdir+'/actions.json',os.getcwd()+'/actions.json')
    shutil.copy(hostdir+'/settings.json',os.getcwd()+'/settings.json')

    os.chdir(curdir)

def wav_cleanup():
    # remove .wav files in current directory to clean it up
    # before next query 
    listdir=os.listdir()
    for i in range(len(listdir)):
        if listdir[i][-4:]=='.wav':
            os.remove(listdir[i])

##############################################################################
##                           LOAD DATABASE                                  ##
##############################################################################

# try to load vars in baseline.json file or register a user 

try:
    # load database 
    os.chdir(hostdir)

    # registration.json data 
    try:
        database=json.load(open('registration.json'))
    except:
        # restore database if corrupted
        print('registration database corrupted, restoring...')
        os.chdir(hostdir+'/data/baseline/')
        database=json.load(open('registration.json'))
        os.chdir(hostdir)
        os.remove('registration.json')
        shutil.copy(hostdir+'/data/baseline/registration.json',hostdir+'/registration.json')

    name=database['name']
    regdate=database['registration date']
    rest_time=database['rest time']

    # actions.json data 
    try:
        database=json.load(open('actions.json'))
    except:
        # restore database if corrupted
        print('actions database corrupted, restoring...')
        os.chdir(hostdir+'/data/baseline/')
        database=json.load(open('actions.json'))
        os.chdir(hostdir)
        os.remove('actions.json')
        shutil.copy(hostdir+'/data/baseline/actions.json',hostdir+'/actions.json')
        
    logins=database['logins']
    logouts=database['logouts']
    session=database['active session']
    sessions=database['sessions']
    query_count=database['query count']
    queries=database['queries']
    noise=database['noise']
    action_count=database['action count']
    action_log=database['action log']
    loopnum=database['loopnum']
    avail_actions = database['available actions']
    #print(database)

    # settings.json data
    try:
        database=json.load(open('settings.json'))
    except:
        # restore database if corrupted
        print('settings database corrupted, restoring...')
        os.chdir(hostdir+'/data/baseline/')
        database=json.load(open('settings.json'))
        os.chdir(hostdir)
        os.remove('settings.json')
        shutil.copy(hostdir+'/data/baseline/settings.json',hostdir+'/settings.json')
        
    alarm=database['alarm']
    alarm_time=database['alarm time']
    greeting=database['greeting']
    end=database['end']

    # instantiate variables 
    logins.append(get_date())
    t=1
    query_request=False 
    turn_off = False

except:
    # register user if no user exists
    print('registering new user!')
    register_user(action_list, hostdir)

    # load database
    os.chdir(hostdir)

    # registration data 
    database=json.load(open('registration.json'))
    name=database['name']
    regdate=database['registration date']
    rest_time=database['rest time']

    # action data 
    database=json.load(open('actions.json'))
    logins=database['logins']
    logouts=database['logouts']
    session=database['active session']
    sessions=database['sessions']
    query_count=database['query count']
    queries=database['queries']
    noise=database['noise']
    action_count=database['action count']
    action_log=database['action log']
    loopnum=database['loopnum']
    avail_actions = database['available actions']
    
    # settings.json
    settings=json.load(open('settings.json'))
    alarm=settings['alarm']
    alarm_time=settings['alarm time']
    greeting=settings['greeting']
    end=settings['end']

    # instantiate variables
    logins.append(get_date())
    t=1
    query_request=False 
    turn_off = False

##############################################################################
##                           MAIN SCRIPT                                    ##
##############################################################################

while turn_off == False:
    # record a 3.0 second voice sample
    # use try statement to avoid errors 
    try:

        # welcome user back if it's been over an hour since login 
        start=time.time()

        # set alarm and make false after you trigger alarm 
        if alarm == True and alarm_time == datetime.now().hour:
            os.chdir(hostdir+'/actions')
            os.system('python3 alarm.py %s'%(hostdir))
            alarm == False
            os.chdir(hostdir)

        if abs(end-start) > 60*60:

            end=time.time()

            if greeting == True:
               speaktext(hostdir,'welcome back, %s'%(name.split()[0]))
               os.chdir(hostdir+'/actions')
               os.system('python3 weather.py %s'%(hostdir))
               os.chdir(hostdir)

            # log session if the time of activity is greater than 60 minutes
            sessions.append(session)
            # start a new session 
            session=list()

        # change to host directory 
        os.chdir(hostdir)

        os.chdir(hostdir+'/data/models/')
        os.system('python detect_nala.py Nala.pmdl')
        
        query_num=0
        query_request=False

        while query_request==False and query_num <= 3: 

            os.chdir(hostdir)
            if query_num==0:
                speaktext(hostdir,'how can I help you?')
                playbackaudio(hostdir+'/data/tone.wav')
            else:
                speaktext(hostdir,"Sorry, I did not get that. How can I help?")
                playbackaudio(hostdir+'/data/tone.wav')

            time.sleep(0.50)
            
            unique_sample='sample'+str(loopnum)+'_'+str(query_num)+'.wav'
            record_to_file(os.getcwd(),unique_sample, 3.0)
            transcript=transcribe_audio_google(unique_sample)
            print('google: '+transcript)
            shutil.move(hostdir+'/'+unique_sample,hostdir+'/data/queries/'+unique_sample)
            query_transcript=transcript.lower().split()

            # break if it finds a query 
            for i in range(len(query_transcript)):

                # iterate through transcript 
                os.chdir(hostdir+'/actions')
                print(query_transcript[i])

                if query_transcript[i] in ['weather', 'whether']:
                    os.system('python3 weather.py %s'%(hostdir))
                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 weather.py'
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True 

                elif query_transcript[i] in ['event','social', 'friends', 'go out']:
                    # either get a meetup or pull from db 
                    randint=random.randint(0,1)

                    if randint==0:
                        os.system('python3 events.py %s'%(hostdir))
                        query={
                            'date':get_date(),
                            'audio': unique_sample,
                            'transcript type': 'google speech API',
                            'query transcript': query_transcript[i],
                            'transcript': transcript,
                            'response': 'python3 events.py'
                        }

                    elif randint==1:
                        os.system('python3 social.py %s'%(hostdir))
                        query={
                            'date':get_date(),
                            'audio': unique_sample,
                            'transcript type': 'google speech API',
                            'query transcript': query_transcript[i],
                            'transcript': transcript,
                            'response': 'python3 social.py'
                        }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True   

                elif query_transcript[i] in ['coffee']:

                    os.system('python3 yelp.py %s coffee'%(hostdir))
                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 yelp.py'
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True 

                elif query_transcript[i] in ['news']:

                    os.system('python3 news.py %s'%(hostdir))
                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 news.py'
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True 

                elif query_transcript[i] in ['music']:

                    os.system("python3 music.py %s '%s'"%(hostdir, transcript))
                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 music.py'
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True 
                    break

                elif query_transcript[i] in ['joke']:

                    os.system("python3 makeajoke.py %s"%(hostdir))
                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 makeajoke.py'
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True 
                    break  

                elif query_transcript[i] in ['exercise','run','workout']:

                    os.system('python3 exercise.py %s'%(hostdir))
                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 exercise.py'
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True 
                    break

                elif query_transcript[i] in ['sport','sports','nba','cavs']:

                    os.system('python3 espn.py %s nba'%(hostdir))
                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 espn.py'
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True 
                    break

                elif query_transcript[i] in ['book', 'flight', 'travel']:

                    speaktext(hostdir,'Ok, great %s! I need a bit more information to do that.'%(name.split()[0]))
                    os.system('python3 plan_trip-speak.py %s'%(hostdir))
                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 plan_trip.py'
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True 
                    break

                elif query_transcript[i] in ['alarm']:

                    if transcript == 'set alarm ':

                        speaktext(hostdir,'setting alarm for %s in the morning'%(str(alarm_time)))

                        query={
                            'date':get_date(),
                            'audio': unique_sample,
                            'transcript type': 'google speech API',
                            'query transcript': query_transcript[i],
                            'transcript': transcript,
                            'response': 'setting alarm for %s in the morning'%(str(alarm_time)),
                        }

                        alarm=True

                    elif transcript == 'stop alarm ':

                        speaktext(hostdir,'stopping all alarms')

                        query={
                            'date':get_date(),
                            'audio': unique_sample,
                            'transcript type': 'google speech API',
                            'query transcript': query_transcript[i],
                            'transcript': transcript,
                            'response': 'stopping all alarms',
                        }

                        alarm=False

                    else: 

                        print('doing nothing...')

                        query={
                            'date':get_date(),
                            'audio': unique_sample,
                            'transcript type': 'google speech API',
                            'query transcript': query_transcript[i],
                            'transcript': transcript,
                            'response': 'doing nothing',
                        }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True
                    break    

                elif query_transcript[i] in ['search']:

                    speaktext(hostdir,"what would you like to search for?")
                    playbackaudio(hostdir+'/data/tone.wav')
                    unique_sample='sample'+str(loopnum)+'_'+str(query_num)+'_1.wav'
                    record_to_file(os.getcwd(),unique_sample, 5.0)
                    search_query=transcribe_audio_google(unique_sample)
                    print('google: '+search_query)
                    shutil.move(os.getcwd()+'/'+unique_sample,hostdir+'/data/queries/'+unique_sample)

                    os.system('python3 search.py %s %s'%(hostdir, search_query.replace('search','')))
                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 search.py %s %s'%(hostdir, search_query.replace('search',''))
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True    
                    break

                elif query_transcript[i] in ['food', 'eat', 'restaurants']:

                    speaktext(hostdir,"Okay, %s. I will find you a place to eat nearby."%(name.split()[0]))
                        
                    os.system('python3 yelp.py %s food'%(hostdir))

                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 yelp.py %s food'%(hostdir)
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True 
                    break

                elif query_transcript[i] in ['nightlife']:

                    speaktext(hostdir,"Okay, %s. I will find you some things to do tonight."%(name.split()[0]))

                    os.system('python3 yelp.py %s nightlife'%(hostdir))

                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 yelp.py %s nightlife'%(hostdir)
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True 
                    break

                elif query_transcript[i] in ['bar','beer','beers']:

                    speaktext(hostdir,"Okay, %s. I will find you a bar."%(name.split()[0]))

                    os.system('python3 yelp.py %s beers'%(hostdir))

                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 yelp.py %s beers'%(hostdir)
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True 
                    break

                elif query_transcript[i] in ['ice','cream'] or transcript.find('ice cream')>=0:

                    speaktext(hostdir,"Okay, %s. I will find you some ice cream nearby."%(name.split()[0]))

                    os.system("python3 yelp.py %s 'ice cream'"%(hostdir))

                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': "python3 yelp.py %s 'ice cream'"%(hostdir)
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True   
                    break   

                elif query_transcript[i] in ['grateful', 'gratitude']:

                    os.system('python3 grateful.py %s'%(hostdir))

                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 grateful.py %s'%(hostdir)
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True  
                    break

                elif query_transcript[i] in ['meditation', 'meditate', 'relax']:

                    os.system('python3 meditation.py %s'%(hostdir))

                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 meditation.py %s'%(hostdir)
                    }

                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True 
                    break

                elif query_transcript[i] in ['chill'] or transcript.find('chill out')>=0:

                    speaktext(hostdir,'Okay, %s. I will play some chillout vibes to calm you down. Namaste!'%(name.split()[0]))
                    
                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'python3 chillout.py',
                    }

                    logouts.append(get_date())
                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True  
                    end=time.time()
                    os.system('python3 chillout.py %s'%(hostdir))
                    break 

                elif query_transcript[i] in ['sleep']:

                    speaktext(hostdir,"Okay, %s. I will sleep for 30 minutes."%(name.split()[0]))

                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': 'sleep for 30 minutes',
                    }

                    time.sleep(60*30)
                    query_request=True 
                    speaktext(hostdir,"Okay, I am back %s. I am here if you need me."%(name.split()[0]))
                    break

                elif query_transcript[i] in ['off'] or transcript.find('log out')>=0:

                    speaktext(hostdir,'Okay, %s. I will turn myself off. See you next time!'%(name.split()[0]))
                    
                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': '',
                        'meta': 'logged off with turn_off = True',
                    }

                    logouts.append(get_date())
                    query_count=query_count+1 
                    queries.append(query)
                    session.append(query)
                    action_count=action_count+1
                    query_request=True  
                    end=time.time()
                    session.append('updated database @ %s'%(get_date()))
                    update_database(hostdir,logins,logouts,session,sessions,query_count,queries,noise,action_count,loopnum, alarm, end)
                    turn_off=True 
                    break 

                elif query_transcript[i] in ['shut', 'down', 'restart']:

                    if query_transcript.index('shut')>=0 and query_transcript.index('down')>=0:
                        # only shutdown if both shut and down are present in google transcript 
                        speaktext(hostdir,'Okay, %s. I will shutdown the computer. See you next time!'%(name.split()[0]))
                       
                        query={
                            'date':get_date(),
                            'audio': unique_sample,
                            'transcript type': 'google speech API',
                            'query transcript': query_transcript[i],
                            'transcript': transcript,
                            'response': "python3 shutdown.py",
                        }

                        query_count=query_count+1 
                        queries.append(query)
                        session.append(query)
                        action_count=action_count+1
                        query_request=True  
                        end=time.time()
                        print(query_request)
                        session.append('updated database @ %s'%(get_date()))
                        update_database(hostdir,logins,logouts,session,sessions,query_count,queries,noise,action_count,loopnum, alarm, end)
                        os.system('python3 shutdown.py')
                        break

                    elif query_transcript[i] == 'restart':
                        # restart computer using a forced reboot 
                        speaktext(hostdir,'Okay, %s. I will restart the computer. See you next time!'%(name.split()[0]))
                        
                        query={
                            'date':get_date(),
                            'audio': unique_sample,
                            'transcript type': 'google speech API',
                            'query transcript': query_transcript[i],
                            'transcript': transcript,
                            'response': "python3 reboot.py",
                        }

                        query_count=query_count+1 
                        queries.append(query)
                        session.append(query)
                        action_count=action_count+1
                        query_request=True  
                        end=time.time()
                        print(query_request)
                        session.append('updated database @ %s'%(get_date()))
                        update_database(hostdir,logins,logouts,session,sessions,query_count,queries,noise,action_count,loopnum, alarm, end)
                        os.system('python3 reboot.py')
                        break

                else:

                    query={
                        'date':get_date(),
                        'audio': unique_sample,
                        'transcript type': 'google speech API',
                        'query transcript': query_transcript[i],
                        'transcript': transcript,
                        'response': "Sorry, I didn't get that. How can I help?"
                    }
                    noise.append(query)
                    session.append(query)

            query_num=query_num+1 
            os.chdir(hostdir)

        # update database 
        end=time.time()
        # can include this info in session, but I have left out because it can get a bit messy
        # session.append('updated database @ %s'%(get_date()))
        try:
            update_database(hostdir,logins,logouts,session,sessions,query_count,queries,noise,action_count,loopnum, alarm, end)
        except:
            print('error updating database')

        # clean up wav files in host directory 
        try:
            os.chdir(hostdir)
            wav_cleanup()
        except:
            pass

    except:
        pass 
    
    # sleep appropriately before each query to not harm the processor and suck battery 
    time.sleep(rest_time)
    loopnum=loopnum+1 

# say goodbye if loop breaks and is turned off 
speaktext(hostdir,'Goodbye')
    