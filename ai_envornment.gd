extends Node2D

@onready var player: Player = $Game/Player
@onready var gateManager: GameManager = $Game/GateManager

var reset_position: Vector2
var reset_rotation: float
var reward = 0
var terminated = false
var learning = false
var attempt = 0

func _ready() -> void:
	reset_position = player.position
	reset_rotation = player.rotation
	player.inputDisabled = false
	
	# Connect signals from the player for tracking collisions
	player.connect("hit_track", _on_player_hit_track)
	player.connect("hit_gate", _on_player_hit_gate)
	
func _input(event: InputEvent) -> void:
	if event.is_action_pressed("swap"):
		player.inputDisabled = true
		learning = true

func _process(delta: float) -> void:
	if not learning:
		var observation = player.get_observation()
	if learning:
		if not terminated:
			var observation = player.get_observation()
			var action_idx = %"AI".get_action(observation)
			var action = %"AI".get_godot_action(action_idx)
			player.move(delta, action[0], action[1])
			var new_observation = player.get_observation()
			%"AI".update_q_table(observation, action_idx, reward, new_observation, terminated)
			#reward -= 1
		if terminated:
			print(%"AI".exploration_rate)
			%"AI".decay_exploration()
			reward = 0
			player.position = reset_position
			player.rotation = reset_rotation + deg_to_rad(randf_range(-45.0, 45.0))
			player.velocity = Vector2(0,0)
			gateManager.reset_gates()
			terminated = false
	
func _on_player_hit_gate() -> void:
	reward += 80
	
func _on_player_hit_track() -> void:
	reward -= 200
	terminated = true
