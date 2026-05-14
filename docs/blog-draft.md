# I re-ran the same AI coding agent twice. The score went from 0 to 0.7.

> **Draft for launch day.** Publish on dev.to / Medium / personal blog the same day as the HN/Twitter push, link from the HN top comment.
> Voice: personal, first-person, "I noticed something weird" — *not* corporate.
> Length: ~1500 words, 5 min read. Long enough to be substantive, short enough to finish.
> **Edit before publishing**: replace n=2-3 numbers with whatever Day-2 fresh runs produce.

---

## The setup

I've been building [AgentBench-Live](https://github.com/jackjin1997/AgentBench-Live), an open benchmark for AI coding agents — Claude Code, Gemini CLI, Codex CLI, Aider. Ten tasks across five domains: code generation, data analysis, multi-step orchestration, research, tool use. Each task runs in a Docker sandbox. Auto-eval (pytest) for code tasks, LLM-as-Judge for the rest.

Standard agent-benchmark stuff. The kind of project where you publish a leaderboard with single-trial scores, get some traffic, get told you're either too easy on Anthropic or too easy on Google, and move on.

I almost did exactly that. Then I made a mistake that surfaced something more interesting.

## The mistake

I re-ran the Claude Code suite to confirm the scores before publishing. Same agent. Same Docker image. Same task definitions. Just because I wanted a clean run for the README screenshots.

The numbers came back different. Not trivially — `tool-001` had gone from **0.7 to 0.0**. A complete reversal.

My first reaction was to debug the sandbox. Maybe Docker had a stale layer. Maybe there was a network blip during the GitHub API call this task makes. I rebuilt everything and ran it again.

Got 0.7 again.

Ran it once more, same task. Got 0.5.

So I started doing what I should have done from the beginning: I ran the *full* suite multiple times for both agents I'd benchmarked.

## What I found

Three things, in increasing order of how unsettling I find them.

### 1. "Tied overall" hides 7× per-axis gaps

The headline number — **Claude Code 0.63 vs Gemini CLI 0.52** — looks like a near-tie. That's the kind of result that produces a Twitter thread saying "they're basically equivalent, pick whichever you like."

But pull the per-domain scores apart and the picture shatters:

| Domain | Claude Code | Gemini CLI | Gap |
|---|---:|---:|---:|
| Code | 1.00 | 1.00 | tied |
| Data | 0.49 | 0.32 | 1.5× |
| Multi-Step | 0.74 | 0.77 | tied (Gemini) |
| Research | 0.70 | 0.45 | **1.6×** Claude |
| **Tool Use** | **0.35** | **0.05** | **7× Claude** |

Claude is **seven times better at tool use**. Gemini is **slightly better at multi-step orchestration**. They are not the same product. The average is a lie.

If you've been recommending one of these agents to colleagues based on a top-line score, you've been recommending an artifact of arithmetic averaging.

### 2. Code tasks are commodity now

This is the boring finding, but it's the one I think will age the fastest.

Both agents score **1.00 on every code task** in the suite. Both. Every. Code. Task. 

Code-001 is "fix this bug, here are the failing tests." Code-002 is "implement this feature, here's the spec." They're not toy problems — they have realistic file structures and pytest suites. And both agents nail them, every time, deterministic auto-eval.

If you're still benchmarking AI coding agents primarily on "can it write code" you're benchmarking a solved problem. The differentiation is now in: can it use tools, can it search and synthesize, can it orchestrate a multi-step plan, can it know when to stop and ask. Those are the axes that move the per-domain numbers.

I expect by 2027 there will be papers titled "agent code generation has saturated benchmark X" and the entire field will quietly pivot. The pivot is already visible in the data above.

### 3. Same agent. Same task. 70-point swing.

This is the one I keep thinking about.

For Claude Code, two independent runs of `tool-001` gave me 0.0 and 0.7. Two runs of `research-001` gave me 0.0 and 0.7. The overall benchmark score moved between 0.604 and 0.656 across full reruns.

Gemini CLI, by contrast, was striking in its determinism: three full reruns produced overall scores of 0.516, 0.516, and 0.518. I'd assumed both agents would have similar variance because they're both LLM-driven. They don't.

So now I have two questions.

**The narrow question**: which one is "the better agent"? Do I report the Claude high-water mark of 0.7 (favorable to Claude), the low-water mark of 0.0 (unfavorable to Claude), or the median? *And does it matter if I make that decision before or after I've seen the numbers?*

**The wide question**: why does almost every published agent leaderboard report a single trial?

