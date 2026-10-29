# 面试演练 Skill

给通用 Agent 用的跨行业模拟面试 Skill。Agent 在当前对话里对齐岗位、入戏追问、按原话复盘，并只练最弱的一项。

## 让 Agent 安装

把下面这段交给 Agent，它会自己装好，不需要再开发一套面试 Agent：

```text
安装 https://github.com/cadetnicolas/interview_practice 里的面试演练 Skill。
执行：
curl -fsSL https://raw.githubusercontent.com/cadetnicolas/interview_practice/main/scripts/install.sh | bash
装好后告诉我新开一轮对话，并说「模拟面试」。
```

已经克隆本仓库时，在仓库根目录执行：

```bash
bash scripts/install.sh
```

安装位置是 `~/.cursor/skills/interview-practice`。脚本没有确认提示。本机已有同名面试 Skill 时会替换为指向本仓库的链接；同路径上如果是别的 Skill，脚本会停下来，不会覆盖。

备选安装方式需要 Node.js 22.20 或更高版本：

```bash
npx skills add https://github.com/cadetnicolas/interview_practice --skill interview-practice -g -a cursor -y
```

在 Cursor 里也可以从 GitHub 导入这个仓库。仓库根目录的 `.cursor-plugin/marketplace.json` 会提供 `interview-practice` 插件。

## 使用

新开一轮对话，说「模拟面试」或「帮我准备面试」。需要准备行业、岗位、职级、轮次、简历和 JD。

## 仓库结构

- `plugins/interview-practice/skills/interview-practice/`：Skill 正文和行业包
- `scripts/install.sh`：给 Agent 执行的安装脚本
- `.cursor-plugin/marketplace.json`：Cursor 从 GitHub 导入时读取的插件清单
