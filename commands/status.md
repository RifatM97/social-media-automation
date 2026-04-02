---
description: Show a dashboard of the current workflow state — pending videos, content awaiting approval, scheduled posts, and config summary
---

You are displaying the current status of the Social Content Automation workflow.

Run the following command and relay the full output to the user:

```bash
cd "/Users/rifatmahammod/Library/CloudStorage/OneDrive-VodafoneGroup/Documents/personal projects/upwork/automated_social_content/social-content-automation-plugin" && python - <<'EOF'
import sys, os
sys.path.insert(0, 'scripts')
from excel_manager import list_videos, list_content, get_config, EXCEL_PATH
from collections import Counter

print(f"\n{'='*62}")
print("  Social Content Automation — Status Dashboard")
print(f"{'='*62}")
print(f"\nTracker: {EXCEL_PATH}")
print(f"Exists:  {'yes' if os.path.exists(EXCEL_PATH) else 'NO — run setup first'}\n")

print("CONFIGURATION")
for key in ('content_types', 'publish_rate_per_day', 'default_platforms', 'last_check'):
    val = get_config(key) or '(not set)'
    print(f"  {key:<28} {val}")

all_videos = list_videos()
print(f"\nVIDEOS  ({len(all_videos)} total)")
for status, count in sorted(Counter(v['Status'] for v in all_videos).items()):
    print(f"  {status:<30} {count}")

all_content = list_content()
print(f"\nCONTENT  ({len(all_content)} total)")
for status, count in sorted(Counter(c['Status'] for c in all_content).items()):
    print(f"  {status:<30} {count}")

pending_videos  = [v for v in all_videos  if v['Status'] == 'Pending Review']
selected_videos = [v for v in all_videos  if v['Status'] == 'Selected']
pending_content = [c for c in all_content if c['Status'] == 'Pending Approval']
approved        = [c for c in all_content if c['Status'] == 'Approved']

print(f"\nACTION NEEDED")
if pending_videos:
    print(f"  {len(pending_videos)} video(s) awaiting review — set Status to Selected or Ignored")
    print(f"  then run: /social-content-automation:process-videos")
if selected_videos:
    print(f"  {len(selected_videos)} video(s) selected — run: /social-content-automation:process-videos")
if pending_content:
    print(f"  {len(pending_content)} content piece(s) awaiting approval — set Status to Approved or Rejected")
    print(f"  then run: /social-content-automation:publish-content")
if approved:
    print(f"  {len(approved)} approved piece(s) ready — run: /social-content-automation:publish-content")
if not any([pending_videos, selected_videos, pending_content, approved]):
    print("  Nothing pending — all caught up!")
print(f"\n{'='*62}\n")
EOF
```

If the Excel file does not exist, tell the user to run `/social-content-automation:setup` first.
