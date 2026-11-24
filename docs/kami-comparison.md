# 和 Kami 的差距

对照仓库是 [tw93/Kami](https://github.com/tw93/Kami)，观察时的 `main` 为 `27177605ad0007bc29fa3f9c203c347aa91074e2`（2026-11-21）。许可证是 MIT，版权属于 Tw93。本仓库没有复制 Kami 的模板、脚本、色值或字体。

## 当时两边实际有什么

本仓库在改动前只有 `SKILL.md`、`references/prompt-template.md`、`references/slide-outline-template.md` 和 `agents/openai.yaml`。规则写了中文标题换行、卡片溢出和 showcase / report 两种页数，但没有内容文件、HTML 模板、检查脚本、示例或测试。

Kami 是面向 Agent 的通用排版系统，版本 1.20.0。`skills/kami/SKILL.md` 负责选模板和按需打开参考；`references/schemas/slides.json` 约束幻灯片内容；`references/deck-preflight.md` 和 `references/design.md` 第 8 节规定断言标题、一种证据、页边距和字号；`assets/templates/slides-weasy.html` 用 WeasyPrint 输出 PDF，默认页面是 `280mm 158mm`；`slides.py` 在明确要求时可编辑 PPTX。`scripts/build.py --deliver` 会检查占位符、页数、密度和孤行。它同时覆盖简历、信件、研报、社交卡片和落地页。

## 和本仓库定位有关的差距

| 观察到的差距 | 本次 |
| --- | --- |
| 只有提示词，没有可校验的 `deck.json` | 已加契约、schema 和校验器 |
| 中文换行和防溢出只写在规则里 | 标题行写入数据，CSS 和浏览器检查执行 |
| 没有可复用的 16:9 版式 | 已加两套主题、三种密度和 10 种汇报版式 |
| 没有离线单文件交付 | 渲染结果内嵌 CSS 和 JS，不请求外链 |
| 没有正反例和回归测试 | 已加示例、失败样例和 `tests/test_deck.py` |
| 格式边界没有写明 | HTML 是默认交付；PDF 由 Chrome 打印验证；不生成 PPTX |

## 有意没有照搬的部分

- 不把本仓库改成简历、信件或通用文档平台。
- 保留 10-15 页汇报里的章节页。Kami 的 `deck-preflight.md` 写明不用独立分隔页，本技能原来的长汇报结构需要章节重置。
- 不使用 Kami 的羊皮纸色 `#f5f4ed`、油墨蓝 `#1B365D`，也不使用仓耳今楷。本仓库色板是会议室青绿和展示金色，字体用系统中文栈。
- 不引入 WeasyPrint、python-pptx 或 Marp。可编辑 PPTX 没有实现，也不能从这次改动推断它可用。
- 不把 Kami 禁止中文括号的规则写成硬性错误。

## 还没做

- 没有像素级密度分析。空白检查看的是文字量和内容区高度。
- 没有把浏览器打印之外的 PDF 引擎做成依赖。
- 没有英文成稿示例。契约接受 `en`，但完整示例是中文业务汇报。
- 没有可编辑 PPTX。
