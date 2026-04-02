---
name: publish-content
description: Schedule and publish approved social media content via Blotato, and mark newsletter content as ready for CRM. Defaults to one post per day.
tools:
  - Bash
  - Read
---

You are running Step 3 of the Social Content Automation workflow.

## What this skill does

Calls `scripts/publish_content.py` which:
1. Reads all rows in the **Content** sheet with Status == `Approved`
2. **Newsletter** items → updated to `Ready for CRM` (text only; the manager sends these via their own CRM)
3. **Social media** items → scheduled via Blotato API starting tomorrow at 09:00, one per day (configurable)
4. Updates each row with the scheduled date and new status

If `BLOTATO_API_KEY` is not set, the script runs in **simulation mode** — posts are scheduled in Excel but not sent to Blotato.

## Steps to follow

1. Check environment:
   ```bash
   echo "BLOTATO_API_KEY set: $([ -n "$BLOTATO_API_KEY" ] && echo yes || echo "NOT SET - simulation mode")"
   ```
   Inform the user whether real scheduling or simulation mode will be used.

2. Run the publish script:
   ```bash
   python scripts/publish_content.py
   ```

3. Read and relay the full output to the user, including the schedule table.

4. After completion:
   - If simulation mode: remind user to set `BLOTATO_API_KEY` to enable real scheduling
   - If real mode: confirm posts are queued in Blotato
   - Remind user that newsletter content is in the Content sheet with status `Ready for CRM`

## Configuring publish rate

The `publish_rate_per_day` setting in the **Config** sheet controls how many posts are published per day (default: 1). To change it:
- Open `data/content_tracker.xlsx` → **Config** sheet
- Edit the Value cell for `publish_rate_per_day`
- Re-run this command — the new rate takes effect immediately

## Notes

- The scheduler starts from **tomorrow** to avoid accidentally posting immediately.
- Multiple posts on the same day are staggered by `8 / rate` hours (e.g., rate=2 → 09:00 and 13:00).
- Newsletter items are never sent to Blotato — the text is stored in Excel for manual copy-paste into your CRM.
