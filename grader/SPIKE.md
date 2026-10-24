# 实测记录

本地 MySQL **8.0.44**，严格模式，`utf8mb4_0900_ai_ci`。

## 已经跑通的

```text
db/99_reset.sql                hw_clean 14 行 / hw_legacy 28 行
grader/solutions 全参考解      必做 100 / 100，加分 10 / 10
全量评测耗时                   19 秒（含生成 20 万行）
```

逐个确认过的语法：

| 东西 | 结果 |
| --- | --- |
| `CHECK (student_id REGEXP '^[0-9]{8}$')` | 能建，脏数据插不进去，报 3819 |
| `UNIQUE KEY (student_id, (IF(deleted_at IS NULL, 1, NULL)))` | 能建，两条活跃行 1062，软删除的不占位 |
| `EXPLAIN FORMAT=JSON` 的 `used_key_parts` | 有，B1 的两段能断住 |
| `DELETE m FROM members m JOIN (SELECT ... FROM members) d` | 不报 1093 |
| 20 万行生成 | 18 秒，`ANALYZE TABLE` 后四条 B2 查询都走索引、无 filesort |
| `db/99_check_part3.sql` | 洗完显示「全对 / 明细 0 条」 |
| `db/99_check_part4.sql` | 7 行全 OK，`CHECK` 只算用户建的 5 个 |

反例也验过：DML 里写死 `id`、清洗脚本里 `DROP TABLE`、建新表再 `RENAME`，
分别被「id 偏移的评测数据」「关键字拦截」「`INNODB_TABLES.TABLE_ID` 比对」抓住。

## 还要在 GitHub 上确认

1. `mysql:8.0.44` 这个镜像在 Actions 上能拉到（第一次 PR 就能看出来）；
2. fork 来的 PR 里 `GITHUB_STEP_SUMMARY` 能正常写（只读 token 只能写 Summary）；
3. Guard 那段 bash 只在 Actions 的 `ubuntu-latest` 上跑过才算数，本地没有 bash，只做了人工检查。

## 版本口径

本地是 8.0.44，所以 `docker-compose.yml` 和 CI 都钉在 `mysql:8.0.44`，
不再写 8.0.36。文档里要求学生 `MySQL 8.0`（推荐 8.0.44，最低 8.0.16），`SELECT VERSION();` 自查。
