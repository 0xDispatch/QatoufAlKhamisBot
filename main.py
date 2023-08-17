# Import modules
import os
import pytz
import time
import shutil
import traceback
import logging
from datetime import datetime
from downloader import VideoDownloader
from uploading import upload_media
from tweeting import tweet
from login import login
import config
# Set up logging
logging.basicConfig(filename="log.txt", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Log in to Twitter
session = login(username=config.USERNAME, password=config.PASSWORD)

# Create a video downloader object
video_downloader = VideoDownloader("othmanelkamees_vids.json")

# Define a function to tweet a random video
def tweet_random_video():
    """Tweet a random video from the video downloader object."""
    # Create a directory to store the downloaded video
    download_dir = "downloaded_vids"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # Get a random video from the video downloader object
    random_video = video_downloader.get_random_vid()
    logging.info(f"Selected video: {random_video}")
    
    # Download the video to the download directory
    result = video_downloader.download_vid(random_video["id"], download_dir)
    media = [os.path.join(result, f"{random_video['title']}.mp4")]
    
    # Create the tweet text with the video, title and link
    text = f"""
{random_video["title"]}

‏رابط المقطع ⬇️
https://youtu.be/{random_video["id"]}️         
                """
    
    # Tweet the text and media. 
    tweet(text=text, media=media, session=session)
    
    # Delete the download directory
    shutil.rmtree(download_dir)
    
    logging.info("Tweeted successfully")

# Define a main function to run the program
def main():
    """Run the program in an infinite loop."""
    while True:
        try:
            # Get the current minute in Riyadh timezone
            minute = datetime.now(pytz.timezone("Asia/Riyadh")).minute
            
            # If the minute is zero, tweet a random video
            if minute == 0:
                tweet_random_video()
                
                # Wait for 120 seconds before checking again.
                time.sleep(120)
            
            # Wait for 10 seconds before checking again
            time.sleep(10)
        
        except Exception as err:
            # Log the exception and wait for 100 seconds before retrying
            logging.error(err)
            traceback.print_exc()
            time.sleep(100)

# Run the main function if this file is executed as a script
if __name__ == "__main__":
    main() 