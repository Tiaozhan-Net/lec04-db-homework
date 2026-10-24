# 第 4 部分：拦得住——加约束与预测报错（10 分）

第 3 部分把存量数据洗干净了，但数据库本身还不知道什么叫干净。明天有人手动插一条 7 位学号的记录、把分数写成 101、把专业写成「计算机」，数据库照样收下。等你发现的时候，又是第 3 部分重来一遍。

这一部分做两件事：把规则写进表结构，让脏数据根本插不进去；再写四条“必定被拦下”的语句，验证这些规则真的在工作。

> **开始之前**
>
> - 读：第 3 部分的终态；`ALTER TABLE`、`MODIFY COLUMN`、`NOT NULL`、`UNIQUE`、`CHECK`；[常见问题](../docs/02-常见问题.md) 里的错误码。
> - 数据：`hw_legacy.members`，第 3 部分洗完之后的表。
> - 如果第 3 部分刚做完，表已经洗完，直接写 `constraints.sql`；下面的准备命令是给“从零重做”用的，不要重复跑。
> - 从零重做时，在仓库根目录依次执行（`<你的用户名>` 换成自己的）：
>   ```powershell
>   mysql -u root -p --default-character-set=utf8mb4 -e "source db/01_legacy.sql" hw_legacy
>   mysql -u root -p --default-character-set=utf8mb4 -e "source submissions/<你的用户名>/part3/clean.sql" hw_legacy
>   ```
>   第 3 部分还没跑通也能做这一部分：评测用的是参考解洗好的数据。本地想测结构，先把自己第 3 部分的 `clean.sql` 跑通。
> - 要重做第 4 部分，按末尾「重置本部分」。
>
> 提交的 SQL 里不要写 `USE` 或 `CREATE DATABASE`。

## 任务 1：`constraints.sql`

### 六列不能为空

`student_id`、`name`、`class_name`、`major`、`score`、`joined_at` 六列都要加 `NOT NULL`。学号已经保证有值了，但其他列还没有 `NOT NULL` 约束；加上之后，再有人漏填就会被拦下。

### 学号唯一

在 `student_id` 上建**单列**唯一索引，索引名用 `uk_student_id`。第 5 部分要按这个名字把它换成“活跃才唯一”，名字对不上会卡住。不要建成 `(student_id, name)` 这种复合唯一索引；它不能保证学号唯一。

### 类型收敛

| 列 | 现在 | 改成 |
| --- | --- | --- |
| `joined_at` | `VARCHAR(32)` | `DATETIME(3)` |
| `score` | `DECIMAL(5,2)` 可空 | `DECIMAL(5,2)` 非空 |

### 五个 CHECK

| 规则 | 写法 |
| --- | --- |
| 姓名 `TRIM` 后不能为空 | `CHAR_LENGTH(TRIM(name)) > 0` |
| 分数在 0 到 100 之间 | `score BETWEEN 0 AND 100` |
| 学号是 8 位数字 | `student_id REGEXP '^[0-9]{8}$'` |
| 专业在白名单 | `major IN ('计算机科学与技术', '软件工程', '数据科学与大数据技术')` |
| 班级格式 | `class_name REGEXP '^[0-9]{4}-[1-9]$'` |

> **要求**
>
> - 六列 `NOT NULL`。
> - `student_id` 单列唯一索引，名字 `uk_student_id`。
> - `joined_at` 改成 `DATETIME(3)`，`score` 是 `DECIMAL(5,2)` 且非空。
> - 五个 `CHECK` 全部加上；约束名建议用 `chk_members_*`，报 3819 时好认。
> - 结构和行为都要对：建了 `CHECK`、脏数据却插得进去，那一分不给。

