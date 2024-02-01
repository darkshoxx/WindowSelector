from tkinter import BOTTOM, END, LEFT, MULTIPLE, RIGHT, SINGLE, TOP, Entry, Listbox, Tk, Button, Frame
SAMPLE_LIST_1 = ["A","B","C","D","E","F"]
SAMPLE_LIST_2 = ["Myst", "Myst 2 Riven", "Myst 3 Exile", "7th Guest"]

# Functions
def add_click_games_to_display_list():
    # get selected
    selected = click_games_listbox.curselection()
    # add selected
    for index in selected:
        game_data = click_games_listbox.get(index)
        games_listbox.insert(0, game_data)
    # remove selected in reversed order
    for index in reversed(selected):
        click_games_listbox.delete(index)

def delete_from_click_games_list():
    # get selected
    selected = click_games_listbox.curselection()
    # remove selected in reversed order
    for index in reversed(selected):
        click_games_listbox.delete(index)

def remove_unmatched_games():
    # get search term
    search_term = search_entrybox.get().lower()
    # find match games
    good_games = [game for game in seach_games_listbox.get(0,END) if search_term in game.lower()]
    # remove nonmatched windows
    seach_games_listbox.delete(0, END)
    for game in good_games:
        seach_games_listbox.insert(0, game)
root = Tk()
root.title("Window Selector Config")
root.geometry("600x450")

# root = prep + gdf
prep_frame = Frame(root)
prep_frame.pack(side=TOP, expand=True)

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
click_games_listbox.insert(0,*SAMPLE_LIST_1)
click_games_listbox.pack(side=TOP)
add_click_frame_button = Button(select_game_by_clicking_frame, text="Add Game", command=add_click_games_to_display_list)
add_click_frame_button.pack(side=LEFT)
remove_click_frame_button = Button(select_game_by_clicking_frame, text="Remove Game from List", command=delete_from_click_games_list)
remove_click_frame_button.pack(side=RIGHT)

# right = search + listbox + buttons
select_game_by_search_frame = Frame(adder_frame)
select_game_by_search_frame.pack(side=RIGHT)
search_frame = Frame(select_game_by_search_frame)
search_frame.pack(side=TOP)
search_entrybox = Entry(search_frame)
search_entrybox.pack(side=LEFT)
apply_search_frame_button = Button(search_frame, text="Apply Search", command=remove_unmatched_games)
apply_search_frame_button.pack(side=RIGHT)
seach_games_listbox = Listbox(select_game_by_search_frame, selectmode=SINGLE)
seach_games_listbox.insert(0,*SAMPLE_LIST_2)
seach_games_listbox.pack(side=TOP)
add_search_frame_button = Button(select_game_by_search_frame, text="Add Game", command=None)
add_search_frame_button.pack(side=BOTTOM)

# GDF = listbox + remove + confirm
game_display_frame = Frame(root)
game_display_frame.pack(side=BOTTOM, expand=True)
games_listbox = Listbox(game_display_frame, selectmode=MULTIPLE)
games_listbox.pack(side=TOP)
remove_game_button = Button(game_display_frame, text="Delete Game", command=None)
remove_game_button.pack(side=LEFT)
confirm_games_button = Button(game_display_frame, text="Confirm Games", command=None)
confirm_games_button.pack(side=RIGHT)






root.mainloop()