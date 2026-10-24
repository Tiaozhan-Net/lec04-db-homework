# 数据库课后作业

一次作业，一个业务对象：`members`（社团报名表）。

5 个必做部分 + 1 个加分部分，全部通过 GitHub PR 提交，自动评测。
必做合计 100 分，**50 分及格**；做完第 1、2 部分就已经及格。

## 三步开始

1. **装 MySQL**：看 [docs/00-环境搭建.md](docs/00-环境搭建.md)。装一次就行，不用 Docker。
2. **读题**：[homework/README.md](homework/README.md)，里面是分值表和整体要求。
3. **交作业**：[docs/01-提交与评测.md](docs/01-提交与评测.md)，fork、建分支、复制模板、写 SQL、发 PR。

## 题目

| 文件 | 主题 | 分值 |
| --- | --- | ---: |
| [homework/part1-crud.md](homework/part1-crud.md) | 会用：增删改查与基础查询 | 35 |
| [homework/part2-diagnose.md](homework/part2-diagnose.md) | 看得懂：脏数据诊断 | 20 |
| [homework/part3-clean.md](homework/part3-clean.md) | 洗得干净：清洗（硬删除） | 25 |
| [homework/part4-constraints.md](homework/part4-constraints.md) | 拦得住：加约束与预测报错 | 10 |
| [homework/part5-softdelete.md](homework/part5-softdelete.md) | 删得回来：软删除迁移 | 10 |
| [homework/bonus-index.md](homework/bonus-index.md) | 看得见：索引与执行计划 | +10 |

## 提交目录

```text
submissions/<你的 GitHub 用户名>/
├─ part1/  01_dml.sql  02_q1.sql  03_q2.sql  04_q3.sql  05_q4.sql  06_q5.sql
├─ part2/  q1_dup.sql  q2_name.sql  q3_score.sql  q4_date.sql  q5_whitelist.sql  q6_sid.sql
├─ part3/  clean.sql
├─ part4/  constraints.sql  errors.sql
├─ part5/  05a_softdelete.sql  05b_migrate.sql  05c_reinsert.sql
└─ bonus/  b1_functional_key.sql  b2_indexes.sql
```

只交 `.sql`，不写文字说明。没做的部分可以不建目录，那部分就是 0 分，不会影响其他部分。

## 数据

| 文件 | 用在 | 本地库名 |
| --- | --- | --- |
| `db/00_clean.sql` | 第 1 部分 | `hw_clean` |
| `db/01_legacy.sql` | 第 2–5 部分 | `hw_legacy` |
| `db/02_big.sql` | 加分部分 | `hw_bonus` |

一键重置前两个库：见 [docs/00-环境搭建.md](docs/00-环境搭建.md)。

评测用的是另一份数据，字段和规则完全一样，只是人名、分数、学号不同。
**不要把某一行写死在 SQL 里**，评测库里没有你本地看到的那一行。

## 本地怎么检查

判分在 PR 上跑，**本地不用装 Docker、也不用装 Python**。
交上去 1–2 分钟就能在 PR 里看到分数表，每项都写清了「应为多少、实际多少」。

本地只想对答案的话：

- 第 1、2 部分：跑完自己的查询，再跑一遍 `grader/solutions/` 里对应的参考查询，两个结果对一眼；
- 第 3 部分：`db/99_check_part3.sql`，逐行对比，全对就没有输出；
- 第 4 部分：`db/99_check_part4.sql`，看 7 行结构检查是不是全 `OK`。

用法见 [docs/00-环境搭建.md](docs/00-环境搭建.md) 第 4 节。

## 交完在哪看分数

PR 页面的 **Checks → autograde → Summary**。每次 push 都会重跑，分数以最后一次为准。
