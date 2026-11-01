extends SceneTree

func find_type(node: Node, type_name: String) -> Node:
	if node.is_class(type_name): return node
	for child in node.get_children():
		var found := find_type(child, type_name)
		if found != null: return found
	return null

func _initialize() -> void:
	call_deferred("validate")

func validate() -> void:
	var expected := ["Idle", "Walk", "Run", "SwordIdle", "SpearIdle", "SwordSlash", "SpearThrust", "TakeDamage"]
	var report := {}
	var failures := []
	var references = JSON.parse_string(FileAccess.get_file_as_string("D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1/pose-reference.json"))
	for label in ["brother", "sister"]:
		var document := GLTFDocument.new()
		var state := GLTFState.new()
		var error := document.append_from_file("D:/GodotProjects/dungeons-n-academics/Assets/Characters/Animated/v1/%s-animations-v1.glb" % label, state)
		if error != OK:
			failures.append(label + " failed to load")
			continue
		var actor := document.generate_scene(state) as Node3D
		root.add_child(actor)
		var player := find_type(actor, "AnimationPlayer") as AnimationPlayer
		var skeleton := find_type(actor, "Skeleton3D") as Skeleton3D
		var clips := {}
		for clip in expected:
			if not player.has_animation(clip):
				failures.append(label + " missing " + clip)
				continue
			var animation := player.get_animation(clip)
			player.stop()
			for bone in skeleton.get_bone_count(): skeleton.reset_bone_pose(bone)
			player.play(clip)
			var samples := []
			var sample_index := 0
			for fraction in [0.0, 0.25, 0.5, 0.75, 1.0]:
				player.seek(animation.length * fraction, true)
				player.advance(0)
				skeleton.force_update_all_bone_transforms()
				var R := skeleton.global_transform * skeleton.get_bone_global_pose(skeleton.find_bone("hand.R"))
				var L := skeleton.global_transform * skeleton.get_bone_global_pose(skeleton.find_bone("hand.L"))
				var hand_error := (L * Vector3(-0.025, 0.085, 0)).distance_to(R * Vector3(0.025, 0.085, 0.28)) if clip.begins_with("Spear") else 0.0
				if hand_error > 0.001: failures.append(label + " " + clip + " spear contact " + str(hand_error))
				var pose_error := 0.0
				var reference: Dictionary = references[label][clip][sample_index]["points"]
				for bone_name in reference:
					var v: Array = reference[bone_name]
					var wanted := Vector3(v[0], v[1], v[2])
					var actual := (skeleton.global_transform * skeleton.get_bone_global_pose(skeleton.find_bone(bone_name))).origin
					pose_error = max(pose_error, wanted.distance_to(actual))
				if pose_error > 0.005: failures.append(label + " " + clip + " pose error " + str(pose_error))
				samples.append({"fraction": fraction, "spear_contact_error_m": hand_error, "blender_pose_error_m": pose_error})
				sample_index += 1
			clips[clip] = {"seconds": animation.length, "tracks": animation.get_track_count(), "samples": samples}
		report[label] = {"bones": skeleton.get_bone_count(), "clips": clips}
		actor.queue_free()
	report["failures"] = failures
	var file := FileAccess.open("D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1/godot-validation-v1.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	print("CHARACTER_ANIMATION_VALIDATION " + JSON.stringify(report))
	quit(0 if failures.is_empty() else 1)
