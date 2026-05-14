# Launch Copy · v0.2 (2026-05-14)

> 多平台文案库 · 同一 narrative，按平台调性微调
> Hook: **反共识 — single-trial agent benchmark 不可信**
> 主数据点：Tool Use 7× 差距 · 同 task 重跑 0.0 → 0.7
> Day 2 跑完真新数据后回到这里 polish 数字

---

## 0 · 通用素材

**主链接**
- GitHub: https://github.com/jackjin1997/AgentBench-Live
- Live Leaderboard: https://jackjin1997.github.io/AgentBench-Live/
- Findings doc: https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/findings.md
- Methodology: https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/methodology.md

**主图（必配）**
- `docs/social-card-v2.png`（day 1 task d1-4 生成）— Twitter/X、小红书、即刻、Reddit 必配
- HN / V2EX 不配图（HN 不支持，V2EX 不强求）

**Hook 句式（备用）**
- 主：「Two agents look tied. They're not. Claude is 7× better at Tool Use.」
- 副：「We re-ran the same agent twice. Got 0.0 once, 0.7 the next.」
- 中文主：「我们重跑同一个 agent 同一个 task 两次。一次 0%，一次 70%。这才是 AI agent benchmark 的真相。」

---

## 1 · Hacker News · Show HN

**Title (限 80 字符)**
```
Show HN: AgentBench-Live – Why we don't trust single-trial agent benchmarks
```

**Body**
```
We built an open benchmark for AI coding agents (Claude Code, Gemini CLI, Codex CLI, Aider) on 10 real tasks. While running it, we noticed three things that surprised us:

1. "Tied overall" hides 7× per-axis gaps. Claude Code 0.63 vs Gemini CLI 0.52 looks close. But on Tool Use specifically, Claude is 7× better. On Multi-Step, Gemini is slightly ahead. The average is misleading — pick the agent for the task, not the leaderboard.

2. Code tasks are commodity now. Both agents score 1.00 on every code task we threw at them. The interesting differences live in tool calling, multi-step orchestration, and research.

3. Re-running the same agent on the same task can flip the result. Claude Code on tool-001: trial 1 = 0.0, trial 2 = 0.7. Same prompt, same sandbox. Most agent leaderboards (SWE-bench, PinchBench, OSWorld) publish single-trial numbers. We don't think that's honest, so v0.2 reports min/max/median across multiple trials.

The benchmark is open source (MIT). Adding a new agent adapter is ~15 lines of Python. Each task runs in a Docker sandbox with auto-eval (pytest) for code tasks and LLM-as-Judge for subjective tasks.

Findings doc with the full data and methodology:
https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/findings.md

Live leaderboard:
https://jackjin1997.github.io/AgentBench-Live/

Happy to take any feedback on task design, scoring, or what variance threshold should disqualify a single-trial benchmark.
```

**Posting tips**
- 北京时间凌晨 0:00-3:00 = 美西早 9:00-11:00（HN 黄金窗口）
- 周二/三/四发，周末不发
- 提交后头 1 小时是命门：自己 +1，朋友们随手 +1，盯着评论快速回
- 如果 1 小时还没上 new page 顶端，基本沉了，等下周再发不要重发同一帖
- 第一条评论应该是你自己的"为什么做这个"补充，不要让别人主导讨论方向

---

## 2 · Twitter / X · 主推文 + thread

**主推文（限 280 字符）**
```
We re-ran the same coding agent on the same task twice.

Trial 1: 0.0
Trial 2: 0.7

Same agent. Same prompt. Same sandbox.

Most AI agent leaderboards report a single number. We don't think that's honest.

Open benchmark, MIT licensed:
github.com/jackjin1997/AgentBench-Live
```
配图：social-card-v2.png

