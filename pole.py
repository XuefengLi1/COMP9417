
import gym
from gym import wrappers
import numpy as np
import random
import math
from time import sleep

ENVIRONMENT = 'CartPole-v0'
    #'MountainCar-v0'

MONITOR = False
UPLOAD = False
env = gym.make(ENVIRONMENT)

if(MONITOR):
    env = wrappers.Monitor(env, '/Users/smountain/Desktop/9417ASSN2/Monitor')

## Defining the environment related constants

NUM_BUCKETS = (1, 1, 6, 3)  # (x, x', theta, theta')

NUM_ACTIONS = env.action_space.n # (left, right)

# Bounds for each discrete state
STATE_BOUNDS = list(zip(env.observation_space.low, env.observation_space.high))
STATE_BOUNDS[0] = [-2.4, 2.4]
STATE_BOUNDS[1] = [-1.0, 1.0]
STATE_BOUNDS[2] = [-math.radians(15), math.radians(15)]
STATE_BOUNDS[3] = [-math.radians(50), math.radians(50)]

# Index of the action
ACTION_INDEX = len(NUM_BUCKETS)

## Creating a Q-Table for each state-action pair
q_table = np.zeros(NUM_BUCKETS + (NUM_ACTIONS,))

## Learning related constants
MIN_EXPLORE_RATE = 0.01
MIN_LEARNING_RATE = 0.1
DISFACTOR = 1

## Defining the simulation related constants
NUM_EPISODES = 1000
MAX_T = 250
STREAK_TO_END = 120
SOLVED_T = 199
DEBUG_MODE = False


def simulate():

    ## Instantiating the learning related parameters
    learning_rate = get_learning_rate(0)
    explore_rate = get_explore_rate(0)
    discount_factor = DISFACTOR  # since the world is unchanging

    num_streaks = 0

    for episode in range(NUM_EPISODES):

        # Reset the environment
        obv = env.reset()

        # the initial state
        state_0 = state_to_bucket(obv)

        for t in range(MAX_T):
            env.render()

            # Select an action
            action = select_action(state_0, explore_rate)

            # Execute the action
            obv, reward, done, _ = env.step(action)

            # Observe the result
            state = state_to_bucket(obv)

            # Update the Q based on the result
            best_q = np.amax(q_table[state])
            q_table[state_0 + (action,)] += learning_rate*(reward + discount_factor*(best_q) - q_table[state_0 + (action,)])

            # Setting up for the next iteration
            state_0 = state


            if done:
               print("Episode %d finished after %f time steps" % (episode, t))
               if (t >= SOLVED_T):
                   num_streaks += 1
               else:
                   num_streaks = 0
               break

            #sleep(0.25)

        # solved condition may be changed in the future
        if num_streaks > STREAK_TO_END:
            break

        # Update parameters
        explore_rate = get_explore_rate(episode)
        learning_rate = get_learning_rate(episode)

    #close and upload
    env.close()
    if(UPLOAD):
        gym.upload('/Users/smountain/Desktop/9417ASSN2/Monitor', api_key='sk_8xuCUXp9TOSW0DFIUgB12A')


def select_action(state, explore_rate):
    # Select a random action
    if random.random() < explore_rate:
        action = env.action_space.sample()
    # Select the action with the highest q
    else:
        action = np.argmax(q_table[state])
    return action


def get_explore_rate(t):
    return max(MIN_EXPLORE_RATE, min(1, 1.0 - math.log10((t+1)/25)))

def get_learning_rate(t):
    return max(MIN_LEARNING_RATE, min(0.5, 1.0 - math.log10((t+1)/25)))


def state_to_bucket(state):
    bucket_indice = []
    for i in range(len(state)):
        if state[i] <= STATE_BOUNDS[i][0]:
            bucket_index = 0
        elif state[i] >= STATE_BOUNDS[i][1]:
            bucket_index = NUM_BUCKETS[i] - 1
        else:
            # Mapping the state bounds to the bucket array
            bound_width = STATE_BOUNDS[i][1] - STATE_BOUNDS[i][0]
            offset = (NUM_BUCKETS[i]-1)*STATE_BOUNDS[i][0]/bound_width
            scaling = (NUM_BUCKETS[i]-1)/bound_width
            bucket_index = int(round(scaling*state[i] - offset))
        bucket_indice.append(bucket_index)
    return tuple(bucket_indice)

if __name__ == "__main__":
    simulate()
