# 第 1 部分 会用：增删改查（35 分）

## 1. 数据与准备

- 表：`hw_clean.members`，14 行规范数据，已有约束。
- 第一次（练习库还没建）：

  ```powershell
  mysql -u root -p --default-character-set=utf8mb4 -e "source db/99_reset.sql"
  ```

- 每次重来（只重置这张表）：

  ```powershell
  mysql -u root -p --default-character-set=utf8mb4 -e "source db/00_clean.sql" hw_clean
  ```

## 2. 要做什么

### 2.1 四条 DML

写在同一个文件里，按顺序执行。

**1）新增一条**

| 字段 | 值 |
| --- | --- |
| `student_id` | `20239001` |
| `name` | 你的 GitHub 用户名 |
| `class_name` | `2024-1` |
| `major` | `软件工程` |
| `score` | `90` |
| `joined_at` | `2025-10-01 09:00:00` |

**2）用一条语句批量新增三条**

| student_id | name | class_name | major | score | joined_at |
| --- | --- | --- | --- | ---: | --- |
| `20239002` | 张同学 | `2023-1` | 计算机科学与技术 | 77 | `2025-10-02 10:00:00` |
| `20239003` | 李同学 | `2023-2` | 软件工程 | 82 | `2025-10-02 11:00:00` |
| `20239004` | 王同学 | `2024-1` | 数据科学与大数据技术 | 68 | `2025-10-02 12:00:00` |

**3）改一条**

把学号 `20230003` 的分数改成 `80`，必须带 `WHERE`。

**4）删一条**

删除学号 `20230008` 的记录，必须带 `WHERE`。这是硬删除。

做完这一步，表里一共 17 行。

### 2.2 五条查询

一个文件一条 `SELECT`，不要 `SELECT *`，列名与题目一致。

**`02_q1.sql`** 条件 + 排序 + 截断

- 分数 `>= 85` 的同学
- 输出列：`name`, `score`
- 排序：`score DESC, student_id ASC`
- 取前 5 条

**`03_q2.sql`** 前缀匹配

- 姓张的同学（`name` 以「张」开头）
- 输出列：`name`, `student_id`
- 排序：`student_id ASC`

**`04_q3.sql`** 分数最高的 3 位

- 输出列：`name`, `score`
- 排序：`score DESC, student_id ASC`
- 取前 3 条

**`05_q4.sql`** 带条件的计数

- 专业是 `计算机科学与技术` 的人数
- 输出列：`cnt`，只有一行

**`06_q5.sql`** 分组计数

- 每个专业各有多少人
- 输出列：`major`, `cnt`
- 排序：`cnt DESC, major ASC`

## 3. 交什么

```text
part1/01_dml.sql   四条 DML
part1/02_q1.sql    一条 SELECT
part1/03_q2.sql
part1/04_q3.sql
part1/05_q4.sql
part1/06_q5.sql
```

模板在 `homework/templates/part1/`。

## 4. 怎么评测

| 项目 | 分值 |
| --- | ---: |
| 新增一条 | 5 |
| 批量新增三条 | 5 |
| 改一条 | 5 |
| 删一条 | 5 |
| 五条查询 | 3 × 5 |

- DML 看表变成什么样：多了哪几行、谁被改了、谁被删了、一共几行。
- 查询比对列名、行、顺序，三项全对才给分。
- 评测用另一份数据，表结构和规则相同，学号、人名、分数不同，所以不要写死某一行。
- 本地对答案：跑完自己的查询，再跑 `grader/solutions/part1_q1.sql` 到 `part1_q5.sql`，结果一致就是对的。
- 提交后看 PR 的 Summary，说明列会写「应为多少、实际多少」。
