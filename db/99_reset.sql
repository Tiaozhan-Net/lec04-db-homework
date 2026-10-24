-- 一键把本地练习库建好并灌上初始数据。
-- 在仓库根目录执行（注意是仓库根目录，SOURCE 用的是相对路径）：
--   mysql -u root -p --default-character-set=utf8mb4 -e "source db/99_reset.sql"
--
-- 这里只灌前两份数据。加分题的 20 万行单独跑：
--   mysql -u root -p --default-character-set=utf8mb4 -e "source db/02_big.sql" hw_bonus

CREATE DATABASE IF NOT EXISTS hw_clean
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE DATABASE IF NOT EXISTS hw_legacy
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE DATABASE IF NOT EXISTS hw_bonus
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE hw_clean;
SOURCE db/00_clean.sql;

USE hw_legacy;
SOURCE db/01_legacy.sql;

SELECT 'hw_clean' AS db, COUNT(*) AS rows_loaded FROM hw_clean.members
UNION ALL
SELECT 'hw_legacy', COUNT(*) FROM hw_legacy.members;
