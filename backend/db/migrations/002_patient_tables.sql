CREATE TABLE patient_data.patients (
  patient_id          text PRIMARY KEY CHECK (patient_id ~ '^P-[0-9]{3}$'),
  display_alias       text NOT NULL,
  age_years           smallint NOT NULL CHECK (age_years BETWEEN 18 AND 100),
  gender_identity     text NOT NULL DEFAULT 'unknown',
  primary_category    text NOT NULL CHECK (primary_category IN ('alcohol','cannabis','opioid','stimulant','behavioral')),
  motivation_stage    text NOT NULL DEFAULT 'unknown'
                      CHECK (motivation_stage IN ('precontemplation','contemplation','preparation','action','maintenance','unknown')),
  social_context      text NOT NULL,
  co_occurring_symptoms text[] NOT NULL DEFAULT '{}',  -- short free-text list; not queried relationally
  summary             text NOT NULL,
  case_reference_date date NOT NULL,                   -- the "as of" date of the case snapshot
  is_synthetic        boolean NOT NULL DEFAULT true CHECK (is_synthetic),
  synthetic_notice    text NOT NULL DEFAULT 'Entirely fictional case for education. Not a real person or record.',
  created_at          timestamptz NOT NULL DEFAULT now(),
  updated_at          timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE patient_data.patients IS 'SYNTHETIC. Category describes the presenting pattern only; it does not determine treatment suitability.';
CREATE INDEX patients_category_idx ON patient_data.patients (primary_category);

CREATE FUNCTION patient_data.touch_updated_at() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END $$;
CREATE TRIGGER patients_touch BEFORE UPDATE ON patient_data.patients
  FOR EACH ROW EXECUTE FUNCTION patient_data.touch_updated_at();

CREATE TABLE patient_data.patient_history_events (
  event_id       bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  patient_id     text NOT NULL REFERENCES patient_data.patients ON DELETE CASCADE,
  event_seq      integer NOT NULL CHECK (event_seq > 0),   -- order within the patient's timeline
  event_date     date,                                      -- NULL only when precision is 'unknown'
  date_precision text NOT NULL CHECK (date_precision IN ('year','month','day','unknown')),
  event_type     text NOT NULL CHECK (event_type IN ('onset','escalation','life_event','assessment',
                 'intervention_start','intervention_end','abstinence_start','relapse','other')),
  description    text NOT NULL,
  is_synthetic   boolean NOT NULL DEFAULT true CHECK (is_synthetic),
  created_at     timestamptz NOT NULL DEFAULT now(),
  UNIQUE (patient_id, event_seq),
  CHECK ((event_date IS NULL) = (date_precision = 'unknown'))
);
CREATE INDEX history_patient_date_idx ON patient_data.patient_history_events (patient_id, event_date);

CREATE TABLE patient_data.substance_or_behavior_use (
  use_id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  patient_id     text NOT NULL REFERENCES patient_data.patients ON DELETE CASCADE,
  name           text NOT NULL,
  category       text NOT NULL CHECK (category IN ('alcohol','cannabis','opioid','stimulant','behavioral')),
  is_primary     boolean NOT NULL DEFAULT false,
  pattern        text NOT NULL,
  frequency_text text NOT NULL DEFAULT 'unknown',
  quantity_text  text NOT NULL DEFAULT 'unknown',   -- free text to avoid false precision
  start_date     date NOT NULL,                     -- when the pattern of concern began
  end_date       date,                              -- when current use stopped; NULL if not stopped
  status         text NOT NULL CHECK (status IN ('ongoing','reduced','abstinent','in_maintenance_treatment','unknown')),
  is_synthetic   boolean NOT NULL DEFAULT true CHECK (is_synthetic),
  created_at     timestamptz NOT NULL DEFAULT now(),
  CHECK (end_date IS NULL OR end_date >= start_date),
  CHECK (status <> 'abstinent' OR end_date IS NOT NULL),
  CHECK (status <> 'ongoing' OR end_date IS NULL)
);
CREATE INDEX use_patient_idx ON patient_data.substance_or_behavior_use (patient_id);
CREATE UNIQUE INDEX use_one_primary_idx ON patient_data.substance_or_behavior_use (patient_id) WHERE is_primary;

CREATE TABLE patient_data.triggers_and_risk_factors (
  factor_id    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  patient_id   text NOT NULL REFERENCES patient_data.patients ON DELETE CASCADE,
  kind         text NOT NULL CHECK (kind IN ('trigger','risk_factor','protective_factor','observed_behavior')),
  domain       text NOT NULL CHECK (domain IN ('emotional','social','environmental','financial','physical','occupational','behavioral','other')),
  description  text NOT NULL,
  is_synthetic boolean NOT NULL DEFAULT true CHECK (is_synthetic),
  created_at   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX factors_patient_kind_idx ON patient_data.triggers_and_risk_factors (patient_id, kind);

CREATE TABLE patient_data.previous_interventions (
  intervention_id   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  patient_id        text NOT NULL REFERENCES patient_data.patients ON DELETE CASCADE,
  intervention_type text NOT NULL,
  setting           text NOT NULL DEFAULT 'unknown',
  start_date        date NOT NULL,
  end_date          date,
  status            text NOT NULL CHECK (status IN ('completed','ongoing','discontinued','unknown')),
  outcome_note      text NOT NULL DEFAULT 'not recorded',  -- fictional case note, not a research finding
  is_synthetic      boolean NOT NULL DEFAULT true CHECK (is_synthetic),
  created_at        timestamptz NOT NULL DEFAULT now(),
  CHECK (end_date IS NULL OR end_date >= start_date),
  CHECK (status NOT IN ('completed','discontinued') OR end_date IS NOT NULL),
  CHECK (status <> 'ongoing' OR end_date IS NULL)
);
CREATE INDEX interventions_patient_idx ON patient_data.previous_interventions (patient_id, start_date);

CREATE TABLE patient_data.progress_observations (
  observation_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  patient_id     text NOT NULL REFERENCES patient_data.patients ON DELETE CASCADE,
  observed_on    date NOT NULL,
  domain         text NOT NULL CHECK (domain IN ('use','motivation','engagement','mood','sleep','functioning','social','other')),
  direction      text NOT NULL CHECK (direction IN ('improved','stable','worsened','mixed','unknown')),
  observation    text NOT NULL,
  is_synthetic   boolean NOT NULL DEFAULT true CHECK (is_synthetic),
  created_at     timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX progress_patient_date_idx ON patient_data.progress_observations (patient_id, observed_on);
