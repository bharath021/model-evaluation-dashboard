# Database Schema

The dashboard stores one prompt-level evaluation in `eval_runs` and one row per
candidate model output in `model_responses`.

## Tables

### `eval_runs`

| Column | PostgreSQL type | Notes |
| --- | --- | --- |
| `id` | `BIGINT` identity | Primary key |
| `prompt` | `TEXT` | Prompt sent to every candidate model |
| `created_at` | `TIMESTAMPTZ` | Evaluation creation time |

### `model_responses`

| Column | PostgreSQL type | Notes |
| --- | --- | --- |
| `id` | `BIGINT` identity | Primary key |
| `run_id` | `BIGINT` | Foreign key to `eval_runs.id` |
| `model_name` | `TEXT` | Provider model ID used for generation |
| `response_text` | `TEXT` | Candidate model output |
| `score_relevance` | `SMALLINT` | Claude judge score from 0 through 10 |
| `score_clarity` | `SMALLINT` | Claude judge score from 0 through 10 |
| `score_length` | `SMALLINT` | Claude judge score from 0 through 10 |
| `response_time_ms` | `INTEGER` | Candidate generation latency in milliseconds |
| `created_at` | `TIMESTAMPTZ` | Response row creation time |

`model_responses.run_id` cascades deletes from `eval_runs`, so a run and its
candidate outputs stay consistent. The score columns use database check
constraints for the 0 through 10 rubric, and `response_time_ms` cannot be
negative.

## Indexes

- `idx_eval_runs_created_at` supports recent history reads.
- `idx_model_responses_run_id` supports joining each run to its response rows.
- `idx_model_responses_model_created_at` supports per-model time-series charts.

## Files

- PostgreSQL deployment DDL: `backend/db/postgresql_schema.sql`
- SQLite local schema: `backend/app/db/repository.py`
