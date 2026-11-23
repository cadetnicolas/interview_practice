# 信贷风控 × 智能体 面试教练

这个仓库只有一个 Skill，供通用 Agent 安装。**不要**在这里新建应用、机器人、服务或另一套 Agent。

## 安装或更新

用户要求安装、更新或启用这个 Skill 时，在仓库根目录直接执行，不要先征求确认：

```bash
bash scripts/install.sh
```

当前目录不是本仓库时：

```bash
curl -fsSL https://raw.githubusercontent.com/cadetnicolas/interview_practice/main/scripts/install.sh | bash
```

脚本会把 Skill 链接到 `~/.workbuddy/skills/credit-agent-interview-coach` 和/或 `~/.cursor/skills/credit-agent-interview-coach`。完成后告诉用户新开一轮对话，说「模拟面试」。

## 开始演练

先确认 SKILL.md 可读（仓库根目录，或 `~/.workbuddy/skills/credit-agent-interview-coach/SKILL.md`）。文件不存在时先跑上面的安装命令，再按 `SKILL.md` 的流程演练。

**不要把 Skill 改写成新的服务代码，也不要另建一套面试逻辑。**

## 改动这个 Skill 时

- 主流程改 `SKILL.md`；评分口径改 `references/rubric.md`；追问话术改 `references/protocol.md`。
- 加考点：加到 `references/coverage/` 对应文件，保持「触发 / 好回答 / 假好 / 追问」四行格式。
- **不要往任何地方加固定题目。** 题目一律按 `references/question-design.md` 的方法从他简历现场生成；考点地图只用于评分校准，不许拿来抽题。
- 改维度权重：只改 `references/roles/*.md`，不要动 `rubric.md` 的 1–5 分语义和通过线。
- 改完跑一次 `python3 scripts/interview_log.py append --json '...'` 验证脚本仍可用。
