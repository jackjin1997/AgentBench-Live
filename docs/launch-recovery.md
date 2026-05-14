# Launch-day recovery playbook

> What to do when the launch is *not* going to plan.
> Read this BEFORE launch day so you have the playbook in your head, not after you panic.

---

## Stop-light system

Use these signals at T+1h, T+4h, T+24h to decide what's working and what to do next.

### 🟢 Green — keep doing what you're doing

- HN: front-page (top 30) at T+30 min
- Reddit r/ClaudeAI: 50+ upvotes, comments by other users (not just you)
- Twitter: main tweet has 100+ impressions per minute, organic retweets from non-friends
- Stars: ≥30 stars at T+1h, ≥100 at T+4h

**Action**: nothing. Reply quickly to comments. Do NOT post to additional channels — momentum is enough.

### 🟡 Yellow — push harder, don't panic

- HN: stuck on `new` page (rank 30-100), not climbing
- Reddit: posted but 5-10 upvotes after 1h, 0-2 comments
- Twitter: <50 impressions per minute, friends-only engagement
- Stars: 5-15 at T+1h

**Action plan** (do all):
1. Check whether you missed engaging with any *thoughtful* HN/Reddit comment that's been sitting >5 min unreplied. Quality replies revive a stuck thread.
2. Tweet a single follow-up sub-tweet on the original Twitter thread linking to the most interesting Reddit/HN comment (creates cross-platform traffic).
3. Send the GitHub link to 5-10 specific people whose work touches AI evaluation, *with a specific reason* it'd interest them. Not a broadcast DM.
4. Post one *additional* tweet at T+4h with a different angle (e.g., a screenshot of a particularly stark variance case from the data).

**Do NOT**:
- Post the same content to a new subreddit
- Reply to your own HN/Reddit thread to bump it
- Tweet at celebrities desperately
- DM more than ~10 people total

### 🔴 Red — launch failed, plan a re-launch

- HN: dropped to page 3+ within 1h, no traction
- Reddit: ≤5 upvotes at T+4h, no comments (or only critical comments)
- Twitter: <500 total impressions at T+4h
- Stars: <10 at T+4h

**Immediate actions**:
1. **Do NOT delete posts.** They stay; they're learning data. Reposting same content gets you banned on most platforms.
2. **Take notes (not screenshots — actual notes)** on:
   - Which platforms got which engagement, what kind of comments
   - Specific feedback (positive or negative)
   - What hooks landed, what didn't
3. **Postpone any planned follow-up content** (blog post, KOL outreach) — they'd burn the same audience again.

**Then sleep on it.** Most "failed" launches are overcorrected the same day. Wait 7+ days, change the hook substantively (not cosmetically), pick *different* subreddits, then re-attempt.

---

## Common failure modes and what they actually mean

### "HN flagged my post"

- Why: tagged as 'show off' / blogspam / political. Show HN posts get aggressive flagging if the title sounds clickbait.
- Fix: don't repost same title. Wait 1+ week, post under a more sober title from `launch-copy.md` § HN Q&A as guidance.

### "r/MachineLearning removed my post"

- Why: forgot the [P] / [R] / [N] tag, or weighted as self-promotion. The mod team is strict.
- Fix: read pinned mod post on the sub. The 9-out-of-10 issue is not having `[P]` (project) in the title. Re-post with proper tag if mod permits.

### "Twitter 0 retweets"

- Why: account doesn't have engagement velocity. Algorithm is heavily seeded.
- Fix: this is an account-strength issue, not a content issue. Re-launch with a friend account that has more engagement, or invest 2-3 weeks building a relevant Twitter follower base before re-launching.

### "Got 50 upvotes but they're all from your friends"

- Why: launch is socially supported but didn't break out organically.
- Fix: this is harder to diagnose. Possible causes:
  - Hook is interesting to insiders but doesn't pass the "stranger in 3 seconds" test
  - Demo is too text-heavy; needs a visual or short video
  - Project isn't actually solving a problem outsiders feel
- Investigate before re-launching: ask 5 strangers (not friends, not coworkers — real strangers in a Discord or DM cold) what they think after looking at the repo for 60 seconds.

### "One person dunked on it in HN, comment got 30 upvotes"

- Don't argue. Engage substantively if there's a real critique; ignore if it's just dismissal.
- The dunk comment **does not kill** the post. What kills the post is *you* arguing back defensively for 6 comments.
- Edit your README to address the substantive critique before next launch.

### "Got featured on Trending for 2h then fell off"

- That happened because the post was trending the *day* and got bumped. Common.
- This is actually a success: you should now have ~100-500 stars and the project is in the GitHub graph for "people who looked at agent benchmarks".
- Plan a v0.3 milestone push in 2-4 weeks to ride the secondary wave.

---

## What 'good' looks like for v0.2

For a project at our maturity (4 stars baseline, no prior virality):

| Metric | "Decent" | "Good" | "Trending" |
|---|---:|---:|---:|
| Stars at T+24h | 30-100 | 100-300 | 300+ |
| HN best position | top 100 | top 30 | top 10 |
| Reddit best score | 50 upvotes | 200 upvotes | 500+ upvotes |
| Twitter impressions | 5k | 50k | 500k+ |
| GitHub clones | 50 | 300 | 1000+ |

**Realistic expectation**: "Decent" is the most likely outcome. "Trending" requires either (a) extraordinary timing (a major agent launches the same day), (b) one or more of `@simonw` / `@swyx` / `@karpathy` retweets, or (c) the variance angle accidentally becomes a meme. None can be forced.

**That's OK.** v0.2 is a foundation. The variance narrative compounds — every subsequent benchmark release ("we ran it again, here's what changed") gets free attention. Long-term reach > one-day spike.

---

## Specific recovery if Day 2 sweep produced numbers that don't support the headline

The headline is "we re-ran the same agent twice, got 0.0 then 0.7."

If after Day 2 multi-trial sweep this finding **disappears** (e.g. all agents now show low variance), do this:

1. **Don't fudge the data to keep the hook.** Transparency is the brand.
2. **Update findings.md** with the actual new finding from the data.
3. **Pick the next-most-dramatic finding** as the new headline. Likely candidates:
   - 7× per-axis gap on Tool Use (probably still holds)
   - Code commodity (almost certainly still holds at 1.00 for everyone)
   - Cost / latency 3-axis ranking (if you populated those axes)
4. **Postpone launch by 1-2 days** to give the new hook time to be reflected in README, leaderboard, social card, all 8-channel copy.
5. **Save the original variance finding as `docs/findings-v0.2-rc1.md`** with a note "did not replicate at scale; preserved for honesty".

This actually *strengthens* the project's credibility. "We had a finding, ran more trials, it didn't replicate, here's the corrected story" is exactly the kind of thing that makes HN respect you. It's the opposite of agent-vendor marketing.

---

## After the launch (whatever the outcome)

48 hours after launch:

1. **Write a short retrospective** in `docs/retros/v0.2-launch.md`. What worked, what didn't, what surprised you. Keep it for v0.3 launch.
2. **Thank the people who engaged**, especially the ones who critiqued. Email/DM, not public.
3. **Sweep the issues filed** during launch. Triage: real bugs, real feature requests, drive-by takes.
4. **Decide whether v0.3 ships in 4 weeks or 8 weeks** based on the energy you have left. Burn-out kills more OSS projects than indifference.
