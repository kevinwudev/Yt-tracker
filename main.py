import asyncio
import argparse
from datetime import date, timedelta

from vtt.llm import summarize
from vtt.yt import fetch_videos_all, download_video_byID
from vtt.tg import send_msg

yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datetime", help="The dateTime for video published, YYYY-MM-DD")
    parser.add_argument("-t", "--telegram", help="Report to telegram?", action="store_true")
    args = parser.parse_args()
    
    return args

def main(date: str):
    
    videos = fetch_videos_all(date)
    
    msg = ""
    for video in videos:
 
        transcript = video.get("transcript", "")
        videoID = video.get("videoId", "")
        title = video.get("title", "")

    if transcript == "":

        from vtt.llm import transcribe_m4a

        print(f"[Download] m4a file : {title}")
        download_video_byID(videoID)

        print(f"[Transcript] {title}")
        transcript = transcribe_m4a("audio.m4a")
        
        print(f"[Summary] {title}")
        video["summary"] = summarize(transcript, lines=5).choices[0].message.content if transcript != "" else ""
    
        res = [ f" 創作者 : {video.get('videoOwnerChannelTitle', '')}",
                f" 發布日期 : {video.get('published', '')} (UTC+0)",
                f" 標題 : {video.get('title', '')}",
                f" 摘要 : {video.get('summary', '')}"
                ]
        
        msg += "\n".join(res) + "\n\n"

    return msg

if __name__ == "__main__":

    args = parse()
    date = args.datetime if args.datetime else yesterday
    send_telegram = args.telegram if args.telegram else False

    msg = main(date)
    print(msg)
    if send_telegram : asyncio.run(send_msg(msg))


    
    
    

    
