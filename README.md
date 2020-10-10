# word_clip_downloader
Downloads a short clip with the desired word in it if a transcript of the video is available and the word exists in it.

## installation
```
pip install -r requirements.txt
```
and also
```
apt-get install ffmpeg
```
## Usage
```
python yt_word_downloader.py <yt_link> <word> <path_to_mp4>
```
if word exists in the video's transcript, it'll download a clip with the word in it to path_to_mp4.


