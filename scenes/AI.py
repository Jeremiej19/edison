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
	state_size = 5
	action_size = 4
	learning_rate = 0.8
	learning_rate_start = 0.8
	discount_factor = 0.8
	exploration_rate = 1.0
	exploration_rate_start = 1
	exploration_decay = 0.998
	min_exploration_rate = 0.05
	min_learning_rate = 0.05
	reward = []
	
	q_table = defaultdict(lambda: {0:0, 1:0, 2:0, 3:0})
	actions = [
		[-1, 0],  # Turn left
		[0, 0],   # No action
		[1, 0],   # Turn right
		[0, 1],   # Accelerate
	]
	
	def discretize_ray(self, ray_value):
		buckets = [100, 200, 300, 450, 600]# Add more if needed
		for i, threshold in enumerate(buckets):
			if ray_value < threshold:
				return i
		return len(buckets)
		
	def discretize_valocity(self, valocity):
		buckets = [100, 200, 300, 400, 500]  # Add more if needed
		for i, threshold in enumerate(buckets):
			if valocity.length() < threshold:
				return i
		return len(buckets)
	
	def get_godot_action(self, action_idx: int):
		vec = Vector2.new3(self.actions[action_idx][0], self.actions[action_idx][1])
		return vec
	
	def discretize_state(self, state):
		"""Convert continuous state values to discrete buckets for Q-table indexing"""
		ray1, ray2, ray3, ray4, ray5, velocity = state
		
		ray1_disc = self.discretize_ray(ray1)
		ray2_disc = self.discretize_ray(ray2)
		ray3_disc = self.discretize_ray(ray3)
		ray4_disc = self.discretize_ray(ray4)
		ray5_disc = self.discretize_ray(ray5)	
		
		vel_disc = self.discretize_valocity(velocity)
		
		return (ray1_disc, ray2_disc, ray3_disc, ray4_disc, ray5_disc)
	
	def get_action(self, state):
		"""Select action using epsilon-greedy policy"""
		disc_state = str(self.discretize_state(state))
		
		# Exploration (random action)
		if random.random() < self.exploration_rate:
			action_idx = random.randrange(self.action_size)
		# Exploitation (best known action)
		else:
			action_idx = max(self.q_table[disc_state], key=self.q_table[disc_state].get)
		
		return action_idx
	
	def update_q_table(self, state, action_idx, reward, next_state, done):
		"""Update Q-table using the Q-learning formula"""
		disc_state = str(self.discretize_state(state))
		disc_next_state = str(self.discretize_state(next_state))
		
		## Q-learning formula: Q(s,a) = Q(s,a) + α[r + γ·max(Q(s',a')) - Q(s,a)]
		current_q = self.q_table[disc_state][action_idx]
		
		max_next_q = max(self.q_table[disc_next_state].values())			
			
		new_q = (1-self.learning_rate)*current_q + self.learning_rate * (reward + self.discount_factor * max_next_q)
		
		# Update Q-table
		self.q_table[disc_state][action_idx] = new_q
	
	def decay_exploration(self):
		"""Decay exploration rate"""
		self.exploration_rate = max(self.min_exploration_rate, 
								   self.exploration_rate * self.exploration_decay)
	def decay_learning_rate(self):
		"""Decay exploration rate"""
		self.learning_rate = max(self.min_learning_rate, 
								   self.learning_rate * self.exploration_decay)
	def decay_exploration_linear(self, r):
		"""Decay exploration rate"""
		self.exploration_rate = (self.exploration_rate_start - self.min_exploration_rate) * r + self.min_exploration_rate
		print(self.exploration_rate)
	def decay_learning_rate_linear(self, r):
		"""Decay exploration rate"""
		self.learning_rate = (self.learning_rate_start - self.min_learning_rate) * r + self.min_learning_rate
	
	def append_reward(self, reward: int):
		self.reward.append(reward)
	#def print_q_table(self):
		#print(self.q_table)
	def save_rewards(self):
		with open("rewards.json", "w") as f:
			json.dump(self.reward, f)
	
	def save_q_table(self):
		"""Save Q-table to a file"""
		
		with open("q_table.json", "w") as f:
			dd = dict(self.q_table)
			json.dump(dd, f)
			
	def save_q_table_name(self, name):
		"""Save Q-table to a file"""
		
		with open(name, "w") as f:
			dd = dict(self.q_table)
			json.dump(dd, f)
	#
	def load_q_table(self):
		"""Load Q-table from a file if it exists"""
		try:
			if os.path.exists("q_table.json"):
				with open("q_table.json", "r") as f:
					self.q_table = json.load(f)
				# Convert the loaded dict to a defaultdic
				print("Q-table loaded successfully")
		except Exception as e:
			print(f"Error loading Q-table: {e}")
			# Keep the default initialized defaultdict if loadin