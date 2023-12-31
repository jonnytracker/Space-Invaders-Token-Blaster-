print('hello')
import gymnasium as gym 

import random
import pyautogui
import time
import numpy as np
import mss as mss
from gymnasium import Env
from gymnasium.spaces import Box, Discrete
import pydirectinput
import cv2
import pytesseract
from matplotlib import pyplot as plt


width = 640
height = 480

time.sleep(3)
########################################################################################################################################




if pyautogui.locateOnScreen('Start.png', confidence=0.9) != None: 
        print("game button found")       
        image = pyautogui.locateOnScreen('Start.png', confidence=0.9)
        if image != None:
            x, y = pyautogui.center(image)
            pyautogui.moveTo(x + 5, y + 20)
            time.sleep(1)
            pyautogui.click()  



time.sleep(4)
result = pyautogui.locateOnScreen('GameScreen.png', confidence=0.6)


if result is not None:
    print("game screen found program starting...")  
    left, top, width, height = result
    print(f"Left: {left}, Top: {top}, Width: {width}, Height: {height}")
else:
    print("Game not found program not started")


#####################################################################################  Environment Class ###################
class WebGame(Env):
    ################# Environment setup ##########################################################
    def __init__(self):
        super().__init__()
        self.observation_space = Box(low=0, high=255, shape=(width, height, 3), dtype=np.uint8)
        self.action_space = Discrete(4)
        self.cap = mss.mss()
        self.game_location = {'top': 0, 'left': 0, 'width': width, 'height': height}
        self.done_location = {'top': 0, 'left': 0, 'width': width, 'height': height}        
        self.initial_alien_population = 0
       
        

    ################ Step function ##############################################################
    def step(self, action):
        
        # Implement the step logic for your game
        action_map = {
            0: 'space',
            1: 'left',
            2: 'no_op',
            3: 'right'
        }

        if action != 2:
            pydirectinput.press(action_map[action])

        # Detect the current alien population
        current_alien_population = self.detect_aliens()

        
        #calculate the game state
        done, _ = self.get_done()  


        # Reward for staying aliveive
        reward = 1 if not done else 0  

        
        # Reward when the number of aliens decreases
        kill_rewards = 5
        if current_alien_population < self.current_alien_population:
            reward += kill_rewards  # Reward when aliens decrease

        # Update the current alien population for the next step
        self.current_alien_population = current_alien_population
      


      
        new_observation = self.get_observation()        
        info = {}
        return new_observation, reward, done, info
    


    #############################   Detect aliens in game #####################################################
    def detect_aliens(self):
        population = 0
        aliens = list(pyautogui.locateAllOnScreen('alienshipgreen.png', grayscale=True, confidence=0.5))
        population = len(aliens)
        print(f"detecting aliens amount {population}")
        return population
        

    



    ################################ Rendering function ##############################################################
    def render(self):
        cv2.imshow('Game', self.get_observation())
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.close()



    
    ########################### Close function ################################################################
    def close(self):
        cv2.destroyAllWindows()
    




    ################################################### Reset the game ########################################################
    def reset(self):
        time.sleep(1)      

        if pyautogui.locateOnScreen('Restart.png', confidence=0.9) != None:        
            image = pyautogui.locateOnScreen('Restart.png', confidence=0.9)
            if image != None:
                x, y = pyautogui.center(image)
                pyautogui.moveTo(x + 5, y + 20)
                time.sleep(2)
                pyautogui.click()                
                time.sleep(1)


        # Capture the initial alien population when the game is reset
        self.initial_alien_population = self.detect_aliens()

        return self.get_observation()
    




    ##################### Get part of the game  ###################################
    def get_observation(self):        
        raw = np.array(self.cap.grab(self.game_location))[:,:,:3].astype(np.uint8)
        desired_width = int(width / 2)
        desired_height = int(height / 2)
        resized = cv2.resize(raw, (desired_width, desired_height))
        channel = np.reshape(resized, (3,desired_height,desired_width))
        return channel
 





    ################### Get done text  ######################################
    def get_done(self):
        done=False
        image = None      
        if pyautogui.locateOnScreen('Restart.png', confidence=0.9) != None:        
            image = pyautogui.locateOnScreen('Restart.png', confidence=0.9)
            if image != None:
                done = True
            
        else:
            done = False
            
        return done, image
################################################################################################################################

env = WebGame()

obs=env.get_observation()

for episode in range(10): 
    obs = env.reset()
    done = False  
    total_reward   = 0
    while not done: 
        obs, reward,  done, info =  env.step(env.action_space.sample())
        total_reward  += reward
    print('Total Reward for episode {} is {}'.format(episode, total_reward))    
