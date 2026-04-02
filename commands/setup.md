---
description: First-time setup — install dependencies, validate API keys, initialise the Excel tracker
---

You are running the first-time setup for the Social Content Automation plugin.

Work through each step below in order. Show the output of each command to the user before moving to the next step.

## Step 1 — Check Python version
```bash
python --version
```
Python 3.10+ is required. Stop and inform the user if lower.

## Step 2 — Install dependencies
Run from the plugin root directory:
```bash
cd "/Users/rifatmahammod/Library/CloudStorage/OneDrive-VodafoneGroup/Documents/personal projects/upwork/automated_social_content/social-content-automation-plugin" && pip install -r requirements.txt
```

## Step 3 — Validate environment variables
```bash
echo "YOUTUBE_API_KEY:   $([ -n "$YOUTUBE_API_KEY" ] && echo SET || echo MISSING)"
echo "ANTHROPIC_API_KEY: $([ -n "$ANTHROPIC_API_KEY" ] && echo SET || echo MISSING)"
echo "BLOTATO_API_KEY:   $([ -n "$BLOTATO_API_KEY" ] && echo SET || echo "NOT SET (simulation mode for publishing)")"
```
If YOUTUBE_API_KEY or ANTHROPIC_API_KEY are missing, show the user the `.env.example` file and tell them to:
1. Copy it to `.env` and fill in their keys
2. Load it with: `export $(grep -v '^#' .env | xargs)`
Then re-run from Step 3.

## Step 4 — Initialise the Excel tracker
```bash
cd "/Users/rifatmahammod/Library/CloudStorage/OneDrive-VodafoneGroup/Documents/personal projects/upwork/automated_social_content/social-content-automation-plugin" && python -c "import sys; sys.path.insert(0, 'scripts'); from excel_manager import get_workbook; get_workbook(); print('Excel tracker ready.')"
```

## Step 5 — Check channel config
```bash
cat "/Users/rifatmahammod/Library/CloudStorage/OneDrive-VodafoneGroup/Documents/personal projects/upwork/automated_social_content/social-content-automation-plugin/config/channels.json"
```
If only the placeholder channel ID is present, tell the user to edit `config/channels.json` and replace the placeholder with a real YouTube channel ID (24 characters, starts with `UC`). They can find it in the channel's URL: `youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxxxxx`.

## Step 6 — Summary
Print a clear summary showing:
- Which API keys are set ✓ or missing ✗
- Path to the Excel tracker file
- The four commands available:
  1. `/social-content-automation:check-channels` — fetch new videos from YouTube
  2. `/social-content-automation:process-videos` — generate content for selected videos
  3. `/social-content-automation:publish-content` — schedule approved content via Blotato
  4. `/social-content-automation:status` — view current workflow state
