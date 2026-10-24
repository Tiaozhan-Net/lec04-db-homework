# 第 5 部分：删得回来——软删除迁移（10 分）

有位同学退社，管理员直接 `DELETE` 了记录。一周后他想回来，同一个学号插不进去——`uk_student_id` 还记着他，虽然那条记录已经不在表里了。

这次要把“删除”改成软删除：记录留着，只是标记成已取消。然后处理随之而来的问题：唯一索引还认不认这个学号。

> **开始之前**
>
> - 读：第 4 部分的终态；`UNIQUE` 索引和 `NULL` 的关系。
> - 数据：`hw_legacy.members`，第 4 部分做完的终态（已清洗、已加约束）。
> - 如果第 4 部分刚做完，表已经加好约束，直接从 `05a` 开始；下面的准备命令是给“从零重做”用的，不要重复执行 `constraints.sql`（会报 1061）。
> - 从零重做时，在仓库根目录依次执行（`<你的用户名>` 换成自己的）：
>   ```powershell
>   mysql -u root -p --default-character-set=utf8mb4 -e "source db/01_legacy.sql" hw_legacy
>   mysql -u root -p --default-character-set=utf8mb4 -e "source submissions/<你的用户名>/part3/clean.sql" hw_legacy
>   mysql -u root -p --default-character-set=utf8mb4 -e "source submissions/<你的用户名>/part4/constraints.sql" hw_legacy
>   ```
>   第 3、4 部分还没跑通也能做这一部分：评测用的是参考解做好的表。本地想测，先把自己前两部分跑通。
> - 要重做第 5 部分，按末尾「重置本部分」。
>
> 提交的 SQL 里不要写 `USE` 或 `CREATE DATABASE`。

## 任务 1：`05a_softdelete.sql` 加列，改成软删除

先给表加一列 `deleted_at DATETIME(3) NULL`，放在 `joined_at` 后面。默认 `NULL` 表示“还在社里”。

然后处理学号 `20230002` 的取消报名。这一次不写 `DELETE`，改成把 `deleted_at` 写成当前时间 `NOW(3)`。

> **要求**
>
> - 加列 `deleted_at DATETIME(3) NULL`。
> - 学号 `20230002` 的那条记录被软删除：`deleted_at` 不是 `NULL`。
> - 做完后表里还是 14 行，其中 13 行活跃。

**提示**
- 加列用 `ALTER TABLE members ADD COLUMN deleted_at DATETIME(3) NULL AFTER joined_at;`。
- 软删除用 `UPDATE`，不要 `DELETE`。
- `NOW(3)` 生成带毫秒的当前时间；用 `NOW()` 也行，但类型是 `DATETIME(3)` 时建议写 `NOW(3)`。
- `ADD COLUMN` 不能重复执行；重来要从「开始之前」第一条命令开始。

## 任务 2：`05b_migrate.sql` 把唯一索引改成“活跃才唯一”

现在的 `uk_student_id` 是“学号唯一”，不管这条记录是否已删除。所以一个人被软删除之后，就再也报不上名。

改成：**同一个学号最多只能有一条活跃记录**，已软删除的记录不占位。索引名还叫 `uk_student_id`。

这里的关键是“唯一索引允许多个 `NULL`”。把活跃标记做成函数键：

```text
活跃行：  (student_id, 1)
已删除行：(student_id, NULL)
```

同一个学号可以有很多条 `(sid, NULL)`，因为唯一索引不把多个 `NULL` 当成重复；但只能有一条 `(sid, 1)`。这样既放过了已删除的记录，又拦住了两条活跃记录。

> **要求**
>
> - 删掉旧的 `uk_student_id`，建成两段的唯一索引：第一段 `student_id`，第二段是“活跃标记”。
> - 索引名仍然用 `uk_student_id`。
> - 四条行为要成立：
>
> | 情况 | 结果 |
> | --- | --- |
> | 两条活跃记录同学号 | 报 `1062` |
> | 一条已软删除 + 一条新的活跃 | 允许 |
> | 把旧的已删除记录恢复成活跃，而新的还在 | 报 `1062` |
> | 两条都已软删除 | 允许 |

