"""Main file with functions, windows and runners."""
from tkinter import (
    BOTTOM, END, LEFT, MULTIPLE, RIGHT, TOP,
    Entry, Label, Listbox, Scrollbar, Tk, Button, Frame
)
from typing import List, Tuple
from utils import (
    LIST_OF_WRONG_WINDOWS,
    write_to_file,
    read_from_file,
    check_for_active_handles,
    get_all_handles,
    gui
)
from runner import the_client
from functools import partial
import keyboard
import pywintypes
import os
SHELL = the_client.Dispatch("WScript.Shell")
ABORT = False
HERE = os.path.abspath(os.path.dirname(__file__))
CONFIGFILE = os.path.join(HERE, "config.txt")
# Classes

# colours, using ANSI escape sequences

class bcolours:
    GREEN = '\033[92m'
    DEFAULT = '\033[0m'

class Window:
    """Class that generates window data from the handle.

    Args:
        handle (int): handle ID of the window
    """

    def __init__(self, handle: int, label: str = None) -> None:
        """Set handle, get label from handle if None."""
        self.handle = handle
        self.label = label
        if not self.label:
            self.label = gui.GetWindowText(handle)

    def __repr__(self):
        return self.label

    def window_to_listbox_entry(self):
        return (self.label, "Window handle:", self.handle)


def listbox_entry_to_window(window_tuple: Tuple[str,int]) -> Window:
    return Window(handle=window_tuple[2])


class Game(Window):
    """Class that generates game data from window handle.

    Args:
        handle (int): handle ID of the window
    """

    def __init__(self, handle, label: str = None) -> None:
        """Inherit from Window: set handle, get label from handle."""
        super().__init__(handle, label)

    def set_button(self, keypress: str) -> None:
        """Set the button association in keypress class variable."""
        self.button = keypress

    def get_button(self) -> str:
        """Get the button association from keypress class variable."""
        return self.button


# Functions
def load_config_from_file(root):
    file_contents = read_from_file(CONFIGFILE)
    handles = [int(handle_string) for handle_string in file_contents.split() if handle_string]
    global FINAL_GAMES_LIST
    FINAL_GAMES_LIST = [Game(handle) for handle in handles]
    root.destroy()


def get_list_of_windows() -> List[Window]:
    """Get list of all handles with window names."""
    handles = get_all_handles()
    window_list = []
    for handle in handles:
        window_text = gui.GetWindowText(handle)
        if window_text not in LIST_OF_WRONG_WINDOWS:
            # print(f"This Window has and window_text {window_text}") 43ewrrrr# TODO:Log
            window_list.append(Window(handle=handle, label=window_text))
    window_list.sort(key=lambda x: x.label.lower())
    # print(window_list)
    return window_list

def add_games_to_display_list(listbox: Listbox, games_listbox: Listbox) -> None:
    """Add games from listbox to games_listbox.

    Args:
        listbox (Listbox): source lisbox
        games_listbox (Listbox): destination listbox
    """
    # get selected
    selected = listbox.curselection()
    # add selected
    for index in selected:
        window_data = listbox.get(index)
        games_listbox.insert(0, window_data)
    # remove selected in reversed order
    for index in reversed(selected):
        listbox.delete(index)

def delete_from_list(listbox: Listbox) -> None:
    """Remove selected entires from listbox.

    Args:
        listbox (Listbox): listbox to remove selections from
    """
    # get selected
    selected = listbox.curselection()
    # remove selected in reversed order
    for index in reversed(selected):
        listbox.delete(index)

def remove_unmatched_games(
    search_entrybox: Entry,
    search_games_listbox: Listbox
) -> None:
    """Remove unmatched games from listbox.

    Args:
        search_entrybox (Entry): entrybox to get search-string from
        search_games_listbox (Listbox): listbox to filter
    """
    # get search term
    search_term = search_entrybox.get().lower()
    # find match games
    good_windows = [
        window_tuple
        for window_tuple in search_games_listbox.get(0, END)
        if search_term in window_tuple[0].lower()
    ]
    # remove nonmatched windows
    search_games_listbox.delete(0, END)
    for window in good_windows:
        search_games_listbox.insert(0, window)

