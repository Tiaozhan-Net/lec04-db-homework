SELECT student_id, COUNT(*) AS cnt
FROM members
WHERE student_id IS NOT NULL
  AND TRIM(student_id) <> ''
GROUP BY student_id
HAVING COUNT(*) > 1
ORDER BY cnt DESC, student_id ASC;