**Thread 后续**
```
2/ Why this matters:

If single-trial scores can swing 70 points, every "X agent beats Y agent" headline you've seen this year is downstream of which trial happened to be sampled.

We re-ran each agent multiple times. Claude Code is high-variance. Gemini CLI is low-variance. Both deserve to be reported.

3/ The other surprise:

"Tied overall" hides per-axis gaps that are 7× wide.

Claude Code 0.63 vs Gemini CLI 0.52 looks close. But:
• Tool Use: Claude 7× better
• Research: Claude 1.6× better
• Multi-Step: Gemini slightly ahead
• Code tasks: both perfect

The average lies. Pick the agent for the task.

4/ Adding your agent is 15 lines of Python. We'd love adapters for Cursor, Windsurf, OpenHands, Devin.

→ github.com/jackjin1997/AgentBench-Live
→ Live leaderboard: jackjin1997.github.io/AgentBench-Live/
→ Findings: bit.ly/agentbench-findings
```

**Posting tips**
- 主推文发出后头 10 分钟必须有 ≥10 个真实 like / reply 才会被算法分发
- 提前找 3-5 个朋友约好同时互动
- 主动 @ Anthropic / Google AI / OpenAI Devs 等账号有概率被转
- @ swyx, @simonw 这种 dev infra KOL 比 @ 大公司账号更可能转

---

## 3 · Reddit · r/ClaudeAI

**Title**
```
We benchmarked Claude Code vs Gemini CLI 4 different ways. The results disagree with each other.
```

**Body**
```
Built an open-source benchmark for AI coding agents. Spent the last few weeks running Claude Code and Gemini CLI on 10 real-world tasks.

Three things surprised me:

**1. The overall scores are close. The per-task scores aren't.**

Claude Code 0.63 vs Gemini CLI 0.52 — looks tied-ish. But broken down:
- Tool Use: Claude 0.35 vs Gemini 0.05 (7x)
- Research: Claude 0.70 vs Gemini 0.45
- Multi-Step: Gemini 0.77 vs Claude 0.74 (Gemini wins this one)
- Code tasks: both perfect

So depending on what you actually do with the agent, the answer flips.

**2. Re-running the same task gives wildly different scores.**

Claude Code on tool-001: trial 1 = 0.0 (totally failed), trial 2 = 0.7 (mostly succeeded). Same prompt, same Docker sandbox, same model, just different runs.

Gemini CLI was much more deterministic — 3 trials, overall scores 0.516 / 0.516 / 0.518.

**3. Code tasks are basically a commodity now.**

Both agents nail every code task at 1.00. The differentiation is elsewhere.

Repo: https://github.com/jackjin1997/AgentBench-Live
Live leaderboard: https://jackjin1997.github.io/AgentBench-Live/
Findings doc with all data: https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/findings.md

Adding a new agent adapter is ~15 lines of Python. If anyone here uses Aider, Cursor, OpenHands, Codex CLI — would love help getting them on the leaderboard.

Curious what others have seen with re-running prompts. Is the variance just an artifact of LLM stochasticity, or are these agents genuinely non-deterministic in interesting ways?
```

---

## 4 · Reddit · r/MachineLearning

**Title**
```
[P] AgentBench-Live: open agent benchmark that reports variance, not just rank
```

**Body**
```
TL;DR: Built an open benchmark for AI coding agents that reports run-to-run variance. Found that single-trial leaderboards can be misleading — same agent, same task, scores can differ by 70 percentage points.

**Setup**
- 10 tasks across 5 domains (code, data analysis, multi-step orchestration, research, tool use)
- Docker sandbox per task with isolated workspace
- Two scoring modes: pytest auto-eval (for code) and LLM-as-Judge (for subjective)
- Currently 4 agents: Claude Code, Gemini CLI, Codex CLI, Aider (last two pending full multi-trial run)

**Findings (n=2-3 per agent, more coming)**
- Claude Code overall: 0.604 / 0.656 (spread 5%)
- Gemini CLI overall: 0.516 / 0.516 / 0.518 (spread 0.4%)
- Per-task variance is much higher: tool-001 went 0.0 → 0.7 between Claude trials
- Code tasks score 1.00 for both agents — code generation is essentially solved at the benchmark level

**Why post here**
- Sample size is small (n=2-3); want feedback on whether the variance numbers warrant the conclusion
- Looking for agreement / disagreement on "single-trial leaderboards aren't statistically meaningful for agents with this much variance"
- Methodology critique welcome (link below)

Repo: https://github.com/jackjin1997/AgentBench-Live
Methodology: https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/methodology.md
Findings: https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/findings.md

MIT licensed. Adding a new agent is ~15 LOC. PRs welcome.
```

