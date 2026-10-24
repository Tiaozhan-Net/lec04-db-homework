# 数据库课后作业

这份作业围绕一张社团报名表 `members` 展开。你从最日常的增删改查开始，逐步处理一份从 Excel 导进来的脏数据：先诊断问题，再清洗、加约束、做软删除，最后用索引让查询变快。

共 5 个必做部分和 1 个加分部分，通过 GitHub PR 提交，自动评测。必做合计 100 分，**50 分及格**；加分 10 分单独统计，不计入 100 分。

## 实验地图

| 部分 | 主题 | 数据 | 分值 | 建议时间 |
| --- | --- | --- | ---: | ---: |
| [1](homework/part1-crud.md) | 会用：增删改查 | `hw_clean.members`，14 行 | 35 | 80 min |
| [2](homework/part2-diagnose.md) | 看得懂：脏数据诊断 | `hw_legacy.members`，28 行 | 20 | 20 min |
| [3](homework/part3-clean.md) | 洗得干净：清洗 | `hw_legacy.members`，28 → 14 行 | 25 | 45 min |
| [4](homework/part4-constraints.md) | 拦得住：加约束与预测报错 | 第 3 部分洗完的表 | 10 | 25 min |
| [5](homework/part5-softdelete.md) | 删得回来：软删除迁移 | 第 4 部分做完的表 | 10 | 20 min |
| [B](homework/bonus-index.md) | 看得见：索引与执行计划 | `hw_bonus.members`，20 万行 | +10 | 40 min |

第 1、2 部分共 55 分，做完这两部分就能及格；第 3–5 部分决定分数高低。每个部分独立判分，前一部分没写完，后面照样能拿分。

## 开始

1. Fork 并 clone 仓库，按[提交与评测](docs/01-提交与评测.md) 的第 1–3 步建好分支和 `submissions/<你的用户名>/` 目录。
2. 读[环境搭建](docs/00-环境搭建.md)，确认 MySQL 版本，装好 Python 和评测依赖，建好练习库。
3. 从[第 1 部分](homework/part1-crud.md)开始，按顺序做。
4. 写完后按[提交与评测](docs/01-提交与评测.md) 提交 PR。

每个部分末尾都要在本地跑一次评测。以第 1 部分为例：

```powershell
python grader/run.py --part 1 --user <你的 GitHub 用户名>
```

看到分数表里 `第 1 部分 ...` 一行是 `35 / 35`，这一部分就通过了。最终分数以 PR 的 Summary 为准。

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

模板在 `homework/templates/`，文件名不要改。没做的部分不用建目录，那部分是 0 分。

## 四条规则

1. 只改 `submissions/<你的 GitHub 用户名>/` 下的文件。
2. 不写 `DROP TABLE`、`DROP DATABASE`、`TRUNCATE`，不建新表再改名。
3. 提交的 `.sql` 里不要写 `USE` 或 `CREATE DATABASE`；评测会在自己的库里执行。
4. 一个 PR 只提交一个人的作业。

## 遇到问题

先看[常见问题](docs/02-常见问题.md)。报错码、中文乱码、命令行用法、评测没触发都在里面。
