@tool
extends EditorPlugin

## Dialogic 2 简体中文语言包
##
## 实现方式（刻意不依赖 TranslationServer）：
## 实测在 Godot 4.7 编辑器进程里，无论项目设置原生加载还是运行时
## add_translation，TranslationServer.translate 都查不到插件翻译
## （域机制对编辑器 UI 不生效）。因此本插件把 zh_CN.po 读入自己的
## 词典，在编辑器场景树中对 Dialogic 相关节点做文本替换：
##   - Control.text / tooltip_text
##   - Window.title / AcceptDialog.dialog_text
##   - PopupMenu 的菜单项
##   - inspector 的 EditorProperty 标签
## 词典查不到的字符串原样保留，因此用户输入内容（对话文本、变量值等）
## 不受任何影响；整体操作幂等，可重复调用。
##
## 使用前提：Godot 编辑器语言设置为简体中文（或 auto 且系统为中文）。
## 本插件只在编辑器中生效，不影响游戏运行时的行为。

const PO_PATH := "res://addons/dialogic_zh_cn/translations/zh_CN.po"

## msgid -> msgstr 词典
var _dict: Dictionary = {}


func _enter_tree() -> void:
	_load_dict()
	if _dict.is_empty():
		push_warning("[dialogic_zh_cn] 词典为空或加载失败，界面将保持英文。")
		return
	print("[dialogic_zh_cn] 已加载 %d 条翻译（编辑器 locale=%s）" % [
		_dict.size(), TranslationServer.get_locale()])
	get_tree().node_added.connect(_on_node_added)
	# Dialogic 主界面在本插件之前加载，对已存在的界面做一轮补翻
	_apply_to_existing_tree.call_deferred()
	# 自愈兜底：部分菜单项/默认值在补翻之后才动态填充（如 PopupMenu 的
	# 事件分类项、LineEdit 默认值），node_added 抓不到。用低频定时补翻
	# 收尾，任何时序的文本最终都会被替换。替换是幂等的，重复跑无副作用。
	var timer := Timer.new()
	timer.wait_time = 2.0
	timer.timeout.connect(_apply_to_existing_tree)
	timer.autostart = true
	add_child(timer)
	# 诊断：启动数帧后统计漏网节点，输出样例帮助定位替换盲区。
	_diagnose.call_deferred()


## 启动数秒后统计漏网节点，输出样例帮助定位替换盲区。
func _diagnose() -> void:
	# 等 3 秒真实时间：让自愈定时器至少跑过一轮，再统计残留
	await get_tree().create_timer(3.0).timeout
	var missed: Array[String] = []
	_collect_missed(get_tree().root, missed)
	if missed.is_empty():
		print("[dialogic_zh_cn] 诊断：无漏网节点")
	else:
		print("[dialogic_zh_cn] 诊断：词典可命中但仍为英文的节点 %d 个，样例：" % missed.size())
		for m in missed.slice(0, 12):
			print("    - ", m)


func _collect_missed(node: Node, missed: Array[String]) -> void:
	if node is Control:
		var c := node as Control
		if c.tooltip_text != "" and _dict.has(c.tooltip_text):
			missed.append("%s(%s).tooltip = %s" % [node.get_class(), node.name, c.tooltip_text])
		if "text" in c:
			var t: String = c.get("text")
			if t != "" and _dict.has(t):
				missed.append("%s(%s).text = %s" % [node.get_class(), node.name, t])
	if node is PopupMenu:
		var pm := node as PopupMenu
		for i in range(pm.item_count):
			var it := pm.get_item_text(i)
			if it != "" and _dict.has(it):
				missed.append("PopupMenu(%s) item %d = %s" % [node.name, i, it])
	for child in node.get_children():
		_collect_missed(child, missed)


func _exit_tree() -> void:
	if get_tree().node_added.is_connected(_on_node_added):
		get_tree().node_added.disconnect(_on_node_added)


