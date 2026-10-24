# 第 4 部分 拦得住：加约束与预测报错（10 分）

起点：第 3 部分洗完的表（已经干净，可以直接加约束）。

交两个文件：

```text
part4/constraints.sql    DDL
part4/errors.sql         4 条必定被拦下的语句
```

---

## 一、`constraints.sql`

### 1. 六列都不能为空

`student_id`、`name`、`class_name`、`major`、`score`、`joined_at`

### 2. 学号唯一

`student_id` 上建唯一索引，**索引名用 `uk_student_id`**（第 5 部分要按这个名字改它）。

### 3. 类型收敛

| 列 | 现在 | 改成 |
| --- | --- | --- |
| `joined_at` | `VARCHAR(32)` | `DATETIME(3)` |
| `score` | `DECIMAL(5,2)` 可空 | `DECIMAL(5,2)` 非空 |

> 提示：MySQL 没有 `ALTER COLUMN ... SET NOT NULL` 这种写法，要用 `MODIFY COLUMN`。

### 4. 五个 CHECK

| 规则 | 写法 |
| --- | --- |
| 姓名 `TRIM` 后不能为空 | `CHAR_LENGTH(TRIM(name)) > 0` |
| 分数在 0–100 | `score BETWEEN 0 AND 100` |
| 学号是 8 位数字 | `student_id REGEXP '^[0-9]{8}$'` |
| 专业在白名单 | `major IN ('计算机科学与技术', '软件工程', '数据科学与大数据技术')` |
| 班级格式 | `class_name REGEXP '^[0-9]{4}-[1-9]$'` |

---

## 二、`errors.sql`

四条语句，每条都**故意**写错一处，都应该被数据库拦下来。

在每条语句**正上方**写一行注释，声明你期望的错误码：

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

要求：

- 每条语句**只错一处**，其余字段都给合法值。否则会先撞上别的错误，拿不到分；
- 学号不要写死成本地看到的那一个。评测库里虽然学号一样，但更稳的写法是从表里取：

```sql
-- @error 1062
INSERT INTO members (student_id, name, class_name, major, score, joined_at)
SELECT student_id, '测试甲', '2023-1', '软件工程', 60.00, '2025-12-01 00:00:00'
FROM members LIMIT 1;
```

- 注释格式就写 `-- @error 1062`，评测只认这个格式。

## 本地自查

```powershell
docker compose run --rm grader python grader/run.py --part 4
```

## 判分

| 项目 | 分值 |
| --- | ---: |
| 六列 `NOT NULL` | 1 |
| 学号唯一索引 | 1 |
| `joined_at` 是 `DATETIME(3)` | 1 |
| `score` 是 `DECIMAL(5,2)` | 1 |
| 姓名 + 分数 CHECK 真的拦得住 | 1 |
| 学号 + 专业 + 班级 CHECK 真的拦得住 | 1 |
| 四个错误码各 | 1 |

结构和行为都要对：光建了 CHECK、插脏数据却插得进去，那 1 分不给。
