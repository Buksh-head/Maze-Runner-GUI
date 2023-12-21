import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from typing import *
from PIL import Image, ImageTk
from a2_solution import *
from a3_support import *
from a3_support import AbstractGrid
from constants import GAME_FILE, TASK

__author__ = "<Adnaan Buksh>, <47435568>"
__email__ = "<adnaan.buksh@uqconnect.edu.au>"
__version__ = 1.0

COIN_WORD_POS = (0, 3)
COIN_NUM_POS = (1, 3)
STAT_DIMENSIONS = (2, 4)
TITLE_HEIGHT = 150
MAX_SEC = 60
stat_num = ["HP", "Hunger", "Thirst", "Coins"]
WINDOW_WIDTH = MAZE_WIDTH + INVENTORY_WIDTH
WINDOW_HEIGHT = MAZE_HEIGHT + STATS_HEIGHT + TITLE_HEIGHT


# Write your classes here
class LevelView(AbstractGrid):
	"""Displays the colour representation of
	   maze (tiles) along with the entities."""
	def __init__(self, master: Union[tk.Tk, tk.Frame],
	             dimensions: tuple[int, int], size: tuple[int, int],
	             **kwargs: object):

		super().__init__(master, dimensions, size, **kwargs)
		self.master = master
		self.pack(side=tk.LEFT)

	def draw(self,
	         tiles: list[list[Tile]],
	         items: dict[tuple[int, int], Item],
	         player_pos: tuple[int, int]) -> None:
		"""Draws the current game state.

        Parameters:
            tiles (list[list[Tile]]): The tiles on the maze
            items (dict[tuple[int, int], Item]): The items on the maze
            player_pos (tuple[int, int]): The position of the player
        """
		count_row = 0

		for rows in tiles:
			count_col = 0
			for columns in rows:
				self.create_rectangle(self.get_bbox((count_row, count_col)),
				                      fill=TILE_COLOURS[columns.get_id()])
				count_col = count_col + 1

			count_row = count_row + 1

		for pos, name in items.items():
			self.create_oval(self.get_bbox(pos),
			                 fill=ENTITY_COLOURS[name.get_id()])
			self.annotate_position(pos, name.get_id())

		self.create_oval(self.get_bbox(player_pos),
		                 fill=ENTITY_COLOURS[PLAYER])
		self.annotate_position(player_pos, PLAYER)


class StatsView(AbstractGrid):
	"""displays the player’s stats (HP,health, thirst),
	   along with the number of coins collected"""
	def __init__(self, master: Union[tk.Tk, tk.Frame], width: int,
	             dimensions: tuple[int, int], size: tuple[int, int],
	             **kwargs: object) -> None:
		"""
		Parameters:
			width: Pixel width of stat
		"""
		super().__init__(master, dimensions, size, **kwargs)

		self.master = master
		self.config(bg=THEME_COLOUR, width=width, height=STATS_HEIGHT)
		self.pack(fill=tk.BOTH, expand=1)

	def draw_stats(self, player_stats: tuple[int, int, int]) -> None:
		"""Draws the player’s stats (hp, hunger, thirst)
		Parameters:
			player_stats: Player HP, health and thirst
		"""
		count = 0
		for info in player_stats:
			self.annotate_position((0, count), stat_num[count])
			self.annotate_position((1, count), info)
			count = count + 1

	def draw_coins(self, num_coins: int) -> None:
		"""Draws the number of coins.
		Parameters:
			num_coins: number fo coins collected
		"""
		self.annotate_position(COIN_WORD_POS, stat_num[3])
		self.annotate_position(COIN_NUM_POS, num_coins)


class InventoryView(tk.Frame):
	"""displays the items the player has in their inventory and
	   provides a mechanism through which the user can apply items"""
	def __init__(self, master: Union[tk.Tk, tk.Frame], **kwargs) -> None:
		"""Packs the inherited frame to the master and the Inventory label
		to the frame"""
		super().__init__(master)
		self.pack()
		self._title = tk.Label(self, text="Inventory",
		                       font=HEADING_FONT)
		self._title.pack(side=tk.TOP, anchor=tk.E)

	def set_click_callback(self, callback: Callable[[str], None]) -> None:
		"""Sets the function to be called when an item is clicked
		   Parameters:
	            callback: takes one argument"""
		self.callback = callback

	def clear(self) -> None:
		"""Clears all widgets in the Frame"""
		for widget in self.master.winfo_children():
			if widget is not tk.Menu:
				widget.destroy()

	def _draw_item(self, name: str, num: int, colour: str) -> None:
		"""Creates and binds a single Label in the frame.
		Parameters:
			name: name of the item
			num: amount of items player has
			colour: background colour of the label
		"""
		self.name = name
		self.num = num
		if name != "Coin":
			self._items = tk.Label(self,
			                       text=f'{self.name}: {self.num}',
			                       bg=colour)

			self._items.pack(side=tk.TOP, expand=1, fill=tk.X)
			self._items.bind('<Button-1>', lambda e: self.callback(name))

	def draw_inventory(self, inventory: Inventory) -> None:
		"""Draws any non-coin inventory items with their quantities
		   and binds the callback
		   Parameters:
		   	  inventory: Inventory class"""
		for name, amount in inventory.get_items().items():
			self._draw_item(name, len(amount), ENTITY_COLOURS[name[0]])


