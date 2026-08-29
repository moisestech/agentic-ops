# Constraints

## In scope

- Retrieve approved public/synthetic records and show source ids.
- Read calendar and budget fixtures for the named scenario.
- Propose an internal task list.
- Pause on every WRITE.
- Fail closed when the corpus has no record.

## Out of scope

- Sending email or calendar invites.
- ServiceNow, Salesforce, or any named enterprise platform ownership.
- Live student or applicant PII.
- Invented attendance, learning-gain, or revenue numbers.
- Fine-tuning.
- Autonomous multi-venue expansion.

## Kill criteria

Stop the agent and use a form or a checklist if:

- The brief is a single known field update.
- There is no approved corpus.
- A write would leave the building (email, purchase, directory change) without a named reviewer.
