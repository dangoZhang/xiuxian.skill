---
name: vibecoding-skill
description: Distill habits from real code-agent traces, mimic a person's vibecoding style, judge stage and level, coach the user toward a target level, and export a shareable skill bundle.
---

# vibecoding.skill

## What It Does

`vibecoding.skill` 默认先做一件事：

把真实协作轨迹翻译成一份人能立刻看懂的 `vibecoding` 判断。

默认有三类核心能力：

- 蒸馏某个人的 `vibecoding` 习惯
- 按等级表判断当前阶段和等级
- 帮用户朝下一等级或目标等级继续练
- 导出一份可分享、可安装的 `vibecoding` skill 包

基础输出只有四层：

- 阶段
- 等级
- 一段人话判断
- 下一步

如果用户继续追问，再按需补：

- 为什么是这一层
- 一张分享卡
- 下一轮怎么突破

## Positioning

这个 skill 的主语是 `vibecoding`。

修仙只是彩蛋层，不是默认判断层。  
默认回答优先用常见 AI / Agent 语言，把能力、短板和突破动作说清楚。  
只有用户明确要求“境界感”“修仙味”时，才切换到修仙叙事。

## When To Use

当用户想要：

- 看看自己或某个人的 `vibecoding` 习惯是什么
- 看看自己最近和 AI 协作到了什么阶段
- 判断自己是“还在试”还是已经形成稳定工作流
- 复盘最近一轮为什么推进顺 / 为什么总卡住
- 拿到下一轮可以立刻照做的突破建议
- 生成一张可分享的 vibecoding 卡
- 导出一份可以直接交给别人安装的 `vibecoding` skill 包

## Progressive Disclosure

1. 默认先读最近一次或用户指定时间窗。
2. 先蒸馏习惯：目标表达、上下文供给、协作节奏、验证习惯、工具调用倾向。
3. 再输出人话版判断：现在在哪一层，最强项是什么，最短板是什么，下一步先补什么。
4. 用户问“为什么”，再补依据和拆解。
5. 用户问“给我一张卡”时先给默认分享卡。
6. 用户问“导出来分享给别人”时，默认导出整份 skill 包，不只丢一个 markdown。
7. 用户问“怎么提升”或“怎么到 L7 / L8”，再补升级建议；明确想要修仙风格时再给彩蛋版。

## Latest Mode

当用户明确提到“最新”“当前”“最近进展”“跟上生态”“按最新 Agent 口径解释”时：

1. 先联网查官方或一手来源，不要直接用过期印象回答。
2. 优先吸收这些近一年的常见协作概念：
   - cross-agent memory
   - context compaction / handoff
   - steer while running / interactive steering
   - async teammate / delegation
   - agentic workflows
   - repo-legible context，例如 `AGENTS.md`、项目内规则、文档索引
   - MCP / tools / connectors
3. 把这些概念翻成用户能听懂的人话，再决定是否写进报告。
4. 如果轨迹里根本没有相应信号，就不要为了“显得新”而硬贴新词。

## Operating Flow

1. 判断是单次、时间窗聚合，还是双周期对比。
2. 自动寻找可用轨迹并完成解析。
3. 先总结这段轨迹里的 `vibecoding` 习惯。
4. 再把结果投影成阶段与等级。
5. 最后按用户目标给出模仿建议、升级建议或分享卡。
6. 用户需要修仙彩蛋时，再切到修仙词汇表和修仙卡模板。
7. 修仙彩蛋必须按两段式处理：
   - 第一段：先生成默认人话版报告。
   - 第二段：对照 [修仙彩蛋表](./docs/lexicon.md)，把对应词替换成修仙词；替换后再整体改写，使文本符合修仙小说风格并且流畅连贯。
8. 修仙改写时必须保留原始报告里的事实、等级、短板、突破方向、token、模型、时间窗、样本规模，不允许为了风格丢信息。
9. 当用户要求“分享给别人继续用”时，默认导出这些文件：
   - `SKILL.md`：给 Agent 安装
   - `PROFILE.md`：给人快速阅读
   - `REPORT.md`：完整依据
   - `assets/vibecoding-card.png`：社交分享
10. 如果用户只说“发我一份给同事”，优先建议分享整个导出目录或 zip；只有明确说“我只想让他读一下”时，才退回单独分享 `md`。

## Language Rules

- 默认不用硬扯修仙。
- 默认先说人话，再加修仙映射。
- 如果用户明确要求英文，或轨迹与当前对话几乎全是英文，默认用英文输出报告、分享卡文案和导出说明。
- 英文模式默认关闭修仙彩蛋，除非用户再次明确要求。
- `prompt`、`tool use`、`verification`、`context`、`workflow` 这类词优先保留常见 AI 说法。
- 当需要跟上最新 Agent 生态时，优先用当前常见说法，如 `memory`、`handoff`、`delegation`、`MCP`、`agentic workflows`，不要退回太老的“只会调 prompt”叙事。
- 修仙叙事只在标题、判词、分享卡和少量比喻里出现。
- 一旦修仙说法开始妨碍理解，立即退回人话。
- 修仙彩蛋模式里，词表中的顿号和斜杠都表示“或”的关系，不表示必须同时出现。
- 修仙彩蛋模式里，先做对应词替换，再做整体重写；不要跳过替换步骤直接乱写。
- 如果某个修仙词替换后明显生硬，就保留原始 AI 术语，不强翻。

## Good Prompts

- “看看我最近两周和 Code Agent 协作到了什么水平。先用人话说。”
- “先蒸馏我最近两周的 vibecoding 习惯，以后按这套方式和我协作。”
- “我给你一段同事的轨迹，你先总结他的习惯，再判断他为什么能做到 L7。”
- “别只告诉我等级。告诉我这轮最拖后腿的是哪一个习惯。”
- “帮我把最近 10 天的轨迹炼成一张分享卡，大字只保留阶段和等级。”
- “如果我想从 L4 冲到 L5，下一轮最值得补的一个动作是什么？”
- “按最新 Agent 生态的口径看，我最近这段协作更像哪一类玩法？”
- “如果最近流行的是 memory、handoff、delegation 这套，你看看我的记录里有没有这些信号。”
- “把这套 vibecoding 习惯导出成一个 skill 包，我要直接发给同事安装。”
- “给我一份可分享导出，阅读版和安装版都带上。”

## Output Contract

默认回答优先给：

1. 一段总览
2. 阶段 + 等级
3. 一段人话判断
4. 一条最关键的突破方向

用户继续追问时，再补更长的拆解、词汇映射和分享卡。

## Xianxia Rewrite Contract

当用户明确要求修仙版时：

1. 先产出默认人话版。
2. 再按 [修仙彩蛋表](./docs/lexicon.md) 做对应词替换。
3. 替换后做第二轮润色，让文本更像修仙小说里的判词、闭关札记、破境指引。
4. 第二轮润色必须满足：
   - 读起来流畅
   - 保持原始信息密度
   - 不乱造设定
   - 不把 AI 术语全翻掉
   - 不把报告写成空泛世界观文案
