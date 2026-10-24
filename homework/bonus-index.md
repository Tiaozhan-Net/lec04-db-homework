# 加分 看得见：索引与执行计划（+10 分）

数据：`hw_bonus`，20 万行。

```powershell
mysql -u root -p --default-character-set=utf8mb4 -e "source db/02_big.sql" hw_bonus
```

大约半分钟到一分钟。加分部分不影响及格，做不完可以不做。

---

## B1（4 分）让函数键参与定位

文件：`bonus/b1_functional_key.sql`

写一条 `SELECT`：

- 只查 `id` 和 `name`；
- `WHERE` 里同时有：
  - `student_id` 的等值条件；
  - 第 5 部分 `05b` 里建索引用的那个函数键表达式。

判分不看你说什么，只看 `EXPLAIN`：这条查询必须把唯一索引的**两段**都用上
（`used_key_parts` 是 2）。

> 提示：表达式要和 `05b` 里写的一模一样，MySQL 不会自动把 `deleted_at IS NULL` 认成函数键。

## B2（6 分）索引预算

文件：`bonus/b2_indexes.sql`，只写 `CREATE INDEX`。

表上有这四条查询（评测时参数是固定的）：

| # | 查询 |
| --- | --- |
| 1 | `WHERE student_id = '90000001' AND deleted_at IS NULL` |
| 2 | `WHERE major = '计算机科学与技术' AND score >= 60 ORDER BY score DESC LIMIT 20` |
| 3 | `WHERE class_name = '2023-1' ORDER BY joined_at` |
| 4 | `WHERE major = '软件工程' AND name LIKE '张%'` |

要求：

- 第 1 条用现成的唯一索引，**不要新建**；
- 剩下三条各走一个索引，**最多新建 3 个**；
- 每条查询都要走索引，而且没有 `filesort`；
- 索引建多了（超过 3 个），B2 直接 0 分。

判分由评测脚本跑 `EXPLAIN FORMAT=JSON`，不需要你交执行计划。

## 判分

| 项目 | 分值 |
| --- | ---: |
| B1 两段都用上 | 4 |
| B2 第 1 条 | 1 |
| B2 第 2 条 | 2 |
| B2 第 3 条 | 2 |
| B2 第 4 条 | 1 |

加分单独统计，不加进 100 分。
