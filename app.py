from time import time

st_time = time()

import customtkinter as ctk
from customtkinter import filedialog
import tkinter as tk

from PIL import Image, ImageTk
import math
from json import dumps, loads

from modules.field_items import Background, Path
from modules.pointer import Pointer
from modules.listbox import CtkHoverSelectListbox
from modules.confirm_window import ConfirmationWindow
from modules.converter import Converter
from modules.opath_converter import OPath_converter

from config import key_binds_txt, APP_STATES

from logger import Logger

st_time = time() - st_time

# Dear reader, dot = pathpoint


class App(ctk.CTk):
    def __init__(
        self, logger: Logger, background="static/images/field.png", xsize=960, ysize=640
    ):
        app_init_time = time()
        super().__init__()
        self.logger = logger
        self.logger.info("Papa window inited!")

        # Init
        self.title("Omni Robot Simulation")
        self.resizable(False, False)

        # Create canvas
        self.canvas = ctk.CTkCanvas(self, width=xsize, height=ysize, bg="white")
        self.canvas.grid(row=0, column=0)

        # Create right frame
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        self.dotbox = CtkHoverSelectListbox(self.right_frame)
        self.dotbox.grid(row=2, column=0, pady=(10, 0), padx=10, sticky="n")

        # Create mode lable
        self.mode_label = ctk.CTkLabel(self.right_frame, text="Режим: ничего")
        self.mode_label.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="n")

        # Create keybind map
        self.keybinds_map = ctk.CTkLabel(self.right_frame, text=key_binds_txt)
        self.keybinds_map.grid(row=1, column=0, pady=(10, 0), padx=10, sticky="n")

        # Save/open buttons
        self.opn_sv_frame = ctk.CTkFrame(self.right_frame)
        self.save_button = ctk.CTkButton(
            self.opn_sv_frame, text="Сохранить путь", command=self.save_path
        )
        self.open_button = ctk.CTkButton(
            self.opn_sv_frame, text="Открыть путь", command=self.open_path
        )
        self.opn_sv_frame.grid(row=3, column=0, pady=(10, 0), padx=10, sticky="n")
        self.save_button.grid(row=0, column=0, pady=2, padx=2)
        self.open_button.grid(row=0, column=1, pady=2, padx=2)

        # Robot path
        self.opath_frame = ctk.CTkFrame(self.right_frame)
        self.save_opath_button = ctk.CTkButton(
            self.opath_frame, text="Сохранить opath", command=self.export_robot_path
        )
        self.open_opath_button = ctk.CTkButton(self.opath_frame, text="Открыть opath")
        self.opath_frame.grid(row=4, column=0, pady=(3, 0), padx=10, sticky="n")
        self.save_opath_button.grid(row=0, column=0, pady=2, padx=2)
        self.open_opath_button.grid(row=0, column=1, pady=2, padx=2)

        self.logger.info("Added elements")

        # Defines
        self.xsize = xsize
        self.ysize = ysize
        self.status = 0  # 0 - chill, 1 - set start point, 2 - add point
        self.current_dot = None

        # Initing
        self.bg = Background(background, xsize, ysize, logger=self.logger)
        self.pointer = Pointer()
        self.path = Path()
        self.logger.info("Items inited")
        self.converter = Converter((xsize, ysize), (3000, 2000))

        # Binds
        self.canvas.bind("<Motion>", self.on_move)
        self.canvas.bind("<Button-1>", self.on_left_mouse)

        # Bind path adding
        self.bind("s", self.on_button_click)  # Add start button
        self.bind("n", self.on_button_click)  # Add new path point

        # Binds for changing path
        # Delite binds
        self.bind("d", self.on_button_click)
        self.bind("<Delete>", self.on_button_click)
        self.bind("<BackSpace>", self.on_button_click)

        self.bind("m", self.on_button_click)  # Move dots

        self.bind("<Escape>", self.on_button_click)
        self.dotbox.bind("<<ListboxSelect>>", self.dot_selected)
        self.logger.info("Binded!")

        app_init_time = time() - app_init_time

        self.logger.info("Modules imported by", st_time)
        self.logger.info("App inited by", app_init_time)
        self.logger.info("Total running time:", st_time + app_init_time)

        self.update()

    def update(self):
        # Update dots list
        dots_txt = []
        for index, dot in enumerate(self.path.path):
            dots_txt.append(f"{index}: {dumps(dot)}")
        self.dotbox.sync_with_data(dots_txt)

        # Pre update
        self.canvas.delete("all")

        # Draw static
        self.bg.draw(self.canvas)

        # Draw non static
        self.path.draw(self.canvas)
        self.pointer.draw(self.canvas)

        self.after(1, self.update)

    def dot_selected(self, event):
        self.current_dot = self.dotbox.curselection()[0]
        self.path.underline_point(self.current_dot)

    def on_button_click(self, event):
        self.status = 0
        self.pointer.change_state(1)
        if event.keysym == "s":
            # Change start point
            self.status = 1
            self.pointer.change_state(2)
        elif event.keysym == "n":
            # Add new point
            self.status = 2
            self.pointer.change_state(3)
        elif event.keysym in ["d", "BackSpace", "Delete"]:
            # Change start point
            self.delite_dot()
        elif event.keysym == "Escape":
            # Escape :)
            self.reset()
        elif event.keysym == "m" and (
            self.current_dot is not None and self.current_dot < len(self.path.path)
        ):
            # Move dot
            self.status = 3
            self.pointer.change_state(4)

        self.static_update()

    def reset(self):
        self.status = 0
        self.current_dot = None
        self.pointer.change_state(1)
        self.path.deunderline_point()

    def delite_dot(self):
        if self.current_dot != 0 and (
            not self.current_dot or self.current_dot >= len(self.path.path)
        ):
            self.logger.warning("No dot selected")
            self.reset()
            return
        confirm_window = ConfirmationWindow(
            self,
            title="Потвердите удаление.",
            message="Вы уверены, что хотите удалить точку?",
        )
        self.wait_window(confirm_window)
        if confirm_window.result:
            self.logger.info("Delited dot", self.current_dot)
            self.path.path.pop(self.current_dot)

    def static_update(self):
        self.mode_label.configure(text=APP_STATES[self.status])

    def on_move(self, event):
        self.pointer.update(event.x, event.y)
        if self.status == 3:  # Processing dot moving
            self.path.path[self.current_dot] = [event.x, event.y]

    def on_left_mouse(self, event):
        if self.status == 1:
            self.logger.info("Setted start point to", (event.x, event.y))
            self.path.set_start_point(event.x, event.y)
        elif self.status == 2:
            self.logger.info("Added dot to", (event.x, event.y))
            self.path.add_point(event.x, event.y)
        elif self.status == 3:
            self.logger.info("Moved dot", self.current_dot)
            self.reset()

    def save_path(self):
        self.logger.info("Asked path saving")
        if len(self.path.path) == 0:
            self.logger.warning("No path, canseling")
            return
        file = filedialog.asksaveasfile(
            title="Save path As",
            defaultextension=".path",  # Default file extension
            filetypes=[("path file", ("*.path", ".pth")), ("All Files", "*.*")],
        )
        if file:
            self.logger.info("Started saving to", file.name)
            t = time()
            file_content = {
                "format": "json-1",
                "create_time": time(),
                "start_point": self.path.start_point,
                "path": self.path.path,
            }
            file.write(dumps(file_content))
            file.close()
            self.logger.info("Saved path to", file.name + ",", "by", time() - t)
        else:
            self.logger.warning("No path selected")

    def open_path(self):
        self.logger.info("Asked path opening")
        if len(self.path.path) != 0:
            confirm_window = ConfirmationWindow(
                self,
                title="Потверждение",
                message="Вы действительно хотите заменить текущий путь?",
                buttons=("Заменить", "Галя, у нас отмена"),
            )
            self.wait_window(confirm_window)
            if not confirm_window.result:
                self.logger.info("User canseled file opening")
                return
        file = filedialog.askopenfile(
            title="Open path",
            defaultextension=".path",  # Default file extension
            filetypes=[("path file", ("*.path", ".pth")), ("All Files", "*.*")],
        )
        if file:
            self.logger.info("Start opening file", file.name)
            t = time()

            content = loads(file.read())
            self.path.start_point = content["start_point"]
            self.path.path = content["path"]

            self.logger.info("File opened by", round(time() - t, 4))
        else:
            self.logger.warning("No file selected")

    def export_robot_path(self):
        self.logger.info("Stated exporting")
        if len(self.path.path) == 0:
            self.logger.warning("No path, we can`t export")
            return
        
        t = time()
        pathmm = self.converter.list_pxs_to_mms(self.path.path)
        startpoint_mm = self.converter.pxs_to_mms(self.path.start_point)
        opath = OPath_converter.export(pathmm, startpoint_mm)
        self.logger.info("Exported to opath by", time()-t)
        
        self.logger.info("Asking filename")
        file = filedialog.asksaveasfile(
            title="Save opath As",
            defaultextension=".opth",  # Default file extension
            filetypes=[("omni bot path file", ("*.opth")), ("All Files", "*.*")],
        )
        if file:
            file.write(dumps(opath))
            file.close()
            self.logger.info("Omni path saved to", file.name)
        else:
            self.logger.info("No path selected")



if __name__ == "__main__":
    logger = Logger()
    logger.info("Started loading")
    app = App(logger=logger)
    app.mainloop()
