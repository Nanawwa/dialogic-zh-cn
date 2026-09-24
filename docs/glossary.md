# 术语表与翻译规范

本文件是 `zh_CN.po` 的唯一翻译依据。所有译文必须先对齐术语表，
再谈通顺；条目之间不一致时，以本文件为准并回改术语表。

## 1. 核心概念（Dialogic 专有）

| 英文 | 中文 | 备注 |
|---|---|---|
| Timeline | 时间轴 | 剧情时间轴，不译"时间线" |
| Event | 事件 | |
| Character | 角色 | |
| Portrait | 立绘 | 视觉小说社区通用译法，不译"肖像" |
| Glossary | 术语表 | Dialogic 的名词释义功能 |
| Style | 样式 | |
| Layer | 图层 | 样式分层语境 |
| Layout | 布局 | |
| Textbubble / Text Bubble | 气泡文本 | 气泡对话样式 |
| Name Label | 名字标签 | 显示说话人名字的控件 |
| Next Indicator | 下一句指示器 | "点击继续"的箭头 |
| Advance | 推进 | 泛指"进入下一句对话" |
| Auto Advance | 自动推进 | |
| Auto Skip | 自动跳过 | |
| Manual Advance | 手动推进 | |
| Definition | 定义 | Dialogic 1 遗留概念，出现时保留 |
| Unique Identifier | 唯一标识符 | |
| Reference | 引用 | 资源引用，不译"参照" |
| Broken Reference | 失效引用 | 比"损坏的引用"更准确 |
| Reference Manager | 引用管理器 | |
| Shortcode | 短代码 | 文本事件语法标记 |
| Header / Body | 头部 / 主体 | 事件编辑器的两个区域 |
| Portrait Scene | 立绘场景 | |
| Portrait Group | 立绘分组 | |
| Mood | 情绪 | 打字音/口型相关的情绪分组 |

## 2. 模块与事件类型

| 英文 | 中文 | 备注 |
|---|---|---|
| Text | 文本 | 事件类型 |
| Character Event | 角色事件 | |
| Choice | 选项 | 不译"选择"，选项按钮语境 |
| Condition | 条件 | |
| Variable | 变量 | |
| Label | 标记 | Jump/Label 语境指时间轴锚点；控件 Label 才译"标签" |
| Jump | 跳转 | |
| Go To | 转至 | |
| Call | 调用 | |
| Signal | 信号 | |
| Setting | 设置 | 作为事件类型时指"修改变量设置" |
| Wait | 等待 | |
| Wait Input | 等待输入 | |
| Audio | 音频 | |
| Music | 音乐 | |
| Sound | 音效 | |
| Voice | 配音 | |
| Background | 背景 | |
| Save | 保存 | 存档语境译"保存" |
| End | 结束 | |
| Clear | 清空 | |
| Comment | 注释 | |
| Style (event) | 样式 | |
| Text Input | 文本输入 | |

## 3. Godot / 通用词（对齐 Godot 官方简中）

| 英文 | 中文 | 备注 |
|---|---|---|
| tooltip_text | 工具提示 | Godot 官方译法 |
| placeholder | 占位符 | |
| Add / Remove | 添加 / 移除 | |
| Rename | 重命名 | |
| Duplicate | 复制 | |
| Delete | 删除 | |
| Browse | 浏览 | |
| Open / Edit | 打开 / 编辑 | |
| Select | 选择 | |
| Filter | 过滤 | 列表筛选语境 |
| Search | 搜索 | |
| Load | 载入 | 读档语境译"载入"，区别于"加载"资源 |
| Save / Load (slots) | 存档 / 读档 | 槽位语境 |
| Enable / Disable | 启用 / 禁用 | |
| Export | 导出 | |
| Import | 导入 | |
| Override | 覆盖 | |
| Reset | 重置 | |
| Apply | 应用 | |
| Default | 默认 | |
| Custom | 自定义 | |
| Preview | 预览 | |
| Scene | 场景 | |
| Resource | 资源 | |
| Fade | 淡入淡出 | 双向；单向时按语义译"淡入/淡出" |
| Crossfade | 交叉淡入淡出 | |
| Volume | 音量 | |
| Loop | 循环 | |
| Audio Bus | 音频总线 | |
| Channel | 通道 | 音频/动画通道 |
| Scale / Offset / Mirror | 缩放 / 偏移 / 镜像 | 立绘变换三件套 |
| Real Scale | 实际缩放 | |
| Fit into preview | 适配预览 | |

## 4. 文风规范（避免机翻味的硬规则）

1. **按钮/菜单项**：动词短语，不带句号。"Add Portrait" → "添加立绘"。
2. **工具提示/说明文字**：完整句，句末带句号（与英文一致时才带）。
3. **不做主谓补全**：英文省略主语的句子，中文同样省略。
   "Can be changed in the settings." → "可在设置中更改。"
4. **括号占位符原样保留**："(No one)" → "（无）"，外层括号本土化，
   但 `%s`、`{var}`、`\n` 等格式占位一字不动。
5. **拼接片段**：`'Preview of "'` 这类与变量拼接的片段，译成
   `预览：\"`——优先用冒号结构回避中文语序问题；确无回避方案时
   在译文中保留拼接可行性。
6. **专有名词不译**：Dialogic、Godot、GDScript、CDN、Steam。
7. **不译之译**：纯符号、变量名、路径、单个功能词若翻成中文反而
   妨碍理解（如 "OK"、"ID"），保留英文。
8. **术语唯一**：同一概念全库只用一种译法；发现新概念先入术语表。
