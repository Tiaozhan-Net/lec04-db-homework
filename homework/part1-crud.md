# 第 1 部分：会用——增删改查（35 分）

社团招新第一天，你手里有几份纸质报名表要录进 `hw_clean.members`，还要复核一条分数、删掉一条重复登记的记录。忙完这些，社长要几张报表：85 分以上的是谁、姓张的有几个、分数最高的三位、每个专业各多少人。本部分练习 `INSERT`、`UPDATE`、`DELETE`、`SELECT` 这四个最日常的动作。

> **开始之前**
>
> - 读：[环境搭建](../docs/00-环境搭建.md) 的「数据与表结构」，确认六个字段的标准格式。
> - 数据：`hw_clean.members`，14 行规范数据，已有约束。
> - 准备：在仓库根目录执行 `mysql -u root -p --default-character-set=utf8mb4 -e "source db/00_clean.sql" hw_clean`。
> - 注意：`01_dml.sql` 会改数据，不要重复执行；想重跑先看末尾「重置本部分」。
>
> 提交的 SQL 里不要写 `USE` 或 `CREATE DATABASE`。

## 任务 1：四条 DML

四条语句写在 `part1/01_dml.sql`，按顺序执行。表一开始 14 行，这一节做完是 17 行。

### 1. 新增一条

有人现场填了表，把这一条插进去。`name` 写你的 GitHub 用户名，评测按 PR 作者核对；其他字段按下表给。

| 字段 | 值 |
| --- | --- |
| `student_id` | `20239001` |
| `name` | 你的 GitHub 用户名 |
| `class_name` | `2024-1` |
| `major` | `软件工程` |
| `score` | `90` |
| `joined_at` | `2025-10-01 09:00:00` |

### 2. 一条语句录三个人

三个人是一起报的名，要求**用一条 `INSERT`** 写进去，不要拆成三条。

| student_id | name | class_name | major | score | joined_at |
| --- | --- | --- | --- | ---: | --- |
| `20239002` | 张同学 | `2023-1` | 计算机科学与技术 | 77 | `2025-10-02 10:00:00` |
| `20239003` | 李同学 | `2023-2` | 软件工程 | 82 | `2025-10-02 11:00:00` |
| `20239004` | 王同学 | `2024-1` | 数据科学与大数据技术 | 68 | `2025-10-02 12:00:00` |

### 3. 改一个人的分数

学号 `20230003` 补交了材料，复核之后分数改成 `80`。改一条记录要带 `WHERE`，而且用**学号**定位。

### 4. 删一条记录

学号 `20230008` 退社了，这条记录要删掉。这是硬删除，软删除在第 5 部分才出现。同样用学号定位，带 `WHERE`。

> **要求**
>
> - 四条语句按顺序写在 `part1/01_dml.sql`。
> - 第二条必须是一条 `INSERT`，不能拆成三条。
> - 做完后 `members` 一共 17 行，`20230003` 的 `score` 是 `80.00`，`20230008` 不存在。
> - 评测库的自增 `id` 和本地不一样；第 3、4 条必须用 `student_id` 定位，不能写 `WHERE id = 3`。
> - 四条按顺序执行；任何一条报错，后面的不会执行，四项都会没分。能执行但结果写错，才只扣那一项。

**提示**
- 一条 `INSERT` 可以带多组 `VALUES`，逗号隔开：`INSERT INTO t (a, b) VALUES (1, 2), (3, 4), (5, 6);`
- 批量插入时，列名和每组 `VALUES` 的个数要一致，否则报 1136。
- `name` 是 `VARCHAR(32)`；GitHub 用户名超过 32 个字符时先联系老师，不要自己截断。
- 字符串和日期都用单引号；`score` 写 `90` 或 `90.00` 都可以。

## 任务 2：五条查询

一个文件一条 `SELECT`，不要 `SELECT *`。列名要和下面写的一模一样，评测比列名。

