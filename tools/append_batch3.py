# -*- coding: utf-8 -*-
"""第三批增补：标签页标题 / Tree 列头 / 多行帮助文本等（+65 条）。"""
import polib

T = {
    "Timeline": "时间轴",
    "Layouts": "布局",
    "Variables": "变量",
    "Scale:": "缩放：",
    "Offset:": "偏移：",
    "Mirror:": "镜像：",
    "Nicknames": "别名",
    "Description": "描述",
    "Rename": "重命名",
    "Duplicate": "复制",
    "Delete": "删除",
    "Prefix": "前缀",
    "Suffix": "后缀",
    "Close": "关闭",
    "Use": "使用",
    "Everywhere": "所有位置",
    "Add/Save": "添加/保存",
    "State": "状态",
    "Identifier": "标识符",
    "Resource Path": "资源路径",
    "Install": "安装",
    "Documentation": "文档",
    "Features": "功能",
    "Tools": "工具",
    "Extensions": "扩展",
    "Reload": "重新加载",
    "Name:": "名称：",
    "Complex": "复杂",
    "Create": "创建",
    "Basics": "基础",
    "Testing": "测试",
    "Actions": "动作",
    "Labels": "标记",
    "SaveLoad": "存读档",
    "Paused": "已暂停",
    "Join": "加入",
    "Wait:": "等待：",
    "Leave": "离开",
    "Cross-Fade": "交叉淡入淡出",
    "Behaviour": "行为",
    "Instantly": "立即",
    "Hide": "隐藏",
    "Disable": "禁用",
    "Confirm": "确认",
    "Glossaries": "术语表",
    "Defaults": "默认值",
    "Color": "颜色",
    "Entries": "条目",
    "Alternatives": "备选",
    "Title": "标题",
    "Extra": "额外",
    "Enabled": "已启用",
    "Autosave": "自动存档",
    "Style:": "样式：",
    "Style": "样式",
    "Layers": "图层",
    "Info:": "信息：",
    "Appended": "已追加",
    "Auto-Advance": "自动推进",
    "Auto-Skip": "自动跳过",
    "Auto-Pauses": "自动暂停",
    "Mode:": "模式：",
    "Interrupt": "打断",
    "Overlap": "重叠",
    "Await": "等待",
    "File/Folder:": "文件/文件夹：",
    "Pitch:": "音调：",
    "Skip:": "跳过：",
    "Default Value": "默认值",
}

POT = "addons/dialogic_zh_cn/translations/dialogic.pot"
PO = "addons/dialogic_zh_cn/translations/zh_CN.po"
pot = polib.pofile(POT, wrapwidth=0)
po = polib.pofile(PO, wrapwidth=0)

existing = {e.msgid for e in po if e.msgstr.strip()}
added = 0
for k, v in T.items():
    if k in existing:
        continue
    po.append(polib.POEntry(msgid=k, msgstr=v))
    added += 1

# BBCode 长文（首页轮播）：保留全部 BBCode 标签结构，只译文字
LONG_PREFIX = "[i]You can[/i] [b]create custom[/b] events"
for e in pot:
    if e.msgid.startswith(LONG_PREFIX) and e.msgid not in existing:
        src = e.msgid
        zh = (src
              .replace("[i]You can[/i] [b]create custom[/b] events, [i][b]subsystems, text effects and even editors for[/b][i] [code]dialogic!",
                       "[i]你可以[/i] [b]创建自定义[/b]事件、[i][b]子系统、文本效果，甚至为[/b][i] [code]Dialogic 打造编辑器！"))
        if zh != src:
            po.append(polib.POEntry(msgid=src, msgstr=zh))
            added += 1

# 扩展系统警告长文
WARN_PREFIX = "[color=yellow]Warning: Extension <name> is the same as an existing subsystem."
for e in pot:
    if e.msgid.startswith(WARN_PREFIX) and e.msgid not in existing:
        zh = e.msgid.replace(
            "[color=yellow]Warning: Extension <name> is the same as an existing subsystem. If you do not intend to override the base subsystem, choose a new name.",
            "[color=yellow]警告：扩展 <name> 与现有子系统同名。若并非有意覆盖该基础子系统，请换一个名称。")
        if zh != e.msgid:
            po.append(polib.POEntry(msgid=e.msgid, msgstr=zh))
            added += 1

po.save(PO)
po.save_as_mofile(PO.replace(".po", ".mo"))
print("追加:", added, "条")
