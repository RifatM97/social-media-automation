---
description: Step 2 — Transcribe videos marked as Selected and generate social media content (tweet thread, LinkedIn post, newsletter, Instagram caption) using Claude
---

You are running Step 2 of the Social Content Automation workflow.

## What this does
- Reads all rows in the **Videos** sheet with Status == `Selected`
- Fetches the transcript for each video (falls back to title + summary if unavailable)
- For each configured content type, generates content using Claude Sonnet
- Writes each piece to the **Content** sheet with status `Pending Approval`
- Updates the video status to `Processed`

Default content types: `tweet_thread`, `linkedin_post`, `newsletter`
Optional: add `instagram_caption` to the `content_types` row in the Config sheet.

Writing style is read from `config/style_guide.txt`.

## Steps

### 1. Verify environment
```bash
echo "ANTHROPIC_API_KEY: $([ -n "$ANTHROPIC_API_KEY" ] && echo SET || echo MISSING)"
```
Stop and inform the user if missing.

### 2. Run the processing script
```bash
cd "/Users/rifatmahammod/Library/CloudStorage/OneDrive-VodafoneGroup/Documents/personal projects/upwork/automated_social_content/social-content-automation-plugin" && python scripts/process_video.py
```

### 3. Relay the full output to the user.

### 4. After completion
Remind the user:
- Open `data/content_tracker.xlsx` → **Content** sheet
- Review each generated piece
- Set Status to `Approved` for content ready to publish
- Set Status to `Rejected` to discard a piece
- Then run `/social-content-automation:publish-content`

If no videos have Status `Selected`, tell the user to open the Videos sheet first and mark videos as Selected.
