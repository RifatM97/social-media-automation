---
name: check-channels
description: Check monitored YouTube channels for new videos, generate AI summaries, and add them to the local Excel tracker for review
tools:
  - Bash
  - Read
---

You are running Step 1 of the Social Content Automation workflow.

## What this skill does

Calls `scripts/fetch_videos.py` which:
1. Reads channel IDs from `config/channels.json`
2. Calls the YouTube Data API for each channel to fetch videos published since the last check
3. Generates a short AI summary for each new video using Claude
4. Writes new videos to the **Videos** sheet in `data/content_tracker.xlsx` with status `Pending Review`
5. Updates the `last_check` timestamp in the Config sheet

## Steps to follow

1. Verify the required environment variables are available:
   ```bash
   echo "YOUTUBE_API_KEY set: $([ -n "$YOUTUBE_API_KEY" ] && echo yes || echo NO - missing)"
   echo "ANTHROPIC_API_KEY set: $([ -n "$ANTHROPIC_API_KEY" ] && echo yes || echo NO - missing)"
   ```
   If either is missing, inform the user they need to export it (or set it in `.env`) and stop.

2. Run the fetch script:
   ```bash
   cd "$(dirname "$0")/../.." 2>/dev/null || true
   python scripts/fetch_videos.py
   ```
   Use the working directory of the plugin root (where `scripts/` lives).

3. Read and relay the full output to the user.

4. If new videos were added, remind the user:
   - Open `data/content_tracker.xlsx` → **Videos** sheet
   - Change **Status** to `Selected` for videos to process, or `Ignored` to skip
   - Then run `/social-content-automation:process-videos`

5. If no channels are configured yet, tell the user to edit `config/channels.json` and add real channel IDs (24-character strings starting with `UC`).

## Error handling

- `YOUTUBE_API_KEY` quota exceeded → inform user that YouTube API has a daily quota of 10,000 units; fetching is cheap (1 unit each) but they may need to wait until quota resets or use a different project key.
- `TranscriptsDisabled` or similar transcript errors are handled in process-videos, not here.
- If the script crashes, show the full traceback and suggest checking the API key and internet connectivity.
