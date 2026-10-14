-- Separate schemas keep patient data apart from documents, users/sessions and logs.
CREATE SCHEMA IF NOT EXISTS patient_data;  -- synthetic patient cases (this batch)
CREATE SCHEMA IF NOT EXISTS research;      -- reserved: documents and chunks (batches 05-06)
CREATE SCHEMA IF NOT EXISTS app;           -- reserved: users and sessions (batch 04)
CREATE SCHEMA IF NOT EXISTS audit;         -- reserved: activity logs (batch 09)
COMMENT ON SCHEMA patient_data IS 'ENTIRELY SYNTHETIC. Fictional adult cases for education. Not real people or records.';
