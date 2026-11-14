SELECT id, name, CHAR_LENGTH(name) AS len
FROM members
WHERE name IS NULL
   OR TRIM(name) = ''
   OR CHAR_LENGTH(name) <> CHAR_LENGTH(TRIM(name))
ORDER BY id ASC;
