from flask import Flask, render_template, Response, request
import cv2
import datetime, time
import os, sys
import numpy as np
from threading import Thread
from deepface import DeepFace
from werkzeug.utils import secure_filename
import pandas as pd
import random


global capture,rec_frame, switch, face, rec, out 
capture=0
face=0
switch=1
rec=0

#make shots directory to save pics
try:
    os.mkdir('./shots')
except OSError as error:
    pass

#Load pretrained face detection model    
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

#instatiate flask app  
app = Flask(__name__, template_folder='./templates')


camera = cv2.VideoCapture(0)

df = pd.read_excel('dataset.xlsx')
xf = pd.read_excel('dataset.xlsx',  index_col= 1)
moods = ['happy', 'sad', 'surprise', 'neutral']
mood_dict ={} #{mood: [] for mood in moods}

for index, row in df.iterrows():
    
    mood = row['Mood']
    song = row['Song Name']
        #youtube_link = row['YouTubeLink']
    
        # if song in mood_dict[mood]:
        #     # Handle duplicate songs 
        
        #     suffix = 1
        #     while f"{song}_{suffix}" in mood_dict[mood]:
        #         suffix += 1
        #     song = f"{song}_{suffix}"
        # mood_dict[mood][song] = youtube_link
    if mood not in mood_dict:
        mood_dict[mood]=[]  
    mood_dict[mood].append(song)
    

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)
        
def detect_face(frame):
    global faceCascade
    if frame is None:
        raise ValueError('Unable to get a frame!')
    result = DeepFace.analyze(frame,actions=['emotion'])
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray,1.1,4)
    for(x,y,w,h) in faces :
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
    
    print(result)
        
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    cv2.putText(frame,
                result[0]['dominant_emotion'],
                (50,50),
                font, 3,
                (0,0,255),
                2,
                cv2.LINE_4)
    return frame

def gen_frames():  # generate frame by frame from camera
    global out, capture,rec_frame
    while True:
        success, frame = camera.read() 
        if success:
            if(face):                
                frame= detect_face(frame)
            if(capture):
                capture=0
                now = datetime.datetime.now()
                p = os.path.sep.join(['shots', "shot.png".format(str(now).replace(":",''))])
                cv2.imwrite(p, frame)
            
            if(rec):
                rec_frame=frame
                frame= cv2.putText(cv2.flip(frame,1),"Recording...", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                frame=cv2.flip(frame,1)
            
                
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
                
        else:
            pass
        
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/requests',methods=['POST','GET'])
def tasks():
    global switch,camera
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            global capture
            capture=1
        elif  request.form.get('face') == 'Face Only':
            global face
            face=not face 
            if(face):
                time.sleep(4)   
        elif  request.form.get('stop') == 'Stop/Start':
            
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()
                
            else:
                camera = cv2.VideoCapture(0)
                switch=1
        elif  request.form.get('rec') == 'Start/Stop Recording':
            global rec, out
            rec= not rec
            if(rec):
                now=datetime.datetime.now() 
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('vid_{}.avi'.format(str(now).replace(":",'')), fourcc, 20.0, (640, 480))
                #Start new thread for recording the video
                thread = Thread(target = record, args=[out,])
                thread.start()
            elif(rec==False):
                out.release()
                          
                 
    elif request.method=='GET':
        return render_template('index.html')
    return render_template('index.html')

@app.route('/mood')
def mood():
    img = cv2.imread("shots\shot.png")
    result = DeepFace.analyze(img,actions=['emotion'])
    mood = str(result[0]['dominant_emotion'])
    #print(recommend_song(mood))
    #emotion_songs[mood]=youtube_link
    #recommended_song = emotion_songs.get(emotion, [])
    songs1 = recommend_song(mood)
    youtube = recomend_link(songs1)
    return youtube
    

def recommend_song(mood):
    print(mood)
    if mood not in mood_dict:
        print("Invalid mood. Please choose from:", ", ".join(str(mood_dict.keys())))
        return

    #songs = list(mood_dict[mood].keys())
    songs = mood_dict[mood]
    if len(songs) == 0:
        print("No songs available for the given mood.")
        return

    # Select a random song
    song = random.choice(songs)
  #  youtube_link = mood_dict[mood][song]

    return song #youtube_link
#mood = 'happy'
#print(recommend_song(mood))
#emotion_songs[mood]=youtube_link
#recommended_song = emotion_songs.get(emotion, [])
#songs1 = recommend_song(mood)

def recomend_link(songs1):
    yt = xf.loc[[songs1],['YoutubeLink']].values
    youtube_link=str(yt).lstrip("[['").rstrip("']]")
    return youtube_link

#print(recomend_link(songs1))
    

if __name__ == '__main__':
    app.run()
