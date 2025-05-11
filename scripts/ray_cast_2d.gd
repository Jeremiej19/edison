extends RayCast2D

func _process(delta: float) -> void:
	if is_colliding():
		if Logger.RAY_LOGGER:
			print(self.global_position.distance_to(get_collision_point()))
