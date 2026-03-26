---
name: task-status
description: Show all in-flight tasks (Team Inbox) and completed deliverables (Owner's Inbox) as a status dashboard
disable-model-invocation: false
---

Read all .md files in "Team Inbox/" and "Owner's Inbox/" at the project root.
Format output as two tables:

**In Progress (Team Inbox)**
| Date | Assigned To | Task |
...

**Delivered (Owner's Inbox)**
| Date | From | Deliverable |
...

Parse filenames using the YYYY-MM-DD_[TeamMember]_[ShortTitle].md convention to populate each column.

If an inbox is empty, say so explicitly.

Note any tasks that have been in Team Inbox for more than 3 days based on the date in the filename vs today's date.
