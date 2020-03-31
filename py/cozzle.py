#!/bin/env python3

import random
import tkinter as tk

gradient_steps = 10
window_width = 500
window_height = 100

def _hex_to_rgb(hex):
    """
    Convert a color from hexadecimal format to rgb format
    :param hex: a hexadecimal string ( "#XXXXXX" )
    :return: a tuple of rgb components ( (r,g,b) )
    """
    h = hex.lstrip('#')
    if len(h) != 6:
        raise ValueError("hex value should be a 6 characters string, but got : %s" % hex)
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def _rgb_to_hex(rgb):
    """
    Convert a color from rgb format to hexadecimal format
    :param rgb: a list of rgb components ( [r,g,b] )
    :return: a hexadecimal string ( "#XXXXXX" )
    """
    t = tuple(rgb)
    return "#%0.2X%0.2X%0.2X" % t

def _random_rgb():
    return random.choices(range(0,255),k=3)

def make_gradient(start_color, end_color, steps):
    """
    Generate a gradient from start_color to end_color
    :param start_color: the first color of the gradient (list of [r,g,b])
    :param end_color: the last color of the gradient (list of [r,g,b])
    :param steps: the number of colors in the final list
    :return: a list of colors (hex strings)
    """
    if steps < 2:
        return None
    colors = [_rgb_to_hex(start_color)]
    for n in range(1,steps-1):
        color = [int(start_color[i] + (n / steps) * (end_color[i] - start_color[i])) for i in range(3)]
        colors.append(_rgb_to_hex(color))
    colors.append(_rgb_to_hex(end_color))
    return colors

class CozzleApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.ordered_pieces = []
        self.canvas = tk.Canvas(self, width=window_width, height=window_height)
        self.selected_for_move = None

        self.reset()

        self.canvas.bind("<ButtonPress-1>", self.select_and_swap)
        self.bind("<KeyPress-r>", self.renew_gradient)

        # Give focus to the frame (self) to receive Keyboard events
        self.focus_set()
        self.canvas.pack()

    def reset(self):
        """
        Clear the canvas and draw a new gradient list
        """
        g = make_gradient(_random_rgb(), _random_rgb(), gradient_steps)
        # clear canvas
        self.canvas.delete("all")
        # draw pieces on canvas with colors from g, the generated gradient
        for s in range(gradient_steps):
            col = g[s]

            # make items movable except the first and the last
            tag = 'movable'
            if s == 0 or s == gradient_steps - 1:
                tag = 'fixed'

            tags = (tag, 'color_piece')
            r_id = self.canvas.create_rectangle(s * window_width / gradient_steps, 0,
                                                (s + 1) * window_width / gradient_steps, window_height, outline=col,
                                                fill=col, tags=tags)

            # store pieces ids in order
            self.ordered_pieces.append(r_id)

    # https://stackoverflow.com/a/38256215
    def select_and_swap(self, event):
        """
        """
        r_id = self.canvas.find_closest(event.x, event.y)[0] # returns a tuple of length 1 so get the first element
        if "fixed" in self.canvas.gettags(r_id):
            return
        col = self.canvas.itemcget(r_id, "fill")
        if self.selected_for_move is None:
            self.selected_for_move = (r_id, col)
        else:
            # swap items
            (r_id1,col1) = self.selected_for_move
            self.canvas.itemconfigure(r_id, fill=col1, outline=col1)
            self.canvas.itemconfigure(r_id1, fill=col, outline=col)
            self.selected_for_move = None

    def renew_gradient(self, event):
        """
        Respond to the renew_gradient event
        """
        print("Drawing a new gradient")
        self.reset()

def main():
    # create the base window
    window = tk.Tk()
    # create the app
    CozzleApp(window).pack()
    # run the actual app
    window.mainloop()

if __name__=='__main__':
    main()
