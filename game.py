# https://github.com/jcoriell/room-adventure-241-002/

from tkinter import (
    # Widgets
    Frame, Label, Text, PhotoImage, Entry,

    # Constants
    X, Y, BOTH,
    BOTTOM, RIGHT, LEFT,
    DISABLED, NORMAL, END,

    # Additional stuff for Type Hints
    Tk
)
from room import Room # from the room.py file
import os  # for building filepaths

class Game(Frame):

    # statuses
    STATUS_DEFAULT = "I don't understand. Try verb noun. Valid verbs are go, look, take."
    STATUS_DEAD = "You are dead."
    STATUS_BAD_EXIT = "Invalid Exit."

    STATUS_ROOM_CHANGE = "Room Changed."
    STATUS_GRABBED = "Item grabbed."
    STATUS_BAD_GRABBABLE = "I can't grab that."

    STATUS_BAD_ITEM = "I don't see that."

    # exit actions
    EXIT_ACTIONS = ["quit", "exit", "bye", "adios", "q"]

    # game dimensions
    WIDTH = 800
    HEIGHT = 600

    def __init__(self, parent: Tk):
        """
            The Game Class.
            There should be only one game class.
            Responsible for the flow of the game.

            parent: Tk - a Tk object representing the window the game runs in.
        """
        self.inventory = []
        Frame.__init__(self, parent)
        self.pack(fill=BOTH, expand=1) 

    def setup_game(self):
        """
            Creates the rooms and adds items and exits to the rooms.
        """
        # create Rooms
        r1 = Room("Room 1", os.path.join("images", "room1.gif"))
        r2 = Room("Room 2", os.path.join("images", "room2.gif"))
        r3 = Room("Room 3", os.path.join("images", "room3.gif"))
        r4 = Room("Room 4", os.path.join("images", "room4.gif"))

        # create the exits
        r1.add_exit("east", r2)
        r1.add_exit("south", r3)

        r2.add_exit("west", r1)
        r2.add_exit("south", r4)

        r3.add_exit("north", r1)
        r3.add_exit("east", r4)

        r4.add_exit("north", r2)
        r4.add_exit("west", r3)
        r4.add_exit("south", None) # None for death sequence

        # add items to the rooms
        r1.add_item("chair", "Its made of wicker.")
        r1.add_item("bigger_chair", "It's made of more wicker. There is a key on it.")

        r2.add_item("smaller_chair", "Its made of less wicker.")
        r2.add_item("fireplace", "It is not a chair. Please don't sit in it.")

        r3.add_item("desk_chair", "Its made of wicker too. So is the desk.")
        r3.add_item("chair", "Yet another chair.")

        r4.add_item("croissant", "Its made of chairs.")

        # add grabbables
        r1.add_grabbable("key")
        r2.add_grabbable("fire")
        r3.add_grabbable("chair")

        # set current room
        self.current_room = r1


    def setup_gui(self):
        # setup the input element
        self.player_input = Entry(self, bg="white", fg="black")
        self.player_input.bind("<Return>", self.process_input)
        self.player_input.pack(side=BOTTOM, fill=X)
        self.player_input.focus()
        
        # setup the image element
        img = None                      # the actual image
        img_width = Game.WIDTH // 2
        self.image_container = Label(   # the Label element containing the image
            self,
            width = img_width,
            image = img
        )
        self.image_container.image = img                # persists the image past this function
        self.image_container.pack(side=LEFT, fill=Y)
        self.image_container.pack_propagate(False)      # prevent image width from controlling container width

        # setup the info area
        text_container_width = Game.WIDTH // 2
        text_container = Frame(self, width=text_container_width)

        self.text = Text(
            text_container,     # parent element is the text_container this time, not self (the Game)
            bg="lightgrey",
            fg="black",
            state=DISABLED      # making so the text cannot be changed
        )
        self.text.pack(fill=Y, expand=1)

        text_container.pack(side=RIGHT, fill=Y)
        text_container.pack_propagate(False)


    def set_status(self, status):
        self.text.config(state=NORMAL)  # make it editable
        self.text.delete(1.0, END)      # Delete everything in the text

        if self.current_room == None:
            self.text.insert(END, Game.STATUS_DEAD)
        else:
            content = f"{self.current_room}\n"
            content += f"You are carrying: {self.inventory}\n\n"
            content += status
            self.text.insert(END, content)

        self.text.config(state=DISABLED)


    def set_image(self):
        if self.current_room == None:
            img = PhotoImage(file=os.path.join("images", "skull.gif"))
        else:
            img = PhotoImage(file = self.current_room.image)
        
        self.image_container.config(image=img)
        self.image_container.image = img        # again, persist past the function

        

    def clear_entry(self):
        self.player_input.delete(0, END)

    def handle_verb_go(self, destination):
        status = Game.STATUS_BAD_EXIT

        if destination in self.current_room.exits:      # .exits is a dictionary 
            self.current_room = self.current_room.exits[destination]    # the 'exits' attribute is a dictionary
            status = Game.STATUS_ROOM_CHANGE

        self.set_status(status)
        self.set_image()

    def handle_verb_look(self, item):
        status = Game.STATUS_BAD_ITEM

        if item in self.current_room.items:             # .items is a dictionary
            status = self.current_room.items[item]
        
        self.set_status(status)

    def handle_verb_take(self, grabbable):
        status = Game.STATUS_BAD_GRABBABLE

        if grabbable in self.current_room.grabbables:   # .grabbables is a list
            self.inventory.append(grabbable)
            self.current_room.delete_grabbable(grabbable)
            status = Game.STATUS_GRABBED

        self.set_status(status)

    def handle_default(self):
        self.set_status(Game.STATUS_DEFAULT)
        self.clear_entry()

    def play(self):
        self.setup_game()
        self.setup_gui()
        self.set_image()
        self.set_status("")

    def process_input(self, event):
        action = self.player_input.get()
        action = action.lower()

        if action in Game.EXIT_ACTIONS:
            exit()                      # kills the game

        if self.current_room == None:
            self.clear_entry()
            return                      # this kills the process_input function
        
        words = action.split()

        if len(words) != 2:
            self.handle_default()
            return 
        
        verb = words[0]
        noun = words[1]

        match verb:
            case "go": self.handle_verb_go(destination=noun)
            case "look": self.handle_verb_look(item=noun)
            case "take": self.handle_verb_take(grabbable=noun)

        self.clear_entry()