| 文件 | 查什么 | 输出列 | 排序 / 截断 |
| --- | --- | --- | --- |
| `02_q1.sql` | 85 分以上的人 | `name`、`score` | `score DESC, student_id ASC`，前 5 条 |
| `03_q2.sql` | 姓张的同学 | `name`、`student_id` | `student_id ASC` |
| `04_q3.sql` | 分数最高的三位 | `name`、`score` | `score DESC, student_id ASC`，前 3 条 |
| `05_q4.sql` | 专业是 `计算机科学与技术` 的人数 | `cnt` | 只有一行 |
| `06_q5.sql` | 每个专业各多少人 | `major`、`cnt` | `cnt DESC, major ASC` |

> **要求**
>
> - 每条查询只写一条 `SELECT`，不要加 `USE`、`SET`、`SHOW`。
> - 列名按上表写；第 4 条的计数列必须叫 `cnt`，写成 `COUNT(*) AS cnt`。
> - 第 1、3 条必须写 `ORDER BY score DESC, student_id ASC`；第 1 条再 `LIMIT 5`，第 3 条再 `LIMIT 3`。

**提示**

讲义没讲的写法先看这里：

| 写法 | 作用 |
| --- | --- |
| `LIKE '张%'` | 前缀匹配，`%` 代表任意字符 |
| `ORDER BY score DESC, student_id ASC` | 先按分数降序，再按学号升序 |
| `LIMIT 5` | 只取前 5 条 |
| `COUNT(*) AS cnt` | 统计行数，并把结果列命名为 `cnt` |
| `GROUP BY major` | 按专业分组 |

- 本地这份数据上，85 分以上一共 7 人。第 2、3 名同为 92 分，第 5、6 名同为 88 分，`LIMIT 5` 正好切在两个 88 分之间。只按 `score` 排序时，第 5 名取到谁由数据库决定；加上 `student_id` 才能固定顺序。
- 姓张用前缀匹配：`LIKE '张%'`。`LIKE '%张'` 是“以张结尾”，不是这个意思。
- 第 4 条只统计一个专业，用 `WHERE major = '计算机科学与技术'`，不要 `GROUP BY`。
- 第 5 条用 `GROUP BY major`；人数相同的专业按 `major` 升序，排序才稳定。
- 评测用的是另一份数据：表结构和规则相同，学号、人名、分数不同。查询不要写死某一行的结果。

## 评测

在仓库根目录运行：

```powershell
python grader/run.py --part 1 --user <你的 GitHub 用户名>
```

看到分数表里 `第 1 部分 ...` 一行是 `35 / 35`，这一部分就通过了。有 ❌ 的项，按“说明”列改；DML 的四条按顺序执行，查询逐行比对列名、行和顺序。

环境配置（Python、`MYSQL_PASSWORD`）见[环境搭建](../docs/00-环境搭建.md)。最终分数以 PR 的 Summary 为准。

## 提交

```text
part1/01_dml.sql   四条 DML，按顺序
part1/02_q1.sql    一条 SELECT
part1/03_q2.sql
part1/04_q3.sql
part1/05_q4.sql
part1/06_q5.sql
```

模板在 `homework/templates/part1/`，文件名不要改。提交步骤见[提交与评测](../docs/01-提交与评测.md)。

## 评分

| 项目 | 分值 |
| --- | ---: |
| 新增一条 | 5 |
| 批量新增三条 | 5 |
| 修改一条 | 5 |
| 删除一条 | 5 |
| 五条查询 | 3 × 5 |

## 重置本部分

第 1 部分的 DML 会改 `hw_clean`。想从头再跑，先在仓库根目录进入 `hw_clean`：

```powershell
mysql -u root -p --default-character-set=utf8mb4 hw_clean
```

然后在 `mysql>` 提示符下依次执行：

```text
source db/00_clean.sql
source submissions/<你的用户名>/part1/01_dml.sql
```

五条查询是只读的，不用重置；单独 `source` 对应文件即可。
