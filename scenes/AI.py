from py4godot import gdproperty, signal, private, gdclass, SignalArg
from py4godot.classes.core import Vector2, Vector3
import numpy as np
import random
import os
import json
from collections import defaultdict
from py4godot.classes.Node2D import Node2D

@gdclass
class AI(Node2D):
	state_size = 4
	action_size = 4
	learning_rate = 0.3
	discount_factor = 0.90
	exploration_rate = 1.0
	exploration_decay = 0.998
	min_exploration_rate = 0.01
	
	q_table = defaultdict(lambda: {0:0, 1:0, 2:0, 3:0})
	actions = [
		[-1, 0],  # Turn left
		[0, 0],   # No action
		[1, 0],   # Turn right
		[0, 1],   # Accelerate
	]
	
	def discretize_ray(self, ray_value):
		buckets = [50, 100, 150, 200, 300]  # Add more if needed
		for i, threshold in enumerate(buckets):
			if ray_value < threshold:
				return i
		return len(buckets)
		
	def discretize_valocity(self, valocity):
		buckets = [50, 100, 150, 200, 300, 400, 600]  # Add more if needed
		for i, threshold in enumerate(buckets):
			if valocity.length() < threshold:
				return i
		return len(buckets)
	
	def get_godot_action(self, action_idx: int):
		vec = Vector2.new3(self.actions[action_idx][0], self.actions[action_idx][1])
		return vec
	
	def discretize_state(self, state):
		"""Convert continuous state values to discrete buckets for Q-table indexing"""
		ray1, ray2, ray3, velocity = state
		
		# Discretize ray distances (0-1000) into 10 buckets
		ray1_disc = self.discretize_ray(ray1)
		ray2_disc = self.discretize_ray(ray2)
		ray3_disc = self.discretize_ray(ray3)
		
		# Discretize velocity magnitude (0-2000) into 10 buckets
		vel_disc = self.discretize_valocity(velocity)
		
		return (ray1_disc, ray2_disc, ray3_disc)
	
	def get_action(self, state):
		"""Select action using epsilon-greedy policy"""
		disc_state = self.discretize_state(state)
		
		# Exploration (random action)
		if random.random() < self.exploration_rate:
			action_idx = random.randrange(self.action_size)
		# Exploitation (best known action)
		else:
			action_idx = max(self.q_table[disc_state], key=self.q_table[disc_state].get)
		
		return action_idx
	
	def update_q_table(self, state, action_idx, reward, next_state, done):
		"""Update Q-table using the Q-learning formula"""
		disc_state = self.discretize_state(state)
		disc_next_state = self.discretize_state(next_state)
		
		## Q-learning formula: Q(s,a) = Q(s,a) + α[r + γ·max(Q(s',a')) - Q(s,a)]
		current_q = self.q_table[disc_state][action_idx]
		
		if done:
			max_next_q = 0
		else:
			max_next_q = max(self.q_table[disc_next_state].values())
			
		new_q = (1-self.learning_rate)*current_q + self.learning_rate * (reward + self.discount_factor * max_next_q)
		
		# Update Q-table
		self.q_table[disc_state][action_idx] = new_q
	
	def decay_exploration(self):
		"""Decay exploration rate"""
		self.exploration_rate = max(self.min_exploration_rate, 
								   self.exploration_rate * self.exploration_decay)
	
	#def print_q_table(self):
		#print(self.q_table)
	
	#def save_q_table(self):
		#"""Save Q-table to a file"""
		## Convert defaultdict to a regular dict for serialization
		#serializable_q_table = {key: list(value) for key, value in self.q_table.items()}
		#
		#with open("q_table.json", "w") as f:
			#json.dump(serializable_q_table, f, indent=2)
	#
	#def load_q_table(self):
		#"""Load Q-table from a file if it exists"""
		#try:
			#if os.path.exists("q_table.json"):
				#with open("q_table.json", "r") as f:
					#q_table_dict = json.load(f)
					#
				## Convert the loaded dict to a defaultdict
				#for key, value in q_table_dict.items():
					#self.q_table[key] = value
				#print("Q-table loaded successfully")
		#except Exception as e:
			#print(f"Error loading Q-table: {e}")
			## Keep the default initialized defaultdict if loadin