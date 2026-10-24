# 加分 看得见：索引与执行计划（+10 分）

## 1. 情景

社团的报名表涨到 20 万行，名单页从 0.1 秒变成 3 秒。

社长问你能不能加个索引。加索引不是越多越好：写得不对，优化器根本不用；写得太多，插入变慢，还会把执行计划带偏。

这一部分做两件事：先看懂一条查询到底用了索引用了几段，再在「最多三个索引」的预算里让四条查询都快起来。

不影响及格，做不完可以不做。

## 2. 数据与准备

- 表：`hw_bonus.members`，20 万行，已经带 `deleted_at` 和函数唯一索引。
- `db/99_reset.sql` 已经建好这个库，这里只灌数据，大约一分钟：

  ```powershell
  mysql -u root -p --default-character-set=utf8mb4 -e "source db/02_big.sql" hw_bonus
  ```

## 3. 要做什么

### 3.1 B1 让函数键参与定位

第 5 部分那个唯一索引是两段的：`student_id`，加上一个算出来的活跃标记。

如果查询里只写 `student_id`，优化器只用第一段；想让第二段也参与定位，`WHERE` 里必须出现和建索引时**一模一样**的表达式。

写一条 `SELECT`：

- 只查 `id` 和 `name`
- `WHERE` 里同时有 `student_id` 的等值条件，和第 5 部分 `05b` 里那个函数键表达式

判分只看 `EXPLAIN`：这条查询要把唯一索引的两段都用上，`used_key_parts` 为 2。

`deleted_at IS NULL` 和函数键是两回事，MySQL 不会自动把它们认成同一个东西。

讲义 7.4 末尾讲过 `EXPLAIN FORMAT=JSON` 里怎么看 `key`、`key_len` 和 `used_key_parts`。

### 3.2 B2 索引预算

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

第 2 条是「等值 + 范围 + 排序」三件事压在一个索引上，列的顺序决定能不能省掉排序。第 4 条的 `LIKE '张%'` 是前缀匹配，能走索引；`'%张'` 这种就不行。

## 4. 交什么

```text
bonus/b1_functional_key.sql
bonus/b2_indexes.sql
```

模板在 `homework/templates/bonus/`。

## 5. 怎么评测

| 项目 | 分值 |
| --- | ---: |
| B1 两段都用上 | 4 |
| B2 第 1 条 | 1 |
| B2 第 2 条 | 2 |
| B2 第 3 条 | 2 |
| B2 第 4 条 | 1 |

评测脚本自己跑 `EXPLAIN FORMAT=JSON`，不需要交执行计划。

本地看计划：

```sql
USE hw_bonus;
EXPLAIN FORMAT=JSON
SELECT id, name FROM members
WHERE student_id = '90000001' AND (IF(deleted_at IS NULL, 1, NULL)) = 1\G
```

`key` 是用到的索引名，`used_key_parts` 是用到的段数，`filesort` 说明这次排序没有靠索引。

加分单独统计，不进 100 分。
