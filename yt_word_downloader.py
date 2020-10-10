import sys
import youtube_dl
import subprocess
import urlparse4 as urlparse
from youtube_transcript_api import YouTubeTranscriptApi

MINUTE_IN_SECONDS = 60
HOUR_IN_SECONDS = 3600
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

def time_convert(time):
	"""converts time from seconds to HH:MM:SS format"""
	hours = time / HOUR_IN_SECONDS
	time = time - (hours * HOUR_IN_SECONDS)
	minutes = time / MINUTE_IN_SECONDS
	time = time - (minutes * MINUTE_IN_SECONDS)
	seconds = time
	units = [hours, minutes, seconds]
	t = ""
	for u in units:
		if u < 10:
			t += "0"+str(u)+":"
		else:
			t += str(u)+":"
	return t[:-1]

def from_to_calc(url, word):
	"""returns tuple (start_time, duration)
	where the word is first said in the video
	"""
	vid_id = return_vid_id(url)
	transcript = YouTubeTranscriptApi.get_transcript(vid_id)
	found = dict()
	for sentence in transcript:
		if word in sentence[TRANSCRIPT_TEXT]:
			found = sentence
			break
	if found == dict():
		return None
	else:
		start = int(sentence[START_TIME])
		finish = int(sentence[DURATION])
		return (time_convert(start), time_convert(finish))

def get_download_url(url):
	"""returns a url where the youtube video is easly downloadble from"""
	with youtube_dl.YoutubeDL({'format': 'best'}) as ydl:
		result = ydl.extract_info(url, download=False)
		video = result['entries'][0] if 'entries' in result else result
		return video['url']

def download_video(URL, FROM, TO, PATH):
	"""downloads a clip starting at FROM that its duration is TO 
	from URL and stores it in PATH """
	subprocess.call('ffmpeg -ss %s -t %s -i "%s" -c:v copy -c:a copy "%s"' % (FROM, TO, URL, PATH), shell=True)

def download_wrapper(url, word, path):
	"""looks for the first instance word is said in the video and downloads a short clip
	where the word is said"""
	time_tup = from_to_calc(url, word)
	if time_tup == None:
		print("Word not found!")
		return 1
	start = time_tup[0]
	end = time_tup[1]
	download_url = get_download_url(url)
	download_video(download_url, start, end, path)


def main():
	if len(sys.argv) < 4:
		print("Usage: <youtube url> <word> <output_file_path>")
		return 1
	try:
		download_wrapper(YOUTUBE_URL, DESIRED_WORD,	FILE_PATH)
	except:
		print("Failed, Terminating")
		raise
	return 0

	

if __name__ == "__main__":
	main()