class GraphicalInterface(UserInterface):
	"""manages the overall view the title banner and the three major widgets
	   and enables event handling"""
	def __init__(self, master: tk.Tk) -> None:
		"""Sets the title of the window to MazeRunner"""
		self.master = master
		self.master.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
		self.master.title("MazeRunner")

	def create_interface(self, dimensions: tuple[int, int]) -> None:
		"""Creates the components
		Parameters:
			dimensions: (row, column) of maze
		"""
		self._frame = tk.Frame(self.master)
		self._frame.pack(fill=tk.BOTH)
		self.dimensions = dimensions

		titlebar = tk.Label(self._frame,
		                    text="MazeRunner",
		                    background=THEME_COLOUR,
		                    font=BANNER_FONT)
		titlebar.pack(fill=tk.X)

		self.make_stat = StatsView(self.master, WINDOW_WIDTH, STAT_DIMENSIONS,
		                           (WINDOW_WIDTH, STATS_HEIGHT))
		self.make_maze = LevelView(self._frame, dimensions, (MAZE_WIDTH,
		                                                     MAZE_HEIGHT))
		self.make_inv = InventoryView(self._frame)

	def clear_all(self) -> None:
		"""Calls the clear function"""
		LevelView(self.master, (5, 5), (MAZE_WIDTH, MAZE_HEIGHT)).clear()
		InventoryView(self.master).clear()

	def set_maze_dimensions(self, dimensions: tuple[int, int]) -> None:
		"""Sets maze dimensions
		Parameters:
			dimensions: (row, column) of maze"""
		self.clear_all()
		self.create_interface(dimensions)

	def bind_keypress(self, command: Callable[[tk.Event], None]) -> None:
		"""Binds the given command to the general keypress event"""
		self.master.bind('<Key>', command)

	def set_inventory_callback(self, callback: Callable[[str], None]) -> None:
		"""Sets the function to be called when an item is clicked in the
		   inventory view to be callback."""
		self.make_inv.set_click_callback(callback)

	def draw_inventory(self, inventory: Inventory) -> None:
		"""Draws any non-coin inventory items with their quantities
		   and binds the callback
		   Parameters:
		   	  inventory: Inventory class"""
		self.make_inv.draw_inventory(inventory)

	def _draw_inventory(self, inventory: Inventory) -> None:
		"""Draws the inventory and number of coins
		   Parameters:
		   	  inventory: Inventory class"""
		self.draw_inventory(inventory)
		if 'Coin' not in inventory.get_items().keys():
			self.make_stat.draw_coins(0)
		else:
			self.make_stat.draw_coins(len(inventory.get_items()['Coin']))

	def _draw_level(self, maze: Maze, items: dict[tuple[int, int], Item],
	                player_position: tuple[int, int]) -> None:
		"""Draws the level
		   Parameters:
			  maze: tiles of maze
			  item: items on maze
			  player_pos: Position of player (row, column)
		   """

		self.make_maze.draw(maze.get_tiles(), items, player_position)

	def _draw_player_stats(self, player_stats: tuple[int, int, int]) -> None:
		"""Draws the player stats
		   Parameters:
			  player_stats: players stat"""
		self.make_stat.draw_stats(player_stats)


