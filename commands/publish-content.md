---
description: Step 3 — Schedule and publish approved social media content via Blotato. Newsletter content is marked Ready for CRM. Default rate is one post per day.
---

You are running Step 3 of the Social Content Automation workflow.

## What this does
- Reads all rows in the **Content** sheet with Status == `Approved`
- **Newsletter** items → marked `Ready for CRM` (text only; no API call — the manager sends via their own CRM)
- **Social media** items → scheduled via Blotato API starting tomorrow at 09:00, at the configured rate
- Updates each row with the scheduled date and new status

If `BLOTATO_API_KEY` is not set, runs in **simulation mode** — posts are scheduled in Excel but not sent to Blotato.

## Steps

### 1. Check environment
```bash
echo "BLOTATO_API_KEY: $([ -n "$BLOTATO_API_KEY" ] && echo SET || echo "NOT SET — simulation mode")"
```
Inform the user which mode will be used.

### 2. Run the publish script
```bash
cd "/Users/rifatmahammod/Library/CloudStorage/OneDrive-VodafoneGroup/Documents/personal projects/upwork/automated_social_content/social-content-automation-plugin" && python scripts/publish_content.py
```

### 3. Relay the full output including the schedule table.

### 4. After completion
- If simulation mode: remind user to set `BLOTATO_API_KEY` for real scheduling
- Newsletter content: remind user the text is in the Content sheet with status `Ready for CRM` — copy it into their CRM to send
- To change the publish rate: edit the `publish_rate_per_day` value in the **Config** sheet of the Excel tracker
