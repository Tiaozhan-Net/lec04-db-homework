START TRANSACTION;

UPDATE members
SET student_id = TRIM(student_id),
    name = TRIM(name),
    class_name = TRIM(class_name),
    major = TRIM(major);

DELETE FROM members
WHERE student_id IS NULL OR student_id NOT REGEXP '^[0-9]{8}$';

DELETE FROM members
WHERE name IS NULL OR name = '';

-- 去重前统一报名时间，使字符串顺序与时间顺序一致。
UPDATE members
SET joined_at = DATE_FORMAT(
    STR_TO_DATE(REPLACE(REPLACE(joined_at, '/', '-'), 'T', ' '), '%Y-%m-%d %H:%i:%s'),
    '%Y-%m-%d %H:%i:%s'
)
WHERE joined_at IS NOT NULL;

UPDATE members
SET class_name = CONCAT(LEFT(class_name, 4), '-', SUBSTRING(class_name, 6, 1))
WHERE class_name REGEXP '^[0-9]{4}(级| )[1-9]班$';

UPDATE members
SET major = CASE
    WHEN major IN ('计算机', '计科', '计算机科学') THEN '计算机科学与技术'
    WHEN major IN ('软件', '软工') THEN '软件工程'
    WHEN major IN ('大数据', '数据科学') THEN '数据科学与大数据技术'
    ELSE major
END;

UPDATE members
SET score = CASE WHEN score > 100 THEN 100 ELSE 0 END
WHERE score IS NULL OR score < 0 OR score > 100;

-- 每个学号保留最早报名的一行，时间相同时保留 id 最小的一行。
DELETE m
FROM members AS m
JOIN (
    SELECT id,
           ROW_NUMBER() OVER (PARTITION BY student_id ORDER BY joined_at, id) AS row_num
    FROM members
) AS ranked ON ranked.id = m.id
WHERE ranked.row_num > 1;

COMMIT;
