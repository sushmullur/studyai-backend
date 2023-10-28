from youtube_transcript_api import YouTubeTranscriptApi

transcript = YouTubeTranscriptApi.get_transcript('X8h4dq9Hzq8')

with open("output.txt", "w") as text_file:
    text_file.write(transcript)