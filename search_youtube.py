import os
import requests
import json

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
            
            # Extract and format video titles and video IDs
            video_data = [
                {"title": item['snippet']['title'], "videoId": item['id']['videoId']}
                for item in data['items']
            ]
            
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
