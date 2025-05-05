extends CharacterBody2D


const WHEEL_BASE = 100
const ROTATE_SPEED = 15
const ENGINE_POWER = 2000

const FRICTION = -0.4
const DRAG = -0.0005


var acceleration = Vector2.ZERO


func _physics_process(delta: float) -> void:
	# Add the gravity.

	# Get the input direction and handle the movement/deceleration.
	# As good practice, you should replace UI actions with custom gameplay actions.
	#var directionH:= Input.get_axis("move_left", "move_right")
	#var directionV := Input.get_axis("move_up", "move_down")
	apply_fricion(delta)
	calculate_rotation(delta)
	move_and_slide()
	
	
func calculate_rotation(delta):
	var turn = Input.get_axis("move_left", "move_right") * deg_to_rad(ROTATE_SPEED)
	var transformX = get_transform().x
	var movement = Input.get_axis("move_down", "move_up")
	
	acceleration = transformX * ENGINE_POWER * movement
	velocity += acceleration * delta
	print(velocity)
	var rear_wheel = position - transformX * WHEEL_BASE/2.0
	var front_wheel = position + transformX * WHEEL_BASE/2.0
	prints(rear_wheel,front_wheel)
	
	rear_wheel += velocity * delta
	front_wheel += velocity.rotated(turn)  * delta
	prints(rear_wheel,front_wheel)
	var new_heading = (front_wheel - rear_wheel).normalized() 
	print(new_heading)
	var direction = new_heading.dot(velocity.normalized())
	if direction > 0:
		velocity = new_heading * velocity.length()
	else:
		velocity = -new_heading * velocity.length() * 0.977 # TODO: a chyba bez tego
	rotation = new_heading.angle()
	
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
	
