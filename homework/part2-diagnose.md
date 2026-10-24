# 第 2 部分 看得懂：脏数据诊断（20 分）

## 1. 数据与准备

- 表：`hw_legacy.members`，28 行，全列可空、没有任何约束，里面有 8 类脏数据。
- 第一次（练习库还没建）：

  ```powershell
  mysql -u root -p --default-character-set=utf8mb4 -e "source db/99_reset.sql"
  ```

- 每次重来（只重置这张表）：

  ```powershell
  mysql -u root -p --default-character-set=utf8mb4 -e "source db/01_legacy.sql" hw_legacy
  ```

## 2. 要做什么

六个文件，一个文件一条 `SELECT`，只读，不改数据。

| 文件 | 查什么 | 输出列 | 排序 |
| --- | --- | --- | --- |
| `q1_dup.sql` | 重复的学号，只列出现次数 > 1 的 | `student_id`, `cnt` | `cnt DESC, student_id ASC` |
| `q2_name.sql` | 姓名为空、全是空格、或者前后有空格 | `id`, `name`, `len` | `id ASC` |
| `q3_score.sql` | 分数小于 0 或大于 100 | `id`, `score` | `id ASC` |
| `q4_date.sql` | 报名时间不是 `YYYY-MM-DD HH:MM:SS` | `id`, `joined_at` | `id ASC` |
| `q5_whitelist.sql` | 专业或班级不在白名单里 | `id`, `major`, `class_name` | `id ASC` |
| `q6_sid.sql` | 学号不是 8 位数字 | `id`, `student_id` | `id ASC` |

约定：

- `cnt` 写 `COUNT(*) AS cnt`；
- `len` 是 `CHAR_LENGTH(name)` 的别名，写 `CHAR_LENGTH(name) AS len`；
- 空学号不算重复：`NULL`、空串、全空格先排除，再找重复；
- 判断学号是不是 8 位数字之前，先 `TRIM`；
- 白名单：专业是 `计算机科学与技术`、`软件工程`、`数据科学与大数据技术`；
  班级形如 `2023-1`，四位年份、短横线、一位班号。

## 3. 交什么

```text
part2/q1_dup.sql   q2_name.sql   q3_score.sql
part2/q4_date.sql  q5_whitelist.sql  q6_sid.sql
```

模板在 `homework/templates/part2/`。

## 4. 怎么评测

| 项目 | 分值 |
| --- | ---: |
| 六条查询 | 3 × 6 |
| 六条全对 | 2 |

- 比对列名、行、顺序，三项全对才给分。
- 文件里出现 `UPDATE`、`DELETE`、`INSERT` 一律 0 分。
- 评测用另一份数据，脏数据的种类和位置相同，人名、分数不同。
- 本地对答案：跑完自己的查询，再跑 `grader/solutions/part2_q1.sql` 到 `part2_q6.sql`，结果一致就是对的。
- 提交后看 PR 的 Summary。
