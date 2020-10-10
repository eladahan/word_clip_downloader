import sys
import re
import time
import youtube_dl
import subprocess
import urllib.parse as urlparse
from youtube_transcript_api import YouTubeTranscriptApi

MINUTE_IN_SECONDS = 60
HOUR_IN_SECONDS = 3600
SUPPORTED_LANGUAGES = ['en', 'en-GB', 'en-US']
TRANSCRIPT_TEXT = "text"
START_TIME = "start"
DURATION = "duration"
YOUTUBE_URL = sys.argv[1]
DESIRED_WORD = sys.argv[2]
FILE_PATH = sys.argv[3]


def return_vid_id(url):
    """extracts the video id from a standard youtube url"""
    url_data = urlparse.urlparse(url)
    query = urlparse.parse_qs(url_data.query)
    video = query["v"][0]
    return video


def time_convert(seconds):
    """
    Converts time from seconds to HH:MM:SS format
    """
    return time.strftime('%H:%M:%S', time.gmtime(seconds))


def from_to_calc(url, word):
    """
    Returns tuple (start_time, duration) where the word is first said in
    the video
    """
    vid_id = return_vid_id(url)
    transcript = YouTubeTranscriptApi.get_transcript(
        vid_id, languages=SUPPORTED_LANGUAGES)
    found_sentence = dict()
    for sentence in transcript:
        formatted_words = {re.sub(r'\W+', '', clip_word.lower()) for
                           clip_word in sentence[TRANSCRIPT_TEXT].split()}
        if word.lower() in formatted_words:
            found_sentence = sentence
            break
    if found_sentence:
        start = int(found_sentence[START_TIME])
        duration = int(found_sentence[DURATION])
        return time_convert(start), time_convert(duration)


def get_download_url(url):
    """returns a url where the youtube video is easily downloadable from"""
    with youtube_dl.YoutubeDL({'format': 'best'}) as ydl:
        result = ydl.extract_info(url, download=False)
        video = result['entries'][0] if 'entries' in result else result
        return video['url']


def download_video(URL, FROM, TO, PATH):
    """downloads a clip starting at FROM that its duration is TO
    from URL and stores it in PATH """
    subprocess.call('ffmpeg -ss %s -t %s -i "%s" -c:v copy -c:a copy "%s"'
                    % (FROM, TO, URL, PATH), shell=True)


def download_wrapper(url, word, path):
    """
    Looks for the first instance word is said in the video and downloads a
    short clip of it.
    """
    time_tup = from_to_calc(url, word)
    if not time_tup:
        print("Word not found!")
        return 1
    start = time_tup[0]
    end = time_tup[1]
    download_url = get_download_url(url)
    download_video(download_url, start, end, path)


def main():
    if len(sys.argv) < 4:
        print("Usage: <youtube url> <word> <output_file_path>")
        sys.exit()
    download_wrapper(YOUTUBE_URL, DESIRED_WORD, FILE_PATH)


if __name__ == "__main__":
    main()
