import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
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


class Brain(nn.Module):
	def __init__(self, input_dims, n_actions, batch_size=256):
		super(Brain, self).__init__()
		self.fc1 = nn.Linear(input_dims, 256)
		self.fc2 = nn.Linear(256, n_actions)
		self.optimizer = optim.Adam(self.parameters(), lr=0.0005)
		self.loss = nn.MSELoss()
		self.batch_size = batch_size
		self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
		self.to(self.device)

	def forward(self, state):
		x = torch.relu(self.fc1(state))
		x = torch.softmax(self.fc2(x), dim=1)
		return x

	def train_step(self, x, y):
		self.optimizer.zero_grad()
		x = torch.tensor(x, dtype=torch.float32).to(self.device)
		y = torch.tensor(y, dtype=torch.float32).to(self.device)
		predictions = self.forward(x)
		loss = self.loss(predictions, y)
		loss.backward()
		self.optimizer.step()

	def predict(self, s):
		self.eval()
		s = torch.tensor(s, dtype=torch.float32).to(self.device)
		with torch.no_grad():
			return self.forward(s).cpu().numpy()

	def predict_one(self, s):
		s = np.reshape(s, [1, -1])
		return self.predict(s).flatten()

	def copy_weights(self, other):
		self.load_state_dict(other.state_dict())


@gdclass
class DDQNAgent(Node2D):
	n_actions = 5
	alpha = 0.0005
	gamma = 0.99
	epsilon = 1.00
	epsilon_dec = 0.9995
	epsilon_min = 0.10
	batch_size = 512
	model_file = 'ddqn_model.pt'
	mem_size = 25000
	replace_target = 25
	input_dims = 10

	action_space = [i for i in range(n_actions)]

	memory = ReplayBuffer(mem_size, input_dims, n_actions, discrete=True)
	brain_eval = Brain(input_dims, n_actions, batch_size)
	brain_target = Brain(input_dims, n_actions, batch_size)

	def remember(self, state, action, reward, new_state, done):
		state = list(state)
		new_state = list(new_state)
		self.memory.store_transition(state, action, reward, new_state, done)

	def choose_action(self, state):
		state = list(state)
		state = np.array(state)[np.newaxis, :]
		rand = np.random.random()
		if rand < self.epsilon:
			return random.randrange(len(self.action_space))
		else:
			actions = self.brain_eval.predict(state)
			return self.fastest_argmax(actions[0])

	def fastest_argmax(self, array):
		return int(np.argmax(array))

	def learn(self):
		if self.memory.mem_cntr > self.batch_size:
			state, action, reward, new_state, done = self.memory.sample_buffer(self.batch_size)
			action_values = np.array(self.action_space, dtype=np.int8)
			action_indices = np.dot(action, action_values)

			q_next = self.brain_target.predict(new_state)
			q_eval = self.brain_eval.predict(new_state)
			q_pred = self.brain_eval.predict(state)

			max_actions = np.argmax(q_eval, axis=1)
			q_target = q_pred.copy()

			batch_index = np.arange(self.batch_size, dtype=np.int32)
			q_target[batch_index, action_indices] = reward + self.gamma * q_next[batch_index, max_actions] * done

			self.brain_eval.train_step(state, q_target)
			self.epsilon = max(self.epsilon * self.epsilon_dec, self.epsilon_min)

	def update_network_parameters(self):
		self.brain_target.copy_weights(self.brain_eval)

	def save_model(self):
		torch.save(self.brain_eval.state_dict(), self.model_file)

	def load_model(self):
		self.brain_eval.load_state_dict(torch.load(self.model_file))
		self.brain_target.load_state_dict(torch.load(self.model_file))
		if self.epsilon == 0.0:
			self.update_network_parameters()
