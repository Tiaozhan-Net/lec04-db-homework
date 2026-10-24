# 上线前必须实测的几件事

仓库是先写出来、没有连库跑过的。下面每一条都要在 `mysql:8.0.36` 上真跑一遍，
有问题就先改这里，再改题面。

## 1. 参考解链路

```bash
mysql -u root -p -e "source db/99_reset.sql"          # hw_clean / hw_legacy
mysql -u root -p hw_legacy -e "source grader/fixtures/eval_legacy.sql"
mysql -u root -p hw_legacy -e "source grader/solutions/part3_clean.sql"
mysql -u root -p hw_legacy -e "source grader/solutions/part4_constraints.sql"
```

期望：清洗后 14 行；第 4 部分是 4 个 `CHECK` 都建得起来。

重点验证：

- `part3_clean.sql` 第 8、9 步的 `DELETE ... JOIN (SELECT ... FROM members)` 在 8.0.36 上不报 1093；
- 清洗后 `student_id` 是 8 位、没有空格（`' 20230020 '` 那一行）；
- `grade 20230002` 那条重复，留下的是 `id = 3`（不是 `id = 5`）；
- `20230003` 的两条同日期，留下的是 `id = 6`。

## 2. `CHECK` 里的 `REGEXP`

```sql
ALTER TABLE members
  ADD CONSTRAINT chk_sid CHECK (student_id REGEXP '^[0-9]{8}$');
```

8.0.16 之后理论上允许。如果不允许，改成：

```sql
CHECK (student_id NOT REGEXP '[^0-9]' AND CHAR_LENGTH(student_id) = 8)
```

改完记得同步 `db/00_clean.sql`、`db/02_big.sql`、`solutions/part4_constraints.sql`、`part4-clean.md` 四处。

## 3. 函数唯一索引

```sql
ALTER TABLE members
  ADD UNIQUE KEY uk_student_id (student_id, (IF(deleted_at IS NULL, 1, NULL)));
```

要验证：两条 `deleted_at IS NULL` 的同学号会 1062；两条都软删除的同学号能共存。

## 4. `EXPLAIN FORMAT=JSON` 的字段

B1 断言用的是 `used_key_parts`，B2 断言用的是 `key` / `filesort`。

```bash
mysql -u root -p hw_bonus -e "EXPLAIN FORMAT=JSON SELECT id,name FROM members WHERE student_id='90000001' AND (IF(deleted_at IS NULL,1,NULL))=1\G"
```

要确认 JSON 里真的有 `used_key_parts`，且 2 段时是 `["student_id", "if(...)"]`。
如果 8.0.36 不带这个字段，B1 改成断言 `key_length` 或改用 `optimizer_trace`。

同时确认 20 万行下四条 B2 查询都走索引、没有 `filesort`，参数值见 `checks/bonus.py`。

## 5. 20 万行生成耗时

```bash
time mysql -u root -p hw_bonus -e "source db/02_big.sql"
```

如果超过 90 秒，把 `db/02_big.sql` 里的 `analyze` 和 CHECK 约束去掉一个数量级再测
（加分部分可以单独用一张没有 CHECK 的表，但要在题面里说清楚）。

## 6. CI

- fork 来的 PR 用的是只读 token，`GITHUB_STEP_SUMMARY` 能写、PR 评论不能写 —— 报告只走 Summary；
- `paths: submissions/**` 意味着只有改提交文件才触发；
- Guard 只认 `submissions/<作者>/...` 三层，确认 `git diff --name-only` 的输出格式。
