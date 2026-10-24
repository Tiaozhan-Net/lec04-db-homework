-- 清空练习环境：把作业用到的库全部删掉。
--
-- 在仓库根目录执行：
--   mysql -u root -p --default-character-set=utf8mb4 -e "source db/99_cleanup.sql"
--
-- 只删下面列出来的这些库，别的库不动。
-- 删完想重新开始，跑 db/99_reset.sql。

DROP DATABASE IF EXISTS hw_clean;
DROP DATABASE IF EXISTS hw_legacy;
DROP DATABASE IF EXISTS hw_bonus;
DROP DATABASE IF EXISTS hw_check;

-- 评测脚本自己建的临时库
DROP DATABASE IF EXISTS hw_p1_dml;
DROP DATABASE IF EXISTS hw_p1_q;
DROP DATABASE IF EXISTS hw_p2;
DROP DATABASE IF EXISTS hw_p3;
DROP DATABASE IF EXISTS hw_p3_ref;
DROP DATABASE IF EXISTS hw_p4;
DROP DATABASE IF EXISTS hw_p5;

-- 确认一下：这条查询应该一行都不返回
SELECT SCHEMA_NAME AS 剩余库
FROM information_schema.SCHEMATA
WHERE SCHEMA_NAME LIKE 'hw\_%';
