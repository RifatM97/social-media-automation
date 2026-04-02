"""
process_video.py  -  Step 2 of the workflow

For each video in the 'Videos' sheet with Status == 'Selected':
  1. Fetch the transcript via youtube-transcript-api
  2. Generate content for each configured content type using Claude
  3. Write results to the 'Content' sheet (status: Pending Approval)
  4. Update video status to 'Processed'

Required environment variables:
  ANTHROPIC_API_KEY - Anthropic API key

Content types (configured in Config sheet):
  tweet_thread       → Twitter/X
  linkedin_post      → LinkedIn
  newsletter         → Newsletter (text only — no email integration)
  instagram_caption  → Instagram
"""

import os
import sys
from datetime import datetime

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import anthropic

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from excel_manager import (
    get_selected_videos, update_video_status,
    add_content, get_config, EXCEL_PATH,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_PLUGIN_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE_GUIDE    = os.path.join(_PLUGIN_ROOT, "config", "style_guide.txt")
DEFAULT_STYLE  = (
    "Tone: engaging, conversational, professional but approachable.\n"
    "Voice: active. Focus on practical value and actionable insights.\n"
    "Avoid jargon unless the audience is clearly technical.\n"
    "Keep sentences short. Use paragraph breaks generously."
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _claude():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise EnvironmentError("ANTHROPIC_API_KEY is not set.")
    return anthropic.Anthropic(api_key=key)


def load_style_guide() -> str:
    if os.path.exists(STYLE_GUIDE):
        with open(STYLE_GUIDE) as f:
            return f.read().strip()
    return DEFAULT_STYLE


def get_transcript(video_id: str) -> str | None:
    """Fetch auto-generated or manual transcript. Returns plain text or None."""
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)
        return " ".join(s.text for s in transcript)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as exc:
        print(f"  Transcript error: {exc}")
        return None


def _call_claude(client, prompt: str, max_tokens: int = 1200) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


# ---------------------------------------------------------------------------
# Content generators
# ---------------------------------------------------------------------------

def make_tweet_thread(client, title: str, transcript: str, style: str) -> str:
    return _call_claude(client, f"""Create a Twitter/X thread based on this YouTube video.

WRITING STYLE:
{style}

VIDEO TITLE: {title}
TRANSCRIPT (excerpt): {transcript[:3000]}

REQUIREMENTS:
- 5 to 7 tweets
- Max 280 characters per tweet
- Open with a compelling hook tweet
- Cover the key insights
- Close with a clear call to action
- Number each tweet: 1/, 2/, etc.
- No hashtags unless they genuinely add value

Return only the numbered tweets, one per line.""", max_tokens=900)


def make_linkedin_post(client, title: str, transcript: str, style: str) -> str:
    return _call_claude(client, f"""Write a LinkedIn post based on this YouTube video.

WRITING STYLE:
{style}

VIDEO TITLE: {title}
TRANSCRIPT (excerpt): {transcript[:3000]}

REQUIREMENTS:
- 150–300 words
- Hook in the first sentence (no "I watched a video" openings)
- 3 clearly communicated key takeaways
- Professional, insight-driven tone
- End with a question or call to action that encourages engagement
- Use short paragraphs and line breaks for readability

Return only the post text.""", max_tokens=600)


def make_newsletter(client, title: str, transcript: str, style: str) -> str:
    return _call_claude(client, f"""Write newsletter-ready text based on this YouTube video. The text will be inserted into an existing email newsletter sent via the company's CRM — do not include a subject line, greeting, or sign-off.

WRITING STYLE:
{style}

VIDEO TITLE: {title}
TRANSCRIPT (excerpt): {transcript[:4500]}

REQUIREMENTS:
- 400–600 words
- Structure: introduction → 3-5 main points → key takeaways → conclusion
- Narrative style — write as if sharing valuable knowledge, not summarising a video
- No placeholders like [Your Name] or [Link]
- Do not mention the YouTube video explicitly unless it adds value

Return only the newsletter body text.""", max_tokens=1400)


def make_instagram_caption(client, title: str, transcript: str, style: str) -> str:
    return _call_claude(client, f"""Write an Instagram caption based on this YouTube video.

WRITING STYLE:
{style}

VIDEO TITLE: {title}
TRANSCRIPT (excerpt): {transcript[:2000]}

REQUIREMENTS:
- 100–200 words
- Strong opening hook (first line visible before 'more')
- Shareable, relatable insight
- Clear call to action
- 5–10 relevant hashtags at the end (separated from body by a blank line)

Return only the caption.""", max_tokens=400)


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

GENERATORS = {
    "tweet_thread":       (make_tweet_thread,       "Twitter/X",  "Tweet Thread"),
    "linkedin_post":      (make_linkedin_post,       "LinkedIn",   "LinkedIn Post"),
    "newsletter":         (make_newsletter,          "Newsletter", "Newsletter"),
    "instagram_caption":  (make_instagram_caption,   "Instagram",  "Instagram Caption"),
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 62)
    print("  Social Content Automation — Step 2: Process Selected Videos")
    print("=" * 62)

    selected = get_selected_videos()
    if not selected:
        print("No videos with Status 'Selected' found.")
        print("Open data/content_tracker.xlsx → 'Videos' sheet and change")
        print("Status to 'Selected' for the videos you want to process.")
        return

    print(f"Processing {len(selected)} video(s)…\n")

    client = _claude()
    style  = load_style_guide()

    raw_types = get_config("content_types") or "tweet_thread,linkedin_post,newsletter"
    types     = [t.strip() for t in raw_types.split(",")]

    total_generated = 0

    for video in selected:
        vid_id = video["video_id"]
        title  = video["title"]
        print(f"Video: {title[:65]}")
        print(f"  URL: {video['url']}")

        update_video_status(vid_id, "Processing")

        # Transcript
        print("  Fetching transcript…")
        transcript = get_transcript(vid_id)
        if transcript:
            print(f"  Transcript: {len(transcript):,} characters")
        else:
            print("  No transcript available — using title + summary for generation.")
            transcript = f"{title}. {video.get('summary', '')}"

        # Generate each content type
        for ct in types:
            if ct not in GENERATORS:
                print(f"  Unknown content type '{ct}' — skipping.")
                continue

            fn, platform, display_name = GENERATORS[ct]
            print(f"  Generating {display_name}…", end=" ", flush=True)

            try:
                text = fn(client, title, transcript, style)
                ts   = datetime.now().strftime("%Y%m%d%H%M%S")
                cid  = f"{vid_id}_{ct}_{ts}"
                add_content(
                    content_id   = cid,
                    video_id     = vid_id,
                    video_title  = title,
                    content_type = display_name,
                    platform     = platform,
                    content_text = text,
                )
                total_generated += 1
                print("done")
            except Exception as exc:
                print(f"ERROR — {exc}")

        update_video_status(vid_id, "Processed")
        print()

    print("=" * 62)
    print(f"  Done — {total_generated} piece(s) of content generated.")
    print(f"  Tracker: {EXCEL_PATH}")
    print()
    print("  Next step:")
    print("  Open data/content_tracker.xlsx → 'Content' sheet.")
    print("  Review each piece. Set Status to 'Approved' to queue for")
    print("  publishing, or 'Rejected' to discard.")
    print("  Then run: /social-content-automation:publish-content")
    print("=" * 62)


if __name__ == "__main__":
    main()