---

## 5 · Reddit · r/LocalLLaMA

**Title**
```
Open agent benchmark — Claude Code vs Gemini CLI head-to-head with variance reporting
```

**Body** (调性更技术、更直接)
```
For folks who care about empirical agent comparison, not vibes:

Built an open benchmark, ran Claude Code and Gemini CLI on 10 real tasks (real Docker sandboxes, real codebases, not synthetic toy problems).

Quick takeaways:
- Both score 1.00 on pure code tasks. Code is solved.
- Claude is 7x better at Tool Use (0.35 vs 0.05).
- Gemini is more deterministic — overall scores cluster within 0.4%.
- Claude is high-variance — same task, two trials, scores 0.0 vs 0.7.

If you've been pissed off about agent leaderboards reporting single-trial numbers like they're scientific facts, this benchmark is built for you. Reports min/max/median across trials.

Adapter is ~15 LOC. If someone here wants to add their local agent setup (llama.cpp + tools, ollama-based agent, custom MCP host), would love a PR.

→ https://github.com/jackjin1997/AgentBench-Live
→ Live leaderboard: https://jackjin1997.github.io/AgentBench-Live/
```

---

## 6 · 小红书

**Title**
```
我重跑了同一个AI Agent两次。一次0分，一次70分。😱
```

**正文**
```
做了个开源的AI Agent评测项目，发现了三件让我怀疑人生的事👇

🔥 反共识发现 #1：「平均分一样」是个统计幻觉
Claude Code总分0.63 vs Gemini CLI总分0.52，看着差不多对吧？
但拆开看：
✅ 工具调用：Claude大胜7倍（0.35 vs 0.05）
✅ 技术调研：Claude领先（0.70 vs 0.45）
✅ 多步任务：Gemini反而更稳（0.77 vs 0.74）
✅ 写代码：两个都满分

→ 平均分骗了你。该按你的具体需求选Agent。

🔥 反共识发现 #2：写代码已经不是差异化
两个Agent在所有"code任务"上都是1.00满分。2026年还在比"哪个AI写代码强"的评测都过时了。真正的战场在工具调用、多步编排、信息搜集。

🔥 反共识发现 #3：同一个Agent同一个task跑两次能差70分
Claude Code跑tool-001这个任务：第一次0分（完全失败），第二次0.7分（基本成功）。同样的prompt、同样的sandbox。

但是大部分Agent排行榜都只跑一次就发布。我觉得这不诚实。

所以我们的项目v0.2开始默认每个task跑3+次，报告min/max/median，让你看到真实的方差。

📌 项目开源 (MIT)，加新Agent只要15行Python
GitHub搜：AgentBench-Live
在线排行榜：jackjin1997.github.io/AgentBench-Live/

#AI编程 #ClaudeCode #GeminiCLI #开源项目 #程序员日常 #AI工具 #编程效率
```

**配图**：social-card-v2.png（必配）

---

## 7 · V2EX · 分享创造

**Title**
```
[开源] AgentBench-Live：把方差报出来的 AI Agent 评测，不再单 trial 装 X
```

