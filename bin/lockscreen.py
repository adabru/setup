#!/usr/bin/env python

import tkinter as tk
from PIL import ImageTk, Image

root = tk.Tk()
root.attributes('-fullscreen', True)

image = Image.open('/home/adabru/graphics/desktop.jpg')
image_copy = image.copy()
photo = ImageTk.PhotoImage(image)
label = tk.Label(root, image = photo)

def resize_image(event):
    print('resize')
    size = (event.width, event.height)
    ratio = max(event.width / image_copy.width, event.height / image_copy.height)
    # print(size)
    # image = image_copy.resize(size, Image.ANTIALIAS)
    image = image_copy.resize((int(image_copy.width*ratio), int(image_copy.height*ratio)), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(image)
    label.config(image = photo)
    label.image = photo #avoid garbage collection
label.bind('<Configure>', resize_image)
label.pack(fill='both', expand=True)

root.bind('<KeyPress>', lambda e: root.destroy())
movecount = 1
def moveClose(e):
  global movecount
  movecount += 1
  if movecount > 5:
    root.destroy()
root.bind('<Motion>', moveClose)

root.mainloop()
