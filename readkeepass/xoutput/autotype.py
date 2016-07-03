from collections import namedtuple, defaultdict
from time import sleep

import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
from gi.repository import GLib

import pyautogui
EventType = Gdk.EventType
CursorType = Gdk.CursorType

# KEY_PRESS      = EventType.KEY_PRESS
KEY_RELEASE    = EventType.KEY_RELEASE
# BUTTON_PRESS   = EventType.BUTTON_PRESS
BUTTON_RELEASE = EventType.BUTTON_RELEASE

LEFT_CLICK = 1
RIGHT_CLICK = 3

ClickTuple = namedtuple('ClickTuple', ('x', 'y', 'down', 'button', 'state'))
QuitLoop = namedtuple('QuitLoop', ('reason', 'gdk_event',))

def _get_seat_n_window():
    "Return a Gdk seat (essentially input devices) and window"
    display = Gdk.Display.get_default()
    screen = display.get_default_screen()
    seat = display.get_default_seat()
    win = screen.get_active_window()
    win = win.get_toplevel()
    win.focus(Gdk.CURRENT_TIME)
    # win.raise_()
    return seat, win

def _grab_seat(seat, win, cursor_type=CursorType.CROSSHAIR):
    "Grab the pointers and keyboard"
    cursor = Gdk.Cursor(cursor_type)
    prep_func = None
    prep_data = None
    events = None
    # capabilities = Gdk.SeatCapabilities.ALL_POINTING
    capabilities = (Gdk.SeatCapabilities.ALL_POINTING |
                    Gdk.SeatCapabilities.KEYBOARD)
    owner_events = False
    gb = seat.grab(win, capabilities, owner_events, cursor, events,
                   prep_func, prep_data)
    return gb

def _get_loop(seat):
    "Return a tuple of (main loop, quit loop fn)"
    loop = GLib.MainLoop()
    def loopquit():
        seat.ungrab()
        loop.quit()
    return loop, loopquit

class Callbacks:
    "The main event loop runs Callbacks.__call__ for each event"
    def __init__(self, eventtype_to_callback, loopquit=None):
        self.eventtype_to_callback = eventtype_to_callback
        self.output = defaultdict(list)
        self.loopquit = loopquit
        self.exit_reason = None

    def __call__(self, event, *pargs, **kwargs):
        d_callback = self.eventtype_to_callback
        
        etype = event.get_event_type()
        try:
            cb = d_callback[etype]
        except KeyError:
            return

        try:
            res = cb(event)
            if res:
                self._process_result(res, etype)
        except Exception as e:
            print('Exception in Callbacks.__call__:', e)
            self.loopquit()
            self.exit_reason = QuitLoop('Other exception in Callbacks.__call__', e)
        return

    def _process_result(self, res, etype):
        if isinstance(res, QuitLoop):
            self.loopquit()
            self.exit_reason = res
        elif res:
            self.output[etype].append(res)


class NClicksCB(Callbacks):
    def __init__(self, n_button_clicks=2, loopquit=None):
        """Create handler that records click events.

        loopquit must be set to some callable which will quit main loop.
        n_button_clicks is the maximum number of *left* clicks that
        will be recorded.

        Hitting Escape or the right mouse button will break out of loop
        
        self.output stores events and is a dict of lists.
        The keys of self.output are eventtypes in Gdk.EventType
        e.g., button_rel_events = self.output[Gdk.EventType.BUTTON_RELEASE]
        """
        self.n_button_clicks = n_button_clicks
        evtype_to_cb = {
            BUTTON_RELEASE : self.handler_button_rel,
            KEY_RELEASE : self.handler_key,
        }
        super().__init__(evtype_to_cb, loopquit)

    def __call__(self, event, *pargs, **kwargs):
        super().__call__(event, *pargs, **kwargs)
        n_button_release = len(self.output[BUTTON_RELEASE])
        if n_button_release >= self.n_button_clicks:
            self.loopquit()
            qreason = '{} button clicks reached'.format(n_button_release)
            self.exit_reason = QuitLoop(qreason, None)

    # @staticmethod
    # def handler_button_press(event):
    #     eb = event.button
    #     if eb.button == RIGHT_CLICK:
    #         return QuitLoop('Right button press', event)
    
    @staticmethod
    def handler_button_rel(event):
        down = False
        eb = event.button
        if eb.button == LEFT_CLICK:
            return ClickTuple(eb.x_root, eb.y_root, down, eb.button, eb.state)
        elif eb.button == RIGHT_CLICK:
            return QuitLoop('Right button release', event)
        return None

    @staticmethod
    def handler_key(event):
        if event.key.keyval == Gdk.KEY_Escape:
            return QuitLoop('Escape key', event)
        return None

def grab_input(callbacks):
    seat, win = _get_seat_n_window()
    _grab_seat(seat, win)
    loop, loopquit = _get_loop(seat)
    callbacks.loopquit = loopquit

    Gdk.event_handler_set(callbacks)
    loop.run()
    return callbacks

def get_clicks_xy(number_of_clicks=2):
    def xy_last_n_clicks(clicklist, n):
        clicks = clicklist[-n:]
        return [(click.x, click.y) for click in clicks]

    cbs = grab_input(NClicksCB(number_of_clicks))
    # disp = Gdk.Display.get_default()
    # disp.close()
    res = cbs.output[BUTTON_RELEASE]
    return xy_last_n_clicks(res, number_of_clicks)

class simulate:
    click = pyautogui.click
    staticmethod(click)

    @staticmethod
    def click_and_type(x, y, text):
        # pyautogui.moveTo(x, y, duration=0.1)
        pyautogui.click(x, y, clicks=2, interval=0.025, duration=0.05)
        sleep(0.1)
        pyautogui.typewrite(text, interval=0.05)

    @staticmethod
    def enter_key():
        sleep(0.05)
        pyautogui.typewrite(['enter',])

    @staticmethod
    def tab_key():
        sleep(0.05)
        pyautogui.typewrite(['tab',])

def run(*text_to_type):
    number_of_clicks = len(text_to_type)
    clicks = get_clicks_xy(number_of_clicks)
    if len(clicks) != number_of_clicks:
        raise Exception("Error: Didn't receive {} mouse clicks".format(number_of_clicks))
    sleep(2.0)
    for click,text in zip(clicks, text_to_type):
        simulate.click_and_type(click[0], click[1], text)
    simulate.enter_key()

# run('first text', 'second text here')
# http://openbooks.sourceforge.net/books/wga/gdk.html
