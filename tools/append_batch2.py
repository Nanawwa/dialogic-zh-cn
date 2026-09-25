# -*- coding: utf-8 -*-
"""把第二批译文追加进 zh_CN.po 并重编译。"""
import polib

T = {
    "Add Text event": "添加文本事件",
    "Add Text event with current character": "添加文本事件（当前角色）",
    "Add Text event with previous character": "添加文本事件（上一角色）",
    "Add Character join event": "添加角色加入事件",
    "Add Character update event": "添加角色更新事件",
    "Add Character leave event": "添加角色离开事件",
    "Add Jump event": "添加跳转事件",
    "Add Label event": "添加标记事件",
    "Move selected events/lines up": "上移所选事件/行",
    "Move selected events/lines down": "下移所选事件/行",
    "Search": "搜索",
    "Replace": "替换",
    "Play timeline": "播放时间轴",
    "Play timeline from here": "从此处播放时间轴",
    "Copy": "复制",
    "Paste": "粘贴",
    "Duplicate selected events/lines": "复制所选事件/行",
    "Cut selected events/lines": "剪切所选事件/行",
    "Toggle Comment": "切换注释",
    "Delete events": "删除事件",
    "Select All": "全选",
    "Select Nothing": "取消全部选择",
    "Select previous event": "选择上一事件",
    "Select next event": "选择下一事件",
    "Undo": "撤销",
    "Redo": "重做",
    "Background": "背景",
    "Call": "调用",
    "Choice": "选项",
    "Condition:": "条件：",
    "Clear": "清空",
    "Comment": "注释",
    "End Branch": "结束分支",
    "End": "结束",
    "Return": "返回",
    "Setting": "设置",
    "Signal": "信号",
    "Change Style": "更换样式",
    "Text Input": "文本输入",
    "Set Variable": "设置变量",
    "Wait for Input": "等待输入",
    "  Getting Started": "  快速入门",
}

PO = "addons/dialogic_zh_cn/translations/zh_CN.po"
po = polib.pofile(PO, wrapwidth=0)
existing = {e.msgid for e in po}
added = 0
for k, v in T.items():
    if k in existing:
        continue
    po.append(polib.POEntry(msgid=k, msgstr=v))
    added += 1
po.save(PO)
po.save_as_mofile(PO.replace(".po", ".mo"))
print("追加译文:", added, "条；词典总数:", len(po))
