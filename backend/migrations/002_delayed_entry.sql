-- Delayed entry: cumulative working hours at enrollment. Legacy rows enroll at zero.
ALTER TABLE followup_events ADD COLUMN entry_hours DOUBLE NOT NULL DEFAULT 0;
