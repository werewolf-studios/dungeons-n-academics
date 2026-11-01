extends Node3D
## Isolated animation review scene. No gameplay/player scene dependencies.
const CLIPS = ["Idle", "Walk", "Run", "SwordIdle", "SpearIdle", "SwordSlash", "SpearThrust", "TakeDamage"]
const LOOPS = ["Idle", "Walk", "Run", "SwordIdle", "SpearIdle"]
## Where the shaft sits in each character's right hand, from fit_contact.py.
const SPEAR_SEAT = {"brother": Vector3(0.08, 0.07, 0), "sister": Vector3(0.07, 0.065, 0)}
var actors: Array[Node3D] = []
var players: Array[AnimationPlayer] = []
var props: Array[Dictionary] = []
var camera: Camera3D
var caption: Label
var selector: OptionButton
var current_clip := "Idle"
var rate := 1.0
var paused := false
var view_angle := 0.35

func _ready() -> void:
	var environment := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("303541")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("d9e0f3")
	env.ambient_light_energy = 0.65
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	environment.environment = env
	add_child(environment)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-45, -25, 0)
	light.light_energy = 1.7
	light.shadow_enabled = true
	add_child(light)
	var floor := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(20, 20)
	floor.mesh = plane
	var material := StandardMaterial3D.new()
	material.albedo_color = Color("505665")
	material.roughness = 0.95
	floor.material_override = material
	add_child(floor)
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 3.0
	add_child(camera)
	set_view(0.35)
	for i in 2:
		var label := "brother" if i == 0 else "sister"
		var packed := load("res://Assets/Characters/Animated/v10/%s-animations-v10.glb" % label) as PackedScene
		var actor := packed.instantiate() as Node3D
		actor.position.x = -0.65 if i == 0 else 0.65
		add_child(actor)
		actors.append(actor)
		var player := find_type(actor, "AnimationPlayer") as AnimationPlayer
		var skeleton := find_type(actor, "Skeleton3D") as Skeleton3D
		players.append(player)
		for clip in CLIPS:
			if player.has_animation(clip):
				player.get_animation(clip).loop_mode = Animation.LOOP_LINEAR if clip in LOOPS else Animation.LOOP_NONE
		player.animation_finished.connect(_on_animation_finished.bind(i))
		var attachment := BoneAttachment3D.new()
		attachment.name = "WeaponAttachment"
		attachment.bone_name = "hand.R"
		skeleton.add_child(attachment)
		var socket := Node3D.new()
		socket.position = Vector3(0.025, 0.085, 0)
		attachment.add_child(socket)
		var weapons := {}
		for weapon in ["Sword", "Spear"]:
			var scene := load("res://Scenes/Weapons/starter_%s.tscn" % weapon.to_lower()) as PackedScene
			var model := scene.instantiate() as Node3D
			model.rotation_degrees.x = -90
			if weapon == "Spear":
				model.position = SPEAR_SEAT[label] - socket.position
			socket.add_child(model)
			model.visible = false
			weapons[weapon] = model
		props.append(weapons)
		var name_label := Label3D.new()
		name_label.text = label.capitalize()
		name_label.position = Vector3(0, 2.05, 0)
		name_label.font_size = 40
		name_label.pixel_size = 0.002
		name_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		actor.add_child(name_label)
	build_ui()
	play_clip("Idle")

func find_type(node: Node, type_name: String) -> Node:
	if node.is_class(type_name):
		return node
	for child in node.get_children():
		var found := find_type(child, type_name)
		if found != null:
			return found
	return null

func build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var panel := PanelContainer.new()
	panel.position = Vector2(18, 18)
	layer.add_child(panel)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 10)
	panel.add_child(box)
	caption = Label.new()
	caption.text = "Dungeons N Academics · Animation review"
	box.add_child(caption)
	selector = OptionButton.new()
	for clip in CLIPS:
		selector.add_item(clip)
	selector.item_selected.connect(func(index: int): play_clip(CLIPS[index]))
	box.add_child(selector)
	var controls := HBoxContainer.new()
	box.add_child(controls)
	for entry in [["Pause", 0], ["Front", 1], ["Side", 2], ["Back", 3], ["Replay", 4]]:
		var button := Button.new()
		button.text = entry[0]
		var command: int = entry[1]
		button.pressed.connect(_on_review_control_pressed.bind(command))
		controls.add_child(button)
	var speed := HSlider.new()
	speed.min_value = 0.25
	speed.max_value = 1.5
	speed.step = 0.25
	speed.value = 1.0
	speed.value_changed.connect(func(value: float): rate = value)
	box.add_child(speed)
	var help := Label.new()
	help.text = "1–8: select clip · Space: pause · R: replay\nOne-shot attacks recover to their weapon-ready idle."
	box.add_child(help)

func _on_review_control_pressed(command: int) -> void:
	match command:
		0:
			paused = not paused
		1:
			set_view(0)
		2:
			set_view(PI / 2)
		3:
			set_view(PI)
		4:
			play_clip(current_clip)

func set_view(angle: float) -> void:
	view_angle = angle
	camera.position = Vector3(sin(angle) * 5, 1.9, cos(angle) * 5)
	camera.look_at(Vector3(0, 1.0, 0.20))

func play_clip(clip: String) -> void:
	current_clip = clip
	selector.select(CLIPS.find(clip))
	caption.text = "Dungeons N Academics · %s" % clip
	for i in players.size():
		players[i].stop()
		var skeleton := find_type(actors[i], "Skeleton3D") as Skeleton3D
		for bone in skeleton.get_bone_count():
			skeleton.reset_bone_pose(bone)
		players[i].play(clip, 0.10)
		props[i]["Sword"].visible = clip in ["SwordIdle", "SwordSlash"]
		props[i]["Spear"].visible = clip in ["SpearIdle", "SpearThrust"]

func _on_animation_finished(clip: StringName, index: int) -> void:
	var guard := "SwordIdle" if clip == &"SwordSlash" else "SpearIdle" if clip == &"SpearThrust" else "Idle"
	players[index].play(guard, 0.12)

func _process(_delta: float) -> void:
	for player in players:
		player.speed_scale = 0.0 if paused else rate

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode >= KEY_1 and event.keycode <= KEY_8:
			play_clip(CLIPS[event.keycode - KEY_1])
		elif event.keycode == KEY_SPACE:
			paused = not paused
		elif event.keycode == KEY_R:
			play_clip(current_clip)
