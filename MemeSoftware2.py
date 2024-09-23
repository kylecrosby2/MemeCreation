#! python3
# MemeSoftware2.py - Completely local version of the meme software.

from functools import partial
from PIL import Image, ImageTk, ImageDraw, ImageFont
from textwrap import wrap
from pathlib import Path
import tkinter as tk
import random
import os
import re
import json

# Image Formatting


def line1(image_path, output_path):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    colors = ["red", "green", "blue", "yellow",
              "purple", "orange"]
    for i in range(0, 100, 20):
        draw.line((i, 0) + image.size, width=5,
                  fill=random.choice(colors))
    image.save(output_path)


def line2(output_path):
    image = Image.new("RGB", (800, 600), "white")
    points = [(100, 100), (150, 200), (200, 50), (400, 400)]
    draw = ImageDraw.Draw(image)
    draw.line(points, width=15, fill="green", joint="curve")
    image.save(output_path)


def get_y_and_heights(text_wrapped, dimensions, margin, font):
    """Get the first vertical coordinate at which to draw text and the height of each line of text"""
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    # Calculate the height needed to draw each line of text (including its bottom margin)
    line_heights = [
        font.getmask(text_line).getbbox()[3] + descent + margin
        for text_line in text_wrapped
    ]
    # The last line doesn't have a bottom margin
    line_heights[-1] -= margin

    # Total height needed
    height_text = sum(line_heights)

    # Calculate the Y coordinate at which to draw the first line of text
    y = (dimensions[1] - height_text) // 2

    # Return the first Y coordinate and a list with the height of each line
    return (y, line_heights)


def font_size_determiner(txt):
    font_size = 50
    if len(txt) < 50:
        font_size = 85
    if 50 <= len(txt) < 75:
        font_size = 60
    if len(txt) >= 75:
        font_size = 50
    return font_size


