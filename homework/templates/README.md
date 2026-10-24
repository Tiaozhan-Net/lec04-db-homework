# 模板

把需要的目录**整个复制**到 `submissions/<你的 GitHub 用户名>/` 下面：

```powershell
$user = "<你的 GitHub 用户名>"
New-Item -ItemType Directory -Force "submissions/$user"
Copy-Item -Recurse homework/templates/part1 "submissions/$user/"
```

要做多个部分，就把 `part1` 换成 `part2`、`part3`……；也可以一次复制全部：

```powershell
$user = "<你的 GitHub 用户名>"
foreach ($p in "part1","part2","part3","part4","part5","bonus") {
  Copy-Item -Recurse "homework/templates/$p" "submissions/$user/"
}
```

每个文件里只有要求和提示，SQL 要自己写。每部分末尾按题目里的「评测」小节运行评测脚本。
文件名不要改，评测按文件名找。

- 没做的部分不用复制；
- 只交 `.sql`，不要交 README、不要交截图；
- 提交的 SQL 里不要写 `USE` 或 `CREATE DATABASE`。
