# 加分 看得见：索引与执行计划（+10 分）

## 1. 数据与准备

- 表：`hw_bonus.members`，20 万行。`db/99_reset.sql` 已经建好这个库，这里只灌数据。
- 灌数据，大约一分钟：

  ```powershell
  mysql -u root -p --default-character-set=utf8mb4 -e "source db/02_big.sql" hw_bonus
  ```

加分部分不影响及格，做不完可以不做。

## 2. 要做什么

### B1 让函数键参与定位（4 分）

写一条 `SELECT`：

- 只查 `id` 和 `name`；
- `WHERE` 里同时有 `student_id` 的等值条件，和第 5 部分 `05b` 里建索引用的那个函数键表达式。

判分只看 `EXPLAIN`：这条查询要把唯一索引的两段都用上，`used_key_parts` 为 2。

表达式要和 `05b` 里写的一模一样，MySQL 不会把 `deleted_at IS NULL` 自动认成函数键。

### B2 索引预算（6 分）

只写 `CREATE INDEX`，最多新建三个索引。表上有这四条查询，评测时参数固定：

| # | 查询 |
| --- | --- |
| 1 | `WHERE student_id = '90000001' AND deleted_at IS NULL` |
| 2 | `WHERE major = '计算机科学与技术' AND score >= 60 ORDER BY score DESC LIMIT 20` |
| 3 | `WHERE class_name = '2023-1' ORDER BY joined_at` |
| 4 | `WHERE major = '软件工程' AND name LIKE '张%'` |

要求：

- 第 1 条用现成的唯一索引，不新建；
- 剩下三条各走一个索引，合计最多新建三个；
- 每条查询都走索引，而且没有 `filesort`；
- 索引超过三个，B2 直接 0 分。

## 3. 交什么

```text
bonus/b1_functional_key.sql
bonus/b2_indexes.sql
```

模板在 `homework/templates/bonus/`。

## 4. 怎么评测

| 项目 | 分值 |
| --- | ---: |
| B1 两段都用上 | 4 |
| B2 第 1 条 | 1 |
| B2 第 2 条 | 2 |
| B2 第 3 条 | 2 |
| B2 第 4 条 | 1 |

- 评测脚本自己跑 `EXPLAIN FORMAT=JSON`，不需要交执行计划。
- 本地看计划：

  ```sql
  USE hw_bonus;
  EXPLAIN FORMAT=JSON
  SELECT id, name FROM members
  WHERE student_id = '90000001' AND (IF(deleted_at IS NULL, 1, NULL)) = 1\G
  ```

  `key` 是用到的索引名，`used_key_parts` 是用到的段数。
- 加分单独统计，不进 100 分。
