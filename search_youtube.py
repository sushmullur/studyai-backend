import os
import requests
import json
import time
from youtube_transcript_api import YouTubeTranscriptApi

# Define a helper method to format the subtitles and build the full transcript
def format_subtitles(subtitle_data):
    formatted_transcript = []

    for subtitle in subtitle_data:
        text = subtitle['text']
        # Add the subtitle text
        formatted_transcript.append(text)
        # Add a period (.) to separate subtitles
        formatted_transcript.append('.')
    # Combine the formatted transcript into a single string
    full_transcript = ' '.join(formatted_transcript)
    
    return full_transcript

# Define the Lambda function handler
def lambda_handler(event, context):
    try:
        # Load environment variables (e.g., YouTube API key)
        API_KEY = os.getenv("YOUTUBE_API_KEY")
        API_URL = os.getenv("YOUTUBE_API_URL")
        
        # Parse the user query from the queryStringParameters
        user_query = event.get("queryStringParameters", {}).get("q")
        
        # Check if the 'q' parameter is missing
        if user_query is None:
            return {
                "statusCode": 400,
                "body": "Missing 'q' parameter"
            }
        
        # Define the parameters for your search
        params = {
            'key': API_KEY,
            'q': user_query,  # Use the user's query
            'part': 'snippet',
            'type': 'video',
            'maxResults': 5
        }
        
        # Make the GET request to the YouTube Data API
        response = requests.get(API_URL, params=params)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            all_transcripts = ""
            
            # Extract and format video titles and video IDs
            video_data = [
                {"title": item['snippet']['title'], "videoId": item['id']['videoId']}
                for item in data['items']
            ]
            
            for video in video_data:
                video_id = video['videoId']
                try: 
                    subtitles = YouTubeTranscriptApi.get_transcript(video_id)
                except:
                    continue
                full_transcript = format_subtitles(subtitles)
                all_transcripts += full_transcript
            
            print(all_transcripts)
            # Return the video data as a JSON response with CORS enabled for any origin
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(video_data)
            }
        else:
            return {
                "statusCode": response.status_code,
                "body": "Error: YouTube API request failed"
            }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