**提示**
- `IF(条件, 值1, 值2)` 是 SQL 里的 if-else：条件为真取 `值1`，否则取 `值2`。
- 函数键写法：`UNIQUE KEY uk_student_id (student_id, (IF(deleted_at IS NULL, 1, NULL)))`。注意函数表达式外面有一层括号。
- 等价写法：加一个生成列 `active_flag TINYINT GENERATED ALWAYS AS (IF(deleted_at IS NULL, 1, NULL)) VIRTUAL`，再在 `(student_id, active_flag)` 上建唯一索引。
- 不要直接用 `(student_id, deleted_at)`：活跃行的 `deleted_at` 都是 `NULL`，唯一索引允许多个 `NULL`，所以两条活跃记录会同时存在；它拦不住“一个学号只能有一条活跃记录”。
- 先 `DROP INDEX uk_student_id`，再建新的；两条 `ALTER TABLE` 分开写更清楚。
- 索引建好后，可以手工试上面四种情况；试完用 `ROLLBACK` 或重新准备数据。

## 任务 3：`05c_reinsert.sql` 重新报名

学号 `20230002` 再报一次名，必须成功。其余字段自己给合法值。

> **要求**
>
> - 用 `INSERT` 新增一条 `20230002` 的活跃记录，`deleted_at` 为 `NULL`。
> - 旧的软删除行保留，不要删。
> - 做完后全表 15 行，`20230002` 有 1 条活跃记录、1 条已删除记录。

**提示**
- 旧行已经软删除，新的活跃行不会撞唯一索引；这正是任务 2 要解决的问题。
- 如果 05c 报 1062，说明 05b 的索引没建对，或者旧行还被当成活跃。
- `05c` 只写一条 `INSERT`；不要顺手把旧行删掉。

## 评测

在仓库根目录运行：

```powershell
python grader/run.py --part 5 --user <你的 GitHub 用户名>
```

看到分数表里 `第 5 部分 ...` 一行是 `10 / 10`，这一部分就通过了。评测不比对 SQL 文本，只看结构和行为；每一步都在事务里测，测完回滚。第 3、4 部分没写完也能做这一部分，最终分数以 PR Summary 为准。

## 提交

```text
part5/05a_softdelete.sql
part5/05b_migrate.sql
part5/05c_reinsert.sql
```

模板在 `homework/templates/part5/`。提交步骤见[提交与评测](../docs/01-提交与评测.md)。

## 评分

| 项目 | 分值 |
| --- | ---: |
| `05a` 加了 `deleted_at` 列 | 1 |
| `05a` 指定的那条被软删除 | 1 |
| `05a` 其余行没被动（14 行，13 条活跃） | 1 |
| `05b` 两段唯一索引生效 | 2 |
| `05b` 同号新活跃行能插进去 | 1 |
| `05c` 重新报名成功 | 2 |
| 恢复旧行时报 `1062` | 2 |

## 重置本部分

第 5 部分的 `ADD COLUMN` 和 `ALTER TABLE` 不能重复执行。想从第 4 部分结束的状态重跑，先在仓库根目录进入 `hw_legacy`：

```powershell
mysql -u root -p --default-character-set=utf8mb4 hw_legacy
```

然后在 `mysql>` 提示符下依次执行：

```text
source db/01_legacy.sql
source submissions/<你的用户名>/part3/clean.sql
source submissions/<你的用户名>/part4/constraints.sql
source submissions/<你的用户名>/part5/05a_softdelete.sql
source submissions/<你的用户名>/part5/05b_migrate.sql
source submissions/<你的用户名>/part5/05c_reinsert.sql
```

只想重跑某一步时，从它前面一步开始，不要直接从 `05a` 重跑。
