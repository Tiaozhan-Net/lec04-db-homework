SELECT name, score
FROM members
WHERE score >= 85
ORDER BY score DESC, student_id ASC
LIMIT 5;
