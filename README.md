# html-presentation-microsite

给业务汇报用的 HTML 演示技能。它把提纲或 PRD 收成 16:9 幻灯片，适合会议室投影和季度复盘，而不是通用文档或简历。

## 它做什么

- 按内容量选择 showcase（6-8 页）或 report（10-15 页）
- 用 `deck.json` 固定听众、决策、判断句标题和版式
- 渲染一份不依赖外链的 HTML
- 用脚本检查占位符、溢出、重叠、近乎空白的内容页，以及 16:9 PDF

中文标题按行写入数据，不靠浏览器自动折行。视觉数值在 `assets/tokens.json`，布局在 `assets/deck.css`。

## 安装

把这个目录复制到本地技能目录：

```text
$CODEX_HOME/skills/html-presentation-microsite
```

技能名保持：

```text
$html-presentation-microsite
```

## 示例

`examples/lingchuan-q3/` 是一份虚构的零售协同季度复盘，数据标明为示例，不是客户材料。

```bash
python3 scripts/render_deck.py examples/lingchuan-q3/deck.json -o examples/lingchuan-q3/index.html
python3 scripts/check_deck.py examples/lingchuan-q3/deck.json --html examples/lingchuan-q3/index.html
python3 scripts/check_layout.py examples/lingchuan-q3/index.html --screenshot-dir /tmp/lingchuan-shots
python3 scripts/export_pdf.py examples/lingchuan-q3/index.html -o /tmp/lingchuan-q3.pdf --expect-slides 12
python3 -m unittest tests/test_deck.py
```

直接打开 `examples/lingchuan-q3/index.html` 即可放映。方向键、滚轮和底部圆点都能翻页。

## 格式边界

| 格式 | 状态 |
| --- | --- |
| HTML | 默认交付。单文件，离线可用 |
| PDF | Chrome 打印同一套 16:9 页面。命令通过才算可用 |
| 可编辑 PPTX | 不生成 |

没有 Chrome 时，`check_layout.py` 和 `export_pdf.py` 退出码为 2。静态检查通过不能代替浏览器里的版式检查。

## 文件

- `SKILL.md`：触发条件和原有汇报规则
- `references/deck-contract.md`：输入和叙事顺序
- `references/layouts.md`：版式
- `docs/kami-comparison.md`：和 Kami 的对照，包括这次改了什么、故意没改什么
- `examples/lingchuan-q3/`：完整中文示例

## 许可

MIT。设计原则参考了 Tw93 的 Kami，说明见 `NOTICE`。
