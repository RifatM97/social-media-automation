---
name: status
description: Show a dashboard of the current workflow state — pending videos, content awaiting approval, scheduled posts, and configuration summary
tools:
  - Bash
  - Read
---

You are displaying the current status of the Social Content Automation workflow.

## Steps to follow

Run a Python one-liner to read and print the current state from the Excel tracker:

```bash
python - <<'EOF'
import sys
sys.path.insert(0, 'scripts')
from excel_manager import list_videos, list_content, get_config, EXCEL_PATH
import os

print(f"\n{'='*62}")
print("  Social Content Automation — Status Dashboard")
print(f"{'='*62}")
print(f"\nTracker: {EXCEL_PATH}")
print(f"Exists:  {'yes' if os.path.exists(EXCEL_PATH) else 'NO - run setup first'}\n")

# --- Config ---
print("CONFIGURATION")
for key in ('content_types', 'publish_rate_per_day', 'default_platforms', 'last_check'):
    val = get_config(key) or '(not set)'
    print(f"  {key:<28} {val}")

# --- Videos ---
all_videos = list_videos()
print(f"\nVIDEOS  ({len(all_videos)} total)")
from collections import Counter
vcounts = Counter(v['Status'] for v in all_videos)
for status, count in sorted(vcounts.items()):
    print(f"  {status:<28} {count}")

# --- Content ---
all_content = list_content()
print(f"\nCONTENT  ({len(all_content)} total)")
ccounts = Counter(c['Status'] for c in all_content)
for status, count in sorted(ccounts.items()):
    print(f"  {status:<28} {count}")

# --- Action prompts ---
pending_videos  = [v for v in all_videos  if v['Status'] == 'Pending Review']
selected_videos = [v for v in all_videos  if v['Status'] == 'Selected']
pending_content = [c for c in all_content if c['Status'] == 'Pending Approval']
approved        = [c for c in all_content if c['Status'] == 'Approved']

print(f"\nACTION NEEDED")
if pending_videos:
    print(f"  {len(pending_videos)} video(s) awaiting your review in the 'Videos' sheet.")
    print(f"  → Set Status to 'Selected' or 'Ignored', then run process-videos.")
if selected_videos:
    print(f"  {len(selected_videos)} video(s) selected but not yet processed.")
    print(f"  → Run: /social-content-automation:process-videos")
if pending_content:
    print(f"  {len(pending_content)} content piece(s) awaiting approval in the 'Content' sheet.")
    print(f"  → Set Status to 'Approved' or 'Rejected', then run publish-content.")
if approved:
    print(f"  {len(approved)} approved piece(s) ready to schedule.")
    print(f"  → Run: /social-content-automation:publish-content")
if not any([pending_videos, selected_videos, pending_content, approved]):
    print("  Nothing pending — all caught up!")

print(f"\n{'='*62}\n")
EOF
```

Relay the full output to the user.

If the Excel file does not exist yet, tell the user to run:
```
/social-content-automation:setup
```
