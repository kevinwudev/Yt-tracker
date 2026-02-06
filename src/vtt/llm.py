from openai import OpenAI
from dotenv import load_dotenv 
import os
import json
import re
from pathlib import Path

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def summarize(text: str = "", lines : int = 10) -> str:

    '''Generate context using OpenAI API based on the given prompt.'''

    prompt = f"""
	Summarize the transcript of {text} in {lines} lines or fewer. Please maintain the original language of the text.    
	"""

    client = OpenAI(
        api_key = OPENAI_API_KEY
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response

def transcribe_m4a(audio_path: str) -> str:
    """Transcribe m4a audio into text using OpenAI."""
    audio_file = Path(audio_path)

    client = OpenAI(
        api_key = OPENAI_API_KEY
    )

    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    with open(audio_file, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=f,
        )

    return transcript.text

def rewrite(text: str = "", style: str = "正式") -> str:

    '''Generate context using OpenAI API based on the given prompt.'''

    prompt = f"""
	Please rewrite the following content in a {style} style.
    ---
    {text}
    """

    client = OpenAI(
        api_key = OPENAI_API_KEY
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response


def translate(text: str = "", target_language: str = "英文") -> str:

    '''Generate context using OpenAI API based on the given prompt.'''

    prompt = f"""
	Please translate the following content into {target_language}.
	Make sure the translation stays true to the original meaning and reads naturally and smoothly.
	It should also fit common real-world usage scenarios.
    ---
    {text}
    """

    client = OpenAI(
        api_key = OPENAI_API_KEY
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response

def summarize_json(text : str, is_json_format: bool = True) -> str:
    prompt = f"""
    將以下內容總結為 JSON 格式，包含主要的關鍵點和細節：
    - summary: 簡要總結內容的主要觀點
    - key_points: 以列表形式列出內容中的關鍵點
    - conclusion: 根據內容得出的結論
    ---
    {text}
    """
    client = OpenAI(
        api_key = OPENAI_API_KEY
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    if not is_json_format: return response

    json_output = response.choices[0].message.content
    match = re.search(r'\{.*\}', json_output, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None

if __name__ == "__main__":
    result = summarize("LEsLFNugJ5Y")
    print(result.choices[0])
