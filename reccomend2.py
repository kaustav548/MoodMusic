
import pandas as pd
df = pd.read_excel('C:\\Users\\Pritam PC\\Downloads\\dataset.xlsx')
moods = ['Happy', 'Sad', 'Surprise', 'Neutral(For any other mood)']
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
    
    

#print(mood_dict)
import random

def recommend_song(mood):
    if mood not in mood_dict:
        print("Invalid mood. Please choose from:", ", ".join(mood_dict.keys()))
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
mood = 'Happy'
print(recommend_song(mood))
#emotion_songs[mood]=youtube_link
#recommended_song = emotion_songs.get(emotion, [])
