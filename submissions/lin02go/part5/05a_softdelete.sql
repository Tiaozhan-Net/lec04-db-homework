ALTER TABLE members
  ADD COLUMN deleted_at DATETIME(3) NULL AFTER joined_at;

UPDATE members
SET deleted_at = NOW(3)
WHERE student_id = '20230002' AND deleted_at IS NULL;
