extends Node2D
class_name GameManager
# Array to hold all gate references
var gates = []
var current_gate_index = 0

func _ready():
	# Collect all gates (children that are StaticBody2D)
	for child in get_children():
		if child is StaticBody2D:
			gates.append(child)
	
	# Initialize - enable first gate, disable others
	update_gates()

func update_gates():
	for i in range(gates.size()):
		gates[i].visible = (i == current_gate_index)
		if i == current_gate_index:
			gates[i].set_collision_layer(1) 
		else:
			gates[i].set_collision_layer(0) 

# Call this when player sends signal
func advance_gate():
	current_gate_index = wrapi(current_gate_index + 1, 0, gates.size())
	update_gates()
	print("Activated gate: ", gates[current_gate_index].name)

func reset_gates():
	current_gate_index = 0
	update_gates()
