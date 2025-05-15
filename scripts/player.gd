extends CharacterBody2D
class_name Player

const WHEEL_BASE = 100
const ROTATE_SPEED = 15
const ENGINE_POWER = 4000

const FRICTION = -0.9
const DRAG = -0.0000001


var acceleration = Vector2.ZERO

@export var gateManager: GameManager
@export var inputDisabled: bool
@onready var ray_1 = $Middle
@onready var ray_2 = $Left
@onready var ray_3 = $Right
var directionH = 0
var directionV = 0

func move(delta: float, directionH: int, directionV: int) -> void:
	apply_fricion(delta)
	calculate_rotation(delta, directionH, directionV)
	move_and_slide()
	
func get_observation() -> Array:
	var ray_1_dist = ray_1.get_distance()
	var ray_2_dist = ray_2.get_distance()
	var ray_3_dist = ray_3.get_distance()
	return [ray_1_dist, ray_2_dist, ray_3_dist, velocity]

func _physics_process(delta: float) -> void:
	# Add the gravity.
	# Get the input direction and handle the movement/deceleration.
	# As good practice, you should replace UI actions with custom gameplay actions.
	if not inputDisabled:
		directionH = Input.get_axis("move_left", "move_right")
		directionV = Input.get_axis("move_down", "move_up")
		apply_fricion(delta)
		calculate_rotation(delta, directionH, directionV)
		move_and_slide()
	
	
func calculate_rotation(delta, directionH, directionV):
	#var turn = Input.get_axis("move_left", "move_right") * deg_to_rad(ROTATE_SPEED)
	#var turn = Input.get_axis("move_left", "move_right") * (deg_to_rad(ROTATE_SPEED) if velocity.length() > 100 else deg_to_rad(ROTATE_SPEED/2))
	var turnDeg = ROTATE_SPEED if velocity.length() < 400 else ROTATE_SPEED * 400/velocity.length()
	var turn = directionH* (deg_to_rad(turnDeg))
	var transformX = get_transform().x
	var movement = directionV
	
	acceleration = transformX * ENGINE_POWER * movement
	velocity += acceleration * delta
	if Logger.PLAYER_LOGGING:
		print(velocity.length())
	var rear_wheel = position - transformX * WHEEL_BASE/2.0
	var front_wheel = position + transformX * WHEEL_BASE/2.0
	if Logger.PLAYER_LOGGING:
		prints(rear_wheel,front_wheel)
	
	rear_wheel += velocity * delta
	front_wheel += velocity.rotated(turn)  * delta
	if Logger.PLAYER_LOGGING:
		prints(rear_wheel,front_wheel)
	var new_heading = (front_wheel - rear_wheel).normalized() 
	if Logger.PLAYER_LOGGING:
		print(new_heading)
	var direction = new_heading.dot(velocity.normalized())
	if direction > 0:
		velocity = new_heading * velocity.length()
	else:
		velocity = -new_heading * velocity.length() * 0.977 # TODO: a chyba bez tego
	rotation = new_heading.angle()
	
	if Logger.PLAYER_LOGGING:
		print(velocity)
		print(direction)
		print()
	
func apply_fricion(delta):
	if abs(velocity.length()) < 15:
		velocity = Vector2.ZERO
	var friction_force = velocity * FRICTION
	var drag_force = velocity * velocity.length() * DRAG
	velocity += (friction_force + drag_force) * delta
	
func positive_sign(x :int):
	if x < 0: return -1
	return 1
	
func _on_area_2d_body_entered(body: Node2D) -> void:
	if body.is_in_group("Track"):
		print("hit")
	if body.is_in_group("Gate"):
		print("gate")
		gateManager.advance_gate()
