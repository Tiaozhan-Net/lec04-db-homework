SELECT id, score
FROM members
WHERE score < 0 OR score > 100
ORDER BY id ASC;
