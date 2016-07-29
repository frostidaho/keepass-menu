#!/usr/bin/env python
# This script prompts the user for some input
# and prints it to stdout
import tkinter as tk
import tkinter.ttk as ttk
import argparse

FONT_SPEC = ('Sans', 18)
DEFAULT_PROMPT = 'Query:'
DEFAULT_BUTTON = 'Go'


def monitor_geometry():
    "Return the current monitor geometry"
    import gi
    gi.require_version('Gdk', '3.0')
    from gi.repository import Gdk
    from collections import namedtuple
    MonitorGeometry = namedtuple(
        'MonitorGeometry',
        ['left', 'right', 'top', 'bottom', 'width', 'height'],
    )

    display = Gdk.Display.get_default()
    screen = display.get_default_screen()
    window = screen.get_active_window()
    monitor = screen.get_monitor_at_window(window)

    g = screen.get_monitor_geometry(monitor)
    right = g.x + g.width
    bottom = g.y + g.height
    return MonitorGeometry(g.x, right, g.y, bottom, g.width, g.height)


class TotalTK:

    def __init__(self, label_txt, button_text, entry_kwargs):
        self.init_root()
        self.init_label(label_txt)
        self.init_entry(**entry_kwargs)
        self.init_button(button_text)
        self.move_window()

    def __call__(self):
        self.run()
        return self.text

    def init_root(self):
        self.root = tk.Tk()
        s = ttk.Style()
        s.theme_use('clam')
        s.configure('.', font=FONT_SPEC)
        s.configure('TButton', padding=0)
        self.root.style = s
        self.style = s

        self.frame = ttk.Frame(self.root)
        self.frame.pack()

        self.root.bind("<Return>", self.get_text_n_close)
        self.root.bind("<Escape>", self.kill)

    def init_label(self, prompt):
        self.label = ttk.Label(self.frame, text=prompt)
        self.label.pack(side=tk.LEFT)

    def init_entry(self, **entry_kwargs):
        e = ttk.Entry(self.frame, font=FONT_SPEC, width=40, **entry_kwargs)
        e.pack(side=tk.LEFT)
        e.focus()
        self.entry = e

    def init_button(self, button_text):
        b = ttk.Button(
            self.frame,
            text=button_text,
            command=self.get_text_n_close,
            width=len(button_text) + 2,
        )
        b.pack(side=tk.LEFT)
        self.button = b

    def kill(self, *pargs, **kwargs):
        self.root.destroy()

    @property
    def text(self):
        try:
            return self._text
        except AttributeError:
            return ''

    def get_text_n_close(self, *pargs, **kwargs):
        self._text = self.entry.get()
        self.kill()

    def move_window(self):
        try:
            geom = monitor_geometry()
            self.root.update_idletasks()
            xposition = int(geom.width - self.root.winfo_reqwidth()) // 2 + geom.left
            yposition = int(0.3 * (geom.bottom - geom.top)) - self.root.winfo_reqheight()
            self.root.geometry('+{}+{}'.format(xposition, yposition))
        except ImportError:
            pass

    def run(self):
        self.root.mainloop()
        return self.text


def run(prompt=DEFAULT_PROMPT, button=DEFAULT_BUTTON, password=False):
    if password:
        entry_kwargs = {'show': '•'}
    else:
        entry_kwargs = {}
    window = TotalTK(prompt, button, entry_kwargs)
    text = window.run()
    return text

# if __name__ == '__main__':
#     def parse_args():
#         parser = argparse.ArgumentParser(description='Display a graphical window' +
#                                          ' with a text entry box. Print the ' +
#                                          'input text to stdout.')

#         parser.add_argument('-p', '--prompt',
#                             help="Set the prompt text on the left side of the box" +
#                             ". Defaults to '{}'".format(DEFAULT_PROMPT),
#                             default=DEFAULT_PROMPT
#                             )
#         parser.add_argument('-b', '--button',
#                             help="Set the button text to the right of the box. " +
#                             "Defaults to '{}'".format(DEFAULT_BUTTON),
#                             default=DEFAULT_BUTTON
#                             )
#         parser.add_argument(
#             '-pw',
#             '--password',
#             help="Show *** in entry box",
#             action='store_true')
#         return vars(parser.parse_args())

#     args = parse_args()
#     res = run(**args)
#     print(res)
