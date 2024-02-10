from tkinter import *

def draw_frame():
    root = Tk()

    def task():
        print("hello")
        root.after(2000, task)  # reschedule event in 2 seconds

    root.after(2000, task)
    root.mainloop()

if __name__ == "__main__":
    # handle = get_active_handle()
    # text = gui.GetWindowText(handle)
    # print(f"current handle:{handle} label: {text}")
    draw_frame()