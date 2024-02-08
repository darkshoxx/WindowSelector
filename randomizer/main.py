from tkinter import BOTTOM, END, LEFT, MULTIPLE, RIGHT, SINGLE, TOP, Entry, Label, Listbox, Text, Tk, Button, Frame
from utils import LIST_OF_WRONG_WINDOWS, check_for_active_handles, get_all_handles, get_exe_from_process_id, get_process_id_from_handle, gui
from functools import partial
import keyboard, pywintypes
SAMPLE_LIST_1 = ["A","B","C","D","E","F"]
SAMPLE_LIST_2 = ["Myst", "Myst 2 Riven", "Myst 3 Exile", "7th Guest"]

# Functions
def get_list_of_exe_windows():
    handles = get_all_handles()
    exe_list = []  # key = hanlde id, value = exe name
    for handle in handles:
        # ident_b = get_process_id_from_handle(handle)
        # exe_name = get_exe_from_process_id(ident_b)
        window_text = gui.GetWindowText(handle)
        if window_text not in LIST_OF_WRONG_WINDOWS:
            print(f"This Window has and window_text {window_text}")
            exe_list.append((window_text, handle)) # alternatively window text
    exe_list.sort(key=lambda x: x[0].lower())
    print(exe_list)
    return exe_list

def add_games_to_display_list(listbox, games_listbox):
    # get selected
    selected = listbox.curselection()
    # add selected
    for index in selected:
        game_data = listbox.get(index)
        games_listbox.insert(0, game_data)
    # remove selected in reversed order
    for index in reversed(selected):
        listbox.delete(index)

def delete_from_list(listbox):
    # get selected
    selected = listbox.curselection()
    # remove selected in reversed order
    for index in reversed(selected):
        listbox.delete(index)

def remove_unmatched_games(search_entrybox, seach_games_listbox):
    # get search term
    search_term = search_entrybox.get().lower()
    # find match games
    good_games = [game for game in seach_games_listbox.get(0,END) if search_term in game.lower()]
    # remove nonmatched windows
    seach_games_listbox.delete(0, END)
    for game in good_games:
        seach_games_listbox.insert(0, game)

def store_list_and_destroy_root(listbox, root):
    all_games = listbox.get(0, END)
    # TODO: yeah maybe avoid global if possible.
    global FINAL_GAMES_LIST
    FINAL_GAMES_LIST = all_games
    root.destroy()

# def wait_for_input(current_handle, list_of_buttons):
#     pass
#     press_not_occured = True
#     while press_not_occured:
#         if bool(check_for_active_handles([current_handle])):
#             return (True, "window")
#         for button in list_of_buttons:
#             if keyboard.is_pressed(button):
#                 action = BUTTON_TO_ACTION_DICT[button]
#                 if action == "next":
#                     to_next_game()
#                 elif action == "previous":
#                     to_previous_game()
#                 elif type(action) == int:
#                     go_to_game(action)

def switch_to_game(next_game):
    try:
        gui.SetForegroundWindow(next_game[1])
    except pywintypes.error as e:
        print(e)
        if e.winerror == 1400:
            print(f"Warning, game {next_game} was closed.")
        else:
            # something happened, we don't know what
            pass

def start_runner():
    number_of_active_games = len(FINAL_GAMES_LIST)
    game_is_alive_dict = {game:True for game in FINAL_GAMES_LIST}
    while number_of_active_games>0:
        current_keypress = keyboard.read_event().name
        if current_keypress in BUTTON_TO_ACTION_DICT.keys():
            next_game = BUTTON_TO_ACTION_DICT[current_keypress]
            game_died = bool(check_for_active_handles([next_game[1]]))
            if game_died:
                game_is_alive_dict[next_game] = False
            else:
                switch_to_game(next_game)
        number_of_active_games = sum([int(value) for value in game_is_alive_dict.values()])



BUTTON_TO_ACTION_DICT = {}
EXE_LIST = get_list_of_exe_windows()
FINAL_GAMES_LIST = []

