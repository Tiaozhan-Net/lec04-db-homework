SELECT id, student_id
FROM members
WHERE student_id IS NULL
   OR TRIM(student_id) NOT REGEXP '^[0-9]{8}$'
ORDER BY id ASC;