def create_meme(image_path, txt, line_num_file):
    background = Image.new("RGBA", (1818, 1364), "white")
    img = Image.open(image_path).convert("RGBA")

    #print(img.size)

    #background = Image.open("background_730_1097.png")

    #print(background.size)

    # resize the image
    size = (1818, 1364)
    background = background.resize(size, Image.ANTIALIAS)

    background.paste(img, (0, 400), img)

    #d = ImageDraw.Draw(background)
    #txt = "Did you ever hear the tragedy of Darth Plagueis the Wise? No. I thought not, it's not a story the Jedi would tell you. It's a sith legend. Darth Plagueis was a dark lord of the sith..."
    #txt = "When you're racing a car named Our Plans"
    watermark_font = ImageFont.truetype('arial.ttf', 35)
    draw_interface = ImageDraw.Draw(background)
    draw_interface.text((100, 700), "@darthmemeus", (100, 100, 100), font=watermark_font)
    font_size = font_size_determiner(txt)
    font = ImageFont.truetype("arial.ttf", font_size)
    # Wrap the `text` string into a list of `CHAR_LIMIT`-character strings
    # 75
    text_lines = wrap(txt, 60)
    # Get the first vertical coordinate at which to draw text and the height of each line of text
    y, line_heights = get_y_and_heights(
        text_lines,
        (400, 500),
        10,
        font
    )

    # Draw each line of text
    for i, line in enumerate(text_lines):
        # Calculate the horizontally-centered position at which to draw this line
        line_width = font.getmask(line).getbbox()[2]
        # 1900
        x = ((1850 - line_width) // 2)

        # Draw this line
        draw_interface.text((x, y), line, font=font, fill="black")

        # Move on to the height at which the next line should be drawn at
        y += line_heights[i]

    background.save('%s/%s/%s.png' % (os.getcwd(), abbreviation + 'MemeFolderPNG', line_num_file), 'PNG')
    im_convert = Image.open('%s/%s/%s.png' % (os.getcwd(), abbreviation + 'MemeFolderPNG', line_num_file))
    rbg_im = im_convert.convert('RGB')
    rbg_im.save('%s/%s/%s.jpg' % (os.getcwd(), abbreviation + 'MemeFolder', line_num_file))
    os.remove('%s/%s/%s.png' % (os.getcwd(), abbreviation + 'MemeFolder', line_num_file))


# Non-image software starts here
# Select movie
movie_num_original = 0
while True:
    user_input = input("Select movie: The Phantom Menace (1), Attack of The Clones (2), Revenge of the Sith (3)")
    input_list = ["1", "2", "3"]
    if user_input in input_list:
        movie_num_original = int(user_input) - 1
        break
    else:
        print("Invalid input. Please input 1, 2, or 3.")


# GUI setup
# Text entry setup
window = tk.Tk()
window.title('Darthmemeus Meme Software')
meme_entry_label = tk.Label(window, text="Type meme here: ").grid(row=1, column=0)
meme_text = tk.StringVar()
meme_entry = tk.Entry(window, textvariable=meme_text, width=80).grid(row=1, column=1)

abbreviation_list = ['TPM', 'AOTC', 'ROTS']
save_folder_path = os.getcwd() + r'\%sMemeFolder' % abbreviation_list[movie_num_original]
# Make folder
try:
    os.mkdir(save_folder_path)
except OSError:
    pass

# Get images
#dir_path = r'C:\Users\kerry\Documents\Kyle Files\EveryLine\ThePhantomMenace'
movie_list = ['ThePhantomMenace', 'AttackOfTheClones', 'RevengeOfTheSith']
movie_num = tk.IntVar()
movie_num.set(movie_num_original)
abbreviation = abbreviation_list[movie_num.get()]
dir_path = os.getcwd() + r'\EveryLineImages\%s' % movie_list[movie_num.get()]
paths = sorted(Path(dir_path).iterdir(), key=os.path.getmtime)
image_num = tk.IntVar()
try:
    with open('%s_image_num_file.json' % abbreviation_list[movie_num.get()], 'r') as f:
        image_num.set(json.load(f) - 1)
except Exception:
    image_num.set(-1)


# Line number entry
line_num = tk.IntVar()
try:
    sorted_lines = sorted(Path(save_folder_path).iterdir(), key=os.path.getmtime)
    first_line_num = int(re.search(r'\d+', str(sorted_lines[-1])).group())
    line_num.set(first_line_num)
except Exception:
    line_num.set(0)
image_num_label = tk.Label(window, text="Image #:").grid(row=3, column=1)
any_line_entry = tk.Entry(window)
any_line_entry.grid(row=4, column=1)
any_line_entry.insert(0, str(image_num.get()))



def next_line_increase():
    image_num.set(image_num.get() + 1)
    with open('%s_image_num_file.json' % abbreviation_list[movie_num.get()], 'w') as f:
        json.dump(image_num.get(), f)
    any_line_entry.delete(0, 'end')
    any_line_entry.insert(0, str(image_num.get()))
    img_pix = Image.open(paths[image_num.get()])
    img_small = img_pix.resize((576, 324), Image.ANTIALIAS)
    global img_tk
    img_tk = ImageTk.PhotoImage(img_small)
    panel = tk.Label(window, image=img_tk)
    panel.grid(row=2, column=1)


def next_line_decrease():
    if image_num.get() > 0:
        image_num.set(image_num.get() - 1)
    with open('%s_image_num_file.json' % abbreviation_list[movie_num.get()], 'w') as f:
        json.dump(image_num.get(), f)
    any_line_entry.delete(0, 'end')
    any_line_entry.insert(0, str(image_num.get()))
    img_pix = Image.open(paths[image_num.get()])
    img_small = img_pix.resize((576, 324), Image.ANTIALIAS)
    global img_tk
    img_tk = ImageTk.PhotoImage(img_small)
    panel = tk.Label(window, image=img_tk)
    panel.grid(row=2, column=1)


def any_line():
    if int(any_line_entry.get()) <= len(paths):
        image_num.set(int(any_line_entry.get()))
    img_pix = Image.open(paths[image_num.get()])
    img_small = img_pix.resize((576, 324), Image.ANTIALIAS)
    global img_tk
    img_tk = ImageTk.PhotoImage(img_small)
    panel = tk.Label(window, image=img_tk)
    panel.grid(row=2, column=1)


next_line_increase()

# Line number entry
line_num_entry = tk.Entry(window)
line_num_entry.grid(row=4, column=0)
line_num_entry.insert(0, str(line_num.get()))
line_num_label = tk.Label(window, text="Current Line #:").grid(row=3, column=0)


def get_meme_info(entry_text, image_num, line_num):
    line_num.set(int(line_num_entry.get()))
    line_num.set(line_num.get() + 1)
    line_num_entry.delete(0, 'end')
    line_num_entry.insert(0, str(line_num.get()))
    image_path = paths[image_num.get()]
    txt = (entry_text.get())
    line_num_file = '%sMemeLine%s' % (abbreviation, str(line_num.get()))
    create_meme(image_path, txt, line_num_file)


# Create button
get_meme_info = partial(get_meme_info, meme_text, image_num, line_num)
create_button = tk.Button(text='Create Meme', command=get_meme_info, bg='black', fg='white').grid(row=1, column=3)

# Change line button
next_line_button = tk.Button(text="Next Line", command=next_line_increase, bg='black', fg='white').grid(row=2, column=3)
previous_line_button = tk.Button(text="Previous Line", command=next_line_decrease, bg='black', fg='white').grid(row=2, column=0)
go_to_line_button = tk.Button(window, text="Go to image", bg='black', fg='white', command=any_line).grid(row=5, column=1)


window.mainloop()