class GraphicalMazeRunner(MazeRunner):
	"""Controller class for a game of MazeRunner"""
	def __init__(self, game_file: str, root: tk.Tk) -> None:
		""" Sets up initial game state

        Parameters:
            game_file: Path to the file from which the game levels are loaded
            root: root window
        """
		self.master = root
		self.game_file = game_file
		self.model = Model(self.game_file)
		self.min = 0
		self.sec = -2  # Buffer before the game starts

		self.interface = GraphicalInterface(self.master)

	def _handle_keypress(self, e: tk.Event) -> None:
		"""handles key press
		   Parameters:
		   	  e: the key that was pressed"""
		if e.char in MOVE_DELTAS.keys():
			self.model.move_player(MOVE_DELTAS[e.char])
			if self.model.has_won():
				messagebox.showinfo(title="Result",
				                    message=WIN_MESSAGE)
				self.master.destroy()

			else:
				self.interface.clear_all()
				self.play()

			if self.model.has_lost():
				messagebox.showinfo(title="Result",
				                    message=LOSS_MESSAGE)
				self.master.destroy()

	def _apply_item(self, item_name: str) -> None:
		"""Applies item to player
		   Parameters:
		   	  item_name: name of the item"""
		item = self.model.get_player().get_inventory().remove_item(
			item_name)
		item.apply(self.model.get_player())
		self.interface.clear_all()
		self.play()

	def timer(self) -> None:
		"""Increments every second to count time"""
		self.sec = self.sec + 1
		if self.sec == MAX_SEC:  # Adds to minute after 60 seconds
			self.sec = self.sec - MAX_SEC
			self.min = self.min + 1

		self.master.after(1000, self.timer)

	def play(self) -> None:
		"""Causes gameplay"""
		self.interface.clear_all()
		self.interface.create_interface(self.model.get_current_maze()
		                                .get_dimensions())
		self.interface.bind_keypress(self._handle_keypress)
		self.interface.set_inventory_callback(self._apply_item)
		self.interface.draw(self.model.get_current_maze(),
		                    self.model.get_current_items(),
		                    self.model.get_player().get_position(),
		                    self.model.get_player_inventory(),
		                    self.model.get_player_stats())


# Task 2 Classes
class ImageLevelView(LevelView):
	"""Displays the Image representation of
	   maze (tiles) along with the entities."""
	def __init__(self, master, dimensions, size, **kwargs) -> None:
		super().__init__(master, dimensions, size, **kwargs)
		self.box_size = self.get_cell_size()
		self.width = list(self.box_size)[0]
		self.height = list(self.box_size)[1]
		self.all_image = {}
		# Saves all the images in a dictionary
		for name, path in ENTITY_IMAGES.items():
			self.all_image[name] = ImageTk.PhotoImage(Image.open('images/'+path)
			                           .resize(self.box_size))
		for name, path in TILE_IMAGES.items():
			self.all_image[name] = ImageTk.PhotoImage(Image.open('images/'+path)
			                                        .resize(self.box_size))

	def draw(self, tiles: list[list[Tile]],
	         items: dict[tuple[int, int], Item],
	         player_pos: tuple[int, int]) -> None:
		"""Draws the images maze"""
		buffer_width = self.width / 2
		buffer_height = self.height / 2
		count_row = buffer_height

		for row in tiles:
			count_col = buffer_width
			for column in row:
				self.create_image(count_col, count_row,
				                  image=self.all_image[column.get_id()])
				count_col = count_col + self.width

			count_row = count_row + self.height
		# Position is times by width then + buffer to get correct position
		# on the canvas
		for x, y in items.items():
			pos = list(x)
			new_pos = (pos[1] * self.width + buffer_width,
			           pos[0] * self.height + buffer_height)
			self.create_image(new_pos, image=self.all_image[y.get_id()])

		old_player = list(player_pos)
		new_player = (old_player[1] * self.width + buffer_width,
		              old_player[0] * self.height + buffer_height)
		self.create_image(new_player, image=self.all_image[PLAYER])


class ImageGraphicalInterface(GraphicalInterface):
	"""Manages the images interface"""
	def create_interface(self, dimensions: tuple[int, int]) -> None:
		"""Makes the class instances and the title bar
		Parameters:
			dimensions: (row, column) of the maze
		"""
		self.dimensions = dimensions
		self._frame = tk.Frame(self.master)
		self._frame.pack(fill=tk.BOTH)

		titlebar = tk.Label(self._frame,
		                    text="MazeRunner",
		                    background=THEME_COLOUR,
		                    font=BANNER_FONT)
		titlebar.pack(fill=tk.X)
		self.make_stat = StatsView(self.master, WINDOW_WIDTH, STAT_DIMENSIONS,
		                           (WINDOW_WIDTH, STATS_HEIGHT))
		self.make_maze = ImageLevelView(self._frame, dimensions, (MAZE_WIDTH,
		                                                          MAZE_HEIGHT))
		self.make_inv = InventoryView(self._frame)

	def clear_all(self) -> None:
		"""Clears the widgets in there Frames and canvas"""
		ImageLevelView(self.master, (5, 5), (MAZE_WIDTH, MAZE_HEIGHT)).clear()
		InventoryView(self.master).clear()


