"""
publish_content.py  -  Step 3 of the workflow

For each row in the 'Content' sheet with Status == 'Approved':
  - Newsletter items → marked 'Ready for CRM' (text only; no API call)
  - Social media items → scheduled via Blotato API
                         (simulation mode if BLOTATO_API_KEY is not set)

Scheduling logic:
  - Starts from the next calendar day at 09:00 local time
  - Spreads posts at the rate of `publish_rate_per_day` (from Config sheet)
  - If multiple posts per day, they are staggered every few hours

Required environment variables:
  BLOTATO_API_KEY  - Blotato API key (optional; simulation mode used if absent)
"""

import os
import sys
import requests
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from excel_manager import (
    get_approved_content, update_content_status,
    get_config, EXCEL_PATH,
)

# ---------------------------------------------------------------------------
# Blotato API
# ---------------------------------------------------------------------------

BLOTATO_BASE = "https://app.blotato.com/api/v1"

PLATFORM_MAP = {
    "Twitter/X": "twitter",
    "LinkedIn":  "linkedin",
    "Instagram": "instagram",
    "Facebook":  "facebook",
}


def _blotato_headers() -> dict:
    key = os.environ.get("BLOTATO_API_KEY", "")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
    }


def blotato_schedule(content_text: str, platform: str,
                     scheduled_at: datetime) -> dict:
    """
    POST a scheduled post to Blotato.
    Returns the response JSON on success; raises on HTTP error.
    """
    payload = {
        "content":      content_text,
        "platform":     PLATFORM_MAP.get(platform, platform.lower()),
        "scheduled_at": scheduled_at.isoformat(),
    }
    resp = requests.post(
        f"{BLOTATO_BASE}/posts",
        headers=_blotato_headers(),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Scheduling logic
# ---------------------------------------------------------------------------

def build_schedule(items: list[dict], rate: int) -> list[dict]:
    """
    Attach a `computed_schedule` datetime to each item.
    Posts start tomorrow at 09:00 and are spread at `rate` per day.
    Multiple daily posts are staggered by (8 / rate) hours.
    """
    start = (datetime.now() + timedelta(days=1)).replace(
        hour=9, minute=0, second=0, microsecond=0
    )
    stagger_hours = max(1, 8 // rate)  # spread within a working day

    day_offset  = 0
    day_counter = 0
    result      = []

    for item in items:
        hour_offset = day_counter * stagger_hours
        post_time   = start + timedelta(days=day_offset, hours=hour_offset)
        result.append({**item, "computed_schedule": post_time})

        day_counter += 1
        if day_counter >= rate:
            day_counter  = 0
            day_offset  += 1

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 62)
    print("  Social Content Automation — Step 3: Publish Approved Content")
    print("=" * 62)

    approved = get_approved_content()
    if not approved:
        print("No content with Status 'Approved' found.")
        print("Open data/content_tracker.xlsx → 'Content' sheet and set")
        print("Status to 'Approved' for items you want to publish.")
        return

    print(f"Found {len(approved)} approved item(s).")

    rate = int(get_config("publish_rate_per_day") or "1")
    print(f"Publish rate: {rate} post(s) per day.")

    blotato_available = bool(os.environ.get("BLOTATO_API_KEY"))
    if not blotato_available:
        print("\nNOTE: BLOTATO_API_KEY not set — running in simulation mode.")
        print("      Posts will be scheduled in Excel but not sent to Blotato.\n")

    # Split newsletter from social media posts
    newsletters = [c for c in approved if c["platform"] == "Newsletter"]
    social      = [c for c in approved if c["platform"] != "Newsletter"]

    # --- Newsletter items ---
    if newsletters:
        print(f"Newsletter items ({len(newsletters)}) — marking as Ready for CRM:")
        for item in newsletters:
            update_content_status(
                item["content_id"],
                "Ready for CRM",
                published_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            print(f"  ✓ {item['video_title'][:50]}")

    # --- Social media items ---
    if not social:
        print("\nNo social media posts to schedule.")
    else:
        scheduled_items = build_schedule(social, rate)

        print(f"\nScheduling {len(scheduled_items)} social media post(s):")
        print(f"{'Platform':<15} {'Scheduled':<20} {'Video'}")
        print("-" * 62)

        for item in scheduled_items:
            dt      = item["computed_schedule"]
            dt_str  = dt.strftime("%Y-%m-%d %H:%M")
            excerpt = item["video_title"][:35]
            print(f"  {item['platform']:<13} {dt_str:<20} {excerpt}")

            if blotato_available:
                try:
                    result = blotato_schedule(item["content_text"], item["platform"], dt)
                    update_content_status(
                        item["content_id"],
                        "Scheduled",
                        scheduled_date=dt_str,
                    )
                    post_id = result.get("id", "unknown")
                    print(f"  └ Scheduled via Blotato (post ID: {post_id})")
                except Exception as exc:
                    print(f"  └ ERROR scheduling via Blotato: {exc}")
                    update_content_status(item["content_id"], "Error - Schedule Failed")
            else:
                update_content_status(
                    item["content_id"],
                    "Scheduled (Simulated)",
                    scheduled_date=dt_str,
                )

    print()
    print("=" * 62)
    print(f"  Done — check {EXCEL_PATH}")
    print("  for the full publishing schedule.")
    print("=" * 62)


if __name__ == "__main__":
    main()
