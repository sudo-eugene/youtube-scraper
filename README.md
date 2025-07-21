# YouTube Transcript Scraper

This script uses the YouTube Data API to find all videos from a specific channel and then downloads the transcript for each video.

## Features

- Fetches all video IDs from a given YouTube channel.
- Downloads transcripts for each video.
- Saves each transcript as a separate `.md` file in a `transcripts` directory.
- Compiles all transcripts into a single `master_transcript.md` file, with video titles and URLs.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd youtube-scraper
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API Key:**
    - Create a file named `.env` in the root of the project.
    - Add your YouTube Data API key to the `.env` file like this:
      ```
      YOUTUBE_API_KEY="YOUR_API_KEY_HERE"
      ```
    - You can get a YouTube API key from the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).

## Usage

Run the script from your terminal:

```bash
python scraper.py
```

The script will create a `transcripts` directory and a `master_transcript.md` file in your project folder.
