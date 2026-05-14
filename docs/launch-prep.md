# Launch Day Preparation · AgentBench-Live v0.2

> Launch day 一站式弹药库。开发者侧不依赖 API key 的 Day 2 产物：HN Q&A、demo 视频脚本、KOL outreach 列表、checklist。
> Day 2 真数据出来后回来 polish 数字。

---

## 1 · HN Q&A 弹药库（前 10 个尖锐问题 + 回复 draft）

> HN 头 1 小时是命门，回复速度 + 质量决定上不上 front page。
> 以下问题按"出现概率高 → 低"排序，每条给出 30 秒内可发的 reply draft。

### Q1 · "10 个 task 太少了，得出 7× 差距的结论站得住脚吗？"
**预计概率**：90%。HN 第一波必出。
**Reply draft**：
```
Fair point. n=10 tasks is a starting point, not a destination — we say so explicitly in docs/findings.md and methodology.md ("limitations" section).

Two notes:
1. The 7× gap is at the per-domain level, where each domain has 2 tasks. Yes, this is small. But the gap is also large enough (0.35 vs 0.05) that even with wide error bars you'd struggle to make them overlap.
2. We're actively seeking task contributions — task-authoring guide is in docs/. Adding a task is a YAML file plus a fixtures dir.

What we wanted to push back on more than "the absolute scores" is the *publishing convention* of single-trial averages. That part holds even at n=2.
```

---

### Q2 · "Why not just use SWE-bench / OpenHarness?"
**预计概率**：85%。学术圈标准对比。
**Reply draft**:
```
Different design intent.

SWE-bench tests "can the agent close a real GitHub issue" — single axis, GitHub-issue-shaped. Great for that.

We wanted to test the spread of agent capabilities (tool calls, multi-step orchestration, research, data analysis), because most of what people actually do with these CLIs is *not* "fix this issue". The trials-and-variance angle is also missing from SWE-bench reports.

Both can be useful. We aren't trying to replace SWE-bench; we're trying to surface a different question.
```

---

### Q3 · "LLM-as-Judge has its own variance — how do you separate agent variance from judge variance?"
**预计概率**：70%。技术深度问题，HN 喜欢。
**Reply draft**:
```
Honestly, in v0.2 we don't separate them well. The same LLM judge scores all trials, so judge stochasticity is folded into "agent variance" in the report. This is a real limitation.

v0.3 plan to disentangle:
1. Fix the agent output, run the judge K times → measures judge variance directly.
2. For each agent trial, judge it K times, take the median → reduces judge contribution to per-trial variance.
3. Auto-eval tasks (code-001, code-002 — pytest-based) are deterministic; we already see those are stable, which is one piece of evidence the variance is real on the agent side, not the judge.

If anyone here has a battle-tested method for this kind of decomposition, we'd love a pointer.
```

---

### Q4 · "Did you contact Anthropic / Google to make sure you're using the agents correctly?"
**预计概率**：50%。质疑 fairness。
**Reply draft**:
```
We use the publicly documented CLI invocation for each agent (`claude` for Claude Code, `gemini` for Gemini CLI, `codex` for Codex CLI, `aider` for Aider). The exact command lives in src/agentbench/adapters/<agent>.py — anyone can audit and PR a fix if we're using a CLI flag suboptimally.

We haven't reached out to vendors for "official benchmark mode" — partly because the whole point is *what does the out-of-the-box CLI do for an actual user*. If a vendor wants to PR adapter changes that better reflect intended usage, we'll merge them as long as the change is justified in the PR description.
```

---

### Q5 · "Why include LLM-as-Judge tasks at all? Just use deterministic tests."
**预计概率**：50%。纯粹主义观点。
**Reply draft**:
```
Because most real work doesn't have a clean pytest gate.

Research tasks ("compare 5 vector DBs for RAG"), tool-use tasks ("triage these GitHub issues into priority buckets"), and multi-step workflows can't always be reduced to a unit test. We acknowledge LLM judges add noise; that's why we report variance up front instead of hiding it.

Pure auto-eval would give us a cleaner number on a much narrower benchmark. We took the tradeoff toward "broader coverage with disclosed noise" rather than "narrow coverage with false precision".
```

