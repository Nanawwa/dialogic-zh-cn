@tool
extends EditorPlugin

## Dialogic 2 简体中文语言包
##
## 生效机制分两层：
##  1. 读取 zh_CN.mo 并注册到 TranslationServer。Dialogic 界面中
##     Label/Button/RichTextLabel 的文本、占位符、菜单项等属性，
##     其 setter 在 Godot 引擎内部就走翻译（atr），注册后自动生效，
##     无需改动 Dialogic 任何源码。
##  2. 对引擎不自动翻译的属性做注入：Control.tooltip_text、Window.title、
##     AcceptDialog.dialog_text、inspector 的 EditorProperty 标签。
##     通过监听编辑器场景树的 node_added 信号，在新节点入树时
##     查询翻译并重新赋值。
##
## 说明：刻意不经过 Godot 的资源导入管线（.mo -> .translation），
## 而是直接解析 MO 字节格式构造 Translation。这样新装或更新语言包后
## 无需等待编辑器重新导入。MO 解析支持小端/大端两种字节序。
##
## 使用前提：Godot 编辑器语言设置为简体中文（或 auto 且系统为中文）。
## 本插件只在编辑器中生效，不影响游戏运行时的行为。

const TRANSLATION_PATH := "res://addons/dialogic_zh_cn/translations/zh_CN.mo"
const LOCALE := "zh_CN"

# MO 文件魔数（按小端读出时的两种排布）
const MO_MAGIC_LE := 0x950412de
const MO_MAGIC_BE := 0xde120495

var _translation: Translation = null


func _enter_tree() -> void:
	_translation = _load_mo(TRANSLATION_PATH)
	if _translation == null:
		push_warning("[dialogic_zh_cn] 翻译加载失败，界面将保持英文。详见上方日志。")
		return
	_translation.locale = LOCALE
	TranslationServer.add_translation(_translation)
	printerr("[dialogic_zh_cn] 已注册 %d 条翻译，TranslationServer locale=%s" % [
		_translation.get_message_count(), TranslationServer.get_locale()])
	get_tree().node_added.connect(_on_node_added)
	# 若本插件晚于 dialogic 启用，界面上已渲染的文本不会自动重译，
	# 对现有编辑器界面做一轮补翻。
	_apply_to_existing_tree.call_deferred()


func _exit_tree() -> void:
	if get_tree().node_added.is_connected(_on_node_added):
		get_tree().node_added.disconnect(_on_node_added)
	if _translation != null:
		TranslationServer.remove_translation(_translation)
		_translation = null


# ---------------------------------------------------------- MO 解析

## 直接解析 gettext MO 二进制，绕开编辑器导入管线。
func _load_mo(path: String) -> Translation:
	if not FileAccess.file_exists(path):
		push_warning("[dialogic_zh_cn] 找不到翻译文件: %s" % path)
		return null
	var buf := FileAccess.get_file_as_bytes(path)
	if buf.size() < 28:
		push_warning("[dialogic_zh_cn] 翻译文件损坏（过小）: %s" % path)
		return null

	var magic := _u32(buf, 0, false)
	var big := false
	if magic == MO_MAGIC_LE:
		big = false
	elif magic == MO_MAGIC_BE:
		big = true
	else:
		push_warning("[dialogic_zh_cn] 不是有效的 MO 文件: %s" % path)
		return null

	var count := _u32(buf, 8, big)
	# MO 头部：8=N 条目数，12=原文表偏移，16=译文表偏移，两张表互相独立
	var src_table := _u32(buf, 12, big)
	var dst_table := _u32(buf, 16, big)

	var translation := Translation.new()
	for i in range(count):
		var src_entry := src_table + i * 8
		var dst_entry := dst_table + i * 8
		var src_len := _u32(buf, src_entry, big)
		var src_off := _u32(buf, src_entry + 4, big)
		var dst_len := _u32(buf, dst_entry, big)
		var dst_off := _u32(buf, dst_entry + 4, big)
		if src_off + src_len > buf.size() or dst_off + dst_len > buf.size():
			continue
		var msgid := buf.slice(src_off, src_off + src_len).get_string_from_utf8()
		var msgstr := buf.slice(dst_off, dst_off + dst_len).get_string_from_utf8()
		if msgid.is_empty():
			continue  # 首条是 MO 元数据头
		# 注：gettext 的复数形式用 NUL 分隔 msgid/msgstr，但本语言包
		# Plural-Forms 为 nplurals=1（中文），polib 产出的 MO 中数据区
		# 实测不含任何 NUL 字节，无需按 NUL 切分。
		# 也因此这里禁止使用 String.chr(0) 构造 NUL 做防御性处理——
		# GDScript 编译器的常量折叠会在编译期求值出 NUL 并每处报一条
		# "Unicode parsing error"（Godot 4.7 实测）。
		if msgstr.is_empty():
			continue
		translation.add_message(msgid, msgstr)
	return translation


func _u32(b: PackedByteArray, off: int, big: bool) -> int:
	if big:
		return (b[off] << 24) | (b[off + 1] << 16) | (b[off + 2] << 8) | b[off + 3]
	return b[off] | (b[off + 1] << 8) | (b[off + 2] << 16) | (b[off + 3] << 24)


# ---------------------------------------------------------- 注入层

func _on_node_added(node: Node) -> void:
	_apply_translation.call_deferred(node)


## 对单个节点做注入翻译。tr() 找不到条目时返回原文，重新赋值等于无操作，
## 因此整体是幂等的，可以放心重复调用。
func _apply_translation(node: Node) -> void:
	if not is_instance_valid(node):
		return
	# tooltip：Control 的存取两端都不走引擎翻译
	if node is Control and node.tooltip_text != "":
		var tip := tr(node.tooltip_text)
		if tip != node.tooltip_text:
			node.tooltip_text = tip
	# 文本类属性：Dialogic 主界面在本插件之前加载，text 已定格英文。
	# 重新赋值会再次经过引擎 setter 的翻译路径，命中则变中文。
	# 用属性名动态判断以覆盖 Label/Button/RichTextLabel 等不同类；
	# tr() 查不到条目时返回原文，重新赋值等于无操作，用户输入内容不受影响。
	if node is Control and "text" in node:
		var txt: String = node.get("text")
		if txt != "":
			var t := tr(txt)
			if t != txt:
				node.set("text", t)
	# 窗口与对话框标题
	if node is Window and node.title != "":
		var title := tr(node.title)
		if title != node.title:
			node.title = title
	# 对话框正文
	if node is AcceptDialog and node.dialog_text != "":
		var text := tr(node.dialog_text)
		if text != node.dialog_text:
			node.dialog_text = text
	# inspector 属性控件的可读标签
	if node is EditorProperty and node.label != "":
		var label := tr(node.label)
		if label != node.label:
			node.label = label


func _apply_to_existing_tree() -> void:
	_walk(get_tree().root)


func _walk(node: Node) -> void:
	_apply_translation(node)
	# 让引擎自己的重翻译逻辑跑一遍：Button 的 xl_text、Label 等内部
	# 缓存都在 NOTIFICATION_TRANSLATION_CHANGED 时重算。
	node.notification(Node.NOTIFICATION_TRANSLATION_CHANGED)
	for child in node.get_children():
		_walk(child)
