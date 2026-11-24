# 汇报契约

生成可放映的 HTML 之前先锁定这份契约。能从材料里推断的直接写入 `deck.json`，不要把缺口编成数字。

## 先写下来的六件事

| 字段 | 写什么 |
| --- | --- |
| `meta.audience` | 谁在听，例如事业部负责人 |
| `meta.venue` | 投影会、小范围评审，还是异步传阅 |
| `meta.decision` | 这场会要拍板的那一件事 |
| `meta.narrative` | 一句话故事：为什么现在做这个决定 |
| `meta.mode` | `showcase` 为 6-8 页，`report` 为 10-15 页 |
| `meta.formats` | `html`，需要打印时再加 `pdf` |

`mode` 由内容和 `SKILL.md` 的展示 / 汇报规则决定，脚本不会替你猜。

## 叙事顺序

1. 编辑：把材料收成判断句标题。只读 `title_lines` 应能串起整场会。
2. 排版：运行 `scripts/render_deck.py`，用现成版式，不从零写 CSS。
3. 检查：`check_deck.py` 必须通过。本机有 Chrome 时再跑 `check_layout.py`。

标题不要只写「背景」「目录」「总结」。封面、章节页和结尾可以留白；证据页必须有一块完整证据，不要在同一页混图表、清单和路线图。

## 缺口

未知事实放进 `meta.gaps`，并在某一页用原句写出来。检查脚本会确认这句话出现在成稿里。没有的指标留空，不要补一个看起来合理的数。

## 命令

```bash
python3 scripts/render_deck.py deck.json -o deck.html
python3 scripts/check_deck.py deck.json --html deck.html
python3 scripts/check_layout.py deck.html
python3 scripts/export_pdf.py deck.html -o deck.pdf --expect-slides 12
```

`check_deck.py` 不打开浏览器，检查结构、字数、占位符、外链和对比度。`check_layout.py` 才检查溢出、重叠、近乎空白的内容页、中文是否画出，以及键盘和页码跳转。没有 Chrome 时它退出码为 2，这时不能说版式已经通过。
