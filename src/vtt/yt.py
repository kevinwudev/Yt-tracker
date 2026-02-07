from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from googleapiclient.discovery import build
from typing import List, Dict
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import date, timedelta
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import yt_dlp
from dotenv import load_dotenv
from vtt import data_path


yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
WAITING_LIST = os.getenv("WAITING_LIST")
WAITING_LIST = json.loads(WAITING_LIST)

if "GITHUB_WORKSPACE" in os.environ: data_path = Path(os.environ["GITHUB_WORKSPACE"]) / "data"


def fetch_channel_handle() -> dict:

    channels_path = data_path / "channels.json"
    channels_path.parent.mkdir(parents=True, exist_ok=True)

    if not channels_path.exists():
        channels_path.write_text(json.dumps({}, ensure_ascii=False, indent=4), encoding="utf-8")

    # 讀取 JSON
    with channels_path.open("r", encoding="utf-8") as f:
        channels = json.load(f)

    return channels 

def get_channel_id_by_handle(youtube, channel_handle: str) -> str | None:
    """
    Retrieves a YouTube channel ID using its handle via the Data API v3.
    The handle can be provided with or without the '@' symbol.
    """
    try:
        # The 'forHandle' parameter is used to specify the channel's handle
        request = youtube.channels().list(
            part="id",
            forHandle=channel_handle.replace("@", "") # Remove '@' if present
        )
        response = request.execute()

        # Extract the channel ID from the response
        if 'items' in response and response['items']:
            channel_id = response['items'][0]['id']
            return channel_id
        else:
            print(f"Channel not found for handle: {channel_handle}")
            return None

    except HttpError as e:
        print(f"An HTTP error occurred: {e.resp.status} - {e.content}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def sync_channels(youtube) -> dict:
    """
    Sync channel handles with their IDs and save to channels.json.
    1. Load existing channel cache from channels.json.
    2. For each handle in WAITING_LIST, check if it's in the cache.
    3. If not, fetch the channel ID using get_channel_id_by_handle and update the cache.
    4. Save the updated cache back to channels.json.
    5. Return the updated channel cache.
    """

    channel_cache = fetch_channel_handle()

    waiting_set = set(WAITING_LIST)

    channel_cache = {k: v for k, v in channel_cache.items() if k in waiting_set}

    for key in WAITING_LIST:
        if key not in channel_cache:
            channel_cache[key] = get_channel_id_by_handle(youtube, key)
            print(f"Fetched channel ID for {key}: {channel_cache[key]}")

    with open(data_path / "channels.json", "w", encoding="utf-8") as f:
        json.dump(channel_cache, f, ensure_ascii=False, indent=4)

    return channel_cache


def get_videos_by_date(youtube, channel_id, target_date) -> List[Dict]:
    """Get videos published by channel on target_date (YYYY-MM-DD) with low quota usage."""

    channel = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()

    uploads_playlist = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    videos = []
    next_page = None
    cinfo = {}

    while True:
        res = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist,
            maxResults=50,
            pageToken=next_page
        ).execute()

        for item in res["items"]:
            published = item["snippet"]["publishedAt"][:10]
            if published == target_date:
                cinfo["published"] = published
                cinfo["title"] = item["snippet"]["title"]
                cinfo["videoId"] = item["snippet"]["resourceId"]["videoId"]
                cinfo["videoOwnerChannelTitle"] = item["snippet"]["videoOwnerChannelTitle"]
                cinfo["videoOwnerChannelId"] = item["snippet"]["videoOwnerChannelId"]
                videos.append(cinfo.copy())  # Append a copy of cinfo to avoid reference issues
            elif published < target_date:
                return videos

        next_page = res.get("nextPageToken")
        if not next_page:
            break

    return videos

def download_video_byID(vid: str):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': 'audio.m4a',
        'overwrites': True,
        # 'cookiefile': 'cookie.txt',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'] # Simulate requests from both Android and web clients to increase chances of successful extraction
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={vid}'])
    except Exception as e:
        print(f"[Fail] downloading \n: {e}")


def fetch_youtube_transcript_by_id(video_ID):
    
    try:
        ytt_api = YouTubeTranscriptApi()

        transcript_list = ytt_api.list(video_ID)
        transcript = transcript_list.find_transcript(['zh-Hant', 'zh-Hans', 'en', 'zh-CN'])
        lang = transcript.language_code
        fetched_transcripts = ytt_api.fetch(video_ID, languages=[lang])
    
        return "，".join([seg.text for seg in fetched_transcripts])
    
    except (TranscriptsDisabled):
        print("(No transcript available due to disabled transcripts)")
        return
    except (NoTranscriptFound):
        print("(No transcript available due to no transcript found)")
        return
    except Exception as e:
        print(f"(Transcript error: {e})")
        return
    
def fetch_videos_all(date: str = ""):

    date = yesterday if date == "" else date 
    videos = []
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    creators = sync_channels(youtube)

    for k, v in creators.items():
        channels = get_videos_by_date(youtube, v, date)
        videos.extend([video for video in channels]) if channels else None
    
    for video in videos:
        video_id = video.get("videoId", "")
        transcript = fetch_youtube_transcript_by_id(video_id)
        video["transcript"] = transcript if transcript else ""

    return videos


if __name__ == "__main__":

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    print(fetch_videos_all())
