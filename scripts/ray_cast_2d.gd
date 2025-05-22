extends RayCast2D

var distance = 0

func _process(delta: float) -> void:
	if is_colliding():
		distance = self.global_position.distance_to(get_collision_point())
		if Logger.RAY_LOGGER:
			print(distance)
			
func get_distance() -> float:
	return distance
