"""
This the primary class for the Mario Expert agent. It contains the logic for the Mario Expert agent to play the game and choose actions.

Your goal is to implement the functions and methods required to enable choose_action to select the best action for the agent to take.

Original Mario Manual: https://www.thegameisafootarcade.com/wp-content/uploads/2017/04/Super-Mario-Land-Game-Manual.pdf
"""

import json
import logging
import random

import cv2
from mario_environment import MarioEnvironment
from pyboy.utils import WindowEvent


class MarioController(MarioEnvironment):
    """
    The MarioController class represents a controller for the Mario game environment.

    You can build upon this class all you want to implement your Mario Expert agent.

    Args:
        act_freq (int): The frequency at which actions are performed. Defaults to 10.
        emulation_speed (int): The speed of the game emulation. Defaults to 0.
        headless (bool): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(
        self,
        act_freq: int = 10,
        emulation_speed: int = 1,
        headless: bool = False,
    ) -> None:
        super().__init__(
            act_freq=act_freq,
            emulation_speed=emulation_speed,
            headless=headless,
        )

        self.act_freq = act_freq

        # Example of valid actions based purely on the buttons you can press
        valid_actions: list[WindowEvent] = [
            WindowEvent.PRESS_ARROW_DOWN,
            WindowEvent.PRESS_ARROW_LEFT,
            WindowEvent.PRESS_ARROW_RIGHT,
            WindowEvent.PRESS_ARROW_UP,
            WindowEvent.PRESS_BUTTON_A,
            WindowEvent.PRESS_BUTTON_B,
        ]

        release_button: list[WindowEvent] = [
            WindowEvent.RELEASE_ARROW_DOWN,
            WindowEvent.RELEASE_ARROW_LEFT,
            WindowEvent.RELEASE_ARROW_RIGHT,
            WindowEvent.RELEASE_ARROW_UP,
            WindowEvent.RELEASE_BUTTON_A,
            WindowEvent.RELEASE_BUTTON_B,
        ]

        self.valid_actions = valid_actions
        self.release_button = release_button

    def run_action(self, action: int) -> None:
        """
        This is a very basic example of how this function could be implemented

        As part of this assignment your job is to modify this function to better suit your needs

        You can change the action type to whatever you want or need just remember the base control of the game is pushing buttons
        """

        # Simply toggles the buttons being on or off for a duration of act_freq
        if (action == 6):
            self.pyboy.send_input(self.valid_actions[2])
            self.pyboy.send_input(self.valid_actions[4])
        else:
            self.pyboy.send_input(self.valid_actions[action])

        for _ in range(self.act_freq):
            self.pyboy.tick()

        if (action == 6):
            self.pyboy.send_input(self.release_button[2])
            self.pyboy.send_input(self.release_button[4])
        else:
            self.pyboy.send_input(self.release_button[action])


class MarioExpert:
    """
    The MarioExpert class represents an expert agent for playing the Mario game.

    Edit this class to implement the logic for the Mario Expert agent to play the game.

    Do NOT edit the input parameters for the __init__ method.

    Args:
        results_path (str): The path to save the results and video of the gameplay.
        headless (bool, optional): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(self, results_path: str, headless=False):
        self.results_path = results_path

        self.environment = MarioController(headless=headless)

        self.video = None

    def choose_action(self):
        action = 0
        game_area = self.environment.game_area()
        
        DOWN = 0
        LEFT = 1
        RIGHT = 2
        JUMP = 4
        JUMP_RIGHT = 6
        CHIBIBO = 15
        NOKOBON = 16
        KUMO = 18
        BUNBUN = 19
        
        # Implement your code here to choose the best action

        if (1 in game_area):
            mario = self.get_player_position()

            if(mario[1] == 19):
                action = RIGHT
            elif(mario[0] == 15):
                action = DOWN
            elif(CHIBIBO in game_area):
                chibibo_position = self.get_obstacle_position(CHIBIBO)    # Obtain location of goomba on screen
                # Jump logic for Goomba encounters
                if((game_area[mario[0]][mario[1]+2] == CHIBIBO) or   # If Goomba is in front of Mario
                   (game_area[mario[0]][mario[1]+3] == CHIBIBO) or 
                   (game_area[mario[0]][mario[1]-1] == CHIBIBO) or # If Goomba is behind Mario
                    (game_area[mario[0]][mario[1]-2] == CHIBIBO) or  
                   (game_area[mario[0]][mario[1]+1] != 0)):
                    action = JUMP
                elif(any(game_area[:, mario[1]-1] == CHIBIBO) or (game_area[mario[0]][mario[1]+4] == 10)): # Give some space for goomba to approach
                    action = LEFT
                elif((any(game_area[mario[0]] == CHIBIBO)) or (chibibo_position[0] > mario[0])): # If same level as goomba or goomba is below Mario
                    if(chibibo_position[0] > mario[0]):
                        if((chibibo_position[1] - mario[1] > 3)): # Keep moving if Goomba is far away
                            action = RIGHT
                        elif((chibibo_position[1] - mario[1] < -3)): # Go to the left goomba 
                            action = LEFT
                    elif (mario[1] - chibibo_position[1] > 0): # Go back if goomba is missed
                        action = LEFT
                    else:
                        action = RIGHT
            elif(NOKOBON in game_area):
                nokobon_position = self.get_obstacle_position(NOKOBON)    # Obtain location of nokobon on screen
                # Jump logic for Nokobon encounters
                if((game_area[mario[0]][mario[1]+1] == NOKOBON) or   # If nokobon is in front of Mario
                   (game_area[mario[0]][mario[1]-1] == NOKOBON) or # If nokobon is behind Mario
                    (game_area[mario[0]][mario[1]-2] == NOKOBON) or  
                   (game_area[mario[0]][mario[1]+1] != 0)):
                    action = JUMP
                elif(any(game_area[:, mario[1]-1] == NOKOBON) or (game_area[mario[0]][mario[1]+4] == 10)): # Give some space for nokobon to approach
                    action = LEFT
                elif((any(game_area[mario[0]] == NOKOBON)) or (nokobon_position[0] > mario[0])): # If same level as nokobon or nokobon is below Mario
                    if(nokobon_position[0] > mario[0]):
                        if((nokobon_position[1] - mario[1] > 3)): # Keep moving if Nokobon is far away
                            action = RIGHT
                        elif((nokobon_position[1] - mario[1] < -3)): # Go to the left Nokobon 
                            action = LEFT
                    elif (mario[1] - nokobon_position[1] > 0): # Go back if nokobon is missed
                        action = LEFT
                    else:
                        action = JUMP_RIGHT
                else:
                    action = JUMP_RIGHT
            elif (KUMO in game_area):   
                kumo_position = self.get_obstacle_position(KUMO)    # Obtain position of Kumo

                if ((game_area[mario[0]][mario[1]+1] == KUMO)): # Jump if Kumo detected in front of Mario
                    action = JUMP
                elif ((any(game_area[mario[0]] == KUMO)) or (kumo_position[0] > mario[0])): #  Determine direction of movement
                    if(kumo_position[0] > mario[0]):
                        if((kumo_position[1] - mario[1] < -3)):
                            action = LEFT
                        else:
                            action = RIGHT
                    else:
                        action = RIGHT
                else:
                    action = LEFT
            elif (BUNBUN in game_area):
                BUNBUN = self.get_obstacle_position(BUNBUN) # Obtain position of Bunbun

                if(any(game_area[mario[0]][mario[1]+2] == BUNBUN)):
                    action = JUMP_RIGHT
            else:  
                if ((game_area[mario[0]][mario[1]+1] != 0)):    # Jump if obstacle is detected
                    action = JUMP
                    if ((game_area[mario[0]][mario[1]+1] == 5)): # Continue moving if obstacle is a coin
                        action = RIGHT
                elif (game_area[mario[0]+1][mario[1]+1] == 10):
                    action = RIGHT  # Move right
                elif (game_area[15][mario[1]+1] == 0):  # Jump if there is a gap detected
                    action = JUMP_RIGHT
                else:
                    action = RIGHT
                

        return action
    
    def get_player_position(self):
        """
        Finds the bottom-right corner of the player's position (2x2 matrix of 1s) in the game area.

        Args:
            self: An instance of the agent class.

        Returns:
            A tuple containing the row and column index of the bottom-right corner of the player 
            (2x2 matrix of 1s), or None if not found.
        """
        game_area = self.environment.game_area()
        rows, cols = len(game_area), len(game_area[0])  # Get dimensions of the game area

         # Iterate through all possible bottom-right corners
        for row in range(rows - 1):
            for col in range(cols - 1):
            # Check if top-left corner is 1
                if game_area[row][col] == 1:
                # Check if all elements within the Mario's 2x2 matrix are 1s
                    if (game_area[row][col + 1] == 1 and
                        game_area[row + 1][col] == 1 and
                        game_area[row + 1][col + 1] == 1):
                        return row + 1, col + 1  # Bottom-right corner

        # Mario (2x2 matrix of 1s) not found in the game area
        return (1,1)
    
    def get_obstacle_position(self, obstacle_value):
        """
        Finds the position (row, col) of the first occurrence of an obstacle in the game area.

        Args:
            self: An instance of the agent class.
            obstacle_value: The value representing the obstacle in the game area.

        Returns:
            A tuple containing the row and column index of the obstacle, or None if not found.
        """
        game_area = self.environment.game_area()

        for row, row_data in enumerate(game_area):
            for col, value in enumerate(row_data):
                if value == obstacle_value:
                    return row, col

        # Obstacle not found
        return None



    def step(self):
        """
        Modify this function as required to implement the Mario Expert agent's logic.

        This is just a very basic example
        """

        # Choose an action - button press or other...
        action = self.choose_action()

        # Run the action on the environment
        self.environment.run_action(action)

    def play(self):
        """
        Do NOT edit this method.
        """
        self.environment.reset()

        frame = self.environment.grab_frame()
        height, width, _ = frame.shape

        self.start_video(f"{self.results_path}/mario_expert.mp4", width, height)

        while not self.environment.get_game_over():
            frame = self.environment.grab_frame()
            self.video.write(frame)

            self.step()

        final_stats = self.environment.game_state()
        logging.info(f"Final Stats: {final_stats}")

        with open(f"{self.results_path}/results.json", "w", encoding="utf-8") as file:
            json.dump(final_stats, file)

        self.stop_video()

    def start_video(self, video_name, width, height, fps=30):
        """
        Do NOT edit this method.
        """
        self.video = cv2.VideoWriter(
            video_name, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )

    def stop_video(self) -> None:
        """
        Do NOT edit this method.
        """
        self.video.release()
