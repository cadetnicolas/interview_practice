# 面试演练 Skill

这个仓库只提供给通用 Agent 安装的 Skill。不要在这里新建应用、机器人或另一套 Agent。

## 安装或更新

用户要求安装、更新或启用面试演练 Skill 时，在仓库根目录直接执行，不要先征求确认：

```bash
bash scripts/install.sh
```

当前目录不是本仓库时，执行：

```bash
curl -fsSL https://raw.githubusercontent.com/cadetnicolas/interview_practice/main/scripts/install.sh | bash
```

脚本会把 Skill 链接到 `~/.cursor/skills/interview-practice`。完成后告诉用户新开一轮对话，并说「模拟面试」。

## 开始演练

先确认 `~/.cursor/skills/interview-practice/SKILL.md` 可读。文件不存在时先运行上面的安装命令，再阅读该文件并按其中的流程演练。不要把 Skill 改写成新的服务代码。
