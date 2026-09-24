@tool
extends EditorPlugin

## Dialogic 2 简体中文语言包
##
## 生效机制分两层：
##  1. 加载 zh_CN.mo 到 TranslationServer。Dialogic 界面中 Label/Button/
##     RichTextLabel 的文本、占位符、菜单项等属性，其 setter 在 Godot 引擎
##     内部就走翻译（atr），翻译注册后自动生效，无需改动 Dialogic 任何源码。
##  2. 对 Godot 引擎不自动翻译的属性做注入：Control.tooltip_text、
##     Window.title、AcceptDialog.dialog_text、inspector 的 EditorProperty
##     标签。通过监听编辑器场景树的 node_added 信号，在新节点入树时
##     查询翻译并重新赋值。
##
## 使用前提：Godot 编辑器语言设置为简体中文（zh_CN）。
## 本插件只在编辑器中生效，不会影响游戏运行时的行为。

const TRANSLATION_PATH := "res://addons/dialogic_zh_cn/translations/zh_CN.mo"

var _translation: Translation = null


func _enter_tree() -> void:
	if not ResourceLoader.exists(TRANSLATION_PATH):
		push_warning("[dialogic_zh_cn] 未找到翻译文件: %s，请重新构建语言包。" % TRANSLATION_PATH)
		return
	_translation = load(TRANSLATION_PATH)
	TranslationServer.add_translation(_translation)
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
	for child in node.get_children():
		_walk(child)
