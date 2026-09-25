# -*- coding: utf-8 -*-
"""第四批增补：事件说明 / 多行 tooltip 长文（+约 100 条）。"""
import polib

POT = "addons/dialogic_zh_cn/translations/dialogic.pot"
PO = "addons/dialogic_zh_cn/translations/zh_CN.po"

# 短条目精确翻译
EXACT = {
    "This unique identifier is based on the file name. You can change it in the Reference Manager.":
        "此唯一标识符基于文件名。可在引用管理器中更改。",
    "Refresh": "刷新",
    "No character opened.": "未打开任何角色。",
    "No timeline opened.": "未打开任何时间轴。",
    "Shows or hides a background image or scene.": "显示或隐藏背景图片或场景。",
    "Calls a method on an autoload script or scene.":
        "调用某个 Autoload 脚本或场景上的方法。",
    "center": "居中",
    "Shows a clickable option. Should be grouped together with other choices. Contains events that are played when chosen. Can have a condition.":
        "显示一个可点击的选项。应与其他选项组合使用。包含被选中时执行的事件。可以带条件。",
    "Define the default behaviour (hide or disable) for choices that have a condition that isn't met.":
        "定义未满足条件的选项的默认行为（隐藏或禁用）。",
    "Choices can overwrite this setting individually.": "各选项可单独覆盖此设置。",
    "Clears current state like text, background, portraits, style or audio.":
        "清除当前状态，如文本、背景、立绘、样式或音频。",
    "Has no effect on gameplay, but can help organize your timeline.":
        "对游戏没有实际影响，但有助于整理时间轴。",
    "Allows playing the contained events only if the condition is true.":
        "仅在条件为真时执行所包含的事件。",
    "This is a fallback bubble, that is not actually connected to any character. In game use the following code to add speech bubbles to a character:":
        "这是一个后备气泡，并未实际绑定任何角色。在游戏中请用以下代码为角色添加气泡：",
    "Ends the timeline early. Not required at the timeline end.":
        "提前结束时间轴。时间轴末尾无需此事件。",
    "Performs an action on the simple history.": "对简单历史执行一项操作。",
    "Allows going to another timeline or jumping to a label event in this timeline.":
        "允许跳到其他时间轴，或跳到本时间轴中的标记事件。",
    "Provides a point to jump to with the jump event. Can be used to split a timeline into sections.":
        "提供一个供跳转事件使用的锚点。可用于把时间轴分成多个段落。",
    "Returns to the last jump event or ends the timeline (if no jump happened before).":
        "返回上一个跳转事件，或结束时间轴（若之前没有跳转）。",
    "Plays an audio file (sound effect or music) on one of the audio layers (configured in the settings).":
        "在某一音频层（在设置中配置）上播放音频文件（音效或音乐）。",
    "Changes to one of the styles configured in the style editor.":
        "切换到样式编辑器中配置的某一样式。",
    "Each style consist of a list of layers and settings for each layer.":
        "每个样式由一组图层及各图层的设置组成。",
    "Each layer is a scene and settings that will be applied to that scene.":
        "每个图层是一个场景，以及将应用到该场景上的设置。",
    "Displays text. Can be said by a character. Can contain all kinds of bbcode, text effects or variables.":
        "显示文本。可由角色说出。可包含各种 BBCode、文本效果或变量。",
    "The action that skips text and generally advances to the next event.":
        "用于跳过文本并推进到下一事件的输入动作。",
    "You can modify actions in the Project Settings > Input Map.":
        "可在 项目设置 > 输入映射 中修改这些动作。",
    "If enabled the revealing of text can be skipped with the input action.":
        "启用后，文本的逐字显示可以随时被跳过。",
    "Delay before you can skip.": "可以开始跳过前的延迟。",
    "Delay before you can advance (only if the text finishes revealing on its own).":
        "可以推进前的延迟（仅当文本自行完成显示时生效）。",
    "If enabled dialogic, new lines will be treated as [n] effects,":
        "启用后，Dialogic 会把换行视为 [n] 效果，",
    "An additional delay per character or word can be added.":
        "可以按字符或按词追加额外延迟。",
    "An ignored character will add no delay, this is useful to exclude interpunction and whitespaces.":
        "被忽略的字符不产生延迟，适合排除标点与空白。",
    "Adds pauses after certain letters.": "在特定字母后插入停顿。",
    "The default audio bus used by TypeSound nodes.": "打字音节点默认使用的音频总线。",
    "Default settings for named audio channels.": "命名音频通道的默认设置。",
    "Enter Channel Name": "输入通道名称",
    "Shows a text input field and stores it to a dialogic variable.":
        "显示一个文本输入框，并把输入存入 Dialogic 变量。",
    "Changes a dialogic variable or a variable from an autoload.":
        "修改一个 Dialogic 变量或来自 Autoload 的变量。",
    "Allows setting an audio file that will be played along the next text event.":
        "允许设置一个随下一条文本事件播放的音频文件。",
    "Waits a given amount of time. Can hide the textbox and be skippable.":
        "等待指定时长。可隐藏文本框，且可跳过。",
    "Waits until the next advance input action.": "等待下一次推进输入。",
    "Default scene": "默认场景",
    "Scale, Offset & Mirror": "缩放、偏移与镜像",
    "Typing Sound Mood": "打字音情绪",
    "Select Mood": "选择情绪",
    "Enter Mood Name": "输入情绪名称",
    "Filter Portraits": "过滤立绘",
    "Reference": "引用",
    "Character Prefix & Suffix": "角色前后缀",
    "Filter Entries": "过滤条目",
    "Enter unique name...": "输入唯一名称...",
    "Style": "样式",
    "Filter Variables": "过滤变量",
    "Resave all timelines": "重新保存所有时间轴",
    "Modules": "模块",
    "Translations": "翻译",
    "Saving": "保存",
    "History": "历史",
    "Editor": "编辑器",
    "Text": "文本",
    "Audio": "音频",
    "Portraits": "立绘",
    "Choices": "选项",
    "Refresh": "刷新",
    "Open": "打开",
    "Old": "原文本",
    "New": "新文本",
    "Filter Identifiers/Paths": "过滤标识符/路径",
    "Break": "中断",
    "Shortcuts": "快捷键",
    "Make the dialogic editor floating.": "将 Dialogic 编辑器设为浮动窗口。",
    "New Timeline": "新建时间轴",
    "New Character": "新建角色",
    "Filter Resources": "过滤资源",
    "Remove From List": "从列表移除",
    "Copy Identifier": "复制标识符",
    "Open in External Program": "用外部程序打开",
    "Play Timeline": "播放时间轴",
    "Play from here": "从此处播放",
    "Open Code": "打开代码",
    "Move up": "上移",
    "Move down": "下移",
    "Main": "主要",
    "Flow": "流程",
    "Visuals": "视觉",
    "Logic": "逻辑",
    "Other": "其他",
    "Emit dialogic signal with argument": "带参数发出 Dialogic 信号",
    "(Dictionary in body)": "（正文中为字典）",
    "Select Default Portrait": "选择默认立绘",
    "Enter Mood Name": "输入情绪名称",
    "Filter Portraits": "过滤立绘",
    "No character opened.": "未打开任何角色。",
}

