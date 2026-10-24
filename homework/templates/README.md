# 模板

把需要的目录**整个复制**到 `submissions/<你的 GitHub 用户名>/` 下面：

```powershell
New-Item -ItemType Directory -Force submissions/你的用户名
Copy-Item -Recurse homework/templates/part1 submissions/你的用户名/
```

每个文件里只有要求和一行自查命令，SQL 要自己写。
文件名不要改，评测按文件名找。

- 没做的部分不用复制；
- 只交 `.sql`，不要交 README、不要交截图。
