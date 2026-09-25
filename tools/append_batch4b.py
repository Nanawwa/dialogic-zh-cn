# -*- coding: utf-8 -*-
"""第四批补充（4b）：规范化前缀匹配，处理尾部空格/换行差异。"""
import polib

PO = "addons/dialogic_zh_cn/translations/zh_CN.po"

# (规范化前缀, 完整中文译文)
T = [
    ("This unique identifier is based on the file name. You can change it in the Reference Manager.\nUse this name in timelines",
     "此唯一标识符基于文件名。可在引用管理器中更改。\n在时间轴中引用此角色时，请使用该名称。"),
    ("This unique identifier is based on the file name. You can change it in the Reference Manager.\nThis is what you should use in a jump event",
     "此唯一标识符基于文件名。可在引用管理器中更改。\n在跳转事件中引用此时间轴时，请使用该名称。"),
    ("Reference\nManager", "引用\n管理器"),
    ("No character opened.", "未打开任何角色。\n新建一个角色，或在文件系统中双击打开。"),
    ("Refresh", "刷新"),
    ("[font_size=25]🎉 New alpha, new stuff![/font_size]",
     "[font_size=25]🎉 新的 alpha，新内容！[/font_size]\n如果你一直在使用 Dialogic 2 的 alpha 版本，这次更新会让你兴奋。虽然还不是 beta，但我们越来越近了！和老往常一样，有问题或反馈最好到 [url=https://discord.gg/2hHQzkf2pX]emilios discord[/url] 交流。\n\n这个 alpha 为 Dialogic 带来了几个非常实用的新功能，以及一些语法变更和一次界面大改（还有非常非常多的 bug 修复）。\n"),
    ("Be careful. This will delete the addons/dialogic folder",
     "请务必小心。此操作会删除 addons/dialogic 文件夹并安装新版本，该文件夹内的所有自定义修改都会丢失。\n为保险起见，请使用版本控制！"),
    ("[center]Welcome to Dialogic, a plugin that lets you easily create stories and dialogs for your game!",
     "[center]欢迎使用 Dialogic——一个让你轻松为游戏创作故事与对话的插件！\n\n如果你是新手，请从创建时间轴或角色开始！"),
    ("The layout scene configured in the Layout editor is automatically",
     "布局编辑器中配置的布局场景，会在调用 Dialogic.start() 时自动实例化。根据你的游戏，你可能希望它在对话结束后被删除、被隐藏，或保留在场景中。"),
    ("Configure where dialogic looks for custom modules.",
     "配置 Dialogic 查找自定义模块的位置。\n\n你需要重启项目才能看到更改生效。"),
    ("Change this locale to test your game in a different language (only in-editor).",
     "更改此语言区域，可在编辑器内用其他语言测试游戏。\n等同于测试用的本地项目设置。"),
    ("Choose a folder to let Dialogic save CSV files in.",
     "选择一个文件夹，供 Dialogic 保存 CSV 文件。\n以“翻译文件夹内”方式保存时同样使用此设置。"),
    ("Decides how many CSV files will be created.",
     "决定创建多少个 CSV 文件。\n\n• “按类型”：为每种资源（时间轴、角色、术语表）各建一个 CSV 文件。例如 10 个时间轴会共用同一个 CSV。"),
    ("Decides where to save the generated CSV files.",
     "决定生成的 CSV 文件的保存位置。\n\n• “翻译文件夹内”：使用“翻译文件夹”。\n\n• “时间轴旁”：放在对应资源类型的文件夹里。"),
    ("Adds an empty line into per-project CSVs to differentiate between sections.",
     "在项目级 CSV 中插入空行以区分不同段落。\n\n例如，当出现新的术语表条目或时间轴时，会插入一个空行。"),
    ("This button will scan all timelines and generate or update their CSV files.",
     "此按钮会扫描所有时间轴并生成或更新其 CSV 文件。\n\nDialogic 的 CSV 文件会以“dialogic_”作为前缀。\n\n若“翻译文件夹”设置有误，此操作将被禁用。"),
    ("Godot imports CSV files as \".translation\" files.",
     "Godot 会把 CSV 文件导入为“.translation”文件。\n此按钮会把它们加入“项目设置 -> 本地化”。"),
    ("Be very careful with this button!",
     "使用此按钮请务必小心！\n\n它会尝试删除所有与 Dialogic 相关的“.csv”与“.translation”文件。带“dialogic_”前缀的 CSV 与翻译文件都会被视为 Dialogic 的文件。"),
    ("You have previously generated CSVs and translation files with different Translation Settings!",
     "你之前用不同的翻译设置生成过 CSV 与翻译文件！\n\n建议删除旧的 CSV 后按新设置重新生成。"),
    ("You are about to:",
     "你即将：\n-   删除所有带“dialogic_”前缀的 CSV。\n-   删除相关的 CSV 导入文件。\n-   删除相关的翻译文件。\n-   从时间轴和角色中移除翻译 ID。\n-   从“项目设置 -> 本地化”中移除所有带“dialogic”前缀的翻译。\n-   删除以“Glossary/”开头的“_translation_keys”与“entries”。"),
    ("No timeline opened.", "未打开任何时间轴。\n新建一个时间轴，或在文件系统中双击打开。"),
    ("Allows joining or leaving a character or updating its portrait, position, mirroring, z-index or animation.",
     "允许角色加入或离开，或更新其立绘、位置、镜像、Z 索引或动画。"),
    ("These settings are used for Leave and Join events if no animation is selected.",
     "当加入/离开事件未选择动画时，使用这些设置。\n\n角色立绘变化且未设置动画时，将播放交叉淡入淡出。"),
    ("Define the default behaviour (hide or disable) for choices that have a condition that isn't met.",
     "定义未满足条件的选项的默认行为（隐藏或禁用）。\n\n各选项可单独覆盖此设置。"),
    ("This is a fallback bubble, that is not actually connected to any character. In game use the following code to add speech bubbles to a character:",
     "这是一个后备气泡，并未实际绑定任何角色。在游戏中请用以下代码为角色添加气泡："),
    ("When enabled, some events (Text, Join, Leave, Choice) will store a log.",
     "启用后，部分事件（文本、加入、离开、选项）会记录日志。\n此外，默认布局会提供日志面板选项。"),
    ("Remembers whether events were already met in the timeline.",
     "记录事件是否已在时间轴中出现过。\n启用后会发出 \"Dialogic.History.visited_event\" 与 \"Dialogic.History.unvisited_event\" 信号。"),
    ("Stores the already-visited history in a global save file when an Auto-Save occurs.",
     "自动存档时，把已见历史存入全局存档文件。\n自动存档属于保存设置的一部分。"),
    ("Stores the already-visited history in a global save file when a normal Save occurs.",
     "普通存档时，把已见历史存入全局存档文件。\n可通过 Dialogic.Save.save 方法实现。\n此设置不受自动存档影响。"),
    ("Performs a save to a save slot using Dialogics built-in saving API.",
     "使用 Dialogic 内置的存档 API 保存到某个存档位。"),
    ("For easier debugging dialogic will only encrypt saves made by exported project.",
     "为便于调试，Dialogic 只对导出项目生成的存档加密。\n开启调试模式的导出项目，或在编辑器中运行时的存档不会加密。"),
    ("Each style consist of a list of layers and settings for each layer.",
     "每个样式由一组图层及各图层的设置组成。样式可以继承自其他样式（继承的样式只能覆盖其图层的设置）。"),
    ("Each layer is a scene and settings that will be applied to that scene.",
     "每个图层是一个场景，以及将应用到该场景上的设置。\n图层可以使用预制场景，也可以使用你自己制作的场景。"),
    ("The action that skips text and generally advances to the next event.",
     "用于跳过文本并推进到下一事件的输入动作。\n可在 项目设置 > 输入映射 中修改这些动作。"),
    ("If enabled the revealing of text can be skipped with the input action.",
     "启用后，文本的逐字显示可以随时被跳过。\n禁用时，只有文本显示完毕才能推进到下一事件。"),
    ("Delay before you can skip.", "可以开始跳过前的延迟。\n\n用于防止玩家把时间轴推进得过快。"),
    ("Delay before you can advance (if the text finishes revealing on its own).",
     "可以推进前的延迟（仅当文本自行完成显示时生效）。\n\n用于避免玩家本想跳过逐字显示、却因提前点击而看似在等待输入的情况。"),
    ("If enabled dialogic, new lines will be treated as [n] effects,",
     "启用后，Dialogic 会把换行视为 [n] 效果，\n看起来像在等待输入后再开始新的一段文本。"),
    ("Autoadvance is the concept of automatically progressing to the next event upon completing text display, usually after a certain delay.",
     "自动推进指文本显示完成后自动进入下一事件，通常会有一定延迟。\n\n你可以通过代码启用自动推进："),
    ("An additional delay per character or word can be added.",
     "可以按字符或按词追加额外延迟。\n\n注意：通过代码修改数值时，两种模式实际上可以同时生效。"),
    ("None", "无"),
    ("An ignored character will add no delay, this is useful to exclude interpunction and whitespaces.",
     "被忽略的字符不产生延迟，适合排除标点与空白。\n\n禁用时，将按整行文本长度计算延迟（先剔除 BBCode 标签）。"),
    ("While you would usually enable Auto-Advance via code,",
     "自动推进通常通过代码启用，\n勾选此项后会在开局默认启用。\n这种自动推进（系统级）只有通过代码禁用才会停止。"),
    ("Auto-Skip is the concept of automatically skipping Timeline Events to the next unread Text Event or Event demanding user inputs (e.g. Choice, Wait Input, and Text Input).",
     "自动跳过指自动跳过时间轴事件，直到下一条未读的文本事件，或需要玩家输入的事件（如选项、等待输入、文本输入）。"),
    ("The time until Auto-Skip will execute the next event.",
     "自动跳过执行下一事件前的等待时间。\n\n若设为 0.1 秒，则每个事件最多在该时间内完成。\n自定义事件也必须遵守该时间，内置事件已经处理好了自动跳过。"),
    ("Adds pauses after certain letters.",
     "在特定字母后插入停顿。\n\n每组可包含多个字母，这些字母（分别）之后都会加上相应时长的停顿。"),
    ("Interrupt = The next sound will stop the previous",
     "打断 = 下一音效会停止上一个\n重叠 = 多个音效可同时播放\n等待 = 上一个播放完毕后才会播放下一个"),
    ("Variables are a good way to keep track of all kinds of things during your game: The player name, their health or the state of the world, their relationships, quests, etc.",
     "变量非常适合在游戏中记录各种信息：玩家名字、生命值、世界状态、人际关系、任务等等。"),
    ("Filter variables", "过滤变量"),
]

po = polib.pofile(PO, wrapwidth=0)
done = {e.msgid for e in po if e.msgstr.strip()}
added = 0
for msgid in done and [] or []:
    pass

# 从 POT 找出仍未翻译的条目
POT = "addons/dialogic_zh_cn/translations/dialogic.pot"
pot = polib.pofile(POT, wrapwidth=0)
pending = [e.msgid for e in pot if e.msgid not in done and e.msgid.strip()]

applied = 0
unhit = []
for msgid in pending:
    n = msgid.rstrip()
    zh = None
    for pref, full in T:
        if n.startswith(pref):
            zh = full
            break
    if zh is None:
        # 精确（strip 后相等）
        for pref, full in T:
            if n == pref.strip():
                zh = full
                break
    if zh:
        po.append(polib.POEntry(msgid=msgid, msgstr=zh))
        applied += 1
    else:
        unhit.append(msgid)

po.save(PO)
po.save_as_mofile(PO.replace(".po", ".mo"))
print("本轮应用:", applied, "条 | 未覆盖:", len(unhit))
import json
json.dump(unhit, open("docs/pending_final2.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for u in unhit:
    print("  ?", repr(u)[:100])
