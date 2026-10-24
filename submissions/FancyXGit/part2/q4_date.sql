-- 参考解：第 2 部分 Q4 日期格式不对
-- 只认 YYYY-MM-DD HH:MM:SS 这一种写法，斜杠和 T 都算不合格。
SELECT id, joined_at
FROM members
WHERE joined_at IS NULL
   OR joined_at NOT REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$'
ORDER BY id ASC;
