extends Node2D

@onready var player: Player = $Game/Player
@onready var gateManager: GameManager = $Game/GateManager

const REPLACE_TARGET = 50 
var reset_position: Vector2
var reset_rotation: float
var reward = 0
var terminated = false
var learning = false
var self_driving = false
var attempt = 0.0
var attempt_int = 0
var elapsed_time = 0.0
var r = 1.0
var max_attempts = 500
var sum_delta = 0
var prev_action = Vector2.ZERO
var prev_action_idx = 0
var observation = 0
var steps = 0
var last_espilon = 0

const MOVE_DELTA = 0.3
const MAX_VEL = 1300
const MAX_DISTANCE = 1000

var actions = [
	[0, 0],
	[0, 1],
	[-1, 0],  # Turn left
	[1, 0],   # Turn right
	[0, -1],   # STOpping
]

func normalize_observation(observation):
	var obs = []
	for i in range(len(observation) - 1):
		obs.append((MAX_DISTANCE - observation[i])/MAX_DISTANCE)
	obs.append(observation.get(len(observation) - 1) / MAX_VEL)
	return obs

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
	if event.is_action_pressed("test"):
		%"DDQNAgent".epsilon = 0.0001
		%"DDQNAgent".load_model()
		self_driving = true
		player.inputDisabled = not player.inputDisabled
	if event.is_action_pressed("self_drive"):
		if %"DDQNAgent".epsilon > 0.0001:	
			last_espilon = %"DDQNAgent".epsilon
			%"DDQNAgent".epsilon = 0.0001
		else:
			%"DDQNAgent".epsilon

func _process(delta: float) -> void:
	if not learning:
		observation = player.get_observation()
		#print(observation)
		observation = normalize_observation(observation)
	if learning:
		if terminated:
			var new_observation = player.get_observation()
			new_observation = normalize_observation(new_observation)
			%"DDQNAgent".remember(observation, prev_action_idx, reward, new_observation, terminated)
			reset()
			return
		sum_delta += delta
		#prints(delta, sum_delta)
		if sum_delta < MOVE_DELTA / player.SCALE:
			#var act = actions.get(prev_action)
			#player.move(delta, prev_action[0], prev_action[1])
			player.H = prev_action[0]
			player.V = prev_action[1]
			return
		#player.move(delta, prev_action[0], prev_action[1])
		player.H = prev_action[0]
		player.V = prev_action[1]
		
		elapsed_time += delta
		if elapsed_time >= 60.0:
			terminated = true
		var new_observation = player.get_observation()
		new_observation = normalize_observation(new_observation)

		#print(prev_action)
		#player.H = prev_action[0]
		#player.V = prev_action[1]
		
		sum_delta = 0
		
		#%"AI".update_q_table(observation, action_idx, reward, new_observation, terminated)
		#reward -= 1
		steps += 1
		%"DDQNAgent".remember(observation, prev_action_idx, reward, new_observation, terminated)
		%"DDQNAgent".learn()
		reward = 0
		observation = new_observation
		var action_idx = %"DDQNAgent".choose_action(observation)
		prev_action = actions.get(action_idx)
		prev_action_idx = action_idx
		observation = player.get_observation()
	if self_driving:
		self_driving_step(delta)

func reset():
	#if attempt_int % 50 == 0:
		#%"AI".save_q_table_name("q_table.json")
		#%"AI".save_rewards()
	#if attempt_int == max_attempts:
		#%"AI".save_q_table_name("max_q_table.json")
	#if attempt_int == 300000:
		#learning = false
	#%"AI".decay_exploration_linear(r)
	#%"AI".decay_learning_rate_linear(r)
	#r = max((max_attempts - attempt) / max_attempts, 0)
	#print("r ", r)
	#%"AI".append_reward(reward)
	#print("start")
	#for i in range(10):
		#%"DDQNAgent".learn()
	#print("stop")
	prints(attempt, %"DDQNAgent".epsilon)
	print()
	if attempt_int % 10 == 0:
		%"DDQNAgent".save_model()
		print("save model")
	reward = 0
	elapsed_time = 0.0
	player.position = reset_position
	player.rotation = reset_rotation
	player.velocity = Vector2(100,100)
	gateManager.reset_gates()
	terminated = false
	attempt += 1
	attempt_int += 1
	steps = 0
	sum_delta = 0
	
	if attempt_int % REPLACE_TARGET == 0 and attempt_int > REPLACE_TARGET:
		%"DDQNAgent".update_network_parameters()

func self_driving_step(delta):
	if terminated:
		reset_clear()
		return
	sum_delta += delta
		#prints(delta, sum_delta)
	if sum_delta < MOVE_DELTA / player.SCALE:
		#var act = actions.get(prev_action)
		#player.move(delta, prev_action[0], prev_action[1])
		player.H = prev_action[0]
		player.V = prev_action[1]
		return
		#player.move(delta, prev_action[0], prev_action[1])
	player.H = prev_action[0]
	player.V = prev_action[1]
	var new_observation = player.get_observation()
	new_observation = normalize_observation(new_observation)

	sum_delta = 0

	observation = new_observation
	var action_idx = %"DDQNAgent".choose_action(observation)
	prev_action = actions.get(action_idx)
	prev_action_idx = action_idx
	observation = player.get_observation()

func reset_clear():
	reward = 0
	player.position = reset_position
	player.rotation = reset_rotation
	player.velocity = Vector2(100,100)
	gateManager.reset_gates()
	terminated = false
	attempt += 1
	attempt_int += 1
	steps = 0
	sum_delta = 0
	
func _on_player_hit_gate() -> void:
	reward += 1
	
func _on_player_hit_track() -> void:
	reward -= 1
	terminated = true
