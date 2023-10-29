import os
import requests
import json
import psycopg2
from youtube_transcript_api import YouTubeTranscriptApi

def add_to_db():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])

def _get_index_request_json(customer_id: int, corpus_id: int, transcript: str):
    """ Returns some example data to index. """

    document = {}
    document["document_id"] = "doc-id-2"
    # Note that the document ID must be unique for a given corpus
    sections = []
    section = {}
    section["text"] = transcript
    sections.append(section)
    document["section"] = sections

    request = {}
    request['customer_id'] = customer_id
    request['corpus_id'] = corpus_id
    request['document'] = document

    return json.dumps(request)

def index_document(customer_id: int, corpus_id: int, idx_address: str, api_key: str, transcript: str):
    """ Indexes content to the corpus.
    Args:
        customer_id: Unique customer ID in vectara platform.
        corpus_id: ID of the corpus to which data needs to be indexed.
        idx_address: Address of the indexing server. e.g., api.vectara.io
        jwt_token: A valid Auth token.

    Returns:
        (response, True) in case of success and returns (error, False) in case of failure.

    """

    post_headers = {
        "x-api-key": f"{api_key}",
        "customer-id": f"{customer_id}"
    }
    response = requests.post(
        f"https://{idx_address}/v1/index",
        data=_get_index_request_json(customer_id, corpus_id, transcript),
        verify=True,
        headers=post_headers)

    if response.status_code != 200:
        print("REST upload failed with code %d, reason %s, text %s",
                       response.status_code,
                       response.reason,
                       response.text)
        return response, False
    return response, True

# Define a helper method to format the subtitles and build the full transcript
def format_subtitles(subtitle_data):
    formatted_transcript = []

    for subtitle in subtitle_data:
        text = subtitle['text']
        # Add the subtitle text
        formatted_transcript.append(text)
    # Combine the formatted transcript into a single string
    full_transcript = ' '.join(formatted_transcript)
    
    print(full_transcript)
    return full_transcript

def _get_query_json(customer_id: int, corpus_id: int, query_value: str):
    """ Returns a query json. """
    query = {}
    query_obj = {}

    query_obj["query"] = query_value
    query_obj["num_results"] = 10

    corpus_key = {}
    corpus_key["customer_id"] = customer_id
    corpus_key["corpus_id"] = corpus_id
    query_obj["corpus_key"] = [ corpus_key ]

    summary = {}
    summary["responseLang"] = "en"
    summary["maxSummarizedResults"] = 5
    query_obj["summary"] = [ summary ]

    query["query"] = [ query_obj ]

    return json.dumps(query)

def query(customer_id: int, corpus_id: int, query_address: str, api_key: str, query: str):
    """This method queries the data.
    Args:
        customer_id: Unique customer ID in vectara platform.
        corpus_id: ID of the corpus to which data needs to be indexed.
        query_address: Address of the querying server. e.g., api.vectara.io
        api_key: A valid API key with query access on the corpus.

    Returns:
        (response, True) in case of success and returns (error, False) in case of failure.

    """
    post_headers = {
        "customer-id": f"{customer_id}",
        "x-api-key": api_key
    }

    response = requests.post(
        f"https://{query_address}/v1/query",
        data=_get_query_json(customer_id, corpus_id, query),
        verify=True,
        headers=post_headers)

    if response.status_code != 200:
        print("Query failed with code %d, reason %s, text %s",
                       response.status_code,
                       response.reason,
                       response.text)
        return response, False
        
    return response, True


def call_vectara(transcript):
    print("Inside call vectara")
    query_address = "api.vectara.io"
    customer_id = 1354170844
    corpus_id = 5
    api_key = "zwt_ULcB3HdLImfP3GJ7jDwL7iMTbx0yaJoJ8LLzxg"
    index_document(customer_id, corpus_id, query_address, api_key, transcript)
    USER_QUERY = "Summarize everything you know about this and create a study guide out of it in the form of a rich text markdown file " + transcript
    response, success = query(customer_id, corpus_id, query_address, api_key, USER_QUERY)
    return response.text

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
            'maxResults': 1
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
            print("Calling vectara")
            summary = call_vectara(all_transcripts)
            # Return the video data as a JSON response with CORS enabled for any origin
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(summary)
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
