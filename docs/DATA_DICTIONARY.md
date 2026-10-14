# Data Dictionary: schema `patient_data`

**All records are entirely synthetic.** Every table has `is_synthetic boolean NOT NULL DEFAULT true CHECK (is_synthetic)`, so a non-synthetic row cannot be inserted. Narrative text is fictional case material, not research findings or real outcomes. Patient data lives in its own schema; `research`, `app` (users, sessions) and `audit` (logs) are created empty for later batches.

## Relationships
`patients 1 ── * patient_history_events | substance_or_behavior_use | triggers_and_risk_factors | previous_interventions | progress_observations` (all via `patient_id`, `ON DELETE CASCADE`).
Cross-table consistency (enforced by tests, not FKs): each intervention start/end date has a matching `intervention_start`/`intervention_end` history event; the primary use `start_date` matches the `onset` event.

Date convention: dates are stored as the first day of their period; `date_precision` on events says whether that is a year, month or exact day. Unknown values are explicit: `'unknown'` text/enums, never silent NULLs, except `end_date` (NULL = not ended) and `event_date` (NULL only if precision is `unknown`).

## patients
| Field | Purpose |
|---|---|
| patient_id | Stable ID `P-001`..`P-010` (CHECK `^P-[0-9]{3}$`), primary key |
| display_alias | Fictional name shown in the UI |
| age_years | Adult age, 18-100 |
| gender_identity | Free text; `unknown` allowed |
| primary_category | alcohol, cannabis, opioid, stimulant, behavioral. Descriptive only; does not imply treatment suitability |
| motivation_stage | precontemplation, contemplation, preparation, action, maintenance, unknown |
| social_context | Living, work and support situation |
| co_occurring_symptoms | Short text array (JSON-like list justified: not queried relationally) |
| summary | One-sentence case synopsis; must agree with child tables |
| case_reference_date | "As of" date of the snapshot; no record may be later |
| is_synthetic, synthetic_notice | Synthetic labels |
| created_at, updated_at | Audit timestamps (`updated_at` set by trigger) |

## patient_history_events
| Field | Purpose |
|---|---|
| event_id | Surrogate key |
| patient_id | FK to patients |
| event_seq | Order within the patient's timeline, unique per patient |
| event_date, date_precision | When, and how precisely (year, month, day, unknown) |
| event_type | onset, escalation, life_event, assessment, intervention_start, intervention_end, abstinence_start, relapse, other |
| description | What happened |

## substance_or_behavior_use
| Field | Purpose |
|---|---|
| use_id, patient_id | Key and FK |
| name | Substance or behavior (free text) |
| category | Same five categories as patients |
| is_primary | Exactly one primary row per patient (partial unique index) |
| pattern, frequency_text, quantity_text | Descriptive text; `unknown` when not recorded (avoids false precision) |
| start_date | When the pattern of concern began |
| end_date | When current use stopped; NULL if not stopped. Required when `abstinent`, forbidden when `ongoing` |
| status | ongoing, reduced, abstinent, in_maintenance_treatment, unknown |

## triggers_and_risk_factors
| Field | Purpose |
|---|---|
| factor_id, patient_id | Key and FK |
| kind | trigger, risk_factor, protective_factor, observed_behavior |
| domain | emotional, social, environmental, financial, physical, occupational, behavioral, other |
| description | The factor |

## previous_interventions
| Field | Purpose |
|---|---|
| intervention_id, patient_id | Key and FK |
| intervention_type, setting | What and where (`unknown` allowed) |
| start_date, end_date | Period; end required for completed/discontinued, forbidden for ongoing |
| status | completed, ongoing, discontinued, unknown |
| outcome_note | Fictional case note; `not recorded` by default |

## progress_observations
| Field | Purpose |
|---|---|
| observation_id, patient_id | Key and FK |
| observed_on | Date of the note, within the patient's timeline and not after `case_reference_date` |
| domain | use, motivation, engagement, mood, sleep, functioning, social, other |
| direction | improved, stable, worsened, mixed, unknown |
| observation | Fictional note |

## Functions
- `patient_data.get_patient_profile(p_id)` returns one JSON document (patient, use, factors, interventions, progress).
- `patient_data.patient_timeline(p_id)` returns history events and progress observations in chronological order.
