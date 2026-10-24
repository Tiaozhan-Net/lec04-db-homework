# 数据库课后作业

一次作业，一个业务对象：`members`（社团报名表）。
5 个必做部分 + 1 个加分部分，全部用 GitHub PR 交，自动评测。

## 分值

| Part | 主题 | 交什么 | 分值 | 建议时间 |
| --- | --- | --- | ---: | ---: |
| [1](part1-crud.md) | 会用：CRUD 与基础查询 | 4 条 DML + 5 条查询 | 35 | 80 min |
| [2](part2-diagnose.md) | 看得懂：脏数据诊断 | 6 条只读查询 | 20 | 20 min |
| [3](part3-clean.md) | 洗得干净：清洗 | 1 个清洗脚本 | 25 | 30 min |
| [4](part4-constraints.md) | 拦得住：加约束与预测报错 | DDL + 4 条必错语句 | 10 | 25 min |
| [5](part5-softdelete.md) | 删得回来：软删除迁移 | 3 个脚本 | 10 | 20 min |
| [B](bonus-index.md) | 看得见：索引与执行计划 | 索引脚本 + 1 条查询 | +10 | 40 min |

必做合计 100 分，**50 分及格**。

- 做完第 1 + 2 部分就有 55 分，已经及格，还留 5 分容错；
- 第 3–5 部分决定分数高低；
- 加分 10 分单独统计，不加也不影响及格。

每个部分独立判分：第 3 部分写崩了，第 4、5 部分照样能拿分。

## 交到哪

```text
submissions/<你的 GitHub 用户名>/
├─ part1/  01_dml.sql  02_q1.sql  03_q2.sql  04_q3.sql  05_q4.sql  06_q5.sql
├─ part2/  q1_dup.sql  q2_name.sql  q3_score.sql  q4_date.sql  q5_whitelist.sql  q6_sid.sql
├─ part3/  clean.sql
├─ part4/  constraints.sql  errors.sql
├─ part5/  05a_softdelete.sql  05b_migrate.sql  05c_reinsert.sql
└─ bonus/  b1_functional_key.sql  b2_indexes.sql
```

`homework/templates/` 里有同名骨架，复制过去再写。只交 `.sql`，不写文字说明。
没做的部分可以不建目录，那部分就是 0 分。

## 数据

| 文件 | 内容 | 本地库名 |
| --- | --- | --- |
| `db/00_clean.sql` | 规范数据，14 行，有约束 | `hw_clean` |
| `db/01_legacy.sql` | 遗留脏表，28 行，没有任何约束 | `hw_legacy` |
| `db/02_big.sql` | 20 万行，加分题用 | `hw_bonus` |

评测用的是**另一份数据**：字段、规则、脏数据的种类完全一样，只是人名、学号、分数不同。
所以不要把某一行的结果写死到 SQL 里，评测库里没有那一行。

## 本地跑评测

```powershell
docker compose up -d mysql
docker compose run --rm grader python grader/run.py --part 3
```

`--part` 可以写 `1` `2` `3` `4` `5` `bonus` `all`，也可以 `1,2`。
第一次跑要等 MySQL 起来（`docker compose ps` 看到 healthy 就行）。

## 三条硬规则

1. 只改 `submissions/<你的用户名>/` 下面的文件，改别人的或者改题目的文件，PR 会被拦下；
2. 不要 `DROP TABLE`、不要 `TRUNCATE`、不要建新表再改名 —— 第 3 部分要原地清洗；
3. 一个 PR 只交一个人的作业。
