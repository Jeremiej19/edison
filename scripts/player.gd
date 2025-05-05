extends CharacterBody2D


const WHEEL_BASE = 100
const ROTATE_SPEED = 15
const SPEED = 500


func _physics_process(delta: float) -> void:
	# Add the gravity.

	# Get the input direction and handle the movement/deceleration.
	# As good practice, you should replace UI actions with custom gameplay actions.
	#var directionH:= Input.get_axis("move_left", "move_right")
	#var directionV := Input.get_axis("move_up", "move_down")

	calculate_rotation(delta)
	print(get_last_slide_collision())
	move_and_slide()
	
	
func calculate_rotation(delta):
	var turn = Input.get_axis("move_left", "move_right") * deg_to_rad(ROTATE_SPEED)
	var transformX = get_transform().x
	velocity = Vector2.ZERO
	#if Input.get_action_strength("move_up"):
		#print(transformX)
		#velocity = transformX * SPEED
	#elif Input.get_action_strength("move_down"):
		#print(transformX)
		#velocity = transformX * -SPEED
	
	var movement = Input.get_axis("move_down", "move_up")
	if movement:
		velocity = transformX * SPEED * movement
		
	
	var rear_wheel = position - transformX * WHEEL_BASE/2.0
	var front_wheel = position + transformX * WHEEL_BASE/2.0
	rear_wheel += velocity * delta
	front_wheel += velocity.rotated(turn) * delta
	var new_heading = (front_wheel - rear_wheel).normalized()

	rotation = new_heading.angle()
	velocity = new_heading * velocity.length() * movement
	
