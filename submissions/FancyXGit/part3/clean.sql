-- 参考解：第 3 部分清洗（硬删除）
-- 只改数据，不建表、不删表。

START TRANSACTION;

-- 1) 先把四列的可见空格去掉。学号留下来的值必须是 TRIM 之后的值，
--    否则第 4 部分的 ^[0-9]{8}$ 会拦不住 / 拦错。
UPDATE members SET
  student_id = TRIM(student_id),
  name       = TRIM(name),
  class_name = TRIM(class_name),
  major      = TRIM(major);

-- 2) 学号为空或不是 8 位数字 → 删行
DELETE FROM members
WHERE student_id IS NULL
   OR student_id NOT REGEXP '^[0-9]{8}$';

-- 3) 姓名为空 → 删行
DELETE FROM members
WHERE name IS NULL OR name = '';

-- 4) 日期先统一成 YYYY-MM-DD HH:MM:SS。
--    这一步必须在去重之前，否则字符串比较会留下错误的那一条。
UPDATE members
SET joined_at = DATE_FORMAT(
      STR_TO_DATE(REPLACE(REPLACE(joined_at, 'T', ' '), '/', '-'), '%Y-%m-%d %H:%i:%s'),
      '%Y-%m-%d %H:%i:%s')
WHERE joined_at IS NOT NULL;

-- 5) 班级：2023级1班 / 2023 1班 → 2023-1
UPDATE members
SET class_name = CONCAT(LEFT(class_name, 4), '-', SUBSTRING(class_name, 6, 1))
WHERE class_name REGEXP '^[0-9]{4}(级| )[1-9]班$';

-- 6) 专业同义写法 → 白名单里的三个值
UPDATE members SET major = CASE
    WHEN major IN ('计算机', '计科', '计算机科学')   THEN '计算机科学与技术'
    WHEN major IN ('软件', '软工')                   THEN '软件工程'
    WHEN major IN ('大数据', '数据科学')             THEN '数据科学与大数据技术'
    ELSE major
  END;

-- 7) 分数：NULL → 0，负数 → 0，超过 100 → 100
UPDATE members SET score = 0   WHERE score IS NULL OR score < 0;
UPDATE members SET score = 100 WHERE score > 100;

-- 8) 去重第一步：每个学号只留最早的报名时间
DELETE m FROM members m
JOIN (
  SELECT student_id, MIN(joined_at) AS keep_joined
  FROM members
  GROUP BY student_id
) d ON d.student_id = m.student_id
WHERE m.joined_at > d.keep_joined;

-- 9) 去重第二步：时间并列时保留 id 最小的那一条
DELETE m FROM members m
JOIN (
  SELECT student_id, MIN(id) AS keep_id
  FROM members
  GROUP BY student_id
) k ON k.student_id = m.student_id
WHERE m.id > k.keep_id;

COMMIT;
