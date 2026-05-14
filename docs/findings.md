# AgentBench-Live · Findings (2026-05-14)

> 内部文档，作为 README hook / launch 文案 / HN 帖的事实底盘。
> 数据来源：`results/*.json`（runs 自 2026-03-14 至 2026-03-19）。
> 完整 run 数：Claude Code n=2，Gemini CLI n=3。
> **样本小，所有结论需在 day 2 用 ≥3 trial × 4 agent 全套重跑验证。**

---

## TL;DR · 三个反共识 finding

1. **"总分几乎一样"是统计幻觉。** Claude Code 0.63 vs Gemini CLI 0.52 — 差距 11pp。但每个能力轴上的差距远大于此：Tool Use 7×，Research 1.6×。**总分掩盖了真相**。
2. **代码任务已是 commodity。** 两个 agent 在 `code-001` / `code-002` 上都是满分 1.00。**"哪个 agent 写代码更好"这个问题在 2026 年已经过时**。
3. **同一 agent 同一 task 重跑能差 70 个百分点。** Claude Code 在 `tool-001` 跑两次得分 0.0 / 0.7；`research-001` 同样 0.0 / 0.7。**single-trial benchmark 不可信，但行业里几乎所有 agent leaderboard 都只跑一次。**

---

## Finding 1 · 平均分骗了你

| Domain | Claude Code | Gemini CLI | 比值 | 谁赢 |
|---|---:|---:|---:|---|
| Code | 1.00 | 1.00 | 1.0× | tie |
| Data | 0.49 | 0.32 | 1.5× | Claude |
| Multi-Step | 0.74 | 0.77 | 1.0× | Gemini |
| Research | 0.70 | 0.45 | **1.6×** | Claude |
| Tool Use | 0.35 | 0.05 | **7.0×** | Claude |
| **Overall** | **0.63** | **0.52** | 1.2× | Claude |

**为什么这是反共识**：直接 narrative 通常说"两个 agent 差不多"或"X 全面碾压 Y"。**但真相是"每个能力上差距巨大且方向不同"**——Claude 在 Tool Use 上 7 倍领先 Gemini，但 Multi-Step 上 Gemini 反而略胜。**用一个总分来推荐 agent 是误导性的**。

**Hook 句式**："Don't ask which agent is best. Ask which agent is best at *what you actually do*."

---

## Finding 2 · Code 任务已死

`code-001`（修 bug + 加测试）和 `code-002`（实现一个 feature）在两个 agent 上**都是 1.00 满分**。

> 这不是说 agent 已经能写所有代码。是说**单文件、有 pytest 套件的"教科书任务"已经被 LLM 编码能力解决**。任何 benchmark 如果还在比较"AI 能写代码吗"，已经过时。**真正的差距在工具调用、多步编排、信息搜集——这些"agent 性"任务**。

**Hook 句式**："Both agents ace code-001 and code-002 at 1.00. The interesting differences live elsewhere."

---

## Finding 3 · 重跑的可怕真相

| Task | Agent | Trial 1 | Trial 2 | Trial 3 |
|---|---|---:|---:|---:|
| `tool-001` | Claude Code | **0.0** | **0.7** | — |
| `tool-001` | Gemini CLI | 0.0 | 0.0 | 0.1 |
| `research-001` | Claude Code | **0.0** | **0.7** | — |
| `research-001` | Gemini CLI | 0.0 | 0.0 | 0.3 |
| Overall | Claude Code | 0.604 | 0.656 | — |
| Overall | Gemini CLI | 0.516 | 0.516 | 0.518 |

**两个发现叠加**：
- **Claude Code 是高方差 agent**：同一个 task 跑两次能从全失败到 70% 通过；overall 在 0.604-0.656 之间。
- **Gemini CLI 是低方差 agent**：overall 三次几乎一样（0.516 / 0.516 / 0.518）。

**为什么这是反共识**：业界 agent benchmark（PinchBench、ClawProBench、SWE-bench 等）大多公开**单 trial 排名**。但如果同一 agent 重跑差 70%，这种排名靠谱吗？

**这不是黑别人，是抬自己**：AgentBench-Live 的 v0.3 必须支持：
- 多 trial（默认 ≥3）
- pass@k 报告
- 置信区间（bootstrap）
- 区分"agent 方差"和"judge 方差"（同一 output 多 judge 投票）

**Hook 句式**："We re-ran the same agent on the same task. Got 0.0 once, 0.7 the next. Most agent leaderboards hide this."

---

## 还需要在 day 2 验证的事

- [ ] 用真实 LLM judge（不是 heuristic fallback）重跑 day 1 的所有 task
- [ ] Claude Code 高方差是 agent 真的不稳定，还是 LLM judge 不稳定？方法：固定 agent output，让 judge 评 5 次
- [ ] Codex CLI 和 Aider 加入后，是 4 agent 都高方差，还是只有 Claude？
- [ ] Tool Use 7× 差距在新数据下是否仍成立？还是 Gemini CLI 4 月之后有大幅改进？
- [ ] 加 cost / latency 维度后，"谁性价比最高"的答案会不会颠覆"谁分数最高"

---

## Narrative 选型（按戏剧性递增）

| 选项 | Hook | 风险 |
|---|---|---|
| A · 安全 | "Two agents look tied. They're not. Claude is 7× better at Tool Use." | 平淡，竞品也能复制 |
| B · 中等 | "We re-ran the same agent twice. Got 0.0 then 0.7." | 可能被质疑 sample size |
| C · 激进 | "Most AI agent leaderboards are statistical theater. Here's the data." | 得罪同行，但传播力最强 |

**当前推荐**：**B + 用 A 作为支撑**。先用具体的 0.0/0.7 案例抓眼球，再用"7× Tool Use 差距"作为可信支撑数据，最后产品定位用 "first benchmark that takes variance seriously" 把"问题"接住。

C 等 day 2 数据更扎实再考虑——现在样本太小，强行打 C 会被反噬。
