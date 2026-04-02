---
name: setup
description: First-time setup for the Social Content Automation plugin — installs dependencies, creates the Excel tracker, validates API keys, and initializes config files
tools:
  - Bash
  - Read
  - Write
---

You are running the first-time setup for the Social Content Automation plugin.

## Steps to follow

### 1. Check Python version
```bash
python --version
```
Python 3.10+ is required (for `X | Y` type hints). If the version is lower, inform the user.

### 2. Install dependencies
```bash
pip install -r requirements.txt
```
Show the user the output. If any package fails, diagnose and suggest a fix.

### 3. Validate environment variables
Check for each required key:
```bash
echo "YOUTUBE_API_KEY:   $([ -n "$YOUTUBE_API_KEY" ] && echo SET || echo MISSING)"
echo "ANTHROPIC_API_KEY: $([ -n "$ANTHROPIC_API_KEY" ] && echo SET || echo MISSING)"
echo "BLOTATO_API_KEY:   $([ -n "$BLOTATO_API_KEY" ] && echo SET || echo "NOT SET (simulation mode)")"
```

If any required key is missing, show the user `.env.example` and instruct them to:
```bash
cp .env.example .env
# then edit .env with their actual keys
```
Tell them to load the env file before running commands:
```bash
export $(grep -v '^#' .env | xargs)
```

### 4. Initialise the Excel tracker
```bash
python -c "import sys; sys.path.insert(0, 'scripts'); from excel_manager import get_workbook; get_workbook(); print('Excel tracker ready.')"
```

### 5. Check channel config
```bash
cat config/channels.json
```
If only the sample placeholder is present, tell the user to:
- Find their target YouTube channel
- Copy the channel ID from the URL (format: `UCxxxxxxxxxxxxxxxxxxxxxxxxx`)
- Edit `config/channels.json` and replace the placeholder

### 6. Check style guide
```bash
cat config/style_guide.txt
```
Encourage the user to customise the writing style to match their brand voice.

### 7. Summary
After all steps complete, print a summary:
- Which API keys are set ✓ / missing ✗
- Path to Excel tracker
- How many channels are configured
- The three slash commands available:
  1. `/social-content-automation:check-channels` — fetch new videos
  2. `/social-content-automation:process-videos` — generate content
  3. `/social-content-automation:publish-content` — schedule publishing
  4. `/social-content-automation:status` — view current state
