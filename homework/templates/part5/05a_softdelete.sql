-- 第 5 部分 / 05a 加列 + 把"取消报名"改成软删除
-- 1. 加一列 deleted_at DATETIME(3) NULL
-- 2. 学号 20230002 取消报名：不要 DELETE，写 deleted_at = NOW(3)