def store_list_and_destroy_root(listbox: Listbox, root: Tk):
    """Store game list and destroy root frame.

    Args:
        listbox (Listbox): games listbox to save
        root (Tk): root frame to destroy
    Globals:
        FINAL_GAMES_LIST (List): Final games list to store games in
    """
    all_windows = listbox.get(0, END)
    # TODO: yeah maybe avoid global if possible.
    global FINAL_GAMES_LIST
    FINAL_GAMES_LIST = [Game(window[2]) for window in all_windows]
    to_file = "".join([str(entry.handle) + "\n" for entry in FINAL_GAMES_LIST])
    write_to_file(to_file, CONFIGFILE)
    root.destroy()

def switch_to_game(next_game: Game) -> None:
    """Switch to given game.

    Args:
        next_game (Tuple[str, int]): game to switch to
    """
    try:
        SHELL.SendKeys("%")
        gui.SetForegroundWindow(next_game.handle)
    except pywintypes.error as e:
        print(e)
        if e.winerror == 1400:
            print(f"Warning, game {next_game} was closed.")
        else:
            # something happened, we don't know what
            pass

def start_runner() -> None:
    """Start runner task and keep running."""
    number_of_active_games = len(FINAL_GAMES_LIST)
    game_is_alive_dict = {game: True for game in FINAL_GAMES_LIST}
    while number_of_active_games > 0:
        current_keypress = keyboard.read_event().name
        if current_keypress in BUTTON_TO_ACTION_DICT.keys():
            next_game = BUTTON_TO_ACTION_DICT[current_keypress]
            game_died = bool(check_for_active_handles([next_game.handle]))
            if game_died:
                game_is_alive_dict[next_game] = False
            else:
                switch_to_game(next_game)
        number_of_active_games = sum(
            [int(value) for value in game_is_alive_dict.values()]
        )

def abort_all(root: Tk):
    """Destroy root frame if ABORT is set.

    Args:
        root (Tk): root frame to destroy
    Globals:
        ABORT (bool): if set, destroy root window
    """
    global ABORT
    ABORT = True
    root.destroy()


BUTTON_TO_ACTION_DICT: dict[str,Game] = {}
EXE_LIST: List[Window] = get_list_of_windows()
FINAL_GAMES_LIST: List[Game] = []

def make_scrollable_listbox(
    parent: Frame,
    selectmode: str = MULTIPLE,
    side: str = TOP
) -> None:
    """Make scrollabe listbox.

    Args:
        parent (Frame): frame to attach listbox
        selectmode (str): tkinter constant, from SINGLE, MULTIPLE, BROWSE and
            EXTENDED
        side (str): tkinter constant, from TOP, BOTTOM, LEFT and RIGHT
    """
    listbox_frame = Frame(parent)
    listbox_frame.pack(side=side, expand=True)
    the_listbox = Listbox(listbox_frame, selectmode=selectmode)
    the_listbox.pack(side=LEFT, expand=True)
    reset_button = Button(listbox_frame, text='Refresh\nList')
    reset_button.pack(side=RIGHT, fill='y')
    scrollbar = Scrollbar(listbox_frame, orient='vertical')
    scrollbar.config(command=the_listbox.yview)
    scrollbar.pack(side=RIGHT, fill='y')
    the_listbox.config(yscrollcommand=scrollbar.set)
    return the_listbox, reset_button

