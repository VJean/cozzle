#!/bin/env python3

import random
import tkinter as tk

gradient_steps = 10
window_width = 500
window_height = 100

def _hex_to_rgb(hex):
    h = hex.lstrip('#')
    if len(h) != 6:
        raise ValueError("hex value should be a 6 characters string, but got : %s" % hex)
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def _rgb_to_hex(rgb):
    t = tuple(rgb)
    return "#%0.2X%0.2X%0.2X" % t

def _random_rgb():
    return random.choices(range(0,255),k=3)

def make_gradient(color1, color2, steps):
    if steps < 2:
        return None
    colors = [color1]
    for n in range(1,steps-1):
        color = [int(color1[i] + (n/steps)*(color2[i]-color1[i])) for i in range(3)]
        colors.append(color)
    colors.append(color2)
    return colors

class CozzleApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        start_color = _random_rgb()
        end_color = _random_rgb()
        g = make_gradient(start_color,end_color,gradient_steps)
        self.ordered_pieces = []
        self.canvas = tk.Canvas(self, width=window_width, height=window_height)
        self.selected_for_move = None

        for s in range(gradient_steps):
            col = _rgb_to_hex(g[s])

            # make items movable except the first and the last
            tag = 'movable'
            if s == 0 or s == gradient_steps-1:
                tag = 'fixed'

            tags = (tag, 'color_piece')
            r_id = self.canvas.create_rectangle(s*window_width/gradient_steps, 0, (s+1)*window_width/gradient_steps, window_height, outline=col, fill=col, tags=tags)

            # store pieces ids in order
            self.ordered_pieces.append(r_id)

        # def on click : addTag selected or swap with already selected piece
        self.canvas.bind("<ButtonPress-1>", self.on_click)

        self.canvas.pack()


    # https://stackoverflow.com/a/38256215
    def on_click(self, event):
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


def main():

    window = tk.Tk()
    CozzleApp(window).pack()


    window.mainloop()

if __name__=='__main__':
    main()
