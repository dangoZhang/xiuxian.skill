# 修仙画像生成 Prompt

用于生成「修仙画像」分享图。目标是让用户自己的 LLM 或绘图模型按固定信息结构出图，不要丢字段，不要堆无意义纹样。

## 变量

- `{{title}}`：修仙画像
- `{{username}}`：用户名或道号
- `{{generated_at}}`：生成时间
- `{{realm}}`：境界，如金丹、元婴、化神
- `{{subtitle}}`：一句副题，如“开始把自己的做法封成 skill / 模板 / 模块”
- `{{summary}}`：观气判词，2 到 3 行
- `{{item1_term}}` / `{{item1_value}}` / `{{item1_detail}}`
- `{{item2_term}}` / `{{item2_value}}` / `{{item2_detail}}`
- `{{item3_term}}` / `{{item3_value}}` / `{{item3_detail}}`
- `{{item4_term}}` / `{{item4_value}}` / `{{item4_detail}}`
- `{{item5_term}}` / `{{item5_value}}` / `{{item5_detail}}`
- `{{item6_term}}` / `{{item6_value}}` / `{{item6_detail}}`
- `{{growth}}`：破境机缘，一句话

## Prompt

请生成一张 3:4 竖版中文海报，主题为“修仙画像”，风格是赛博修仙卷轴感，高级、克制、干净，不要廉价玄幻海报感。

整体要求：

1. 画面是深色背景上的一张暖金色符箓卷轴，中心是一张完整的证像卡，不是散乱拼贴。
2. 标题必须是“{{title}}”，置于顶部中央，字体偏书卷气，但整体排版现代、利落。
3. 标题下方有一行副题：“{{subtitle}}”。
4. 顶部信息条需要并列展示：
   - 道号：{{username}}
   - 生成时间：{{generated_at}}
5. 中央主视觉是大号境界字：“{{realm}}”，下方小字“当前境界”。
6. 境界区下面放一个“观气判词”信息区，内容是：{{summary}}。
7. 下半部分必须是 2 列 3 行、共 6 个信息格，字段依次为：
   - {{item1_term}}：{{item1_value}}，说明 {{item1_detail}}
   - {{item2_term}}：{{item2_value}}，说明 {{item2_detail}}
   - {{item3_term}}：{{item3_value}}，说明 {{item3_detail}}
   - {{item4_term}}：{{item4_value}}，说明 {{item4_detail}}
   - {{item5_term}}：{{item5_value}}，说明 {{item5_detail}}
   - {{item6_term}}：{{item6_value}}，说明 {{item6_detail}}
8. 最底部单独放一条“破境机缘”：{{growth}}。

视觉要求：

- 以卷轴、符箓、印泥、朱砂、金墨、留白这些明确修仙元素为主。
- 可以有轻微云气、阵纹、纸张肌理，但必须服务信息层级。
- 不要龙凤、人物立绘、武器、火焰、光污染、无意义八卦纹满屏乱铺。
- 文字必须清晰、可读、层级明确，不能重叠，不能挤压。
- 所有信息格必须对齐，标题、正文、说明三层基线统一。
- 颜色以深棕、暖金、朱砂、米纸色为主，避免脏乱和俗艳。

禁止项：

- 不要生成看不清的小字。
- 不要让信息块高低不齐。
- 不要加入和信息无关的装饰图案。
- 不要把画面做成游戏 UI 或小说封面。

