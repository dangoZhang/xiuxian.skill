# portrait.skill

把你的 Codex / Claude Code / OpenCode / Cursor / VS Code 运行卷宗投入炉中，炼成一张修仙画像，照见你与 AI 的气脉、心法与境界。

`portrait.skill` 不看宣传页，只看真实运行文件。它会从一轮轮协作里提炼三件事：

- 你现在是什么修为，卡在哪一关
- 你的 AI 目前有多强，强在执行、工具、承接还是补救
- 下一轮该怎么闭关，才能真正破境

这不是一个“prompt 打分器”。

这是一个把运行日志炼成修炼结果的 skill。

## 这份 README 该有什么灵魂

像 `Ex.skill`、`Colleague.skill` 这类会爆的项目，核心从来不是“功能列表很全”。

核心是三步：

1. 一句话就让人明白“拿什么来炼”
2. 一句话就让人明白“炼完会得到什么”
3. 一句话就让人明白“这东西会改变我什么”

所以 `portrait.skill` 的灵魂也必须足够直接：

- 拿真实运行文件来炼
- 炼出修仙画像，或者 AI 协作能力证书
- 用下一周期复测，判断自己有没有破境

## 它炼的是什么

它炼的不是模型上限。

它炼的是你和 AI 在真实工作里的协作道行。

炉中会看这些东西：

- 你给目标是否清楚
- 你补上下文是否到位
- 你会不会持续迭代
- AI 有没有真的执行
- 双方有没有验证结果
- 遇到阻力后会不会换打法

最后出炉的，不是一次性的“这轮不错”。

而是一份可复测、可比较、可升级的协作画像。

## 适合谁来炼

- 想复盘自己和 AI 到底怎么配合的人
- 想把“会用 AI”变成可追踪能力的人
- 想做周期性闭关，而不是一次次随机碰运气的人
- 想把 Codex / Claude Code / OpenCode / Cursor / VS Code 的真实日志炼成更有作品感输出的人

## 可投入炉中的卷宗

当前支持的主要输入：

- Codex 运行日志：`~/.codex/archived_sessions/*.jsonl`
- Codex 新版会话目录：`~/.codex/sessions/**/rollout-*.jsonl`
- Claude Code 导出的 JSON / JSONL 会话文件
- OpenCode 的 JSON / JSONL 会话文件
- Cursor Chat 常见目录：`workspaceStorage/*/chatSessions/*.json`
- VS Code Chat / Copilot Chat 常见目录：`workspaceStorage/*/chatSessions/*.json`

当前炉火最稳的是 `Codex`。

`Claude Code / OpenCode / Cursor / VS Code` 已经支持默认目录发现和手动 `--path` 投喂，但不同版本 schema 会有差异，所以真实表现仍取决于你手里的会话文件结构。

## 出炉之物

你可以选择三种结果：

- `user`：只出你的修仙画像
- `assistant`：只出 AI 协作能力证书
- `both`：两炉同开，一次全出

如果你喜欢修仙叙事，这个项目会把你的协作状态炼成一张“修仙画像”，告诉你如今处在炼气、筑基、金丹、元婴还是更高境界。

如果你不喜欢修仙背景也没关系，我们会直接为你颁发一张“AI 协作能力证书”，用更直接的方式告诉你，你和 AI 现在处在什么协作层级，强项和短板分别是什么。

每次出炉都会带上：

- 当前等级
- 核心标签
- 判定依据
- 下一轮闭关任务

如果你拿前后两个周期的卷宗来炼，它还会额外告诉你：

- 这轮有没有破境
- 哪个维度涨得最快
- 哪个维度回落了
- 下轮应该主炼哪一门

如果运行文件里带了模型信息，它还会额外标出：

- 灵根
- 资质
- 炉主模型

## 一轮闭关怎么走

1. 完成一轮真实协作。
2. 把运行文件投给 `portrait.skill`。
3. 看你的修仙画像和 AI 协作能力证书。
4. 按最弱两项去练一轮。
5. 用新日志再炼一次，看自己是否破境。

这时你积累的就不是“我感觉自己更会了”。

而是一条能看到升阶轨迹的协作修炼线。

## 快速开炉

先看本机有哪些卷宗：

```bash
python3 -m portrait_skill.cli scan
```

只扫某一类来源：

```bash
python3 -m portrait_skill.cli scan --source codex
python3 -m portrait_skill.cli scan --source cc
python3 -m portrait_skill.cli scan --source cursor
python3 -m portrait_skill.cli scan --source vscode
```

分析最新的卷宗：

```bash
python3 -m portrait_skill.cli analyze --source codex --certificate both
python3 -m portrait_skill.cli analyze --source cc --certificate both
python3 -m portrait_skill.cli analyze --source cursor --certificate both
python3 -m portrait_skill.cli analyze --source vscode --certificate both
```

手动指定一份卷宗：

```bash
python3 -m portrait_skill.cli analyze \
  --path ~/.codex/archived_sessions/rollout-xxx.jsonl \
  --certificate user
```

导出 Markdown 和 JSON：

```bash
python3 -m portrait_skill.cli analyze \
  --path ./session.jsonl \
  --certificate both \
  --output ./report.md \
  --json-output ./report.json
```

对比前后两次闭关，看有没有破境：

```bash
python3 -m portrait_skill.cli compare \
  --before ./cycle-1.jsonl \
  --after ./cycle-2.jsonl \
  --certificate both
```

## 一个最小示例

仓库里带了一份最小演示样本：

```bash
python3 -m portrait_skill.cli analyze \
  --path examples/demo_codex_session.jsonl \
  --certificate both \
  --output examples/demo_report.md
```

## 炼化依据

用户修仙画像主要看：

- 目标清晰度
- 上下文供给
- 迭代修正力
- 验收意识
- 协作节奏

如果你走“能力证书”这条线，AI 协作能力证书主要看：

- 执行落地
- 工具调度
- 验证闭环
- 上下文承接
- 补救适配

它不追求假精确分数。

它追求的是一套稳定、直观、能指导下一轮行动的判断框架。

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

## 隐私

这个项目不依赖服务端。

你可以全程在本地读取本地运行文件。默认输出会把家目录自动脱敏成 `~`，其他绝对路径只显示文件名，避免把本机身份信息直接写进报告。若要公开演示，仍然建议只提交脱敏日志或合成样本。

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
