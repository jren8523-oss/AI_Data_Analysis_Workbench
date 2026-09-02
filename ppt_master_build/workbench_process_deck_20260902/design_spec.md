<!-- ppt-master-schema: design-spec/v1 -->
# Workbench Process Deck - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | Workbench Process Deck |
| Canvas Format | PPT 16:9, 1280x720 |
| Page Count | 10 |
| Primary Language | zh-CN |
| Target Audience | 学生与课堂旁听者 |
| Communication Intent | 用精炼、客观的方式展示一个数据分析工作台从想法到成品的制作流程，并用少量页面说明成品如何使用。 |
| Desired Audience Outcome | 看完后能复述“先读材料、再定需求、选专家和技能、对齐、设计、实现、检查”的基本逻辑。 |
| Core Message / Ask / Action | 工作台不是一键生成，而是把制作过程拆成几个可检查的步骤。 |
| Delivery Context | 课堂展示或课后浏览，约 5-8 分钟 |
| Artifact Afterlife | 可编辑 PPT，用于课堂介绍和学生了解工作台 |
| Reading Mode | presentation |
| Content Strategy | 精炼改写；保留工具原名与关键截图；不展开复杂技术原理。 |
| Design Style | instructional + editorial |
| AI Image Acquisition Path | not applicable; use provided screenshots only |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | disabled - user confirmed simple visible slides only |
| Custom Animations | disabled - user confirmed simple visible slides only |
| Narration Audio | disabled |
| Created Date | 2026-09-02 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280x720 |
| viewBox | `0 0 1280 720` |
| Margins | 56 px minimum; 72 px preferred |
| Content Area | 72 48 1136 624 |

## III. Visual Theme

### Theme Style

- **Mode**: instructional
- **Visual style**: editorial
- **Theme**: 作品集式的制作复盘；用一条稳定的左侧信息轴、细分隔线和大标题组织内容。
- **Tone**: 清楚、克制、客观、带一点设计感。

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #F7F6F2 | 主页面底色 |
| Secondary background | #EEF1F2 | 截图底板和次级区域 |
| Primary | #1F6EA8 | 重点、步骤编号、界面相关强调 |
| Accent | #C76D3A | 少量章节标记和结论强调 |
| Secondary accent | #5C7A72 | 辅助标签和功能分类 |
| Body text | #171717 | 标题与正文 |
| Secondary text | #6E7476 | 说明、注释、来源标签 |
| Divider | #D4D7D8 | 细线、边界和页眉分隔 |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | clean editorial sans | Microsoft YaHei | Arial | sans-serif |
| Body | clean editorial sans | Microsoft YaHei | Arial | sans-serif |

- **Title stack**: Microsoft YaHei, Arial, sans-serif
- **Body stack**: Microsoft YaHei, Arial, sans-serif

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 24 |
| Title | 54 |
| Subtitle | 30 |
| Annotation | 18 |
| Kicker | 14 |
| Step detail | 21 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: 先用大标题说明本页任务，再用一张主图或一组短句完成解释。
- **Composition tendency**: 采用不对称的编辑式分栏；图片承担证据，文字承担解释。
- **Cross-page continuity**: 保留页眉编号、左对齐标题和细分隔线；封面与结尾更留白，内容页根据截图比例变化。
- **Spacing posture**: open with compact evidence blocks where screenshots require it.
- **Spacing anchors**: page margin 56 px, block gap 24 px, column gutter 32 px, corner radius 10 px, body leading 34 px.

## VI. Icon Usage Specification

- **Primary bundled library**: none
- **Brand-logo library**: none

