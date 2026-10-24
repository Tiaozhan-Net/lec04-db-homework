# 评测脚本

学生不用读这个目录。

根目录的 `docker-compose.yml` 和这个目录下的 `Dockerfile` 用来复现 CI 的 MySQL + 评测环境。

```text
grader/
├─ run.py            入口：编排、汇总、报告
├─ db.py             连接、会话口径、脚本执行、结果规范化
├─ sqltext.py        去注释、切语句
├─ checks/part1..5.py, bonus.py
├─ fixtures/         评测用的数据（和 db/ 下的练习数据不同）
└─ solutions/        参考解
```

## 本地跑

```powershell
docker compose run --rm grader python grader/run.py --part 3 --user 你的用户名
```

或者本机（需要 Python 3.10+）：

```powershell
$env:MYSQL_PASSWORD = "你的 root 密码"
pip install -r grader/requirements.txt
python grader/run.py --part 3 --user 你的用户名
```

`--part` 可以是 `1` `2` `3` `4` `5` `bonus` `all`，也可以 `1,2`。

评测会在 MySQL 里建一批 `hw_*` 库，跑完想清掉：

```powershell
mysql -u root -p --default-character-set=utf8mb4 -e "source db/99_cleanup.sql"
```

## 判分结构

| Part | 库 | 起点 | 判什么 |
| --- | --- | --- | --- |
| 1 | `hw_p1_dml` / `hw_p1_q` | `db/00_clean.sql` | 4 条状态断言 + 5 条结果集 |
| 2 | `hw_p2` | `db/01_legacy.sql` + `eval_legacy.sql` | 6 条结果集 |
| 3 | `hw_p3` | 同上 | 终态逐维度比对 |
| 4 | `hw_p4` | eval_legacy + 参考清洗 | 结构 + 6 条行为 + 4 个错误码 |
| 5 | `hw_p5` | 上一行再 + 参考约束 | 结构与行为，每组测试事务回滚 |
| B | `hw_bonus` | `db/02_big.sql`（20 万行） | `EXPLAIN FORMAT=JSON` |

期望值全部由 `solutions/` 当场算出来，不存手工快照，所以改规则只要改参考解。

## 会话口径

`db.connect()` 里固定：

- `sql_mode = ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION`
- `time_zone = '+00:00'`
- 连接字符集 `utf8mb4`，库排序规则 `utf8mb4_0900_ai_ci`（NO PAD，尾部空格有意义）

`STRICT_TRANS_TABLES` 不能少，否则 `1364` 不会报错，Part 4 会误判。
