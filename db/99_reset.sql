-- 一键把本地两个练习库恢复成初始状态。
-- 在仓库根目录执行（注意是仓库根目录，SOURCE 用的是相对路径）：
--   mysql -u root -p --default-character-set=utf8mb4 -e "source db/99_reset.sql"
--
-- 加分题的 20 万行数据不在这里，需要时单独跑：
--   mysql -u root -p -e "source db/02_big.sql" hw_bonus

CREATE DATABASE IF NOT EXISTS hw_clean
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE DATABASE IF NOT EXISTS hw_legacy
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE hw_clean;
SOURCE db/00_clean.sql;

USE hw_legacy;
SOURCE db/01_legacy.sql;

SELECT 'hw_clean' AS db, COUNT(*) AS rows_loaded FROM hw_clean.members
UNION ALL
SELECT 'hw_legacy', COUNT(*) FROM hw_legacy.members;
