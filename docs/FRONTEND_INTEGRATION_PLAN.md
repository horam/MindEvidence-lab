# Frontend mock-data integration plan (no API built yet)

Status (Batch 03): patient list and detail now load from `GET /api/patients` and `GET /api/patients/{id}` through an adapter in `frontend/js/api.js`. Chat, chunks and citations are still mock. `?mock=1` opens an explicitly labeled demo mode; a backend failure shows an error and never falls back to mock data silently. The steps below record the original plan; steps 1-3 are done.

## Field mapping (mock to database)
| Mock field | Database source |
|---|---|
| id | patients.patient_id |
| name | patients.display_alias |
| category (capitalized) | patients.primary_category (lowercase; map in the adapter) |
| substance | substance_or_behavior_use.name where is_primary |
| age | patients.age_years |
| history | derived from patient_history_events (or patients.summary for the card) |
| treatmentSummary | built from previous_interventions |
| background | patients.social_context |
| behaviors | triggers_and_risk_factors where kind = observed_behavior |
| triggers | kind = trigger |
| interventions | previous_interventions (type + dates + status) |
| progress {status, note} | latest progress_observations row; no single "status" field exists, so show direction + note |
| (new) | motivation_stage, co_occurring_symptoms, protective_factor / risk_factor lists, full timeline |

The mock seed text and the DB seed were written to agree for P-001 to P-010 (names, ages, categories), but wording differs, and some mock timeline years were refined (for example P-001 now has a 2024 relapse). The DB is authoritative once connected.

## Steps
1. Batch 03: add `GET /api/patients` (list) and `GET /api/patients/{id}` (profile), backed by `get_patient_profile` and `patient_timeline`.
2. Add an adapter in `frontend/js/api.js` that converts the profile JSON to the shape `views.js` already expects, so `views.js` and `main.js` stay unchanged.
3. Keep `mock-data.js` behind a flag (for example `?mock=1`) for offline demos until the end of Batch 10.
4. Add a timeline view of `patient_timeline` to the detail panel, and show `is_synthetic` / `synthetic_notice` from the API rather than hard-coded text.
5. Chat, chunks and citations remain mock until Batches 05-08.
