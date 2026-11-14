SELECT id, joined_at
FROM members
WHERE joined_at IS NULL
   OR joined_at NOT REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$'
ORDER BY id ASC;
