# 第 4 部分 拦得住：加约束与预测报错（10 分）

## 1. 情景

第 3 部分把存量数据洗干净了，但数据库本身还不知道什么叫干净。

明天有人手动插一条 7 位学号的记录、把分数写成 101、把专业写成「计算机」，数据库照样收下。等你发现的时候，又是第 3 部分重来一遍。

这一部分做两件事：把规则写进表结构，让脏数据根本插不进去；再写四条「必定被拦下」的语句，验证这些规则真的在工作。

## 2. 数据与准备

- 表：`hw_legacy.members`，第 3 部分洗完之后的终态。
- 准备：从脏数据重新洗一遍，两条依次执行（`<你的用户名>` 换成自己的）。

  ```powershell
  mysql -u root -p --default-character-set=utf8mb4 -e "source db/01_legacy.sql" hw_legacy
  mysql -u root -p --default-character-set=utf8mb4 -e "source submissions/<你的用户名>/part3/clean.sql" hw_legacy
  ```

  加约束不能重复执行，每次重来都从这两条开始。第 3 部分还没写完的话，第二条换成 `grader/solutions/part3_clean.sql`。

## 3. 要做什么

### 3.1 `constraints.sql`

#### 六列不能为空

`student_id`、`name`、`class_name`、`major`、`score`、`joined_at`。

学号已经保证有值了，但其他列还没有。`NOT NULL` 一加，以后再有人漏填就会被拦下。

#### 学号唯一

在 `student_id` 上建唯一索引，**索引名用 `uk_student_id`**。

第 5 部分要按这个名字把它换成「活跃才唯一」，名字对不上会卡住。

#### 类型收敛

| 列 | 现在 | 改成 |
| --- | --- | --- |
| `joined_at` | `VARCHAR(32)` | `DATETIME(3)` |
| `score` | `DECIMAL(5,2)` 可空 | `DECIMAL(5,2)` 非空 |

改列定义用 `MODIFY COLUMN`。MySQL 没有 `ALTER COLUMN ... SET NOT NULL` 这种写法。

#### 五个 CHECK

| 规则 | 写法 |
| --- | --- |
| 姓名 `TRIM` 后不能为空 | `CHAR_LENGTH(TRIM(name)) > 0` |
| 分数在 0 到 100 之间 | `score BETWEEN 0 AND 100` |
| 学号是 8 位数字 | `student_id REGEXP '^[0-9]{8}$'` |
| 专业在白名单 | `major IN ('计算机科学与技术', '软件工程', '数据科学与大数据技术')` |
| 班级格式 | `class_name REGEXP '^[0-9]{4}-[1-9]$'` |

### 3.2 `errors.sql`

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
| 插入 `score = 101` | `3819` | CHECK 被违反 |

两条要求：

- 每条语句只错一处，其余字段都给合法值，否则会先撞上别的错误。1062 那条如果漏写 `joined_at`，报的会是 1364。
- 注释格式就写 `-- @error 1062`，评测只认这个格式。

插入重复学号时，学号从表里取，不写死：

```sql
-- @error 1062
INSERT INTO members (student_id, name, class_name, major, score, joined_at)
SELECT student_id, '测试甲', '2023-1', '软件工程', 60.00, '2025-12-01 00:00:00'
FROM members LIMIT 1;
```

## 4. 交什么

```text
part4/constraints.sql
part4/errors.sql
```

模板在 `homework/templates/part4/`。

## 5. 怎么评测

| 项目 | 分值 |
| --- | ---: |
| 六列 `NOT NULL` | 1 |
| 学号唯一索引 | 1 |
| `joined_at` 是 `DATETIME(3)` | 1 |
| `score` 是 `DECIMAL(5,2)` | 1 |
| 姓名和分数的 CHECK 真的拦得住 | 1 |
| 学号、专业、班级的 CHECK 真的拦得住 | 1 |
| 四个错误码 | 1 × 4 |

结构和行为都要对：建了 CHECK、脏数据却插得进去，那一分不给。

评测跑在参考解洗好的数据上，所以第 3 部分没写完也能做这一部分。

本地看结构：

```powershell
mysql -u root -p --default-character-set=utf8mb4 -e "source db/99_check_part4.sql"
```

七行结果全是 `OK` 就说明约束和类型齐了。然后再手动跑一遍 `errors.sql`，看报出来的错误码对不对。提交后看 PR 的 Summary。