---

### Q6 · "How do you prevent agents from cheating (e.g. caching prior runs, leaking task content into training data)?"
**预计概率**：40%。安全/methodology 问题。
**Reply draft**:
```
Three layers:

1. **Sandbox isolation**: each task runs in a fresh Docker container with only the fixtures it needs. Agents can't access prior runs.
2. **No persistent caches**: the agent CLI starts fresh each trial. (We don't yet test agents with long-running memory like Devin — that's a future axis.)
3. **Training-data leakage**: this is the harder one. Our tasks are written from scratch but they touch popular topics (vector DBs, GitHub issue triage). We can't fully prevent leakage; we mitigate by rotating task fixtures (e.g. swap which 5 vector DBs to compare) and watching for suspiciously specific outputs.

If you have ideas for stronger anti-leakage, please open an issue.
```

---

### Q7 · "What about cost? Speed?"
**预计概率**：40%。
**Reply draft**:
```
v0.3 axis. The EvalScore model already has CostMetrics + LatencyMetrics fields (see docs/methodology.md "Cost and Latency Roadmap"); the adapters just don't populate them yet.

Plan: parse token usage from each CLI's --output-format=json (Claude Code), --usage (Gemini CLI), or --show-token-cost (Aider); wrap invocation in a wall-clock timer. Then the leaderboard becomes 3-axis (score × $ × time) and you pick by your constraint, not ours.

Adding this for one adapter is ~10 LOC if anyone wants to PR before we get to it.
```

---

### Q8 · "Open AI's Codex CLI scores aren't there. Why?"
**预计概率**：30%。
**Reply draft**:
```
Adapter is in (`src/agentbench/adapters/codex_cli.py`), but the multi-trial run is pending — we ran out of OpenAI API quota during the v0.1 sweep. New full sweep with 4 agents × 10 tasks × 3 trials is happening this week.

The leaderboard will auto-refresh when results land in /docs/data/rankings.json.
```

---

### Q9 · "Is this an Anthropic project / shilling Claude?"
**预计概率**：30%。Tribal flag.
**Reply draft**:
```
No affiliation. I'm an indie dev. Claude does win on tool-use in this benchmark (7× margin), but that's an artifact of the benchmark — Gemini wins on multi-step (slightly), and Codex / Aider haven't been fully measured yet.

The benchmark is MIT-licensed; if anyone thinks the task selection systematically favors Claude, the right move is to PR new tasks that test what they think we're missing.
```

---

### Q10 · "Tool-001 = 0.0 → 0.7 sounds like the agent regressed once and you call it variance. How do you know it's not a flaky test or a network blip?"
**预计概率**：25%。技术深度的人才会问。
**Reply draft**:
```
Good challenge. Tool-001 hits the live GitHub API (gh CLI, no auth, public repo), so a transient network failure could absolutely produce 0.0. That'd be a sandbox/eval flakiness, not "agent variance".

We don't yet distinguish "agent failed" vs "environment flaked" cleanly. v0.3 plan: classify per-trial failure modes (agent error / tool error / network timeout / sandbox error) so spread isn't conflated with infra noise.

That said, the variance is also visible on research-001 (zero network requirements after install) — so at least some of it is real agent stochasticity. The exact breakdown is on the v0.3 list.
```

---

### Bonus · "I tried this for 5 minutes and the install broke."
**Reply draft**:
```
Sorry. Open an issue with the OS / Python version / error trace and I'll fix today. CI is on Python 3.9/3.11/3.12 — anything outside that range is currently best-effort.
```

---

## 2 · 90-Second Demo Video Script

