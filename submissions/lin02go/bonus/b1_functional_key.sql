SELECT id, name
FROM members
WHERE student_id = '90000001'
  AND IF(deleted_at IS NULL, 1, NULL) = 1;
