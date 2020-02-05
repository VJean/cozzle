#!/bin/env python3

import random
import tkinter as tk

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

# https://stackoverflow.com/a/38256215

def main():
    gradient_steps = 10
    window_width = 500
    window_height = 100

    start_color = _random_rgb()
    end_color = _random_rgb()
    g = make_gradient(start_color,end_color,gradient_steps)

    master = tk.Tk()
    w = tk.Canvas(master, width=window_width, height=window_height)
    w.pack()

    for s in range(gradient_steps):
        col = _rgb_to_hex(g[s])
        w.create_rectangle(s*window_width/gradient_steps, 0, (s+1)*window_width/gradient_steps, window_height, outline=col, fill=col)

    tk.mainloop()

if __name__=='__main__':
    main()
