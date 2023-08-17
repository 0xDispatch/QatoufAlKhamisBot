import json
import random
from pytube import YouTube

class VideoDownloader:
    def __init__(self, video_data_file):
        self.video_data_file = video_data_file
        self.threshold_str = "2:20"

    def _load_video_data(self):
        with open(self.video_data_file, "r") as f:
            return json.load(f)["videos"]

    def _is_video_longer_than_threshold(self, video_length_str):
        video_length = [int(x) for x in video_length_str.split(':')]
        threshold = [int(x) for x in self.threshold_str.split(':')]
        return video_length[0] > threshold[0] or (video_length[0] == threshold[0] and video_length[1] > threshold[1])

    def get_random_vid(self):
        data = self._load_video_data()
        random.shuffle(data)  # Shuffle the data list
        random_vid = data[0]
        video_length_str = random_vid["length"]
        if self._is_video_longer_than_threshold(video_length_str):
            return self.get_random_vid()
        return random_vid

    def download_vid(self, id, download_path):
        try:
            video_url = f"https://youtu.be/{id}"
            yt = YouTube(video_url)
            video_stream = yt.streams.get_highest_resolution()
            video_stream.download(download_path)
            return download_path
        except Exception as e:
            return f'Error: {e}'