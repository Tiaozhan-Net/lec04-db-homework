# 第 2 部分：看得懂——脏数据诊断（20 分）

社团上一届的报名表是从 Excel 导进来的，导入时没做任何校验。现在 `hw_legacy.members` 里躺着 28 条记录：同一个学号出现了两三次，有人学号是空的，专业写成「计算机」「计科」「软件」「软工」「大数据」等多种写法，报名时间有的是 `2025/09/01`，有的是 `2025-09-01T08:00:00`。

直接动手清洗是第 3 部分的事。这一部分先做体检：把每一类毛病找出来、数清楚，写成六条查询。**只查不改**，文件里出现 `UPDATE`、`DELETE`、`INSERT` 的那一条查询就是 0 分。

> **开始之前**
>
> - 读：[环境搭建](../docs/00-环境搭建.md) 的「数据与表结构」；复习 `TRIM`、`REGEXP`、`GROUP BY`、`HAVING` 和 `NULL` 的判断。
> - 数据：`hw_legacy.members`，28 行，全列可空、没有任何约束。
> - 准备：在仓库根目录执行 `mysql -u root -p --default-character-set=utf8mb4 -e "source db/01_legacy.sql" hw_legacy`。
> - 本部分只读，不需要重置；不要为了“重置”去跑 `01_legacy.sql`，除非数据已经被其他部分改乱。
>
> 提交的 SQL 里不要写 `USE` 或 `CREATE DATABASE`。

## 任务：六条只读查询

六个文件，一个文件一条 `SELECT`。列名和排序按表来，评测逐行比对。

| 文件 | 查什么 | 输出列 | 排序 |
| --- | --- | --- | --- |
| `q1_dup.sql` | 出现次数大于 1 的学号 | `student_id`、`cnt` | `cnt DESC, student_id ASC` |
| `q2_name.sql` | 姓名为 `NULL`、空串、全空格、前后带空格 | `id`、`name`、`len` | `id ASC` |
| `q3_score.sql` | 分数小于 0 或大于 100 | `id`、`score` | `id ASC` |
| `q4_date.sql` | 报名时间不是 `YYYY-MM-DD HH:MM:SS` | `id`、`joined_at` | `id ASC` |
| `q5_whitelist.sql` | 专业或班级不在白名单 | `id`、`major`、`class_name` | `id ASC` |
| `q6_sid.sql` | 学号不是 8 位数字 | `id`、`student_id` | `id ASC` |

> **要求**
>
> - 每条查询只写一条 `SELECT`，不要加 `USE`、`SET`、`SHOW`。
> - `cnt` 用 `COUNT(*) AS cnt`；`len` 用 `CHAR_LENGTH(name) AS len`。
> - 第 1 条先排除空学号（`NULL`、空串、全空格），再按学号分组，用 `HAVING COUNT(*) > 1` 筛出重复组。
> - 第 2 条输出 `name` 的原值，不要 `TRIM`；带空格的行正是要查出来的东西。
> - 第 3 条只查越界分数；`NULL` 属于“没填”，不算越界。
> - 第 4 条只认 `YYYY-MM-DD HH:MM:SS`；不要用 `STR_TO_DATE` 去猜。
> - 第 5 条把“专业不在白名单”或“班级格式不对”的行都列出来，两个条件之间是“或”。
> - 第 6 条判断前先 `TRIM`；前后带空格、去掉后正好 8 位的，不算问题。

**提示**

讲义没讲的函数先看这里：

| 写法 | 作用 |
| --- | --- |
| `TRIM(x)` | 去掉字符串首尾空格 |
| `x REGEXP '...'` | 在 `WHERE` 里做正则匹配，命中返回 1，否则 0；`NOT REGEXP` 取反 |
| `CHAR_LENGTH(x)` | 字符数，不是字节数 |
| `COUNT(*)` | 统计行数 |
| `GROUP BY` / `HAVING` | 分组 / 对分组结果再筛选 |

- `HAVING` 是 `GROUP BY` 之后对“组”做筛选；`WHERE` 筛的是单行。`HAVING COUNT(*) > 1` 就是“人数大于 1 的组”。
- 第 1 条如果只写 `student_id IS NOT NULL`，两条 `NULL` 会被 `GROUP BY` 并成一组，多出一行 `NULL, 2`。空串和全空格各自只有一行，不会出现在 `HAVING COUNT(*) > 1` 里，但先用 `TRIM(student_id) <> ''` 排除更稳。
- 第 2 条三种毛病分别对应 `name IS NULL`、`TRIM(name) = ''`、`name <> TRIM(name)`。`CHAR_LENGTH` 数的是字符数，不是字节数。
- 第 4 条的日期正则：
  ```text
  ^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$
  ```
  `^` 是开头，`$` 是结尾，`[0-9]{4}` 是 4 位数字，中间的空格是日期和时间之间的分隔符。`NULL NOT REGEXP ...` 的结果还是 `NULL`，不算真，所以空值要单独用 `IS NULL` 判断。
- 第 5 条里 `NOT IN` / `NOT REGEXP` 碰到 `NULL` 也返回 `NULL`，不算命中；`major` 和 `class_name` 的可空情况都要单独写 `IS NULL`。
- 第 5 条的班级正则：
  ```text
  ^[0-9]{4}-[1-9]$
  ```
  四位数字、一个短横线、一位 1 到 9 的班号；`^` 和 `$` 不能省。
- 第 6 条学号是 8 位纯数字：`'^[0-9]{8}$'`，`{8}` 表示正好 8 位。

## 评测

在仓库根目录运行：

```powershell
python grader/run.py --part 2 --user <你的 GitHub 用户名>
```

看到分数表里 `第 2 部分 ...` 一行是 `20 / 20`，这一部分就通过了。六条全对再加 2 分，所以满分是 20；有 ❌ 的项，按“说明”列改。

评测用的是另一份数据：脏数据的种类和位置一样，但人名、分数不同。不要写死某一行的结果。环境配置见[环境搭建](../docs/00-环境搭建.md)。

## 提交

```text
part2/q1_dup.sql       q2_name.sql     q3_score.sql
part2/q4_date.sql      q5_whitelist.sql  q6_sid.sql
```

模板在 `homework/templates/part2/`。提交步骤见[提交与评测](../docs/01-提交与评测.md)。

## 评分

| 项目 | 分值 |
| --- | ---: |
| 六条查询 | 3 × 6 |
| 六条全对 | 2 |

## 重置本部分

第 2 部分只读，一般不用重置。如果 `hw_legacy` 被改乱了，先在仓库根目录进入 `hw_legacy`：

```powershell
mysql -u root -p --default-character-set=utf8mb4 hw_legacy
```

然后重新加载：

```text
source db/01_legacy.sql
```