## 解析 gettext PO 文本格式为词典。只需要 msgid/msgstr 对，
## 不依赖外部 gettext 工具，也无法触发引擎导入/域机制的任何玄学。
func _load_dict() -> void:
	if not FileAccess.file_exists(PO_PATH):
		push_warning("[dialogic_zh_cn] 找不到翻译文件: %s" % PO_PATH)
		return
	var f := FileAccess.open(PO_PATH, FileAccess.READ)
	if f == null:
		return
	var msgid := ""
	var msgstr := ""
	var mode := ""            # "id" / "str" / ""
	var in_block := false     # 多行字符串
	var pending := []         # 待续写的字符串行
	while f.get_position() < f.get_length():
		var line := f.get_line()
		var st := line.strip_edges()
		if st.begins_with("msgid "):
			_flush_entry(msgid, msgstr)
			msgid = ""; msgstr = ""; mode = "id"; in_block = false; pending = []
			msgid = _unquote(st.substr(6).strip_edges())
		elif st.begins_with("msgstr "):
			mode = "str"
			msgstr = _unquote(st.substr(7).strip_edges())
		elif st.begins_with("\""):
			# 多行续写：追加到当前 msgid 或 msgstr
			var piece := _unquote(st)
			if mode == "id":
				msgid += piece
			elif mode == "str":
				msgstr += piece
		elif st.is_empty():
			_flush_entry(msgid, msgstr)
			msgid = ""; msgstr = ""; mode = ""
	_flush_entry(msgid, msgstr)


func _flush_entry(msgid: String, msgstr: String) -> void:
	if msgid != "" and msgstr != "":
		_dict[msgid] = msgstr


## 去掉 PO 字符串两侧引号并还原基础转义
func _unquote(s: String) -> String:
	s = s.strip_edges()
	if s.length() >= 2 and s.begins_with("\"") and s.ends_with("\""):
		s = s.substr(1, s.length() - 2)
	return s.replace("\\\"", "\"").replace("\\n", "\n").replace("\\t", "\t")


## 词典查询：命中返回译文，否则返回原文
func _lookup(s: String) -> String:
	return _dict.get(s, s)


# ---------------------------------------------------------- 注入层

func _on_node_added(node: Node) -> void:
	_apply_translation.call_deferred(node)


func _apply_translation(node: Node) -> void:
	if not is_instance_valid(node):
		return
	if node is Control:
		var c := node as Control
		# tooltip：Control 的存取两端都不走引擎翻译
		if c.tooltip_text != "":
			var tip := _lookup(c.tooltip_text)
			if tip != c.tooltip_text:
				c.tooltip_text = tip
		# 文本类属性：Dialogic 部分界面为运行时创建，重赋值补翻
		if "text" in c:
			var txt: String = c.get("text")
			if txt != "":
				var t := _lookup(txt)
				if t != txt:
					c.set("text", t)
	# 窗口与对话框标题
	if node is Window:
		var w := node as Window
		if w.title != "":
			var title := _lookup(w.title)
			if title != w.title:
				w.title = title
	# 对话框正文
	if node is AcceptDialog:
		var ad := node as AcceptDialog
		if ad.dialog_text != "":
			var dt := _lookup(ad.dialog_text)
			if dt != ad.dialog_text:
				ad.dialog_text = dt
	# 菜单项
	if node is PopupMenu:
		var pm := node as PopupMenu
		for i in range(pm.item_count):
			var it := pm.get_item_text(i)
			if it != "":
				var it2 := _lookup(it)
				if it2 != it:
					pm.set_item_text(i, it2)
	# inspector 属性控件的可读标签
	if node is EditorProperty:
		var ep := node as EditorProperty
		if ep.label != "":
			var lb := _lookup(ep.label)
			if lb != ep.label:
				ep.label = lb


func _apply_to_existing_tree() -> void:
	_walk(get_tree().root)


func _walk(node: Node) -> void:
	_apply_translation(node)
	for child in node.get_children():
		_walk(child)
