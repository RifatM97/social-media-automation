"""
fetch_videos.py  -  Step 1 of the workflow

For each configured YouTube channel:
  1. Fetch videos published since the last check (or the 10 most recent on first run)
  2. Generate a short summary for each video with Claude
  3. Write new videos to the 'Videos' sheet of content_tracker.xlsx (status: Pending Review)
  4. Update the last_check timestamp in the Config sheet

Required environment variables:
  YOUTUBE_API_KEY   - Google Cloud project API key with YouTube Data API v3 enabled
  ANTHROPIC_API_KEY - Anthropic API key
"""

import os
import sys
import json
from datetime import datetime, timezone

from googleapiclient.discovery import build
import anthropic

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from excel_manager import add_video, get_config, set_config, EXCEL_PATH

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANNELS_CONFIG = os.path.join(_PLUGIN_ROOT, "config", "channels.json")

# ---------------------------------------------------------------------------
# API clients
# ---------------------------------------------------------------------------

def _youtube():
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        raise EnvironmentError(
            "YOUTUBE_API_KEY is not set.\n"
            "Export it or add it to your .env file."
        )
    return build("youtube", "v3", developerKey=key)


def _claude():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set.\n"
            "Export it or add it to your .env file."
        )
    return anthropic.Anthropic(api_key=key)


# ---------------------------------------------------------------------------
# Channel config
# ---------------------------------------------------------------------------

def load_channels() -> list[dict]:
    if not os.path.exists(CHANNELS_CONFIG):
        sample = {
            "_readme": "Add your YouTube channel IDs below. Find a channel ID by visiting the channel page and copying the ID from the URL (starts with UC).",
            "channels": [
                {
                    "id": "UCxxxxxxxxxxxxxxxxxxxxxx",
                    "name": "Example Channel",
                    "notes": "Replace with a real 24-character channel ID"
                }
            ]
        }
        os.makedirs(os.path.dirname(CHANNELS_CONFIG), exist_ok=True)
        with open(CHANNELS_CONFIG, "w") as f:
            json.dump(sample, f, indent=2)
        print(f"Created sample channel config at: {CHANNELS_CONFIG}")
        print("Edit the file and re-run this command.")
        return []

    with open(CHANNELS_CONFIG) as f:
        data = json.load(f)

    channels = data.get("channels", [])
    real = [c for c in channels if not c["id"].startswith("UCxxxxxx")]
    if len(real) < len(channels):
        print(f"Skipping {len(channels) - len(real)} placeholder channel(s).")
    return real


# ---------------------------------------------------------------------------
# YouTube helpers
# ---------------------------------------------------------------------------

def fetch_channel_videos(yt, channel_id: str, published_after: str | None,
                         max_results: int = 1) -> list[dict]:
    """Return list of video dicts from a channel."""
    params = {
        "part":      "snippet",
        "channelId": channel_id,
        "type":      "video",
        "order":     "date",
        "maxResults": max_results,
    }
    if published_after:
        params["publishedAfter"] = published_after

    response = yt.search().list(**params).execute()
    videos = []
    for item in response.get("items", []):
        if item["id"]["kind"] != "youtube#video":
            continue
        s = item["snippet"]
        videos.append({
            "video_id":       item["id"]["videoId"],
            "title":          s["title"],
            "published_date": s["publishedAt"],
            "description":    s.get("description", ""),
            "url":            f"https://www.youtube.com/watch?v={item['id']['videoId']}",
        })
    return videos


# ---------------------------------------------------------------------------
# Content generation
# ---------------------------------------------------------------------------

def generate_summary(claude_client, title: str, description: str) -> str:
    """Generate a 2-3 sentence summary for the social media manager."""
    desc_snippet = (description or "")[:600]
    prompt = (
        "Write a 2-3 sentence summary of the following YouTube video for a social media manager "
        "who needs to quickly decide whether to turn it into content.\n\n"
        f"Title: {title}\n"
        f"Description: {desc_snippet or '(no description)'}\n\n"
        "Return only the summary — no preamble, no labels."
    )
    msg = claude_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 62)
    print("  Social Content Automation — Step 1: Fetch New Videos")
    print("=" * 62)

    channels = load_channels()
    if not channels:
        return

    yt     = _youtube()
    claude = _claude()

    last_check = get_config("last_check") or None
    if last_check:
        print(f"Fetching videos published after: {last_check}")
    else:
        print("First run — fetching up to 10 most recent videos per channel.")

    total_new = 0

    for ch in channels:
        channel_id   = ch["id"]
        channel_name = ch["name"]
        print(f"\nChannel: {channel_name}")

        try:
            videos = fetch_channel_videos(yt, channel_id, published_after=last_check)
            print(f"  {len(videos)} video(s) found")

            for v in videos:
                print(f"  └ {v['title'][:65]}")
                summary = generate_summary(claude, v["title"], v["description"])
                added   = add_video(
                    video_id       = v["video_id"],
                    channel_name   = channel_name,
                    channel_id     = channel_id,
                    title          = v["title"],
                    published_date = v["published_date"],
                    url            = v["url"],
                    summary        = summary,
                )
                if added:
                    total_new += 1
                    print(f"       → Added (Status: Pending Review)")
                else:
                    print(f"       → Already tracked, skipped")

        except Exception as exc:
            print(f"  ERROR: {exc}")

    # Update last-check timestamp
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    set_config("last_check", now_iso)

    print()
    print("=" * 62)
    print(f"  Done — {total_new} new video(s) added to tracker.")
    print(f"  Tracker location: {EXCEL_PATH}")
    print()
    print("  Next step:")
    print("  Open data/content_tracker.xlsx → 'Videos' sheet.")
    print("  Change Status to 'Selected' for videos to process,")
    print("  or 'Ignored' for videos to skip.")
    print("  Then run: /social-content-automation:process-videos")
    print("=" * 62)


if __name__ == "__main__":
    main()