# 前缀匹配翻译（长文/多行条目，msgid 可能有尾部差异）
PREFIX = [
    ("This unique identifier is based on the file name. You can change it in the Reference Manager.",
     "此唯一标识符基于文件名。可在引用管理器中更改。\n在跳转事件中引用此时间轴时，请使用该名称。"),
    ("No character opened.", "未打开任何角色。\n新建一个角色，或在文件系统中双击打开。"),
    ("Be careful. This will delete the addons/dialogic folder",
     "请务必小心。此操作会删除 addons/dialogic 文件夹并安装新版本，该文件夹内的自定义修改将全部丢失。\n为保险起见，请使用版本控制！"),
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
     "决定创建多少个 CSV 文件。\n\n• “按类型”：为每种资源（时间轴、角色、术语表）各建一个 CSV 文件。例如 10 个时间轴会放进同一个 CSV。"),
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
     "你之前用不同的翻译设置生成过 CSV 与翻译文件！\n\n建议删除旧的 CSV 后重新生成。"),
    ("You are about to:",
     "你即将：\n-   删除所有带“dialogic_”前缀的 CSV。\n-   删除相关的 CSV 导入文件。\n-   删除相关的翻译文件。\n-   从本地化设置中移除对应翻译。"),
    ("Doubleclick to load", "双击载入\n中键点击删除"),
    ("This unique identifier is based on the file name.",
     "此唯一标识符基于文件名。可在引用管理器中更改。\n在跳转事件中引用此时间轴时，请使用该名称。"),
    ("These settings are used for Leave and Join events if no animation is selected.",
     "当加入/离开事件未选择动画时，使用这些设置。\n\n角色立绘变化且未设置动画时，将播放交叉淡入淡出。"),
    ("Choices can overwrite this setting individually.", "各选项可单独覆盖此设置。"),
    ("When enabled, some events (Text, Join, Leave, Choice) will store a log.",
     "启用后，部分事件（文本、加入、离开、选项）会记录日志。\n此外，默认布局会提供日志面板选项。"),
    ("Remembers whether events were already met in the timeline.",
     "记录事件是否已在时间轴中出现过。\n启用后会发出 \"Dialogic.History.visited_event\" 与 \"Dialogic.History.unvisited_event\" 信号。"),
    ("Stores the already-visited history in a global save file when an Auto-Save occurs.",
     "自动存档时，把已见历史存入全局存档文件。\n自动存档属于保存设置的一部分。"),
    ("Stores the already-visited history in a global save file when a normal Save occurs.",
     "普通存档时，把已见历史存入全局存档文件。\n可通过 Dialogic.Save.save 方法实现。\n此设置不受自动存档影响。"),
    ("The Auto-Save is part of the Save settings.", "自动存档属于保存设置的一部分。"),
    ("For easier debugging dialogic will only encrypt saves made by exported project.",
     "为便于调试，Dialogic 只对导出项目生成的存档加密。\n开启调试模式的导出项目或在编辑器中运行时的存档不会加密。"),
    ("Advanced: Changes a setting from the Settings subsystem.",
     "高级：修改设置子系统（Settings）中的一项设置。"),
    ("Emits the Dialogic.signal_event signal with a given argument. You can react to this signal in your code by connecting to it.",
     "发出带有指定参数的 Dialogic.signal_event 信号。你可以在代码中连接该信号做出响应。"),
    ("Each style consist of a list of layers and settings for each layer.",
     "每个样式由一组图层及各图层的设置组成。样式可以继承自其他样式（继承的样式只能覆盖其图层的设置）。"),
    ("A layer can either be a premade scene or a scene you've made yourself.",
     "每个图层是一个场景及将应用到该场景的设置。\n图层可以使用预制场景，也可以使用你自己制作的场景。"),
    ("The action that skips text and generally advances to the next event.",
     "用于跳过文本并推进到下一事件的输入动作。\n可在 项目设置 > 输入映射 中修改这些动作。"),
    ("If enabled the revealing of text can be skipped with the input action.",
     "启用后，文本的逐字显示可以随时被跳过。\n禁用时，只有文本显示完毕才能推进到下一事件。"),
    ("Delay before you can skip.",
     "可以开始跳过前的延迟。\n\n用于防止玩家把时间轴推进得过快。"),
    ("Delay before you can advance (if the text finishes revealing on its own).",
     "可以推进前的延迟（仅当文本自行完成显示时生效）。\n\n用于避免玩家本想跳过逐字显示、却因提前点击而看似在等待输入的情况。"),
    ("If enabled dialogic, new lines will be treated as [n] effects,",
     "启用后，Dialogic 会把换行视为 [n] 效果，\n看起来像在等待输入后再开始新的一段文本。"),
    ("Autoadvance is the concept of automatically progressing to the next event upon completing text display, usually after a certain delay.",
     "自动推进指文本显示完成后自动进入下一事件，通常会有一定延迟。\n\n你可以通过代码启用自动推进："),
    ("Note: When changing values via code, you can actually use both modes simultaniously.",
     "按字符与按词两种模式可同时使用。\n\n注意：通过代码修改数值时，两种模式实际上可以同时生效。"),
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
    ("Set Variable", "设置变量"),
    ("Shows a text input field and stores it to a dialogic variable.",
     "显示一个文本输入框，并把输入存入 Dialogic 变量。"),
]

