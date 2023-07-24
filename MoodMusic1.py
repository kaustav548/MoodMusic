import deepface
from deepface import DeepFace
import cv2
import pandas as pd
from math import isnan

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("CANNOT OPEN WEBCAM")

while True :
    ret,frame = cap.read()
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
    cv2.imshow('original video',frame)
    
    if cv2.waitKey(2) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# print(result[0]['dominant_emotion'])

df = pd.read_excel('dataset.xlsx')
moods = ['happy', 'sad', 'surprise', 'neutral']
mood_dict ={} #{mood: [] for mood in moods}

for index, row in df.iterrows():
    
    mood = row['Mood']
    song = row['Song Name']
    # youtube_link = row['YouTubeLink']
    
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
    
# mood_dict = filter(lambda k: isnan(k), mood_dict)

#print(mood_dict)
import random

def recommend_song(mood):
    # print(mood_dict.keys())
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

    return song, #youtube_link
mood = str(result[0]['dominant_emotion'])
print(recommend_song(mood))
#emotion_songs[mood]=youtube_link
#recommended_song = emotion_songs.get(emotion, [])