def draw_game_selection_frame() -> None:
    """Draw the game selection frame."""
    root_1 = Tk()
    root_1.title("Window Selector Config")
    root_1.geometry("600x450")

    # root = prep + gdf
    prep_frame = Frame(root_1)
    prep_frame.pack(side=TOP, expand=True)

    # GDF = listbox + remove + confirm
    game_display_frame = Frame(root_1)
    game_display_frame.pack(side=BOTTOM, expand=True)
    # scrollable listbox
    games_listbox, _ = make_scrollable_listbox(game_display_frame)
    # buttons
    remove_game_button = Button(
        game_display_frame,
        text="Delete Game",
        command=partial(delete_from_list, games_listbox)
    )
    remove_game_button.pack(side=LEFT, expand=True)
    confirm_games_button = Button(
        game_display_frame,
        text="Confirm Games",
        bg='green',
        command=partial(store_list_and_destroy_root, games_listbox, root_1)
    )
    confirm_games_button.pack(side=RIGHT, expand=True)
    abort_button = Button(
        game_display_frame,
        bg='red',
        text="ABORT ALL!",
        command=partial(abort_all, root_1)
    )
    abort_button.pack(side=RIGHT, expand=True)

    # prep = load + adders
    load_frame = Frame(prep_frame)
    load_frame.pack(side=TOP, expand=True)
    load_button = Button(
        load_frame,
        text="Load from file",
        command=partial(load_config_from_file, root_1)
    )
    load_button.pack(expand=True)
    adder_frame = Frame(prep_frame)
    adder_frame.pack(side=BOTTOM, expand=True)

    # adder = left + right
    select_game_by_clicking_frame = Frame(adder_frame)
    select_game_by_clicking_frame.pack(side=LEFT, expand=True)

    # left = listbox + buttons
    click_games_listbox = make_scrollable_searchbox(
        select_game_by_clicking_frame,
        content=EXE_LIST
    )
    add_click_frame_button = Button(
        select_game_by_clicking_frame,
        text="Add Game",
        command=partial(
            add_games_to_display_list,
            click_games_listbox,
            games_listbox
        )
    )
    add_click_frame_button.pack(side=LEFT, expand=True)
    remove_click_frame_button = Button(
        select_game_by_clicking_frame,
        text="Remove Game from List",
        command=partial(delete_from_list, click_games_listbox))
    remove_click_frame_button.pack(side=RIGHT, expand=True)

    # right = search + listbox + buttons
    select_game_by_search_frame = Frame(adder_frame)
    select_game_by_search_frame.pack(side=RIGHT, expand=True)
    recently_active_windows_list = []
    search_games_listbox = make_scrollable_searchbox(
        select_game_by_search_frame,
        content=recently_active_windows_list
    )
    add_search_frame_button = Button(
        select_game_by_search_frame,
        text="Add Game",
        command=partial(
            add_games_to_display_list,
            search_games_listbox,
            games_listbox
        )
    )
    add_search_frame_button.pack(side=BOTTOM, expand=True)


    def update_active_windows_task():

        current_window = get_active_window()
        if current_window not in recently_active_windows_list:
            recently_active_windows_list.append(current_window)
        root_1.after(100, update_active_windows_task)

    root_1.after(100, update_active_windows_task)
    root_1.protocol("WM_DELETE_WINDOW", partial(abort_all, root_1))
    root_1.mainloop()


def refresh_content(listbox: Listbox, content: List[Window]) -> None:
    """Refresh content of listbox.

    Args:
        listbox (Listbox): listbox to refresh
        content (List[Window]): contents to put in listbox
    """
    listbox.delete(0, END)
    # requires conversion to tuples, because TKinter does not allow arbitrary
    # classes. It allows int, str, tuple and combinations. It does not allow
    # List, bool or dict.
    content_tuples = [window.window_to_listbox_entry() for window in content]
    listbox.insert(0, *content_tuples)

def make_scrollable_searchbox(
    parent: Frame,
    content: List[Window] = None
) -> Listbox:
    """Make a scrollable searchbox.

    Args:
        parent (Frame): parent frame to attach searchbar
        content (List[Window]): Things to fill the listbox with
    Returns:
        search_games_listbox (Listbox): updated listbox
    """
    select_game_by_search_top_frame = Frame(parent)
    select_game_by_search_top_frame.pack(side=TOP)
    search_games_listbox, search_games_reset_button = make_scrollable_listbox(
        select_game_by_search_top_frame,
        selectmode=MULTIPLE,
        side=BOTTOM
    )
    if content:
        refresh_content(search_games_listbox, content)
    search_games_reset_button.config(
        command=partial(refresh_content, search_games_listbox, content)
    )
    make_searchbox(select_game_by_search_top_frame, search_games_listbox)
    return search_games_listbox