**正文**
```
做了一个开源 AI Agent benchmark，跑了 Claude Code 和 Gemini CLI 各 10 个真实任务（Docker sandbox + pytest auto-eval + LLM judge）。

跑的过程中发现三件事：

1. 总分 0.63 vs 0.52 看着差不多，但拆开看 Tool Use 维度 Claude 是 Gemini 的 7 倍。**靠平均分推荐 agent 是误导**。

2. 两个 agent 在所有 code 任务上都是 1.00 满分。**比"哪个 AI 写代码强"已经过时了**。

3. 同一个 agent 同一个 task 跑两次：Claude 在 tool-001 上一次 0.0，一次 0.7。Gemini 三次 overall 在 0.516-0.518 之间。**Claude 高方差，Gemini 低方差**。

第三点最让我意外。SWE-bench、PinchBench、ClawProBench 这些主流榜大多只跑 single trial 就出排名，但如果 agent 本身方差大，排名就是抛硬币。

所以 v0.2 起默认 ≥3 trial，报 min/max/median。

50 行 Python 就能加新 agent。欢迎 PR。

GitHub: https://github.com/jackjin1997/AgentBench-Live
排行榜: https://jackjin1997.github.io/AgentBench-Live/
findings 详细数据: https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/findings.md
```

---

## 8 · 即刻

**正文** (≤500 字)
```
做了个开源 AI Agent 评测，发现一个让我抓狂的事：

Claude Code 在同一个 task 跑两次。一次 0 分，一次 0.7 分。同样的 prompt，同样的 Docker 沙箱，同样的模型。

那么市面上所有"X agent 击败 Y agent"的标题党榜单，可能就是因为某次跑的运气不一样。

我们的 v0.2 默认每个 task 跑至少 3 次，报告 min/max/median。

附带几个反共识发现：
1️⃣ Claude 总分 0.63，Gemini 0.52。看起来打平。但 Tool Use 维度 Claude 是 Gemini 的 7 倍。
2️⃣ 两个 agent 在 code 任务上都是满分 1.00。「哪个 AI 写代码更强」已经不是有意义的问题了。
3️⃣ Claude 高方差，Gemini 低方差。这本身就是个新结论。

GitHub: AgentBench-Live (MIT 开源，加新 agent 15 行代码)

#AI编程 #开源
```

配图：social-card-v2.png

---

## 9 · 微信群 / Telegram · 一句话

```
做了个开源 AI agent 评测，发现 Claude Code 同一 task 跑两次能差 70 分；Gemini CLI 反而很稳。多平台数据 + 方差都公开。
github.com/jackjin1997/AgentBench-Live
```

---

## 10 · Posting timeline · 同日发布顺序

| Time (BJT) | Channel | Why |
|---|---|---|
| T+0 (00:00) | HN Show HN | 最难起飞，先发 |
| T+5 min | Twitter/X 主推 + thread | HN 起飞需要时间，Twitter 立刻分发 |
| T+15 min | r/ClaudeAI | HN 用户已经看到，Reddit 第一波 |
| T+30 min | r/MachineLearning + r/LocalLLaMA | 学术 + LocalLLM 并行 |
| T+1h | 小红书 + 即刻 | 国内用户起床高峰前 |
| T+2h | V2EX + 微信群 | 国内技术圈白天活跃 |
| T+4h | 检查所有 channel 状态 | 决定要不要补发 / 加置顶评论 |

**所有 channel 同日发的关键**：互相引流。HN 看到的人会去 Twitter 转，Twitter 转的人会回流 HN 上 vote。单 channel 单飞效果差 5-10 倍。

---

## 11 · Day 2 polish 清单

跑完真新数据后回这里更新：
- [ ] 替换所有 0.604 / 0.656 / 0.516 数字为新 run 的真实值
- [ ] 替换 0.0 / 0.7 案例为新数据下最戏剧的一对（如果 tool-001 不再是最戏剧的，换成新的）
- [ ] 加 Codex CLI / Aider 数字（如果跑出来了）
- [ ] 重生成 social-card-v2.png 用新数字
- [ ] 检查 HN title 是否需要根据新发现调整 hook
