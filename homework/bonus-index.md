# 加分：看得见——索引与执行计划（+10 分）

社团的报名表涨到 20 万行，名单页从 0.1 秒变成 3 秒。社长问你能不能加个索引。加索引不是越多越好：写得不对，优化器根本不用；写得太多，插入变慢，还会把执行计划带偏。

这一部分做两件事：先看懂一条查询到底用了索引用了几段，再在“最多三个索引”的预算里让四条查询都快起来。加分 10 分单独统计，不影响及格。

> **开始之前**
>
> - 读：第 5 部分的函数唯一索引；`EXPLAIN FORMAT=JSON` 的 `key`、`key_len`、`used_key_parts`、`filesort`。
> - 数据：`hw_bonus.members`，20 万行，已经带 `deleted_at` 和函数唯一索引。
> - 准备：在仓库根目录执行 `mysql -u root -p --default-character-set=utf8mb4 -e "source db/02_big.sql" hw_bonus`，大约一分钟。
> - `b2_indexes.sql` 里的 `CREATE INDEX` 不能重复执行；想重跑先按末尾「重置本部分」重灌 20 万行。
>
> 提交的 SQL 里不要写 `USE` 或 `CREATE DATABASE`。

## 任务 B1：让函数键参与定位

第 5 部分那个唯一索引是两段的：`student_id`，加上一个算出来的活跃标记。如果查询里只写 `student_id`，优化器只用第一段；想让第二段也参与定位，`WHERE` 里必须出现和建索引时**一模一样**的表达式。

写一条 `SELECT`：

- 只查 `id` 和 `name`；
- `WHERE` 里同时有 `student_id` 的等值条件，和第 5 部分 `05b` 里那个函数键表达式。

> **要求**
>
> - 一条 `SELECT`，写在 `bonus/b1_functional_key.sql`。
> - `EXPLAIN FORMAT=JSON` 里 `key = uk_student_id`，`used_key_parts` 是两段。

**提示**
- 先看表上真正的索引表达式（在命令行里执行）：
  ```sql
  SHOW CREATE TABLE hw_bonus.members\G
  ```
- `SHOW CREATE TABLE` 显示建表语句和索引定义；`\G` 只是让结果竖排显示。
- 函数键表达式是 `(IF(deleted_at IS NULL, 1, NULL))`；`WHERE` 里要写成 `(IF(deleted_at IS NULL, 1, NULL)) = 1`，和索引表达式逐字对齐。
- 只写 `deleted_at IS NULL` 是另一回事，优化器不会把它认成函数键，只会用第一段。
- 本地看计划：
  ```sql
  EXPLAIN FORMAT=JSON
  SELECT id, name FROM members
  WHERE student_id = '90000001' AND (IF(deleted_at IS NULL, 1, NULL)) = 1\G
  ```
  `key` 是用到的索引名，`used_key_parts` 是用到的段数。

## 任务 B2：索引预算

只写 `CREATE INDEX`，最多新建三个索引。表上有这四条查询，评测时参数固定：

| # | 查询 |
| --- | --- |
| 1 | `WHERE student_id = '90000001' AND deleted_at IS NULL` |
| 2 | `WHERE major = '计算机科学与技术' AND score >= 60 ORDER BY score DESC LIMIT 20` |
| 3 | `WHERE class_name = '2023-1' ORDER BY joined_at` |
| 4 | `WHERE major = '软件工程' AND name LIKE '张%'` |

> **要求**
>
> - 第 1 条用现成的唯一索引，不新建。
> - 剩下三条各走一个索引，合计最多新建三个。
> - 每条查询都走索引，而且没有 `filesort`。
> - 索引超过三个，B2 直接 0 分。

**提示**
- 联合索引先放等值条件列，再放范围/排序列。第 2 条是“等值 + 范围 + 排序”压在一个索引上：`major` 等值，`score` 范围且要倒序，所以列顺序是 `(major, score)`。
- 第 3 条是 `class_name` 等值、`joined_at` 排序，索引顺序是 `(class_name, joined_at)`。
- 第 4 条是 `major` 等值、`name` 前缀范围，索引顺序是 `(major, name)`。
- `LIKE '张%'` 是前缀匹配，能走索引；`LIKE '%张'` 不能。
- 建完索引跑一次 `ANALYZE TABLE members;`，让优化器拿到统计信息。
- 本地看计划：
  ```sql
  EXPLAIN FORMAT=JSON
  SELECT id FROM members
  WHERE major = '软件工程' AND name LIKE '张%'\G
  ```
  看 `key` 和 `using_filesort`。

> **注意**
>
> 评测只看 `EXPLAIN`，不看 SQL 文本；但题目要求 B1 只查 `id`、`name`，请按题目写。

## 评测

在仓库根目录运行：

```powershell
python grader/run.py --part bonus --user <你的 GitHub 用户名>
```

看到分数表里 `加分 ...` 一行是 `10 / 10`，这一部分就通过了。评测脚本自己跑 `EXPLAIN FORMAT=JSON`，不需要交执行计划。环境配置见[环境搭建](../docs/00-环境搭建.md)。

## 提交

```text
bonus/b1_functional_key.sql
bonus/b2_indexes.sql
```

模板在 `homework/templates/bonus/`。提交步骤见[提交与评测](../docs/01-提交与评测.md)。

## 评分

| 项目 | 分值 |
| --- | ---: |
| B1 两段都用上 | 4 |
| B2 第 1 条 | 1 |
| B2 第 2 条 | 2 |
| B2 第 3 条 | 2 |
| B2 第 4 条 | 1 |

## 重置本部分

想重灌 20 万行并重跑索引脚本，先在仓库根目录进入 `hw_bonus`：

```powershell
mysql -u root -p --default-character-set=utf8mb4 hw_bonus
```

然后在 `mysql>` 提示符下依次执行：

```text
source db/02_big.sql
source submissions/<你的用户名>/bonus/b2_indexes.sql
```

B1 是查询，直接重跑即可，不用重置。