def make_searchbox(parent: Frame, search_games_listbox: Listbox) -> None:
    """Create Searchbox from Listbox and parent.

    Args:
        parent (Frame): parent frame to attach Searchbar
        search_games_listbox (Listbox): Listbox to attach Searchbar
    """
    search_frame = Frame(parent)
    search_frame.pack(side=TOP, expand=True)
    search_entrybox = Entry(search_frame)
    search_entrybox.pack(side=LEFT, expand=True)
    apply_search_frame_button = Button(
        search_frame,
        text="Apply Search",
        command=partial(
            remove_unmatched_games,
            search_entrybox,
            search_games_listbox
        )
    )
    apply_search_frame_button.pack(side=RIGHT, expand=True)

def check_uniqueness_and_destroy_root(root: Tk) -> None:
    """Check windows for uniqueness and destroy root tkinter window.

    Args:
        root (Tk): root frame to destroy
    """
    all_button_labels = [
        widget.cget("text")
        for widget in root.winfo_children()
        if type(widget) == Button
    ][:-1]
    ready_for_destruction = False
    while not ready_for_destruction:
        if len(set(all_button_labels)) == len(all_button_labels):
            global BUTTON_TO_ACTION_DICT
            for button, game in zip(all_button_labels, FINAL_GAMES_LIST):
                BUTTON_TO_ACTION_DICT[str(button)] = game
            ready_for_destruction = True
            root.destroy()
        else:
            print("Buttons must be unique! Please ensure unique button per game!")

def assign_button_to_button(button_object: Button) -> None:
    """Assign a keyboard key to a button.

    Args:
        button_object (Button): button to assign key to
    """
    new_key = keyboard.read_event()
    print(new_key)
    button_object.configure(text=new_key.name)


def draw_button_selection_frame() -> None:
    """Draw frame to assign buttons to windows."""
    number_of_games = len(FINAL_GAMES_LIST)
    root_2 = Tk()
    root_2.title("Button Selector Config")
    info_box = Label(
        root_2,
        text=f"There are {number_of_games} games."
        + "Please choose a key for each game."
    )
    info_box.grid(row=0, column=0, columnspan=2)
    # list_of_game_rows = []
    for index, game in enumerate(FINAL_GAMES_LIST):
        # create game column
        game_box = Label(root_2, text=game)
        game_box.grid(row=index + 1, column=0)
        # create button column
        button_button = Button(root_2, text=index + 1, command=None)
        button_button.configure(
            command=partial(assign_button_to_button, button_button)
        )
        button_button.grid(row=index + 1, column=1)
    confirm_buttons_button = Button(
        root_2,
        text="Confirm Buttons",
        bg='green',
        command=partial(check_uniqueness_and_destroy_root, root_2))
    confirm_buttons_button.grid(row=number_of_games + 1, column=0, columnspan=1)
    abort_button = Button(
        root_2,
        bg='red',
        text="ABORT ALL!",
        command=partial(abort_all, root_2)
    )
    abort_button.grid(row=number_of_games + 1, column=1)

    root_2.mainloop()


def get_active_window() -> Window:
    """Get label and handle of active window.

    Returns:
        (Window): current active window
    """
    handle = gui.GetForegroundWindow()
    return Window(handle)


if __name__ == "__main__":
    draw_game_selection_frame()

    if not ABORT:
        print(bcolours.GREEN
            + "Please ignore the \"invalid command name "
            + "LONGNUMBERupdate_active_windows_task\" error, it's a "
            + "badly handled error by the package that draws the windows"
            + "(Tkinter)" + bcolours.DEFAULT
            )
        draw_button_selection_frame()
    print(BUTTON_TO_ACTION_DICT)
    if not ABORT:
        start_runner()
