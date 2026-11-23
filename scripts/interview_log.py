#!/usr/bin/env python3
"""面试训练档案：追加记录与统计薄弱维度。

评分口径与 references/rubric.md 一致：
  加权均分 = Σ(维度分 × 权重) / Σ权重   （只算已考察的维度）
  通过线   = 所有已考察维度 >= 3 且 加权均分 >= 3.5
  百分制   = 加权均分 / 5 * 100

用法:
  # 追加一场（从 stdin 读 JSON）
  echo '{...}' | python3 interview_log.py append

  # 直接传 JSON
  python3 interview_log.py append --json '{...}'

  # 统计
  python3 interview_log.py stats
  python3 interview_log.py stats --recent 5

  # 看最近原始记录
  python3 interview_log.py tail -n 3

数据落在 --dir（默认 ~/.workbuddy/interview-log）：
  sessions.jsonl     机器可读，每行一场
  YYYY-MM-DD.md      人可读，按日期追加
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_DIR = Path.home() / ".workbuddy" / "interview-log"
PASS_LINE = 3.5
PASS_MIN_DIM = 3


# ---------- 计算 ----------

def compute(dimensions):
    """返回 (加权均分, 是否过线, 已考察维度列表)。未考察的维度需 score 为 None 或缺失。"""
    graded = [d for d in dimensions if d.get("score") is not None]
    if not graded:
        return 0.0, False, graded
    wsum = sum(float(d.get("weight") or 0) for d in graded)
    if wsum <= 0:
        return 0.0, False, graded
    avg = sum(float(d["score"]) * float(d.get("weight") or 0) for d in graded) / wsum
    avg = round(avg, 2)
    all_above = all(float(d["score"]) >= PASS_MIN_DIM for d in graded)
    passed = all_above and avg >= PASS_LINE
    return avg, passed, graded


def level_of(avg):
    if avg >= 4.25:
        return "L3"
    if avg >= 3.5:
        return "L2"
    if avg >= 2.75:
        return "L1-L2"
    return "L1"


def fmt_verdict(passed, avg, dims=None):
    if passed:
        return f"过线（均分 {avg:.2f} ≥ {PASS_LINE}）"
    reasons = []
    if avg < PASS_LINE:
        reasons.append(f"均分 {avg:.2f} < {PASS_LINE}")
    for d in dims or []:
        if d.get("score") is not None and float(d["score"]) < PASS_MIN_DIM:
            reasons.append(f"{d.get('name', '-')} {d['score']} 分低于 {PASS_MIN_DIM}")
    return f"未过线（{'，'.join(reasons) or '有维度未达标'}）"


# ---------- 存储 ----------

def read_sessions(path):
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def render_markdown(rec):
    lines = []
    meta = [rec.get("ts", "")]
    for k in ("mode", "round", "role"):
        if rec.get(k):
            meta.append(str(rec[k]))
    lines.append("## " + " · ".join(meta))
    lines.append("")

    avg = rec.get("avg", 0)
    pct = rec.get("pct", 0)
    dims = rec.get("dimensions") or []
    verdict = ("✅ " if rec.get("passed") else "❌ ") + fmt_verdict(
        rec.get("passed"), avg, dims
    )
    lines.append(f"- 加权均分：**{avg} / 5**（通过线 {PASS_LINE}）· {pct:.0f}/100 · {verdict}")
    if rec.get("level"):
        lines.append(f"- 定级：{rec['level']} 就绪")
    if rec.get("duration_min"):
        lines.append(f"- 时长：{rec['duration_min']} 分钟")
    if rec.get("mode") == "陪练":
        lines.append("- 注：本场为陪练分，不与演练分横向比较")

    if dims:
        lines.append("")
        lines.append("| 维度 | 权重 | 分数 |")
        lines.append("|---|---|---|")
        for d in dims:
            s = d.get("score")
            lines.append(
                f"| {d.get('name', '-')} | {d.get('weight', '-')} | "
                f"{'未考察' if s is None else s} |"
            )
        lines.append("")

    qs = rec.get("questions") or []
    if qs:
        lines.append("")
        lines.append("| 题号 | 题目 | 得分 | 失分点 |")
        lines.append("|---|---|---|---|")
        for q in qs:
            title = str(q.get("title", "")).replace("|", "/")
            gap = str(q.get("gap", "")).replace("|", "/")
            lines.append(f"| {q.get('id', '-')} | {title} | {q.get('score', '-')} | {gap} |")
        lines.append("")

    if rec.get("top_fix"):
        lines.append("")
        lines.append(f"**最该改的一件事**：{rec['top_fix']}")
    if rec.get("next"):
        nxt = rec["next"]
        if isinstance(nxt, list):
            nxt = "、".join(str(x) for x in nxt)
        lines.append(f"**下一轮只练**：{nxt}")

    # 收敛连续空行，保证 markdown 不粘连
    cleaned = []
    for ln in lines:
        if ln == "" and cleaned and cleaned[-1] == "":
            continue
        cleaned.append(ln)
    return "\n".join(cleaned).strip() + "\n"


def cmd_append(args):
    raw = args.json if args.json is not None else sys.stdin.read()
    raw = (raw or "").strip()
    if not raw:
        print("错误：没有收到 JSON。用 --json 传参或从 stdin 输入。", file=sys.stderr)
        return 2
    try:
        rec = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"错误：JSON 解析失败 - {e}", file=sys.stderr)
        return 2

    dims = rec.get("dimensions") or []
    if not dims:
        print("错误：缺少 dimensions。格式：\n"
              '  "dimensions": [{"name": "口径与证据", "weight": 25, "score": 4}]',
              file=sys.stderr)
        return 2

    rec.setdefault("ts", datetime.now().strftime("%Y-%m-%d %H:%M"))
    rec.setdefault("mode", "演练")
    avg, passed, graded = compute(dims)
    rec["avg"] = avg
    rec["pct"] = round(avg / 5 * 100, 1)
    rec["passed"] = passed
    rec["level"] = rec.get("level") or level_of(avg)

    d = Path(args.dir).expanduser()
    d.mkdir(parents=True, exist_ok=True)

    jl = d / "sessions.jsonl"
    with jl.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    day = datetime.now().strftime("%Y-%m-%d")
    md = d / f"{day}.md"
    if not md.exists():
        md.write_text(f"# 面试训练档案 {day}\n\n", encoding="utf-8")
    with md.open("a", encoding="utf-8") as f:
        f.write(render_markdown(rec) + "\n")

    print(f"已记录：{jl}")
    print(f"已追加：{md}")
    print(f"本场：均分 {avg}/5 · {rec['pct']:.0f}/100 · {fmt_verdict(passed, avg, dims)} · {rec['level']} 就绪")
    return 0


def cmd_stats(args):
    d = Path(args.dir).expanduser()
    sessions = read_sessions(d / "sessions.jsonl")
    if not sessions:
        print(f"暂无训练记录（{d}）。先跑一场模拟面试吧。")
        return 0

    recent = sessions[-args.recent:] if args.recent else sessions
    passed_n = sum(1 for s in sessions if s.get("passed"))
    print(f"训练场次：{len(sessions)} · 过线 {passed_n} 场"
          f"（{passed_n / len(sessions) * 100:.0f}%）· 统计窗口：最近 {len(recent)} 场\n")

    avgs = [s.get("avg", 0) for s in recent]
    all_avgs = [s.get("avg", 0) for s in sessions]
    print(f"加权均分：窗口均 {sum(avgs) / len(avgs):.2f} · 历史均 {sum(all_avgs) / len(all_avgs):.2f}"
          f" · 最高 {max(all_avgs):.2f} · 通过线 {PASS_LINE}")

    # 维度聚合（跨场次、同名累加）
    bucket = {}
    for s in recent:
        for dim in s.get("dimensions") or []:
            if dim.get("score") is None:
                continue
            name = dim.get("name", "-")
            bucket.setdefault(name, []).append(float(dim["score"]))
    if bucket:
        print("\n维度均值（最近窗口，括号内为场次数）")
        for name, vals in sorted(bucket.items(), key=lambda kv: sum(kv[1]) / len(kv[1])):
            m = sum(vals) / len(vals)
            bar = "█" * int(round(m * 2)) + "░" * (10 - int(round(m * 2)))
            flag = "  ← 最弱" if m < PASS_MIN_DIM else ("  ← 待补" if m < PASS_LINE else "")
            print(f"  {name:<10} {bar} {m:.2f} ({len(vals)}){flag}")

    # 反复失分题
    gap_counter = {}
    for s in sessions:
        for q in s.get("questions") or []:
            if q.get("gap"):
                gap_counter.setdefault(q.get("id", "-"), []).append(q["gap"])
    if gap_counter:
        print("\n反复失分题（按出现次数）")
        for qid, gaps in sorted(gap_counter.items(), key=lambda kv: -len(kv[1]))[:6]:
            print(f"  {qid} × {len(gaps)}  —— {gaps[-1]}")

    if len(all_avgs) >= 2:
        delta = all_avgs[-1] - all_avgs[0]
        sign = "+" if delta >= 0 else ""
        print(f"\n首场 {all_avgs[0]:.2f} → 最近 {all_avgs[-1]:.2f}（{sign}{delta:.2f}）")

    # 最近一场的「下一轮只练」
    last_next = sessions[-1].get("next")
    if last_next:
        if isinstance(last_next, list):
            last_next = "、".join(str(x) for x in last_next)
        print(f"上次布置的下一轮：{last_next}")
    return 0


def cmd_tail(args):
    d = Path(args.dir).expanduser()
    sessions = read_sessions(d / "sessions.jsonl")
    if not sessions:
        print("暂无记录。")
        return 0
    for s in sessions[-args.n:]:
        print(json.dumps(s, ensure_ascii=False, indent=2))
    return 0


def main():
    p = argparse.ArgumentParser(description="面试训练档案管理")
    p.add_argument("--dir", default=str(DEFAULT_DIR), help="档案目录")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("append", help="追加一场训练记录")
    a.add_argument("--json", help="JSON 字符串；不传则读 stdin")
    a.set_defaults(func=cmd_append)

    s = sub.add_parser("stats", help="统计薄弱维度与趋势")
    s.add_argument("--recent", type=int, default=10, help="统计窗口，0=全部")
    s.set_defaults(func=cmd_stats)

    t = sub.add_parser("tail", help="查看最近记录")
    t.add_argument("-n", type=int, default=3)
    t.set_defaults(func=cmd_tail)

    args = p.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
