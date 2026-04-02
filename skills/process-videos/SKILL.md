---
name: process-videos
description: Transcribe YouTube videos marked as Selected and generate social media content (tweet thread, LinkedIn post, newsletter text, Instagram caption) using Claude
tools:
  - Bash
  - Read
---

You are running Step 2 of the Social Content Automation workflow.

## What this skill does

Calls `scripts/process_video.py` which:
1. Reads all rows in the **Videos** sheet with Status == `Selected`
2. Fetches the transcript for each video (falls back to title + summary if unavailable)
3. For each configured content type (set in Config sheet → `content_types`), generates content using Claude Sonnet
4. Writes each piece to the **Content** sheet with status `Pending Approval`
5. Updates the video status to `Processed`

Default content types: `tweet_thread`, `linkedin_post`, `newsletter`
Optional: add `instagram_caption` to the `content_types` config value.

Writing style is read from `config/style_guide.txt` (if it exists).

## Steps to follow

1. Check environment variable:
   ```bash
   echo "ANTHROPIC_API_KEY set: $([ -n "$ANTHROPIC_API_KEY" ] && echo yes || echo NO - missing)"
   ```
   Stop and inform the user if it is missing.

2. Run the processing script:
   ```bash
   python scripts/process_video.py
   ```

3. Read and relay the full output to the user.

4. After completion, remind the user:
   - Open `data/content_tracker.xlsx` → **Content** sheet
   - Review each piece of generated content
   - Set Status to `Approved` for content that is ready to publish
   - Set Status to `Rejected` to discard a piece
   - Then run `/social-content-automation:publish-content`

## Notes

- Content generation uses `claude-sonnet-4-6` for quality output. A video with 3 content types will make 3 API calls.
- If the transcript cannot be retrieved (channel disabled captions), Claude uses the video title and the summary generated in Step 1. Quality will be lower in this case.
- To add or remove content types, edit the `content_types` row in the **Config** sheet of `data/content_tracker.xlsx`.
- To update the writing style, edit `config/style_guide.txt`.