| Icon Path | Suitable Scenarios |
| --- | --- |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| workbuddy-experts-skills.png | 2356x1644 | 1.43 | 展示可选择的专家与技能 | Screenshot | large evidence image with caption | adaptive | user | Existing | WorkBuddy 专家/技能页面 | native | evidence |
| grill-me-guide.png | 1724x406 | 4.25 | 解释需求追问工具 | Screenshot | wide strip above a short explanation | no-crop | user | Existing | 用户提供截图 | native | evidence |
| taste-skill-example.png | 1080x1623 | 0.67 | 展示审美 Skill 示例 | Screenshot | portrait comparison tile | adaptive | user | Existing | 用户提供截图 | native | evidence |
| ui-ux-pro-max-example.png | 1080x1402 | 0.77 | 展示审美 Skill 示例 | Screenshot | portrait comparison tile | adaptive | user | Existing | 用户提供截图 | native | evidence |
| frontend-design-example.png | 1080x1461 | 0.74 | 展示审美 Skill 示例 | Screenshot | portrait comparison tile | adaptive | user | Existing | 用户提供截图 | native | evidence |
| skill-comparison.png | 1080x1440 | 0.75 | 展示设计 Skill 对比 | Screenshot | secondary comparison tile | adaptive | user | Existing | 用户提供截图 | native | evidence |
| workbench-full.png | 2880x1480 | 1.95 | 展示完整工作台结构 | Screenshot | dominant wide screenshot with three callouts | adaptive | user | Existing | 用户提供截图 | native | hero_page |
| upload-data.png | 452x372 | 1.22 | 展示上传 CSV 数据 | Screenshot | small feature inset | no-crop | user | Existing | 用户提供截图 | native | feature |
| public-datasets.png | 1126x1194 | 0.94 | 展示公开数据源 | Screenshot | small feature inset | adaptive | user | Existing | 用户提供截图 | native | feature |
| bazhuayu-guide.png | 1116x882 | 1.27 | 展示八爪鱼采集流程 | Screenshot | small feature inset | adaptive | user | Existing | 用户提供截图 | native | feature |

## IX. Content Outline

### Part 1: 我如何做出工作台

#### Slide 01 - 我如何做出一个数据分析工作台

- **Audience move**: 从“这是什么”到“这是一条制作流程”。
- **Relationships**: 标题先于副标题；副标题补充主题；编号标记本页为开场。
- **Composition**: 大标题占据左侧；右侧以工作台局部或抽象界面色块作为视觉锚点；底部用一句话收束。
- **Title**: 我如何做出一个数据分析工作台
- **Core message**: 这份 PPT 展示的是制作逻辑，而不是某一次分析结果。
- **Content**: 副标题“从课程材料、需求对齐到界面实现与功能验收”；页脚“制作过程复盘 / 01”。

#### Slide 02 - 先让 AI 读懂课程材料

- **Audience move**: 从“我要做一个工具”到“工具要解决什么课程问题”。
- **Relationships**: 课程 PPT 是输入；AI 总结是中间理解；工作台需求是输出；顺序为输入→理解→需求。
- **Composition**: 左侧大号步骤编号和一句结论；右侧用三段横向流程文字连接输入、理解和需求。
- **Title**: 第一步：先把课程材料交给 AI
- **Core message**: 先让 AI 理解 10 个课程 PPT，再表述我要做什么。
- **Content**: “输入：10 个课程 PPT”；“处理：让 AI 总结课程中的数据分析任务”；“输出：明确需求——做一个可反复使用的数据分析工作台”。

#### Slide 03 - 选择专家和技能

- **Audience move**: 从“有了需求”到“知道让谁来协助完成”。
- **Relationships**: 专家负责工作方式；技能负责具体能力；两者共同服务工作台搭建。
- **Composition**: 左侧短文解释；右侧放 WorkBuddy 专家/技能页面截图，并用一个蓝色标注点出“工作台搭建师”。
- **Title**: 第二步：给 AI 配上合适的角色和能力
- **Core message**: Expert 决定怎么想，Skill 补充会什么。
- **Content**: “WorkBuddy 里可以选择不同专家和技能”；“我选择：工作台搭建师”；“再按需要挂载设计、追问和质量检查 Skill”。
- **Images**: 图片 `workbuddy-experts-skills.png`，展示不同专家与技能的选择空间。

#### Slide 04 - 对齐需求颗粒度

- **Audience move**: 从“有一个大概想法”到“把功能和边界说具体”。
- **Relationships**: 大致想法先出现；多轮追问逐步收窄；清晰需求作为后续设计和实现的依据。
- **Composition**: 上方放 `grill-me` 长截图；下方用三句短文解释“先提出大致想法→多轮追问→形成清晰构思”。
- **Title**: 第三步：先把需求问清楚
- **Core message**: 需求越具体，后面的界面和功能越不容易反复重做。
- **Content**: “工具：grill-me”；“作用：通过多轮提问，把功能、使用方式和交付结果对齐”；“结果：形成可以开始设计的清晰方案”。
- **Images**: 图片 `grill-me-guide.png`。

#### Slide 05 - 用 Skill 画界面