POT = "addons/dialogic_zh_cn/translations/dialogic.pot"
PO = "addons/dialogic_zh_cn/translations/zh_CN.po"
pot = polib.pofile(POT, wrapwidth=0)
po = polib.pofile(PO, wrapwidth=0)

existing = {e.msgid for e in po if e.msgstr.strip()}
added = 0
unhit = []
for e in pot:
    if e.msgid in existing or not e.msgid.strip():
        continue
    zh = None
    if e.msgid in EXACT:
        zh = EXACT[e.msgid]
    else:
        for pref, zh_t in PREFIX:
            if e.msgid.startswith(pref):
                zh = zh_t + e.msgid[len(pref):].lstrip(" ")
                # 前缀外的剩余部分若仍是成段英文则放弃自动拼接，仅在前缀
                # 几乎覆盖全文时使用
                rest = e.msgid[len(pref):].strip()
                if len(rest) > 40:
                    zh = None
                break
    if zh:
        po.append(polib.POEntry(msgid=e.msgid, msgstr=zh))
        existing.add(e.msgid)
        added += 1
    else:
        unhit.append(e.msgid)

po.save(PO)
po.save_as_mofile(PO.replace(".po", ".mo"))
print("追加:", added, "条 | 未命中:", len(unhit))
import json
json.dump(unhit, open("docs/pending_final.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for u in unhit[:30]:
    print("  ?", repr(u)[:110])