Look at SWE-bench. PinchBench. ClawProBench. OSWorld. They all run the agent N times where N is rarely greater than 1 and frequently equal to 1. The number gets published. People cite it. Someone writes a tweet about how X agent "beat" Y agent. The next quarter, Y agent ships a new version, retests, and "beats" X. Round and round.

If the underlying agents have ±25% per-task variance, the rankings produced by these benchmarks are not measuring agent skill. They're measuring which trial happened to be sampled.

## How seriously should you take the variance claim?

I want to be honest about the limits here.

**Sample size is small.** I have 2 full Claude runs and 3 full Gemini runs. That's not enough to make strong statistical claims. It's enough to notice a pattern that warrants more investigation, not enough to publish a paper. I'm explicitly disclosing this in the [findings doc](https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/findings.md).

**Source of variance is not yet decomposed.** When the same agent gets two different scores on the same task, the spread could be coming from: (a) the agent's own stochasticity (LLMs are non-deterministic), (b) the LLM-as-Judge giving different scores for similar outputs, or (c) environmental flakiness (network, sandbox quirks). I haven't disentangled these yet. v0.3 of the benchmark will run dedicated experiments to separate them — judge the same fixed output K times, classify per-trial failure modes by category.

**`tool-001` hits the live GitHub API.** A network failure could explain the 0.0. The fact that `research-001` (no network after install) showed the same pattern is one piece of evidence the variance isn't purely environmental, but it's not conclusive.

So: take this as a *prior worth testing*, not as a published finding. The point of building AgentBench-Live the way I'm building it is so that anyone can run multi-trial sweeps and check.

## What I'm changing in v0.3

Concrete next steps:

1. **Default to multi-trial.** `agentbench run` defaults to `--trials 3`. Single-trial becomes opt-in.
2. **Report variance, not just mean.** Leaderboard shows median with min/max bars per agent per domain.
3. **Separate agent vs judge variance.** Run the LLM judge K times on the same fixed output. If judge variance is significant, weight it down or switch to majority voting.
4. **Add cost and latency axes.** Score is one dimension. The next two are tokens-per-task ($) and seconds-per-task. The leaderboard becomes a 3D matrix and you pick by *your* constraint, not mine.
5. **Bigger task set.** 10 tasks → 30+ tasks via community contributions. Adapter PRs and task PRs are the two highest-leverage ways anyone can help.

## What I want from you

If you're an agent vendor: please add multi-trial reporting to your own evaluation. The current state of the art produces leaderboards that flip with re-runs. That's bad for you because skeptics use it to dismiss the field, and it's bad for users because they make tool-choice decisions based on noise.

If you're a developer choosing an agent: stop trusting headline scores. Open the per-domain breakdown. Pick the agent that scores high *on the tasks you actually do*.

If you want to contribute: AgentBench-Live is MIT, on [GitHub](https://github.com/jackjin1997/AgentBench-Live). Adding a new agent is fifteen lines of Python ([CONTRIBUTING.md](https://github.com/jackjin1997/AgentBench-Live/blob/main/CONTRIBUTING.md)). Adding a new task is a YAML file ([task authoring guide](https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/task-authoring.md)). I'd love help. Particularly from anyone who's already burned by single-trial benchmark results in their own work — your skepticism is the right ingredient.

If you want to read the data: [findings doc](https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/findings.md), [methodology](https://github.com/jackjin1997/AgentBench-Live/blob/main/docs/methodology.md), [live leaderboard](https://jackjin1997.github.io/AgentBench-Live/).

---

*The whole point of measurement is that it tells you something you didn't already know. If we measure agents in ways that just confirm what their marketing already told us, we're not measuring — we're laundering opinions through numbers.*

*— [Your name], building [AgentBench-Live](https://github.com/jackjin1997/AgentBench-Live)*

---

## Pre-publish checklist

- [ ] Replace "I" / "my" with personal voice — this is currently impersonal
- [ ] Verify `tool-001` and `research-001` numbers match what's in `docs/findings.md`
- [ ] Replace "[Your name]" at the bottom
- [ ] Add 1-2 inline screenshots of the live leaderboard (use `cmd+shift+4` on the variance panel)
- [ ] Confirm all GitHub links resolve (especially `findings.md` exists in main)
- [ ] Set canonical URL (so dev.to / Medium / personal blog all credit the original)
- [ ] Schedule for ≤2 hours after the HN post goes up — link from your top HN comment
- [ ] Cross-post: dev.to (best for OSS dev audience), Medium (broader reach), personal blog (canonical)
- [ ] On dev.to use tags: `#opensource #ai #benchmark #showdev #python`
