import os
import re
import time
import random
import argparse
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_URL = "https://www.youtube.com/@RyanClogg"
TRANSCRIPTS_DIR = "transcripts"
MASTER_FILE = "master_transcript.md"

def get_channel_id_from_url(youtube, channel_url):
    """Extracts the channel ID from a YouTube channel URL."""
    # Custom handles like @RyanClogg
    match = re.search(r"@(\w+)", channel_url)
    if match:
        search_response = youtube.search().list(
            q=match.group(1),
            type="channel",
            part="id"
        ).execute()
        if search_response["items"]:
            return search_response["items"][0]["id"]["channelId"]
    # Channel URLs with /channel/UC...
    match = re.search(r"/channel/([\w-]+)", channel_url)
    if match:
        return match.group(1)
    return None

def get_video_ids(youtube, channel_id):
    """Fetches all video IDs from a given channel ID."""
    # Get the uploads playlist ID from the channel
    channel_response = youtube.channels().list(
        id=channel_id,
        part="contentDetails"
    ).execute()
    
    uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    video_ids = []
    next_page_token = None

    while True:
        playlist_response = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part="contentDetails",
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        video_ids.extend([item["contentDetails"]["videoId"] for item in playlist_response["items"]])
        next_page_token = playlist_response.get("nextPageToken")

        if not next_page_token:
            break
            
    return video_ids

def sanitize_filename(name):
    """Removes invalid characters from a string to make it a valid filename."""
    return re.sub(r'[\\/*?"<>|]', "", name)

def main():
    """Main function to orchestrate the transcript scraping process."""
    parser = argparse.ArgumentParser(description="Scrape YouTube video transcripts from a channel.")
    parser.add_argument(
        "--start-at",
        type=int,
        default=1,
        help="The video number to start scraping from (1-indexed). Skips the first N-1 videos."
    )
    args = parser.parse_args()
    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
        print("ERROR: YouTube API key is not set. Please add it to the .env file.")
        return

    youtube = build("youtube", "v3", developerKey=API_KEY, static_discovery=False)

    print(f"Fetching channel ID for {CHANNEL_URL}...")
    channel_id = get_channel_id_from_url(youtube, CHANNEL_URL)

    if not channel_id:
        print("Could not find channel ID.")
        return

    print(f"Found Channel ID: {channel_id}")
    print("Fetching video list...")
    video_ids = get_video_ids(youtube, channel_id)
    total_videos = len(video_ids)
    print(f"Found {total_videos} videos in total.")

    # Slice the list of videos to start from the specified number
    if args.start_at > 1:
        print(f"Starting at video {args.start_at}, skipping the first {args.start_at - 1} videos.")
        video_ids_to_process = video_ids[args.start_at - 1:]
    else:
        video_ids_to_process = video_ids

    print(f"Processing {len(video_ids_to_process)} videos.")

    # Create transcripts directory if it doesn't exist
    if not os.path.exists(TRANSCRIPTS_DIR):
        os.makedirs(TRANSCRIPTS_DIR)

    # Master file is now appended to, so we don't clear it on startup.

    for i, video_id in enumerate(video_ids_to_process):
        # Add a randomized delay to avoid IP ban
        time.sleep(random.uniform(3, 7))
        current_video_number = i + args.start_at
        print(f"Processing video {current_video_number}/{total_videos}: {video_id}")
        try:
            # Get video details
            video_response = youtube.videos().list(
                id=video_id,
                part='snippet'
            ).execute()
            
            if not video_response['items']:
                print(f"  -> Video not found, skipping.")
                continue

            video_title = video_response['items'][0]['snippet']['title']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            sanitized_title = sanitize_filename(video_title)

            # Check if transcript file already exists
            transcript_filepath = os.path.join(TRANSCRIPTS_DIR, f"{sanitized_title}.md")
            if os.path.exists(transcript_filepath):
                print(f"  -> Transcript for '{video_title}' already exists. Skipping.")
                continue

            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([item['text'] for item in transcript_list])

            # Save individual transcript file
            with open(os.path.join(TRANSCRIPTS_DIR, f"{sanitized_title}.md"), "w", encoding="utf-8") as f:
                f.write(f"# {video_title}\n")
                f.write(f"## {video_url}\n\n")
                f.write(transcript_text)

            # Append to master file
            with open(MASTER_FILE, "a", encoding="utf-8") as f:
                f.write(f"# {video_title}\n")
                f.write(f"## {video_url}\n\n")
                f.write(transcript_text + "\n\n---\n\n")
            
            print(f"  -> Transcript for '{video_title}' saved.")

        except Exception as e:
            print(f"  -> Could not retrieve transcript for video {video_id}: {e}")

    print("\nProcess complete.")
    print(f"Individual transcripts are in the '{TRANSCRIPTS_DIR}' directory.")
    print(f"Master transcript file is '{MASTER_FILE}'.")

if __name__ == "__main__":
    main()
