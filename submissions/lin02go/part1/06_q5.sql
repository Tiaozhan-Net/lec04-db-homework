SELECT major, COUNT(*) AS cnt
FROM members
GROUP BY major
ORDER BY cnt DESC, major ASC;
