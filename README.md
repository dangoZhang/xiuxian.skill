# portrait.skill

把你的 Codex / Claude Code / OpenCode 运行文件，炼成一张看得见的协作画像。

`portrait.skill` 会读取真实会话日志，提炼你和 AI 的交互方式，然后发两类结果：

- 用户修仙画像
- AI 协作能力证书

如果你愿意继续修炼，它还会给出下一周期的突破任务。你跑完一轮新协作，再用新日志复测，就能看自己有没有破境。

## 这是什么

很多 AI 工具只展示模型上限。

`portrait.skill` 更关心另一件事：你和 AI 在真实工作里，到底配不配，卡在哪里，强在哪里，下一步该怎么变强。

它不看宣传页，只看运行文件本身：

- 你给目标是否清楚
- 你补上下文是否到位
- 你会不会持续迭代
- AI 有没有真的执行
- 双方有没有验证结果
- 遇到阻力后会不会换打法

最后把这些浓缩成一份可读、可复测、可成长的画像与证书。

## 它适合谁

- 想复盘自己和 AI 的协作方式
- 想做“周期性破境”，而不是一次性 prompt 碰运气
- 想把 AI 协作做成可追踪的个人能力
- 想把 Codex / Claude Code / OpenCode 的真实日志转成作品感更强的输出

## 当前可读的数据

首版重点支持：

- Codex 运行日志：`~/.codex/archived_sessions/*.jsonl`
- Claude Code 导出的 JSON / JSONL 会话文件
- OpenCode 的 JSON / JSONL 会话文件

其中 Codex 解析最稳，Claude Code / OpenCode 目前走适配器和 schema sniffing。后面有了更多真实样本，可以继续补强。

## 它会产出什么

你可以选择三种输出：

- `user`：只看用户修仙画像
- `assistant`：只看 AI 协作能力证书
- `both`：两张一起发

每次输出都包含：

- 当前等级
- 核心标签
- 判定依据
- 下一次突破任务

如果你有前后两个周期的运行文件，还可以直接做一次破境对比。

## 用法

先看本机默认会话目录：

```bash
python3 -m portrait_skill.cli scan
```

分析最新的 Codex 日志：

```bash
python3 -m portrait_skill.cli analyze --source codex --certificate both
```

指定某个文件做分析：

```bash
python3 -m portrait_skill.cli analyze \
  --path ~/.codex/archived_sessions/rollout-xxx.jsonl \
  --certificate user
```

输出 Markdown 报告和 JSON 摘要：

```bash
python3 -m portrait_skill.cli analyze \
  --path ./session.jsonl \
  --certificate both \
  --output ./report.md \
  --json-output ./report.json
```

对比前后两个周期，看有没有升级：

```bash
python3 -m portrait_skill.cli compare \
  --before ./cycle-1.jsonl \
  --after ./cycle-2.jsonl \
  --certificate both
```

## 示例

仓库里放了一个最小的演示样本：

```bash
python3 -m portrait_skill.cli analyze \
  --path examples/demo_codex_session.jsonl \
  --certificate both \
  --output examples/demo_report.md
```

## 画像逻辑

用户修仙画像关注：

- 目标清晰度
- 上下文供给
- 迭代修正力
- 验收意识
- 协作节奏

AI 协作能力证书关注：

- 执行落地
- 工具调度
- 验证闭环
- 上下文承接
- 补救适配

它不追求假精确分数。它追求的是一套稳定、直观、能指导下一轮行动的判断框架。

## 一个推荐周期

1. 完成一轮真实协作。
2. 把运行文件喂给 `portrait.skill`。
3. 拿到你的画像证书。
4. 按最弱两项去练一轮。
5. 用新日志再测一次，看自己是否破境。

这样你积累的就不只是“我好像更会用了”，而是一条能看见成长轨迹的协作修炼线。

## 安装

```bash
cd portrait.skill
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

也可以不安装，直接运行：

```bash
python3 -m portrait_skill.cli scan
python3 -m portrait_skill.cli analyze --source codex --certificate both
python3 -m portrait_skill.cli compare --before ./old.jsonl --after ./new.jsonl --certificate both
```

## 目录结构

```text
portrait.skill/
  portrait_skill/
    analyzer.py
    cli.py
    models.py
    parsers.py
    renderer.py
  examples/
    demo_codex_session.jsonl
    demo_report.md
  README.md
  SKILL.md
  pyproject.toml
```

## 隐私

这个项目不依赖服务端。

你可以全程在本地读取本地运行文件。若要公开演示，建议只提交脱敏日志或合成样本。

## Roadmap

- 多次运行记录的横向对比
- 跨周趋势线
- 更强的 Claude Code / OpenCode 专项适配
- 可直接分享的图片化证书
- 教练模式，把弱项自动转成训练任务

## 灵感来源

README 的结构刻意参考了 Open Skills 上这类“爆款 skill 项目”的写法：一句话钩子、明确数据来源、直接展示输出物、再把“它会改变什么”讲明白。

我参考的公开页面包括 `Ex.skill` 和 `Colleague.skill`。
