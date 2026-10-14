-- Read helpers the future API (batch 03) can call. All output is synthetic.
CREATE FUNCTION patient_data.patient_timeline(p_id text)
RETURNS TABLE (event_date date, date_precision text, source text, event_type text, description text)
LANGUAGE sql STABLE AS $$
  SELECT t.event_date, t.date_precision, t.source, t.event_type, t.description FROM (
    SELECT h.event_date, h.date_precision, 'history'::text AS source, h.event_type, h.description, 0 AS ord, h.event_seq::bigint AS seq
      FROM patient_data.patient_history_events h WHERE h.patient_id = p_id
    UNION ALL
    SELECT o.observed_on, 'day', 'progress', 'observation:' || o.domain || ':' || o.direction, o.observation, 1, o.observation_id
      FROM patient_data.progress_observations o WHERE o.patient_id = p_id
  ) t ORDER BY t.event_date NULLS LAST, t.ord, t.seq;
$$;

CREATE FUNCTION patient_data.get_patient_profile(p_id text) RETURNS jsonb LANGUAGE sql STABLE AS $$
  SELECT (to_jsonb(p) - 'created_at' - 'updated_at') || jsonb_build_object(
    'use', COALESCE((SELECT jsonb_agg(to_jsonb(u) - 'patient_id' - 'created_at' ORDER BY u.start_date) FROM patient_data.substance_or_behavior_use u WHERE u.patient_id = p.patient_id), '[]'),
    'factors', COALESCE((SELECT jsonb_agg(to_jsonb(f) - 'patient_id' - 'created_at' ORDER BY f.factor_id) FROM patient_data.triggers_and_risk_factors f WHERE f.patient_id = p.patient_id), '[]'),
    'interventions', COALESCE((SELECT jsonb_agg(to_jsonb(i) - 'patient_id' - 'created_at' ORDER BY i.start_date) FROM patient_data.previous_interventions i WHERE i.patient_id = p.patient_id), '[]'),
    'progress', COALESCE((SELECT jsonb_agg(to_jsonb(o) - 'patient_id' - 'created_at' ORDER BY o.observed_on) FROM patient_data.progress_observations o WHERE o.patient_id = p.patient_id), '[]'))
  FROM patient_data.patients p WHERE p.patient_id = p_id;
$$;