> 用 OBS / QuickTime / iPhone 横屏录。声音清晰最重要，画面别花哨。
> 录完上传 YouTube unlisted，把链接放进 HN 第一条 comment（不放在帖子 body 里，HN 不爱看 marketing video）。

### Storyboard

| Time | Visual | Voice-over |
|---|---|---|
| 0:00-0:08 | Open `https://jackjin1997.github.io/AgentBench-Live/`, hero with red 0.0 / green 0.7 visible | "Most AI agent leaderboards report a single number. We don't think that's honest." |
| 0:08-0:18 | Scroll to 3 finding cards, hover over each | "Three things surprised us. Tied overall hides 7× per-axis gaps. Code tasks are now commodity. And re-running the same agent on the same task can swing 70 percentage points." |
| 0:18-0:32 | Scroll to variance panel, point at Claude row | "Claude Code is high-variance. Gemini is low-variance. Both deserve to be reported. Most leaderboards quietly publish a single trial." |
| 0:32-0:45 | Switch to terminal, show:<br/>`agentbench run --agent claude-code --tasks all --trials 3` | "Running the benchmark yourself is one command. Adding a new agent is fifteen lines of Python." |
| 0:45-0:60 | Show `src/agentbench/adapters/claude_code.py` in editor | "This is the entire Claude Code adapter. Subclass AgentAdapter, fill in the CLI command, that's it." |
| 0:60-0:75 | Back to leaderboard, scroll to per-domain table | "Pick the agent for the task, not the average." |
| 0:75-0:90 | Hero closing shot, GitHub URL overlay | "AgentBench-Live. Open source, MIT. Github dot com slash jackjin nineteen ninety-seven slash AgentBench dash Live." |

### 录音 tips
- 录两条：英文 (HN/Twitter/r/MachineLearning) + 中文 (小红书/即刻/B站)
- **不要看稿读** — 写下要点，自由发挥更自然
- 不要加背景音乐，会盖过解说
- 文件 < 10MB（Twitter 限制）
- 缩略图：用 `docs/social-card-v2.png` 截一帧

---

## 3 · KOL Outreach 候选清单

> Launch day 前 24h 私信预热（不 spam，附上 1 句 personal hook）。
> 如果对方上 launch day 主动转发，star velocity 能翻 3-5x。

### Twitter/X · 英文圈

| Handle | 为什么相关 | 私信 hook |
|---|---|---|
| @swyx | DX / dev infra KOL，Latent Space 联合创始人 | "Hey shawn, built an agent benchmark that reports run-to-run variance instead of single-trial. Same agent, same task can swing 70 points. Curious what you think — github.com/jackjin1997/AgentBench-Live" |
| @simonw | Datasette 作者，写大量 LLM benchmark 文章 | "Hi Simon, your benchmarking writeups have been very useful. Built an open agent benchmark — main angle is that we report variance because we found single-trial leaderboards hide a lot. Would love your read." |
| @mikeknoop | Zapier co-founder, ARC Prize | "Built an agent benchmark for CLI agents (Claude Code / Gemini CLI / Codex / Aider). Variance reporting is the differentiator. github.com/jackjin1997/AgentBench-Live" |
| @hwchase17 | LangChain 创始人 | "Built an open benchmark for CLI coding agents. Adapter is ~15 LOC; should be easy to add a LangChain-based agent if interesting." |
| @karpathy | 不太回 cold DM 但万一转 | 不私信，只在 Twitter 主推文加 @ 标签 |

### Twitter/X · 中文圈

| Handle | 为什么相关 |
|---|---|
| @baoyu / 宝玉 | AI 编程内容大 V，会转技术含量高的项目 |
| @GoldenaArrow | LangChain 中文社区 |
| @bigeagle | 国内 dev infra 圈活跃 |
| @oxnoxx | 程序员 KOL，会转开源 |

### Reddit · subreddits

