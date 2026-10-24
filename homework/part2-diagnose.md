# 第 2 部分 看得懂：脏数据诊断（20 分）

数据：`hw_legacy`（28 行，全列可空，没有任何约束）。

交 6 个文件，**一个文件一条 `SELECT`**，只读，不许改数据：

```text
part2/q1_dup.sql        q2_name.sql        q3_score.sql
part2/q4_date.sql       q5_whitelist.sql   q6_sid.sql
```

| 文件 | 查什么 | 输出列 | 排序 |
| --- | --- | --- | --- |
| `q1_dup.sql` | 重复的学号，只列出现次数 > 1 的 | `student_id`, `cnt` | `cnt DESC, student_id ASC` |
| `q2_name.sql` | 姓名为空、全是空格、或者前后有空格 | `id`, `name`, `len` | `id ASC` |
| `q3_score.sql` | 分数小于 0 或大于 100 | `id`, `score` | `id ASC` |
| `q4_date.sql` | 报名时间不是 `YYYY-MM-DD HH:MM:SS` | `id`, `joined_at` | `id ASC` |
| `q5_whitelist.sql` | 专业或班级不在白名单里 | `id`, `major`, `class_name` | `id ASC` |
| `q6_sid.sql` | 学号不是 8 位数字 | `id`, `student_id` | `id ASC` |

## 几个约定

- `cnt` 用 `COUNT(*) AS cnt`；
- `len` 是 `CHAR_LENGTH(name)` 的别名，写 `CHAR_LENGTH(name) AS len`；
- **空学号不算重复**：`NULL`、空串、全是空格的学号先排除，再找重复；
- 判断学号是不是 8 位数字之前，先 `TRIM`（前后有空格不算错，见第 3 部分）；
- 白名单：
  - 专业：`计算机科学与技术`、`软件工程`、`数据科学与大数据技术`
  - 班级：形如 `2023-1`，四位年份 + 短横线 + 一位班号。

## 本地自查

判分在 PR 上跑，Summary 会写清「应为几行、第几行不对」，比本地看得还细。

想先在本地对一遍：跑完自己的查询，再跑一遍 `grader/solutions/part2_q1.sql` … `part2_q6.sql`，
两个结果窗口对一眼。

## 判分

- 6 条各 3 分，共 18 分；
- 6 条全对再加 2 分，共 20 分；
- 比对列名、行、顺序，三种都对才给分。

只查不改。文件里出现 `UPDATE` / `DELETE` / `INSERT` 一律 0 分。
