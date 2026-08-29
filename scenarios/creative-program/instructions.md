# Scenario — Creative Institution Program Launch

Someone asks the runtime to prepare a six-week creative technology program.
The agent must retrieve the brief, check calendar capacity, total the budget against the cap, and wait before filing tasks.

## Brief

Prepare a six-week creative technology program launch: schedule, budget, equipment, and staff capacity.

## Expected tools

`search_documents` → `check_calendar` → `calculate_budget` → `manage_actions` (pending).

## Success

- Citations point at `data/creative-program`.
- Budget total is at or under the $4,800 cap.
- No email is sent.
- A human approval is required before tasks are recorded.