class ControlsFrame(tk.Frame):
	def __init__(self, master, game_file, mins, sec, **kwargs) -> None:
		"""Creates the Controller frame
		Parameters:
			game_file: current game file being played
			mins: minutes past on timer
			sec: seconds past on timer
		"""
		super().__init__(master)
		self.pack(fill=tk.BOTH, expand=1)
		self.master = master
		self.current_file = game_file
		self.sec = sec
		self.min = mins
		self.increment()

		self.button = tk.Button(self, text="Restart game", command=self.restart)
		self.button.pack(side=tk.LEFT, anchor=tk.CENTER, expand=1)
		self.button2 = tk.Button(self, text="New game", command=self.new)
		self.button2.pack(side=tk.LEFT, anchor=tk.CENTER, expand=1)

		self.timer_frame = tk.Frame(self)
		self.timer_frame.pack(side=tk.LEFT, anchor=tk.CENTER, expand=1)
		self.timer = tk.Label(self.timer_frame, text="Timer")
		self.timer.pack()
		self.time = tk.Label(self.timer_frame, text=f"{self.min}m {self.sec}s")
		self.time.pack()

	def restart(self) -> None:
		"""Restarts the current game file"""
		ImageGraphicalMazeRunner(self.current_file, self.master).play()

	def new(self) -> None:
		"""Prompts user for a new game file"""
		self.file_choose = tk.Toplevel(self.master)
		self.new_file = tk.Entry(self.file_choose)
		self.new_file.pack(expand=1)
		self.enter_button = tk.Button(self.file_choose, text="Enter",
		                              command=self.change)
		self.enter_button.pack(fill=tk.BOTH, expand=1)

	def change(self) -> None:
		"""Checks to see if users game file is valid"""
		new_file = self.new_file.get()
		try:
			# If it can create a maze then its a valid file
			ImageGraphicalMazeRunner(new_file, self.master).play()
			self.current_file = new_file

		except:
			self.file_choose.destroy()
			messagebox.showerror("Invalid file",
			                     "'" + new_file + "' is not a valid file name!")

	def increment(self) -> None:
		"""Back end timer that updates the label"""
		self.sec = self.sec + 1
		if self.sec == MAX_SEC:
			self.sec = self.sec - MAX_SEC
			self.min = self.min + 1
		# Configs time is the label is created
		try:
			self.time.config(text=f'{self.min}m {self.sec}s')
		except:
			None
		# Waits 1 second after recalling itself
		self.master.after(1000, self.increment)


class ImageGraphicalMazeRunner(GraphicalMazeRunner):
	"""Controller class for an Image version game of MazeRunner"""
	def __init__ (self, game_file: str, root: tk.Tk) -> None:
		super().__init__(game_file, root)
		self.interface = ImageGraphicalInterface(self.master)
		self.timer()

	def quit(self) -> None:
		"""Asks user to confirm quit"""
		response = messagebox.askyesno(title="Quit",
		                               message="Are you sure you want to Quit?")
		if response:
			self.master.destroy()

	def save(self) -> None:
		"""Saves the info of the current game"""
		pass

	def restart(self) -> None:
		"""Restarts the current game file"""
		ImageGraphicalMazeRunner(self.game_file, self.master).play()

	def load(self) -> None:
		"""Loads a new chosen game file that is valid"""
		# If it cant open the chosen file then it is regarded as invalid
		try:
			the_file = filedialog.askopenfilename(filetypes=(("text files",
			                                                  "*.txt"),
			                                                 ("all files",
			                                                  "*.*")))
			ImageGraphicalMazeRunner(the_file, self.master).play()
			self.game_file = the_file
		except:
			messagebox.showerror("Invalid file",
			                     "Invalid file type!")

	def menu(self):
		"""Creates the file menu"""
		# Works on IDLE but not on GradeScope :(
		menu = tk.Menu(self.master)
		self.master.config(menu=menu)
		file_menu = tk.Menu(menu)
		menu.add_cascade(label="File", menu=file_menu)
		file_menu.add_command(label='Save game', command=self.save)
		file_menu.add_command(label='Load game', command=self.load)
		file_menu.add_command(label='Restart game', command=self.restart)
		file_menu.add_separator()
		file_menu.add_command(label='Quit', command=self.quit)

	def play(self) -> None:
		"""Causes gameplay"""
		self.interface.clear_all()
		self.interface.create_interface(self.model.get_current_maze()
		                                .get_dimensions())
		self.interface.draw(self.model.get_current_maze(),
		                    self.model.get_current_items(),
		                    self.model.get_player().get_position(),
		                    self.model.get_player_inventory(),
		                    self.model.get_player_stats())

		ControlsFrame(self.master, self.game_file, self.min, self.sec)
		self.menu()
		self.interface.bind_keypress(self._handle_keypress)
		self.interface.set_inventory_callback(self._apply_item)


def play_game(root: tk.Tk):
	"""Initiates game play depending on Task"""
	if TASK == 1:
		GraphicalMazeRunner(GAME_FILE, root).play()
	if TASK == 2:
		game = ImageGraphicalMazeRunner(GAME_FILE, root)
		game.play()


def main():
	# Write your main function code here
	root = tk.Tk()
	app = play_game(root)
	root.mainloop()


if __name__ == '__main__':
	main()