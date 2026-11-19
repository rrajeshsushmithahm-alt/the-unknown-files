import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube():
    required = ["YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise RuntimeError("Missing GitHub Actions secrets: " + ", ".join(missing))

    credentials = Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YOUTUBE_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    credentials.refresh(Request())
    return build("youtube", "v3", credentials=credentials)

def upload(youtube, path, title, description):
    if not path.exists():
        raise FileNotFoundError(f"Rendered video not found: {path}")

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(path), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    print(f"Uploaded privately: {title} (video ID: {response['id']})")

def main():
    data = json.loads((ROOT / "content/episode.json").read_text(encoding="utf-8"))
    youtube = get_youtube()

    upload(
        youtube,
        OUT / "black-hole-long.mp4",
        data["long"]["title"],
        data["long"]["description"],
    )

    for index, short in enumerate(data["shorts"], 1):
        upload(
            youtube,
            OUT / f"black-hole-short-{index}.mp4",
            short["title"],
            short["description"],
        )

    print("All three videos uploaded with PRIVATE visibility. Review them in YouTube Studio before publishing.")

if __name__ == "__main__":
    main()
