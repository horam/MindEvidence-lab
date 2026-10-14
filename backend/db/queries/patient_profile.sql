-- 1) Whole profile as one JSON document (what an API endpoint would return):
SELECT patient_data.get_patient_profile('P-001');

-- 2) Relational view of the same case (change the id as needed):
SELECT p.patient_id, p.display_alias, p.age_years, p.primary_category, p.motivation_stage, p.social_context,
       p.co_occurring_symptoms, p.summary, p.is_synthetic
FROM patient_data.patients p WHERE p.patient_id = 'P-001';
SELECT kind, domain, description FROM patient_data.triggers_and_risk_factors WHERE patient_id = 'P-001' ORDER BY kind, factor_id;
SELECT intervention_type, setting, start_date, end_date, status, outcome_note
FROM patient_data.previous_interventions WHERE patient_id = 'P-001' ORDER BY start_date;