| sub | 为什么相关 | 提示 |
|---|---|---|
| r/ClaudeAI | Claude 用户最关心的对比 | 标题别像广告 |
| r/MachineLearning | 学术受众，追 [P] tag | 必须强调 methodology + limitations |
| r/LocalLLaMA | LocalLLM + 工具党 | 强调"open source, run yourself" |
| r/coolgithubprojects | 单纯 OSS 列表 | 简短直接 |
| r/coding | 兜底 | 标题要 catchy |

⚠️ **避免**：r/programming（账号 karma 不够会被秒沉）、r/artificial（混杂太多 LLM 噪声）

### GitHub · users to @ in PR/issue

不主动 ping 大 V，但提交"adding your agent"提示后，可以在该 agent 的官方 repo 开 issue：
- anthropics/claude-code · "AgentBench-Live tested Claude Code on 10 tasks; here's what we found"
- google-gemini/gemini-cli · 同上
- openai/codex · 同上
- Aider-AI/aider · 同上

---

## 4 · Launch Day Checklist · T-1h

按这个顺序，每条做完打勾：

- [ ] 浏览器打开 `https://jackjin1997.github.io/AgentBench-Live/` 最后审一遍（loading 速度、所有数字、链接全 OK）
- [ ] GitHub repo 主页：截图 README 看显示效果（HN 上来人会先看 GitHub）
- [ ] HN 账号 logout / login 一次确认账号活跃
- [ ] Reddit 账号检查：karma 是否够 r/MachineLearning（通常 100+）；如果不够，提前用别号或找朋友代发
- [ ] Twitter：约好 3-5 个朋友 T+10min 内 like + reply
- [ ] 提前打开所有平台的发帖页面，文案复制粘贴到草稿框（**不要 launch 时才打开页面**）
- [ ] 关闭所有可能弹通知的 app（避免录视频时被打断）
- [ ] 准备好咖啡 / 水 / 零食（前 4h 全在线回复）

---

## 5 · Launch Day · 失败模式预案

**Pages 不可访问**（罕见但致命）
- T-1h 打开 https://jackjin1997.github.io/AgentBench-Live/ 验证
- 如果 down：延后 launch 4h；先去 GitHub 上看 Pages build 状态

**HN 帖子被 flagged / killed**
- 1h 内没上 new page 顶端 → 沉了
- 不要立刻重发同一帖（会被永久 ban）
- 等 1 周后用稍改的 hook 再发

**Reddit 帖子被 mod 删除**
- 标题违反 sub rule 是常见原因
- r/MachineLearning 强制要 [P] / [R] / [N] tag
- 提前看每个 sub 的 sticky 帖

**Twitter 主推文 0 互动**
- 主推文 10 分钟内没 ≥10 互动 → 算法判定低质量
- 立刻自己回复 2-3 个有内容的子推文（不是 emoji），把整体互动拉起来

**评论怒了 / 被反驳**
- 不要删评论
- 不要 defensive，承认有道理的部分
- 用 docs/findings.md 的 "limitations" 段作为"这是已知的"挡箭牌

---

## 6 · Day 2 真数据出来后必做的 polish

跑完 4 agent × 10 task × ≥3 trial 后：

- [ ] 替换 docs/launch-copy.md 里所有数字（0.604 / 0.656 / 0.516 / 7× / 1.6×）
- [ ] 替换本文件 HN Q&A 里 Q8 的"运用完 OpenAI 配额"措辞为真实状态
- [ ] 重生成 docs/social-card-v2.png（如果数字变了）
- [ ] 更新 docs/findings.md 的 sample size disclaimer (n=2-3 → n=≥3)
- [ ] 更新 docs/index.html 的 variance panel 数字
- [ ] commit + push 让 Pages 反映最新数据
- [ ] T-2h 在 leaderboard 上做最终视觉 QA（移动端、桌面、各浏览器）
