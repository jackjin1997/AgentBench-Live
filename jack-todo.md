# Jack TODO — AgentBench-Live Trending Sprint

> 按顺序做，每一步都可以直接复制粘贴执行

---

## ✅ 已完成

- [x] 安装 Aider CLI
- [x] 安装 Codex CLI
- [x] 跑 Claude Code benchmark（10 tasks）
- [x] 跑 Gemini CLI benchmark（10 tasks）
- [x] 更新 leaderboard 数据

---

## 第 1 步：获取 API Key

你需要至少一个来跑更多 agent 和获得更准确的评分：

| Key | 用途 | 获取地址 |
|-----|------|---------|
| ANTHROPIC_API_KEY | LLM Judge 评分更准 | https://console.anthropic.com/settings/keys |
| OPENAI_API_KEY | 跑 Codex CLI + Aider | https://platform.openai.com/api-keys |

拿到后在终端执行：
```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
export OPENAI_API_KEY=sk-xxxxx
```

然后告诉 Claude "key 设好了，跑 benchmark"，剩下的我来做。

---

## 第 2 步：发帖推广（选周二/三/四，同一天全发）

### 2.1 Twitter/X

直接复制发推：

```
We tested Claude Code vs Gemini CLI on 10 real coding tasks

Results:
• Code: both perfect 1.00
• Multi-step: Gemini 0.77 vs Claude 0.74
• Research: Claude 0.60 vs Gemini 0.45
• Tool use: Claude 0.25 vs Gemini 0.05

Open source. Add your agent in ~50 lines of Python.

🔗 github.com/jackjin1997/AgentBench-Live
📊 Live leaderboard: jackjin1997.github.io/AgentBench-Live/
```

配图：用 `agentbench social-card` 生成的 social-card.png

---

### 2.2 Reddit — r/ClaudeAI

Title:
```
We benchmarked Claude Code vs Gemini CLI on 10 real tasks — results are surprisingly close
```

Body:
```
Built an open-source benchmark for AI coding agents. Not chat quality — actual task execution.

**Results (10 tasks, 5 domains):**

| Domain | Claude Code | Gemini CLI |
|--------|------------|-----------|
| Code | 1.00 | 1.00 |
| Multi-step | 0.74 | 0.77 |
| Research | 0.60 | 0.45 |
| Data | 0.07 | 0.32 |
| Tool Use | 0.25 | 0.05 |
| **Overall** | **0.53** | **0.52** |

Surprising finding: they're nearly tied overall (0.53 vs 0.52), but have very different strengths. Claude Code dominates research and tool use. Gemini CLI is better at data analysis and multi-step workflows.

Both ace pure code tasks — code generation is basically solved.

**Add your own agent in ~50 lines of Python.** We're looking for community contributions to add Codex CLI, Aider, and more.

GitHub: https://github.com/jackjin1997/AgentBench-Live
Live leaderboard: https://jackjin1997.github.io/AgentBench-Live/
Methodology: https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/methodology.md
```

---

### 2.3 Reddit — r/MachineLearning

Title:
```
[P] AgentBench-Live: Open benchmark for AI coding agents — Claude Code vs Gemini CLI results
```

Body: 同 r/ClaudeAI 的内容

---

### 2.4 Hacker News — Show HN

Title:
```
Show HN: AgentBench-Live – Open benchmark for AI coding agents
```

Body:
```
We built an open-source benchmark that tests AI coding agents on real tasks — bug fixes, data analysis, multi-step workflows, research, and tool use.

Current results: Claude Code (0.53) vs Gemini CLI (0.52) across 10 tasks. They're nearly tied overall but have very different strengths.

The benchmark uses auto-eval (pytest) for code tasks and LLM-as-Judge for subjective tasks. Each agent runs in a sandboxed workspace.

Adding a new agent adapter is ~50 lines of Python. We'd love community contributions.

GitHub: https://github.com/jackjin1997/AgentBench-Live
Methodology: https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/methodology.md
```

---

### 2.5 小红书

Title:
```
AI编程Agent排行榜！Claude Code vs Gemini CLI 10个任务实测
```

正文：
```
别再靠感觉选AI编程工具了！

我们用10个真实开发任务做了测评：

📊 总分：Claude Code 0.53 vs Gemini CLI 0.52（几乎打平！）

但各有所长：
✅ 写代码：都是满分
✅ 多步骤任务：Gemini CLI 略胜（0.77 vs 0.74）
✅ 技术调研：Claude Code 大幅领先（0.60 vs 0.45）
✅ 工具调用：Claude Code 领先（0.25 vs 0.05）
✅ 数据分析：Gemini CLI 领先（0.32 vs 0.07）

开源项目，50行Python就能加入你自己的Agent

GitHub搜 AgentBench-Live

#ClaudeCode #GeminiCLI #AI编程 #程序员 #编程工具 #开源
```

---

### 2.6 V2EX — 分享创造节点

Title:
```
AgentBench-Live: AI 编程 Agent 能力排行榜（开源）
```

正文：
```
做了一个开源的 AI Agent benchmark，用 10 个真实任务测试 CLI 编程 agent。

目前测了 Claude Code 和 Gemini CLI，结果很有意思——总分几乎一样（0.53 vs 0.52），但各有强项：

- 代码任务：都满分
- 多步骤：Gemini CLI 0.77 vs Claude Code 0.74
- 技术调研：Claude Code 0.60 vs Gemini CLI 0.45
- 工具调用：Claude Code 0.25 vs Gemini CLI 0.05

50 行 Python 就能加入新的 agent 适配器。欢迎 PR。

GitHub: https://github.com/jackjin1997/AgentBench-Live
排行榜: https://jackjin1997.github.io/AgentBench-Live/
方法论: https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/methodology.md
```

---

### 2.7 即刻

同小红书内容，直接复制

---

### 2.8 微信群 / Telegram

直接甩：
```
做了个开源的 AI Agent 排行榜，Claude Code vs Gemini CLI 10个任务对比，结果出乎意料——几乎打平。开源的，50行代码就能加你的agent：github.com/jackjin1997/AgentBench-Live
```

---

## 发帖技巧

1. **同一天发完所有频道**，选周二/三/四
2. **配图**：先跑 `agentbench social-card --output social-card.png`，Twitter 和小红书一定要配图
3. **HN 发帖时间**：美国西海岸早上 9-11 点（北京时间凌晨 1-3 点）效果最好
4. **Reddit 发完后**：在评论区主动回答可能的问题，保持活跃
5. **前 2 小时关键**：发完后保持在线，快速回复评论
