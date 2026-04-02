---
description: Step 1 — Check monitored YouTube channels for new videos, generate AI summaries, and add them to the Excel tracker for review
---

You are running Step 1 of the Social Content Automation workflow.

## What this does
- Reads channel IDs from `config/channels.json`
- Calls the YouTube Data API for each channel to fetch videos published since the last check
- Generates a short AI summary for each new video using Claude
- Writes new videos to the **Videos** sheet in `data/content_tracker.xlsx` with status `Pending Review`
- Updates the `last_check` timestamp in the Config sheet

## Steps

### 1. Verify environment variables
```bash
echo "YOUTUBE_API_KEY:   $([ -n "$YOUTUBE_API_KEY" ] && echo SET || echo MISSING)"
echo "ANTHROPIC_API_KEY: $([ -n "$ANTHROPIC_API_KEY" ] && echo SET || echo MISSING)"
```
If either is missing, stop and tell the user to set them (see `.env.example`).

### 2. Run the fetch script
```bash
cd "/Users/rifatmahammod/Library/CloudStorage/OneDrive-VodafoneGroup/Documents/personal projects/upwork/automated_social_content/social-content-automation-plugin" && python scripts/fetch_videos.py
```

### 3. Relay the full output to the user.

### 4. After completion
If new videos were added, remind the user:
- Open `data/content_tracker.xlsx` → **Videos** sheet
- Change **Status** to `Selected` for videos to process, or `Ignored` to skip
- Then run `/social-content-automation:process-videos`

If no channels are configured (only placeholder in channels.json), tell the user to edit `config/channels.json` with real channel IDs before running this command.
