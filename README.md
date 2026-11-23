# 信贷风控 × 智能体 面试教练

给通用 Agent 用的面试演练 Skill。深度聚焦**信贷风控**与**智能体（LLM Agent）开发**两条线，以及两者的**交叉复合岗**；其他岗位走「临时岗位包」现场生成。

Agent 在当前对话里对齐岗位、入戏追问、按原话复盘，只练最弱的一项，并把每场成绩记进档案。

## 它和普通「模拟面试」有什么不同

- **有尺子**：每个方向预置岗位包，写清维度、权重、好证据、假好、追问、红旗。评分不是印象分。
- **有通过线**：核心维度都 ≥3 且加权均分 ≥3.5 才算过这一轮，而不是笼统说「不错」。
- **有专业题库**：风控 36 题、智能体 26 题、交叉 13 题，每题带必答 / 加分 / 陷阱三层锚点。
- **有两种压力**：演练（默认，像真面试）和陪练（给结构提示，不给答案）。
- **不编造**：复盘改写时，用户没说过的数字一律标〔待你补充〕，不替他造故事。
- **可追踪**：每场分数、失分题、最弱维度落盘，能看出进步曲线。

## 让 Agent 安装

把下面这段交给 Agent：

```text
安装 https://github.com/cadetnicolas/interview_practice 里的面试教练 Skill。
执行：
curl -fsSL https://raw.githubusercontent.com/cadetnicolas/interview_practice/main/scripts/install.sh | bash
装好后告诉我新开一轮对话，并说「模拟面试」。
```

已经克隆本仓库时，在仓库根目录执行：

```bash
bash scripts/install.sh
```

安装位置（自动检测，已存在的目录才会装）：

- `~/.workbuddy/skills/credit-agent-interview-coach`
- `~/.cursor/skills/credit-agent-interview-coach`

脚本没有交互确认。默认建符号链接（`git pull` 后自动生效）；目标已存在且不是链接时，会先备份成 `.bak.<时间戳>`，不会直接删。想装成实体副本用 `--copy`，指定目录用 `--target workbuddy|cursor|all`。

## 使用

新开一轮对话，说「模拟面试」「面试我」「帮我准备面试」。

**六种形式**，按你说的话自动路由：

| 你说 | 做什么 |
|---|---|
| 模拟面试 / 面试我 | 完整多轮演练（对齐 → 简报 → 演练 → 复盘 → 专项再练） |
| 这题怎么答 / 我说一遍你点评 | 单题打分 + 可直接背的骨架 |
| 出题 / 刷题 / 考考我 | 连续出题速刷，快速暴露范围 |
| 这项目怎么讲 / 帮我改简历 | 五层拷问 + STAR 改写 |
| 我进步了吗 / 看档案 | 跑统计，给 7 天计划 |
| XX 的标准答案是什么 | 查题库讲解，不打分 |

**两档压力**：默认演练；说「切到陪练」「别太压」降到陪练。

第一次会问你：行业岗位、**条线**、职级、轮次、简历、JD、最担心的一点。答完这些才出第一题——没有简历和 JD，出的题与你无关，练了也没用。

## 覆盖方向

| 方向 | 岗位包 | 题库 |
|---|---|---|
| 信贷风控（模型 / 策略 / 反欺诈 / 贷后 / 负责人） | `references/roles/credit-risk.md` | `references/risk-bank.md` |
| 智能体开发（应用 / 工程 / RAG / 评测 / 平台） | `references/roles/agent-dev.md` | `references/agent-bank.md` |
| 复合岗（风控 + AI 落地） | 两个都用 | `references/crossover-bank.md` |
| 其他岗位 | `references/roles/generic.md` 现场生成 | — |

## 仓库结构

```
SKILL.md                     主流程：形式路由、五阶段、出题、档案
references/
  protocol.md                演练/陪练协议、追问纪律、话术校准、敏感提问
  rounds.md                  五种轮次：题量、权重规则
  rubric.md                  1–5 分语义、通过线、红线、复盘格式、定级
  roles/                     岗位包（维度、权重、好证据、假好、题干）
  risk-bank.md               风控题库 R101–R405
  agent-bank.md              智能体题库 A101–A403
  crossover-bank.md          交叉题、项目拷问模板、高压质疑题
scripts/
  install.sh                 安装到 workbuddy / cursor
  interview_log.py           档案追加与统计
assets/
  candidate-profile.md       长期画像模板
```

## 档案

默认写在 `~/.workbuddy/interview-log/`：

- `sessions.jsonl` — 机器可读
- `YYYY-MM-DD.md` — 按天追加，人可读
- `candidate-profile.md` — 长期画像

```bash
python3 scripts/interview_log.py stats          # 薄弱维度、失分题排行、进步曲线
python3 scripts/interview_log.py tail -n 2      # 看最近两场原始记录
```

档案只存分数、题号与缺口描述，**不存简历原文**。

## 隐私与边界

- 简历和经历只在本对话使用。
- 不代写简历，不编造经历、客户、交易或业绩。
- 不承诺录用、通过率或薪资区间。
- 不把歧视性或违法提问（年龄、婚育、地域、宗教、健康）当成压力来演。

## 致谢与来源

方法论骨架（演练/陪练双模式、轮次体系、岗位包「好证据 / 假好」结构、通过线判定、〔待你补充〕改写）来自 [cadetnicolas/interview_practice](https://github.com/cadetnicolas/interview_practice) 的 cross-industry 面试演练 Skill。

本版本在其基础上：

1. 把通用维度替换为**信贷风控**与**智能体开发**两套专业岗位包；
2. 补入 90 道带答案锚点的专业题库与交叉题；
3. 把「印象分」改为**加权均分 + 通过线 + 红线封顶**；
4. 新增**训练档案**（量化追踪）与**六种训练形式**；
5. 话术校准补充了风控、智能体、交叉三类场景的具体追问例句。

原 MIT 许可证保留，见 [LICENSE](LICENSE)。
