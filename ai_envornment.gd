extends Node2D

@onready var player: Player = $Game/Player
@onready var gateManager: GameManager = $Game/GateManager

var reset_position: Vector2
var reset_rotation: float
var reward = 0
var terminated = false
var learning = false
var attempt = 0.0
var attempt_int = 0
var elapsed_time = 0.0
var r = 1.0
var max_attempts = 50000
var sum_delta = 0
var prev_action = Vector2.ZERO

func _ready() -> void:
	reset_position = player.position
	reset_rotation = player.rotation
	player.inputDisabled = false
	
	# Connect signals from the player for tracking collisions
	player.connect("hit_track", _on_player_hit_track)
	player.connect("hit_gate", _on_player_hit_gate)
	
func _input(event: InputEvent) -> void:
	if event.is_action_pressed("swap"):
		player.inputDisabled = not player.inputDisabled
		learning = not learning

func _process(delta: float) -> void:
	if not learning:
		var observation = player.get_observation()

	if learning:
		if terminated:
			reset()
			return
		sum_delta += delta
		#prints(delta, sum_delta)
		if sum_delta < 0.2:
			#player.move(delta, prev_action[0], prev_action[1])
			player.H = prev_action[0]
			player.V = prev_action[1]
			return
		sum_delta = 0
		elapsed_time += delta
		if elapsed_time >= 60.0:
			terminated = true
		var observation = player.get_observation()
		var action_idx = %"AI".get_action(observation)
		var action = %"AI".get_godot_action(action_idx)
		prev_action = action
		#print(prev_action)
		player.H = prev_action[0]
		player.V = prev_action[1]
		#player.move(delta, prev_action[0], prev_action[1])
		var new_observation = player.get_observation()
		%"AI".update_q_table(observation, action_idx, reward, new_observation, terminated)
		#reward -= 1


func reset():
	if attempt_int % 100 == 0:
		%"AI".save_q_table_name("q_table.json")
		%"AI".save_rewards()
	if attempt_int == max_attempts:
		%"AI".save_q_table_name("max_q_table.json")
	if attempt_int == 300000:
		learning = false
	%"AI".decay_exploration_linear(r)
	%"AI".decay_learning_rate_linear(r)
	r = max((max_attempts - attempt) / max_attempts, 0)
	print("r ", r)
	%"AI".append_reward(reward)
	
	print(attempt, reward)
	reward = 0
	elapsed_time = 0.0
	player.position = reset_position
	player.rotation = reset_rotation
	player.velocity = Vector2(0,0)
	gateManager.reset_gates()
	terminated = false
	attempt += 1
	attempt_int += 1

	
func _on_player_hit_gate() -> void:
	reward += 50
	
func _on_player_hit_track() -> void:
	terminated = true
