# Jack TODO — AgentBench-Live Trending Sprint

## 安装 Agent CLI

```bash
# Aider
pip install aider-chat

# Codex CLI (需要 Node.js)
npm install -g @openai/codex

# 验证安装
aider --version
codex --version
claude --version
gemini --version
```

## 设置 API Key

```bash
export ANTHROPIC_API_KEY=your-key    # LLM Judge 评分 + Claude Code
export OPENAI_API_KEY=your-key       # Aider + Codex CLI
export GEMINI_API_KEY=your-key       # Gemini CLI (如需要)
```

## 跑 Benchmark（每个约 30-60 分钟）

```bash
cd ~/AgentBench-Live

agentbench run --agent claude-code --tasks all --output results
agentbench run --agent gemini-cli --tasks all --output results
agentbench run --agent codex-cli --tasks all --output results
agentbench run --agent aider --tasks all --output results
```

## 跑完后交给 Claude 做

- 更新 leaderboard/data/rankings.json
- 生成社交卡片: `agentbench social-card`
- 更新 README 里的分数表
- 更新社交文案（4 agent 版本）
- push + 部署 GitHub Pages

## 社交发帖（选 Tues-Thurs，所有频道同一天发）

- [ ] Twitter/X
- [ ] Reddit r/ClaudeAI
- [ ] Reddit r/MachineLearning
- [ ] Hacker News (Show HN)
- [ ] 小红书
- [ ] V2EX
- [ ] 即刻
- [ ] 微信群 / Telegram
