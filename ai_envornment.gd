extends Node2D

@onready var player: Player = $Game/Player
@onready var AI = $AI

func _ready() -> void:
	player.inputDisabled = false

func _process(delta: float) -> void:
	#var directionH = 1
	#var directionV = 1
	#player.move(delta, directionH, directionV)
	var observation = player.get_observation()
