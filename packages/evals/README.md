# Evals

Versioned golden questions over `data/dcc-public`, `data/creative-program`, and `data/enterprise-intake`.

```bash
make eval-offline
# writes packages/evals/reports/YYYY-MM-DD-fake.json
```

CI fails if any case fails. Live provider reports are opt-in and gitignored
under `reports/live/`.