- **Audience move**: 从“知道要做什么”到“看到工具大概长什么样”。
- **Relationships**: 设计 Skill 是方法；不同 Skill 产生不同视觉取向；选择结果服务于工作台的使用场景。
- **Composition**: 三列或四列竖向截图对比；顶部统一标题；底部一句话说明“先构思，再让 AI 生成界面参考”。
- **Title**: 第四步：先设计界面，再开始实现
- **Core message**: 可以先构思界面，再用不同设计 Skill 生成视觉参考。
- **Content**: “frontend-design：偏前端设计与细节”；“UI-UX-PRO-MAX：偏界面结构与体验”；“taste-skill：偏整体审美”；“效果不同，但目的都是减少试错”。
- **Images**: 图片 `taste-skill-example.png`、`ui-ux-pro-max-example.png`、`frontend-design-example.png`、`skill-comparison.png`。

#### Slide 06 - 从规划到实现

- **Audience move**: 从“有了界面参考”到“工作台真正能运行”。
- **Relationships**: 功能规划先于 UI 搭建；UI 搭建先于功能填充；功能填充后进入质量检查。
- **Composition**: 一条横向四段流程；每段只有一个动词和一行解释；右下角用小结论强调“先骨架，后细节”。
- **Title**: 第五步：先搭骨架，再填功能
- **Core message**: 先把 UI 结构搭好，再让 AI 补上功能细节。
- **Content**: “规划功能：写说明文档，或边讨论边确定”；“搭 UI：在 Codex 里方便微调”；“填功能：让 AI 补上数据处理和交付逻辑”；“质量检查：用 karpathy 与 superpower 检查工程质量”。

#### Slide 07 - 这条流程的重点

- **Audience move**: 从“记住工具名”到“理解自己的制作逻辑”。
- **Relationships**: 制作步骤共同指向一个可复用工作台；每一步都有明确产物；最后由验证闭环。
- **Composition**: 左侧放一句大结论；右侧放 6 个极简步骤编号，形成从 01 到 06 的竖向索引。
- **Title**: 我的做法：把一次任务做成可复用工具
- **Core message**: 我不是让 AI 一键生成，而是让 AI 在每一步承担具体工作。
- **Content**: “读材料：建立课程背景”；“定角色：选择 Expert + Skill”；“做对齐：把想法问具体”；“画界面：先看结构和审美”；“写功能：从 UI 进入可运行工具”；“做检查：确认功能能用、结果可交付”。

### Part 2: 工作台怎么用

#### Slide 08 - 工作台整体怎么使用

- **Audience move**: 从“工作台如何制作”到“学生如何实际使用”。
- **Relationships**: 左栏提供数据；中栏选择分析；右栏承接结果；顺序为输入→分析→交付。
- **Composition**: 右侧或中央铺开完整工作台截图；左侧三行标注解释三栏关系。
- **Title**: Part 2：做出来以后，怎么用？
- **Core message**: 数据放左边，任务选中间，结果看右边。
- **Content**: “左栏：上传数据或选择数据源”；“中栏：选择想做的分析”；“右栏：查看结果和交付内容”。
- **Images**: 图片 `workbench-full.png`，作为本页主视觉。

#### Slide 09 - 数据从哪里来，结果怎么交付

- **Audience move**: 从“看懂三栏结构”到“知道常见入口和出口”。
- **Relationships**: 上传数据、公开数据库和八爪鱼都是数据入口；HTML 是结果出口；入口可替换，分析流程保持一致。
- **Composition**: 左侧放三张小截图；右侧用四行短说明对应“上传、公开数据库、八爪鱼、导出 HTML”。
- **Title**: 三种数据入口，一个交付出口
- **Core message**: 数据来源可以不同，但最后都回到同一个分析工作台。
- **Content**: “上传数据：拖入 CSV，数据不出浏览器”；“公开数据库：从统计法、统计局和常用数据库进入”；“八爪鱼：负责采集，采集后导出 CSV 回到工作台”；“交付结果：根据需要查看或导出 HTML”。
- **Images**: 图片 `upload-data.png`、`public-datasets.png`、`bazhuayu-guide.png`。

#### Slide 10 - 一句话总结

- **Audience move**: 从“听完流程”到“带走一句可复述的话”。
- **Relationships**: 制作逻辑与使用逻辑形成前后闭环；结论先于补充说明。
- **Composition**: 大留白结尾；左侧一句主结论，右下角用“制作→使用→交付”三个词收束。
- **Title**: 最后，我把 AI 组织成了一条制作流程
- **Core message**: 先理解问题，再选择能力；先设计结构，再实现功能；最后用结果验证工具。
- **Content**: “制作：读材料→定需求→选专家和技能→设计→实现→检查”；“使用：放入数据→选择分析→查看并导出结果”；“这就是我做工作台的基本逻辑。”

## X. Speaker Notes Requirements

- **Generation**: disabled
