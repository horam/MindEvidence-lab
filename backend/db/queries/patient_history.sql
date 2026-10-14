-- Chronological history (events + progress observations) for one patient:
SELECT * FROM patient_data.patient_timeline('P-001');

-- History events only, in stored order:
SELECT event_seq, event_date, date_precision, event_type, description
FROM patient_data.patient_history_events WHERE patient_id = 'P-001' ORDER BY event_seq;

-- Cross-case comparison without implying category determines treatment:
SELECT primary_category, motivation_stage, count(*) FROM patient_data.patients GROUP BY 1, 2 ORDER BY 1, 2;
