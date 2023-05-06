import signal
import threading
from getpass import getpass
from random import randint
from time import sleep

import keyboard
import yaml
from yaml import SafeLoader

from ledmatrix.ledmatrix import Image, LEDMatrix

ip_address = "192.168.2.160"  # replace with the receiver's IP address
port = 21324  # replace with the receiver's port number

# Create a UDP socket
game_running = True

ledmatrix = LEDMatrix(ip_address, port)
ledmatrix.connect()

image = Image(16, 16)


class Player:
    def __init__(
        self, x, y, up_button, down_button, left_button, right_button, name
    ) -> None:
        self.up_button = up_button
        self.down_button = down_button
        self.left_button = left_button
        self.right_button = right_button
        self.x = x
        self.y = y
        self.score = 0
        self.name = name
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))

    def set_color(self, color):
        self.color = color

    def update(self):
        if keyboard.is_pressed(self.up_button):
            self.x = max(self.x - 1, 0)
        elif keyboard.is_pressed(self.down_button):
            self.x = min(self.x + 1, 15)
        elif keyboard.is_pressed(self.left_button):
            self.y = min(self.y + 1, 15)
        elif keyboard.is_pressed(self.right_button):
            self.y = max(self.y - 1, 0)


def handle_ctrl_c(*args):
    # stop main thread (which is probably blocked reading input) via an interrupt signal
    # only available for windows in Python version 3.2 or higher
    global game_running
    game_running = False


counter = 0
players = []
with open("snek.yaml", "r") as config_file:
    config = yaml.load(config_file, Loader=SafeLoader)
    for player in config["game"]["players"]:
        p = Player(
            randint(0, 15),
            randint(0, 15),
            player["up_key"],
            player["down_key"],
            player["left_key"],
            player["right_key"],
            player["name"],
        )
        p.set_color(tuple([int(value) for value in player["color"].split(",")]))
        players.append(p)
from time import time_ns

start = time_ns()

gx, gy = randint(0, 15), randint(0, 15)

signal.signal(signal.SIGINT, handle_ctrl_c)


def change_goal_position():
    global gx
    global gy
    gx, gy = randint(0, 15), randint(0, 15)


def main_loop():
    global start
    counter = 0
    while game_running and not keyboard.is_pressed("esc"):
        image.clear(
            (255, 255, 255), opacity=0.05
        )  # randint(0, 255), randint(0, 255), randint(0, 255)))
        counter = (counter + 1) % 255
        delay = 1 / 60

        if time_ns() - start > 1000000 * 5:

            start = time_ns()
            for player in players:
                player.update()

                if player.x == gx and player.y == gy:
                    player.score += 1
                    change_goal_position()

                image.set_pixel(player.x, player.y, player.color)
        image.set_pixel(gx, gy, (0, 0, 255))
        ledmatrix.send(image)
        sleep(delay)

    keyboard.press("enter")
    sleep(0.05)
    keyboard.release("enter")

    for player in players:
        print(player.name + ": " + str(player.score))
    print("")


t = threading.Thread(target=main_loop)
t.start()
getpass("")
t.join()
