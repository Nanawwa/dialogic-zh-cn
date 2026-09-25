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

## 自愈补翻的帧计数（headless 下真实时间不可靠，用帧数）
var _frame_counter: int = 0
const HEAL_INTERVAL_FRAMES := 600


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
	# 事件分类项、LineEdit 默认值），node_added 抓不到。用帧计数低频
	# 补翻收尾（headless 与 GUI 的真实时间流速不同，帧数才可靠），
	# 替换是幂等的，重复跑无副作用。
	set_process(true)
	_frame_counter = 0
	# 诊断：启动数帧后统计漏网节点，输出样例帮助定位替换盲区。
	_diagnose.call_deferred()
	# 全量英文探针：收集所有疑似未翻译文本转储到文件
	_dump_untranslated.call_deferred()


## 启动数秒后统计漏网节点，输出样例帮助定位替换盲区。
func _diagnose() -> void:
	# 等 900 帧：让自愈补翻至少跑过一轮，再统计残留
	for i in 700:
		await get_tree().process_frame
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


# ---------------------------------------------------------- 全量英文探针

## 遍历编辑器整棵树，收集所有"疑似未翻译英文"的用户可见文本，
## 写入 res://addons/dialogic_zh_cn/untranslated_dump.txt 供离线分析。
## 排除：含中文的（已翻译或用户内容）、路径、纯符号、超长用户文本。
func _dump_untranslated() -> void:
	for i in 700:
		await get_tree().process_frame
	var found: Array[String] = []
	_collect_english(get_tree().root, found, {})
	var f := FileAccess.open("res://addons/dialogic_zh_cn/untranslated_dump.txt",
			FileAccess.WRITE)
	if f == null:
		print("[dialogic_zh_cn] 探针：转储文件写入失败")
		return
	f.store_line("总计 %d 条（去重后）" % found.size())
	for s in found:
		f.store_line(s)
	f.close()
	print("[dialogic_zh_cn] 探针：收集疑似未翻译文本 %d 条 -> untranslated_dump.txt" % found.size())


func _looks_english(s: String) -> bool:
	if s.length() < 2 or s.length() > 300:
		return false
	var has_word := false
	for i in range(s.length() - 1):
		var c := s.unicode_at(i)
		if ((c >= 65 and c <= 90) or (c >= 97 and c <= 122)) and \
				((s.unicode_at(i + 1) >= 65 and s.unicode_at(i + 1) <= 90) or \
				(s.unicode_at(i + 1) >= 97 and s.unicode_at(i + 1) <= 122)):
			has_word = true
			break
	if not has_word:
		return false
	for i in s.length():
		var u := s.unicode_at(i)
		if u >= 0x4E00 and u <= 0x9FFF:
			return false
	if s.begins_with("res://") or s.begins_with("uid://") or s.begins_with("C:"):
		return false
	return true


func _collect_english(node: Node, found: Array[String], seen: Dictionary) -> void:
	if node is Control:
		var c := node as Control
		_props_of(c, found, seen, ["text", "tooltip_text", "placeholder_text"])
	if node is Window:
		var w := node as Window
		_check_one(w.title, "Window.title", found, seen, w.get_class())
	if node is PopupMenu:
		var pm := node as PopupMenu
		for i in range(pm.item_count):
			_check_one(pm.get_item_text(i), "PopupMenu.item", found, seen, node.name)
			_check_one(pm.get_item_tooltip(i), "PopupMenu.tip", found, seen, node.name)
	if node is TabContainer:
		var tc := node as TabContainer
		for i in range(tc.get_tab_count()):
			_check_one(tc.get_tab_title(i), "TabContainer.title", found, seen, node.name)
	if node is TabBar:
		var tb := node as TabBar
		for i in range(tb.tab_count):
			_check_one(tb.get_tab_title(i), "TabBar.title", found, seen, node.name)
	if node is Tree:
		var tree := node as Tree
		for i in range(tree.columns):
			_check_one(tree.get_column_title(i), "Tree.col", found, seen, node.name)
	for child in node.get_children():
		_collect_english(child, found, seen)


func _props_of(c: Control, found: Array[String], seen: Dictionary, props: Array) -> void:
	for p in props:
		if p in c:
			var v: String = c.get(p)
			if v != "":
				_check_one(v, p, found, seen, c.get_class())
	if c is ItemList:
		var il := c as ItemList
		for i in range(il.item_count):
			_check_one(il.get_item_text(i), "ItemList.item", found, seen, c.name)


func _check_one(v: String, prop: String, found: Array[String], seen: Dictionary,
		ctx: String) -> void:
	if not _looks_english(v):
		return
	var key := prop + "|" + v
	if seen.has(key):
		return
	seen[key] = true
	var short := v
	if short.length() > 200:
		short = short.substr(0, 200) + "…"
	found.append("[%s|%s] %s" % [ctx, prop, short.replace("\n", " ⏎ ")])


func _process(_delta: float) -> void:
	if _dict.is_empty():
		return
	_frame_counter += 1
	if _frame_counter % HEAL_INTERVAL_FRAMES == 0:
		_apply_to_existing_tree()


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
	# 标签页标题（Dialogic 顶部导航：时间轴/角色/术语表/样式/变量/设置）
	if node is TabContainer:
		var tc := node as TabContainer
		for i in range(tc.get_tab_count()):
			var tt := tc.get_tab_title(i)
			if tt != "":
				var tt2 := _lookup(tt)
				if tt2 != tt:
					tc.set_tab_title(i, tt2)
	if node is TabBar:
		var tb := node as TabBar
		for i in range(tb.tab_count):
			var tt3 := tb.get_tab_title(i)
			if tt3 != "":
				var tt4 := _lookup(tt3)
				if tt4 != tt3:
					tb.set_tab_title(i, tt4)
	# Tree 列头（如变量编辑器的 Name/Default Value）
	if node is Tree:
		var tree := node as Tree
		for i in range(tree.columns):
			var ct := tree.get_column_title(i)
			if ct != "":
				var ct2 := _lookup(ct)
				if ct2 != ct:
					tree.set_column_title(i, ct2)
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
