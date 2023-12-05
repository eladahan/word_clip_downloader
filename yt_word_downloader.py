import re
import time
import yt_dlp
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi
import urllib.parse as urlparse


MINUTE_IN_SECONDS = 60
HOUR_IN_SECONDS = 3600
SUPPORTED_LANGUAGES = ['en', 'en-GB', 'en-US']
TRANSCRIPT_TEXT = "text"
START_TIME = "start"
DURATION = "duration"
TIMESTAMP = 1
TIMED_CLIP = "1"
WORD_CLIP = "2"


def return_vid_id(url):
    """extracts the video id from a standard youtube url"""
    url_data = urlparse.urlparse(url)
    query = urlparse.parse_qs(url_data.query)
    video = query["v"][0]
    return video

def timestamp_to_seconds(timestamp):
    """Converts timestamp string to seconds"""
    m, s = timestamp.split(":")
    return int(m) * MINUTE_IN_SECONDS + int(s)

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
    with yt_dlp.YoutubeDL({'format': 'best'}) as ydl:
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

def download_clip(url, start, duration, path):
    """downloads a clip starting at start, duration seconds long to path"""
    download_url = get_download_url(url)
    download_video(download_url, start, duration, path)


def main():

    print("Please choose the desired option (1/2)")
    print("1. Timed Clip")
    print("2. Clip of a certain word")
    option = input("")

    if option == TIMED_CLIP:
        print("please insert according to the following format:")
        print("<youtube_url> <start_time> <duration (seconds)> <path>")
        print("example:\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ 0:00 10 test.mp4")
        inp = input("").split(" ")
        try:
            timestamp = inp[TIMESTAMP]
            inp[TIMESTAMP] = timestamp_to_seconds(timestamp)
            download_clip(*inp)
        except:
            print("faulty arguments supplied")

    elif option == WORD_CLIP:
        print("please insert according to the following format:")
        print("<youtube url> <word> <output_file_path>")
        print("example:\nhttps://www.youtube.com/watch?v=WniMB85B1ZA Applause test.mp4")
        inp = str(input("")).split(" ")
        try:
            download_wrapper(*inp)
        except:
            print("faulty arguments supplied")
    else:
        print("option unavailable")


if __name__ == "__main__":
    main()
