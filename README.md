# Trump Mentions Engine (MVP)

Trump Mentions Engine is a **local Windows-first Python desktop application** for researching active Trump mention markets. It ingests Polymarket markets, gathers event/transcript context, runs matching rules, computes transparent model probabilities, and displays edges in a multi-screen PySide6 GUI.

## One-click launch (Windows)

Use `launch_trump_mentions_engine.bat`.

The launcher will:
1. Detect Python (`py -3.11`, `py`, or `python`)
2. Create `.venv` if needed
3. Upgrade pip
4. Install `requirements.txt`
5. Create `data/` and `logs/`
6. Launch the app

## Data storage

- SQLite DB: `data/trump_mentions.db`
- Logs: `logs/app.log`

## Screens

- **Dashboard**: summary cards + top opportunities + quick actions
- **Markets**: active Trump mention outcomes and pricing
- **Events**: upcoming/recent event metadata and detail panel
- **Transcripts**: fetched transcript status + full text preview
- **Model / Predictions**: market vs model probabilities + edge/confidence
- **Rules / Matcher**: matcher diagnostics for outcomes/transcripts
- **Logs**: live log console with clear/open controls
- **Settings**: refresh/config toggles and connectivity test

## Full sync pipeline

1. Sync markets
2. Sync events
3. Sync transcripts
4. Run matcher
5. Recompute predictions
6. Refresh GUI tables

Each stage is logged and designed to fail gracefully while preserving existing local data.

## Demo fallback behavior

If live event sources fail, the app inserts fallback demo events so the UI remains usable.

## Validation and tests

Included unit tests:
- Rule parser threshold behavior
- Matcher counting and ambiguity adjustment

Run with:

```bash
python -m pytest
```

## Limitations (MVP)

- Transcript collection uses text-first scraping and may miss some events.
- Polymarket/event schemas can change; parsing is defensive but not exhaustive.
- Model is transparent and deterministic but intentionally simple.
- No betting or trade execution support (research-only).

## Troubleshooting

- If GUI fails to launch, confirm Python 3.11+ and run launcher again.
- If sources fail, check `logs/app.log`; fallback mode should keep core views populated.
- If dependencies fail on first run, rerun the `.bat` after network recovery.
