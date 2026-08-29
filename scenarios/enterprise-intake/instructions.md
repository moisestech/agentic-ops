# Scenario — Enterprise intake (ITSM-shaped)

A requester files a ticket. The agent retrieves policy, cites sources, and routes edge cases to a person.

## Brief

Route this intake ticket: a staff member wants an automated write into the HR directory after a name change. The ticket includes a department name only.

## Expected tools

`search_documents` → `check_calendar` (reviewer hours) → `calculate_budget` (optional cost of the write) → `manage_actions` pending.

## Honesty

This is not a ServiceNow implementation and not a customer production deploy.
It is the transferable pattern: cite, fail closed, pause on writes.
