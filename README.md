# 数据库课后作业

一个业务对象：`members`（社团报名表）。
5 个必做部分 + 1 个加分部分，用 GitHub PR 提交，自动评测。

需要 MySQL 8.0，`SELECT VERSION();` 确认。

## 分值

| Part | 主题 | 交什么 | 分值 | 建议时间 |
| --- | --- | --- | ---: | ---: |
| [1](homework/part1-crud.md) | 会用：增删改查 | 4 条 DML + 5 条查询 | 35 | 80 min |
| [2](homework/part2-diagnose.md) | 看得懂：脏数据诊断 | 6 条只读查询 | 20 | 20 min |
| [3](homework/part3-clean.md) | 洗得干净：清洗 | 1 个清洗脚本 | 25 | 30 min |
| [4](homework/part4-constraints.md) | 拦得住：加约束与预测报错 | DDL + 4 条必错语句 | 10 | 25 min |
| [5](homework/part5-softdelete.md) | 删得回来：软删除迁移 | 3 个脚本 | 10 | 20 min |
| [B](homework/bonus-index.md) | 看得见：索引与执行计划 | 索引脚本 + 1 条查询 | +10 | 40 min |

必做合计 100 分，**50 分及格**。

第 1 + 2 部分共 55 分，做完这两部分即及格；第 3–5 部分决定分数高低；
加分 10 分单独统计，不计入 100。

每个部分独立判分，前一部分没写完，后面照样能拿分。

## 开始

1. 建练习库（只做一次）：

   ```powershell
   mysql -u root -p --default-character-set=utf8mb4 -e "source db/99_reset.sql"
   ```

2. 从[第 1 部分](homework/part1-crud.md)开始。每篇开头都写了用哪张表、怎么准备。
3. 写完提交，见[提交与评测](docs/01-提交与评测.md)。

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

## 去哪看分

PR 页面的 **Checks → autograde → Summary**。每次 push 自动重跑，分数以最后一次为准。

## 三条规则

1. 只改 `submissions/<你的用户名>/` 下的文件。
2. 不写 `DROP TABLE`、`TRUNCATE`，不建新表再改名。
3. 一个 PR 只提交一个人的作业。
