from youtube_transcript_api import YouTubeTranscriptApi

transcript = YouTubeTranscriptApi.get_transcripts(ids)

with open("output.txt", "w") as text_file:
    text_file.write(transcript)