from keras.layers import Dense, Activation
from keras.models import Sequential, load_model
from keras.optimizers import Adam
import random
import numpy as np
import tensorflow as tf
from py4godot import gdproperty, signal, private, gdclass, SignalArg
from py4godot.classes.core import Vector2, Vector3
from py4godot.classes.Node2D import Node2D


class ReplayBuffer(object):
	def __init__(self, max_size, input_shape, n_actions, discrete=False):
		self.mem_size = max_size
		self.mem_cntr = 0
		self.discrete = discrete
		self.state_memory = np.zeros((self.mem_size, input_shape))
		self.new_state_memory = np.zeros((self.mem_size, input_shape))
		dtype = np.int8 if self.discrete else np.float32
		self.action_memory = np.zeros((self.mem_size, n_actions), dtype=dtype)
		self.reward_memory = np.zeros(self.mem_size)
		self.terminal_memory = np.zeros(self.mem_size, dtype=np.float32)

	def store_transition(self, state, action, reward, state_, done):
		state = list(state)
		state_ = list(state_)
		index = self.mem_cntr % self.mem_size
		self.state_memory[index] = state
		self.new_state_memory[index] = state_
		# store one hot encoding of actions, if appropriate
		if self.discrete:
			actions = np.zeros(self.action_memory.shape[1])
			actions[action] = 1.0
			self.action_memory[index] = actions
		else:
			self.action_memory[index] = action
		self.reward_memory[index] = reward
		self.terminal_memory[index] = 1 - done
		self.mem_cntr += 1

	def sample_buffer(self, batch_size):
		max_mem = min(self.mem_cntr, self.mem_size)
		batch = np.random.choice(max_mem, batch_size)

		states = self.state_memory[batch]
		actions = self.action_memory[batch]
		rewards = self.reward_memory[batch]
		states_ = self.new_state_memory[batch]
		terminal = self.terminal_memory[batch]

		return states, actions, rewards, states_, terminal

class Brain:
	def __init__(self, NbrStates, NbrActions, batch_size = 256):
		self.NbrStates = NbrStates
		self.NbrActions = NbrActions
		self.batch_size = batch_size
		self.model = self.createModel()
		
	
	def createModel(self):
		model = tf.keras.Sequential()
		model.add(tf.keras.layers.Dense(256, activation=tf.nn.relu)) #prev 256 
		model.add(tf.keras.layers.Dense(self.NbrActions, activation=tf.nn.softmax))
		model.compile(loss = "mse", optimizer="adam")

		return model
	
	def train(self, x, y, epoch = 1, verbose = 0):
		self.model.fit(x, y, batch_size = self.batch_size , verbose = verbose)

	def predict(self, s):
		return self.model.predict(s)

	def predictOne(self, s):
		return self.model.predict(tf.reshape(s, [1, self.NbrStates])).flatten()
	
	def copy_weights(self, TrainNet):
		variables1 = self.model.trainable_variables
		variables2 = TrainNet.model.trainable_variables
		for v1, v2 in zip(variables1, variables2):
			v1.assign(v2.numpy())
			
@gdclass
class DDQNAgent(Node2D):
	n_actions = 5
	alpha = 0.0005
	gamma = 0.99
	epsilon = 1.00
	epsilon_dec = 0.999995
	epsilon_min = 0.10
	batch_size = 512
	model_file = 'ddqn_model.h5'
	mem_size = 25000
	replace_target = 25
	input_dims = 6
	
	action_space = [i for i in range(n_actions)]

	memory = ReplayBuffer(mem_size, input_dims, n_actions, discrete=True)
	brain_eval = Brain(input_dims, n_actions, batch_size)
	brain_target = Brain(input_dims, n_actions, batch_size)

	def remember(self, state, action, reward, new_state, done):
		self.memory.store_transition(state, action, reward, new_state, done)

	def choose_action(self, state):
		state = list(state)
		state = np.array(state)
		state = state[np.newaxis, :]
		
		rand = np.random.random()
		if rand < self.epsilon:
			action = random.randrange(self.action_space.__len__())
		else:
			actions = self.brain_eval.predict(state)
			action = np.argmax(actions)

		return action 

	def learn(self):
		if self.memory.mem_cntr > self.batch_size:
			state, action, reward, new_state, done = self.memory.sample_buffer(self.batch_size)
			state = list(state)
			new_state = list(new_state)
			action_values = np.array(self.action_space, dtype=np.int8)
			action_indices = np.dot(action, action_values)

			q_next = self.brain_target.predict(new_state)
			q_eval = self.brain_eval.predict(new_state)
			q_pred = self.brain_eval.predict(state)

			max_actions = np.argmax(q_eval, axis=1)

			q_target = q_pred

			batch_index = np.arange(self.batch_size, dtype=np.int32)

			q_target[batch_index, action_indices] = reward + self.gamma*q_next[batch_index, max_actions.astype(int)]*done

			_ = self.brain_eval.train(state, q_target)

			self.epsilon = self.epsilon*self.epsilon_dec if self.epsilon > self.epsilon_min else self.epsilon_min

	def update_network_parameters(self):
		self.brain_target.copy_weights(self.brain_eval)

	def save_model(self):
		self.brain_eval.model.save(self.model_file)
		
	def load_model(self):
		self.brain_eval.model = load_model(self.model_file)
		self.brain_target.model = load_model(self.model_file)
	   
		if self.epsilon == 0.0:
			self.update_network_parameters()
