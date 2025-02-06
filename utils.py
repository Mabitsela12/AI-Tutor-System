# searchapp/utils.py
from googleapiclient.discovery import build

def youtube_search(query):
    api_key = "AIzaSyCXRy0aayiA95hvSc24Igb_g1FXauXsLeg"  # Replace with your API key
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=1  # Limit to 1 video
    )
    response = request.execute()
    
    if response['items']:
        video_data = {
            'title': response['items'][0]['snippet']['title'],
            'url': f"https://www.youtube.com/watch?v={response['items'][0]['id']['videoId']}",
            'description': response['items'][0]['snippet']['description'],
            'video_id': response['items'][0]['id']['videoId'],  # Store the video ID for embedding
        }
        return video_data
    else:
        return None
