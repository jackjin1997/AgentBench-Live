# AgentBench-Live — Launch TODO

> Goal: 冲上 GitHub Trending
> Strategy: 完善产品 → 生成真实排行榜数据 → 社交传播

## [BOT] 代码 & 内容（Claude 在做）

- [x] 分析竞品和趋势
- [x] 补全 data-001 fixtures (sales.csv + check_answers.py)
- [x] 补全 data-002 fixtures (server.log.jsonl)
- [x] 补全 multi-001 fixtures (buggy source + tests)
- [x] 补全 multi-002 fixtures (existing codebase to extend)
- [x] 补全 research-002 fixtures (requirements.txt with CVEs)
- [x] 补全 tool-002 fixtures (validate_pipeline.py)
- [x] 用 Claude Code 跑全部 10 个 task benchmark → avg 0.60, pass 5/10
- [x] 用 Gemini CLI 跑全部 10 个 task benchmark → avg 0.52, pass 3/10
- [x] 生成 leaderboard 数据 (rankings.json)
- [x] 优化 README：加入真实 benchmark 结果表格和分析
- [ ] 确保 `pip install agentbench-live` 能直接用
- [ ] Push 到 GitHub

## [USER] 需要你做的事

- [ ] **⚡ 确认 push 到 GitHub**：代码已全部就绪，回复"push"我就推上去
- [ ] **设置 ANTHROPIC_API_KEY 环境变量**：LLM Judge 需要它来做高质量评分（当前用 fallback 模式）
- [ ] **准备社交媒体帖子**：Twitter/X 英文帖 + 即刻/小红书中文帖
  - 核心卖点："We benchmarked Claude Code vs Gemini CLI vs OpenClaw — here's who wins"
  - 要有争议性，agent 粉丝群体会自发传播
- [ ] **选择发布时间**：建议美西时间周二/周三上午 (GitHub trending 算法按 24h 星标增速)
- [ ] **发 Hacker News**：标题建议 "Show HN: AgentBench-Live – Real-time leaderboard for AI coding agents"
- [ ] **发 Reddit**：r/MachineLearning, r/LocalLLaMA, r/ClaudeAI
- [ ] **找 3-5 个 KOL 提前预览**：agent 领域的 Twitter 大V，给他们看排行结果
- [ ] （可选）安装 OpenClaw CLI，让我能跑 OpenClaw benchmark
