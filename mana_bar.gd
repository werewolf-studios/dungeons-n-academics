extends TextureProgressBar


@onready var timer = $Timer
@onready var mana_depletion_bar = $ManaDepletionBar


var mana = 0 : set = _set_mana

func _set_mana(new_mana):
	var prev_mana = mana
	mana = min(max_value, new_mana)
	value = mana
	
	if mana <= 0:
		queue_free()
		
	if mana < prev_mana:
		timer.start()
	else:
		mana_depletion_bar.value = mana



func init_mana(_mana):
	max_value = _mana
	mana = _mana
	value = mana
	mana_depletion_bar.max_value = mana
	mana_depletion_bar.value = mana
	


func _on_timer_timeout() -> void:
	mana_depletion_bar.value = mana

func _on_reset_mana_pressed() -> void:
	init_mana(100)


func _on_deplete_mana_pressed() -> void:
	mana -= 10