**提示**
- 改列定义用 `MODIFY COLUMN`。MySQL 没有 `ALTER COLUMN ... SET NOT NULL` 这种写法。
- 一个 `ALTER TABLE` 里可以用逗号连写多个 `MODIFY COLUMN`；也可以拆成几条。
- `ALTER TABLE ... ADD CONSTRAINT 约束名 CHECK (...)` 加 `CHECK`。约束名自己取，建议统一前缀。
- `CHAR_LENGTH`、`TRIM`、`REGEXP` 的用法见第 2 部分的函数表。
- 加约束不能重复执行；每次重来都从「开始之前」的两条命令开始。

## 任务 2：`errors.sql`

四条语句，每条故意写错一处，都应该被数据库拦下来。这一题反过来考：不是看报错，而是先预测会报什么错。

在每条语句**正上方**写一行注释，声明期望的错误码：

```sql
-- @error 1062
INSERT INTO ...
```

| 语句 | 期望 | 考什么 |
| --- | --- | --- |
| 插入一个已经存在的学号 | `1062` | 唯一索引 |
| 插入时把 `name` 明确写成 `NULL` | `1048` | 列不能为空 |
| 插入时故意不写 `name` 这一列 | `1364` | 列没有默认值 |
| 插入 `score = 101` | `3819` | `CHECK` 被违反 |

> **要求**
>
> - 四条语句都放在 `part4/errors.sql`，每条上方写 `-- @error 错误码`。
> - 每条只错一处，其余字段都给合法值，否则会先撞上别的错误。
> - 1062 那条的学号从表里取，不要写死；本地抄一个学号到评测库不一定有。
> - 1048 和 1364 要区分开：`NULL` 是“给了空值”，1364 是“根本没给这一列”。

**提示**
- `1062` 那条可以用 `INSERT ... SELECT` 从 `members` 里取一个学号：
  ```sql
  -- @error 1062
  INSERT INTO members (student_id, name, class_name, major, score, joined_at)
  SELECT student_id, '测试甲', '2023-1', '软件工程', 60.00, '2025-12-01 00:00:00'
  FROM members LIMIT 1;
  ```
- `1048` 那条显式写 `name = NULL`；`1364` 那条在列清单里直接不写 `name`。
- `3819` 是 `CHECK` 约束的通用错误码，具体是哪条规则要看错误信息里的约束名。
- 1062 那条如果漏写 `joined_at`，会先报 1364；四条都要保证“只错一处”。
- 1364 只在严格模式下报；MySQL 8.0 默认是严格模式。

## 评测

在仓库根目录运行：

```powershell
python grader/run.py --part 4 --user <你的 GitHub 用户名>
```

看到分数表里 `第 4 部分 ...` 一行是 `10 / 10`，这一部分就通过了。评测跑在参考解洗好的数据上，所以第 3 部分没写完也能做这一部分；最终分数以 PR Summary 为准。

## 提交

```text
part4/constraints.sql
part4/errors.sql
```

模板在 `homework/templates/part4/`。提交步骤见[提交与评测](../docs/01-提交与评测.md)。

## 评分

| 项目 | 分值 |
| --- | ---: |
| 六列 `NOT NULL` | 1 |
| 学号唯一索引 | 1 |
| `joined_at` 是 `DATETIME(3)` | 1 |
| `score` 是 `DECIMAL(5,2)` | 1 |
| 姓名和分数的 `CHECK` 真的拦得住 | 1 |
| 学号、专业、班级的 `CHECK` 真的拦得住 | 1 |
| 四个错误码 | 1 × 4 |

## 重置本部分

第 4 部分的 `ALTER TABLE` 不能重复执行。想重跑 `constraints.sql`，先在仓库根目录进入 `hw_legacy`：

```powershell
mysql -u root -p --default-character-set=utf8mb4 hw_legacy
```

然后在 `mysql>` 提示符下依次执行：

```text
source db/01_legacy.sql
source submissions/<你的用户名>/part3/clean.sql
source submissions/<你的用户名>/part4/constraints.sql
```

`errors.sql` 里的四条语句应该全部失败；如果有哪条插进去了，按上面三条重置。
