# Dialogic zh_CN — Dialogic 2 简体中文语言包

为 [Dialogic 2](https://github.com/dialogic-godot/dialogic)（Godot 4.5+ 对话插件）
提供**非侵入式**的简体中文编辑器界面。

不修改 Dialogic 任何源码。官方插件原样安装，本语言包作为独立插件叠加启用，
上游怎么更新都不冲突。

## 声明

- 本项目是**非官方**的第三方语言包，与 Dialogic 官方团队无隶属关系。
- Dialogic 2 及其全部原始界面文案、资源版权归
  [dialogic-godot/dialogic](https://github.com/dialogic-godot/dialogic)
  及其贡献者所有；本项目仅包含面向简体中文的翻译字符串（`zh_CN.po/.mo`）、
  由上游文案自动提取的翻译模板（`dialogic.pot`），以及本项目原创的加载与
  同步工具脚本，**不包含、不分发上游插件的任何源码或资源**。
  使用本语言包仍需自行安装官方 Dialogic 插件并遵守其
  [MIT 许可证](https://github.com/dialogic-godot/dialogic/blob/main/LICENSE)。
- 本项目自身的代码与译文同样以 MIT 许可证发布。
- 界面文案随上游版本变动，使用时请以 `tools/sync_upstream.py` 重新对齐；
  译文问题欢迎 issue 反馈，也可以考虑将改进回馈上游（上游的本地化支持
  进度以官方仓库为准）。

## 生效原理

经核实（阅读 Godot 引擎源码），Dialogic 界面文本的翻译分两种情况：

1. **引擎自动翻译**：`Label`/`Button`/`RichTextLabel` 的文本、输入框占位符、
   `PopupMenu` 菜单项等属性的 setter 在引擎内部就调用 `atr()`。
   本插件把 `zh_CN.mo` 注册进 `TranslationServer` 后，这部分自动变中文，
   约 250 条，零改动生效。
2. **注入翻译**：`tooltip_text`、窗口标题、对话框正文、inspector 属性标签
   在引擎中不走翻译。插件监听编辑器场景树，对入树节点查询词典并重新赋值。

## 安装

1. Godot **4.5+**，已安装并启用官方 `dialogic` 插件；
2. 将本仓库的 `addons/dialogic_zh_cn/` 复制进你的项目；
3. 在 项目设置 → 插件 中启用 **Dialogic zh_CN 简体中文语言包**；
4. 编辑器语言设为**简体中文**（编辑器 → 编辑器设置 → 常规 → 界面 → 编辑器语言）。

只在编辑器内生效，不影响游戏运行时行为。

## 翻译状态

以 `docs/coverage_report.json` 为准（对上游 `main` 分支自动统计）。
当前：504 / 515 条（97.9%），未翻译条目为代码示例与专有名词，保留英文。

术语以 [`docs/glossary.md`](docs/glossary.md) 为唯一依据，欢迎按 issue 提译法修正。

## 同步上游

上游更新后一条命令完成翻译跟进——重新提取、继承既有译文、报告差异：

```bash
python tools/sync_upstream.py
```

流程：下载上游 main 源码 → 重新生成 `dialogic.pot` → 用既有 `zh_CN.po`
自动合并 → 输出新增/失效条目清单。未变更条目的译文自动保留，
只需补翻新增条目。

## 贡献翻译

`addons/dialogic_zh_cn/translations/zh_CN.po` 是唯一译文源，
直接编辑（Poedit / VSCode PO 插件均可），然后重新编译：

```bash
python tools/build_po.py
```

- 新增/修改译法请先对照术语表；
- `msgid` 一律来自 `dialogic.pot`，不要手写新条目；
- 上下文信息在每条 `#.` 注释（层级 + 所在文件 + 字段类型）。

## 目录结构

```
addons/dialogic_zh_cn/
  plugin.cfg / plugin.gd        插件入口（加载翻译 + 注入层）
  translations/dialogic.pot     上游字符串模板（自动生成，勿手改）
  translations/zh_CN.po/.mo     译文与编译产物
tools/
  extract.py                    POT 提取器（分层规则见文件头注释）
  build_po.py                   po 合成与 mo 编译
  sync_upstream.py              上游同步一键流程
docs/
  glossary.md                   术语表与文风规范
  coverage_report.json          覆盖率报告（自动生成）
upstream/dialogic/              上游源码缓存（不入库）
```

## 已知边界

- 插件脚本尚未在 Godot 4.5 实机回归（开发环境无 Godot），
  首次启用若遇问题欢迎开 issue；
- 动态拼接文案（如 `Preview of "` + 名称）按片段翻译，个别语序是英文式的；
- 上游正在重构 Styles UX（维护者 2026-01 说明），相关文案未来会有变动，
  重跑 `sync_upstream.py` 即可跟进。

## 许可证

MIT（与上游一致）。翻译与工具脚本同许可证发布。
