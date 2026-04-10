# 宣发分析与宣传帖

目标只保留三件事：

- 蒸馏你的 `vibecoding` 能力
- 给出一张可晒的修炼卡
- 让你下一轮继续修炼，并看见破境

## 同类项目在怎么赢

- `vercel-labs/skills` 目前约 `13.5k stars`。README 第一屏直接写 “The CLI for the open agent skills ecosystem”，下一行就是 “Supports OpenCode, Claude Code, Codex, Cursor, and 41 more”，然后立刻给 `npx skills add`。这类仓库赢在分发 friction 低。
- `anthropics/skills` 目前约 `114k stars`。它先用一句话解释 “Skills are folders of instructions, scripts, and resources...”，再马上给 Claude Code / Claude.ai / API 的真实入口。官方信任感和入口清晰度都非常强。
- Vercel 在 2026-02-20 的 `Skills Night` 里给出过生态规模：`69,000+ skills`、`2 million skill CLI installs`。这说明“可复用 agent 能力包”本身就有很强增长势能。
- Vercel 自己的 agent eval 也很直白：`Skill (default behavior)` 通过率 `53%`，加显式指令后到 `79%`，`AGENTS.md docs index` 到 `100%`。结论很明确，skill 要配一条常驻触发语。
- Cursor 产品页已经把 skills 写成真实入口：`discover and run specialized prompts and code`。VS Code 文档则明确把 skills 定义为 `package multi-step capabilities`，并说明任务匹配时会按需加载。用户会期待“装完就能直接叫出来”，不接受一长段手工教程。

## 对修仙.skil 的直接要求

- 第一屏必须先放结果图，先让人想试。
- 第二屏只讲一句话卖点，不讲散文。
- 明确区分“支持安装的宿主”和“支持读取的卷宗来源”。
- 明确支持“全量会话”与“指定时间窗”，并说明默认取稳定高位，不吃单次极端值。
- 给出能直接复制的自然语言用法，少给底层命令。
- 给宿主一条常驻触发语，减少 skill 被漏调的概率。
- 修仙味可以浓，技术词不能丢；真实性来自卷宗、时间窗、token、模型、记忆对比。

## 这一轮已经补上的点

- 新增了 [AI 术语 / 修仙词表](./lexicon.md)，把正式词、废弃词和兼容层分开。
- README 里把“宿主安装”和“卷宗来源”拆开写，避免再把 Cursor / VS Code 讲混。
- README 里加入了时间窗示例，强调可以读全部会话，也可以只读某段时间。
- README 和 SKILL 都加入了宿主常驻引导语，减少 skill 不触发的问题。
- README 的安装方式改成优先 `npx skills add`，更贴近当前爆款 skill 项目的实际分发方式。

## 建议放进宿主的常驻一句

可放进 `AGENTS.md`、`CLAUDE.md`、Copilot instructions 或类似的常驻规则里：

```md
当用户想看最近与 AI 的协作方式、指定时间窗内的修为、和上次相比有没有破境，或想生成可分享的结果图时，优先调用 修仙.skil。先读取真实卷宗并判断境界与等级，只有用户明确要分享图时才生成修仙卡。
```

## 宣传帖

### GitHub 发布帖

做了个 `修仙.skil`。

它不看自述，只读 Codex、Claude Code、OpenCode、OpenClaw、Cursor、VS Code 的真实运行卷宗，把你这一段时间的 `vibecoding` 轨迹炼成一张修炼卡。

你会直接看到：

- 修到了哪一层
- 当前是 L 几
- 这层人到底强在哪
- 下一轮该怎么破境

还能记住上次评测，下次直接告诉你是涨功、停滞，还是破境。

适合拿来晒，也适合拿来复盘。

### X / 即刻短帖

做了个有点中二但很实用的东西：`修仙.skil`

它会读你真实的 agent 卷宗，蒸馏你最近的 `vibecoding` 能力，再给你一张修炼卡。

不靠自评和问卷，直接从真实会话里炼出来。

而且它会记住上次结果。下次再测，直接看你有没有破境。

### 小红书 / 朋友圈长帖

最近把一个一直想做的 idea 做出来了，叫 `修仙.skil`。

我越来越觉得，大家和 AI 协作的关键差距，是“已经修到了哪一层”。会不会用只是起点。有人还停在单轮问答，有人已经能把 workflow、tools、multi-agent orchestration 跑成稳定法门。

所以我做了个 skill，直接去读真实卷宗，不靠自述，把一段时间里的协作轨迹炼成一张修炼卡。上面会写你当前的境界、L1-L10 等级、能力判词、破境之法，还会带上 token、样本规模、模型信息这些真实依据。

更重要的是，它会记住你上一次的结果。过一周、一个月，再炼一次，就能直接看到自己有没有涨功、停滞，还是破境。

我现在最喜欢它的一点，是它把“和 AI 协作”从一句空话，变成了一个能持续修炼、持续复盘、还能直接晒出来的东西。

## 宣发时要避免

- 先讲世界观，再讲结果图。
- 把 README 写成教程长文。
- 用一堆 badge 占掉首屏，却不给结果。
- 把“安装 skill”与“读取卷宗来源”讲混。
- 对外宣传还在讲旧的双卡、画像、证书。
- 只讲修仙，不给 token、模型、时间窗、会话数这些真实依据。

## 参考

- [vercel-labs/skills](https://github.com/vercel-labs/skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [Vercel: AGENTS.md outperforms skills in our agent evals](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)
- [Vercel: Skills Night: 69,000+ ways agents are getting smarter](https://vercel.com/blog/skills-night-69000-ways-agents-are-getting-smarter)
- [Cursor Product](https://cursor.com/product)
- [VS Code Customization](https://code.visualstudio.com/docs/copilot/concepts/customization)
