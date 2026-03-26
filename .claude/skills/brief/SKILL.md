---
name: brief
description: Create a properly formatted task brief in Team Inbox/ for a given team member and task description
disable-model-invocation: false
---

Args: [TeamMember] [task description]

1. Generate filename: YYYY-MM-DD_[TeamMember]_[SlugFromTask].md using today's date
2. Write to "Team Inbox/" with the following sections:

---
**Assigned To:** [TeamMember]
**Date:** YYYY-MM-DD
**Task:** [Short task title]

## Context
[Relevant background for the team member to understand why this task exists]

## Task Description
[Full description of what needs to be done]

## Expected Output
[Specific deliverable format and where it should land — typically Owner's Inbox/]
---

3. Confirm the file was created and show the full path.