def draw_game_selection_frame():

    root = Tk()
    root.title("Window Selector Config")
    root.geometry("600x450")

    # root = prep + gdf
    prep_frame = Frame(root)
    prep_frame.pack(side=TOP, expand=True)

    # GDF = listbox + remove + confirm
    game_display_frame = Frame(root)
    game_display_frame.pack(side=BOTTOM, expand=True)
    games_listbox = Listbox(game_display_frame, selectmode=MULTIPLE)
    games_listbox.pack(side=TOP)
    remove_game_button = Button(game_display_frame, text="Delete Game", command=partial(delete_from_list, games_listbox))
    remove_game_button.pack(side=LEFT)
    confirm_games_button = Button(game_display_frame, text="Confirm Games", command=partial(store_list_and_destroy_root, games_listbox, root))
    confirm_games_button.pack(side=RIGHT)

    # prep = load + adders
    load_frame = Frame(prep_frame)
    load_frame.pack(side=TOP)
    load_button = Button(load_frame, text="Load from file", command=None)
    load_button.pack()
    adder_frame = Frame(prep_frame)
    adder_frame.pack(side=BOTTOM, expand=True)

    # adder = left + right
    select_game_by_clicking_frame = Frame(adder_frame)
    select_game_by_clicking_frame.pack(side=LEFT)

    # left = listbox + buttons
    click_games_listbox = Listbox(select_game_by_clicking_frame, selectmode=MULTIPLE)
    click_games_listbox.insert(0,*EXE_LIST)
    click_games_listbox.pack(side=TOP)
    add_click_frame_button = Button(select_game_by_clicking_frame, text="Add Game", command=partial(add_games_to_display_list, click_games_listbox, games_listbox))
    add_click_frame_button.pack(side=LEFT)
    remove_click_frame_button = Button(select_game_by_clicking_frame, text="Remove Game from List", command=partial(delete_from_list, click_games_listbox))
    remove_click_frame_button.pack(side=RIGHT)

    # right = search + listbox + buttons
    select_game_by_search_frame = Frame(adder_frame)
    select_game_by_search_frame.pack(side=RIGHT)
    search_frame = Frame(select_game_by_search_frame)
    search_frame.pack(side=TOP)
    search_entrybox = Entry(search_frame)
    search_entrybox.pack(side=LEFT)
    search_games_listbox = Listbox(select_game_by_search_frame, selectmode=SINGLE)
    search_games_listbox.insert(0,*SAMPLE_LIST_2)
    search_games_listbox.pack(side=TOP)
    apply_search_frame_button = Button(search_frame, text="Apply Search", command=partial(remove_unmatched_games, search_entrybox, search_games_listbox))
    apply_search_frame_button.pack(side=RIGHT)
    add_search_frame_button = Button(select_game_by_search_frame, text="Add Game", command=partial(add_games_to_display_list, search_games_listbox, games_listbox))
    add_search_frame_button.pack(side=BOTTOM)

    root.mainloop()

def check_uniqueness_and_destroy_root(root):
    all_button_labels = [widget.cget("text") for widget in root.winfo_children() if type(widget) == Button][:-1]
    if len(set(all_button_labels)) == len(all_button_labels):
        global BUTTON_TO_ACTION_DICT
        for button, game in zip(all_button_labels, FINAL_GAMES_LIST):
            BUTTON_TO_ACTION_DICT[str(button)] = game
        root.destroy()

def assign_button_to_button(button_object):
    new_key = keyboard.read_event()
    print(new_key)
    button_object.configure(text=new_key.name)


def draw_button_selection_frame():
    number_of_games = len(FINAL_GAMES_LIST)
    root = Tk()
    root.title("Button Selector Config")
    info_box = Label(root, text= f"There are {number_of_games} games. Please choose a key for each game.")
    info_box.grid(row=0, column=0, columnspan=2)
    # list_of_game_rows = []
    for index, game in enumerate(FINAL_GAMES_LIST):
        # create game column
        game_box = Label(root, text = game)
        game_box.grid(row=index+1, column=0)
        # create button column
        button_button = Button(root, text=index+1, command=None)
        button_button.configure(command=partial(assign_button_to_button, button_button))
        button_button.grid(row=index+1, column=1)
    confirm_buttons_button = Button(root, text="Confirm Buttons",command=partial(check_uniqueness_and_destroy_root,root))
    confirm_buttons_button.grid(row=number_of_games+1,column=0,columnspan=2)


    root.mainloop()

if __name__ == "__main__":
    draw_game_selection_frame()
    draw_button_selection_frame()
    print(BUTTON_TO_ACTION_DICT)

    start_runner()