

#===================================================================================================================
#===================================================================================================================
#===================================================================================================================


# PROGRAM:        Archive Manager
# PROGAMMER:      Jake Springer
# DATE:           6/11/23
# PYTHON VERS:    3.10.6

#-----------------------------------------------------------------------------------

import json
from archive import Archive
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from datetime import datetime
import os 
import math
from clint.textui import progress
import tarfile

#-----------------------------------------------------------------------------------

class Archive:
    def __init__(self):
        self.archive_name = ""
        self.archive_path = ""
        self.target_paths = []
        self.verbose = True
        self.total_files = 0

#-----------------------------------------------------------------------------------
#       Global Vars

root = tk.Tk()
config_file = "config.json"
archive = Archive()


# Fonts/Window stuff
font_family = "Ubuntu"
header_font = (font_family, "18","bold","underline")
body_font = (font_family, "14")
small_font = (font_family, "10")
main_bg = "grey90"
stats_bg = "grey80"

add_dt = tk.IntVar()

#-----------------------------------------------------------------------------------
#       Load JSON config file

with open(config_file, 'r') as file:
    config = json.load(file)
    start_dir = config["start_dir"]
    save_dir = config["save_dir"]
    verbose = config["verbose"]
    show_full_paths = config["show_full_paths"]
    date_fmt = config["date_fmt"]

archive.archive_path = save_dir

#-----------------------------------------------------------------------------------
#       Load/Save JSON

def load_json():
    with open(config_file, 'r') as file:
        return json.load(file)
    

def save_json(data):
    with open(config_file, 'w') as file:
        file.write(json.dumps(data, indent=4))

#-----------------------------------------------------------------------------------

def report(msg):
    if verbose:
        print("[>] " + msg)


def get_date():
    now = datetime.now()
    return now.strftime(date_fmt)
    
# Convert bytes to something more readable 
def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])


# Get size of a directory
def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def count_files(path):
    num=0
    for i in os.walk(path, topdown=True):
        num += len(i[2]) 
    archive.total_files = num




#===================================================================================================================
#===================================================================================================================
#===================================================================================================================
#                                  Archive



def start_archive():
    report("Starting archive")
    global root, archive
    # Window Setup ------------------
    win = tk.Toplevel(root)
    win.title("Progress")
    frame = tk.Frame(
        master=win,
        width=800,
        height=250
    )
    frame.pack()

    # Progress bar ------------------
    pb = ttk.Progressbar(
        win,
        orient="horizontal",
        mode="determinate",
        length=700
    )
    pb.place(x=50,y=160)

    # Labels -------------------------
    lbl = tk.Label(
        win,
        text="Archiving...",
        font=body_font
    )
    lbl.place(x=10,y=20)
    # Name of .tar.gz file being created
    arch_file_lbl = tk.Label(
        win,
        text="",
        font=body_font
    )
    arch_file_lbl.place(x=10,y=50)
    # Current file path
    current_file_lbl = tk.Label(
        win,
        text="",
        font=body_font
    )
    current_file_lbl.place(x=10,y=80)
    # files done / total files
    file_count_lbl = tk.Label(
        win,
        text="",
        font=body_font
    )

    file_count_lbl.place(x=10,y=110)

    done_lbl = tk.Label(
        win,
        text="",
        font=body_font
    )

    done_lbl.place(x=300,y=200)

    # Loop  ---------------------------
    inc = 100 / archive.total_files # PB only works in 0-100
    f_count = 0 # Files looped through
    tarball = os.path.join(archive.archive_path, archive.archive_name) # Archive file to be saved
    arch_file_lbl["text"] = tarball # Updated the label that shows the archive file path
    with tarfile.open(tarball, "w:gz") as tarhandle:
        for path in archive.target_paths:
            for root,dirs,files in os.walk(path):
                for f in files:
                    f_count += 1
                    pb["value"] += inc # Increase the progress bar
                    current_file_lbl["text"] = os.path.join(root,f) # display current file 
                    file_count_lbl["text"] = f"File: {str(f_count)}/{str(archive.total_files)}"
                    win.update_idletasks() # Updates labels/pb during loop
                    tarhandle.add(os.path.join(root, f))
    done_lbl["text"] = "Finished"
    report("Finished archive")

#-----------------------------------------------------------------------------------
#                                  Window Setup

root.title("Archive Manager")

main = tk.Frame(
    master=root,
    width=600,
    height=700,
    bg=main_bg
)

stats = tk.Frame(
    master=root,
    width=500,
    bg=stats_bg
)

main.pack(fill=tk.Y, side=tk.LEFT, expand=True)
stats.pack(fill=tk.Y, side=tk.LEFT, expand=True)


#===================================================================================================================
#===================================================================================================================
#===================================================================================================================
#                               SETTINGS MENU






#===================================================================================================================
#===================================================================================================================
#===================================================================================================================
#                               UI Functions


# File browsers
def add_dir(): # For adding directories to archive.target_paths
    report("Opened directory browser")

    path = filedialog.askdirectory(
        initialdir = "/home/jakers/",
        title = "Select a folder"
    )
    if not path:
        report("File browser closed")
        return    
    archive.target_paths.append(path)
    paths_added_lbl["text"] = str(len(archive.target_paths))
    #update_path_box()
    paths_box.insert(tk.END, path + '\n')
    # Get the estimated size of paths added to the target paths list
    calc_size()
    # Total files to be archived
    count_files(path)
    file_count_lbl["text"] = archive.total_files
    report("Added directory to target path: " + path)


def browse_files(): # return a single file path
    report("Opened file browser")
    filename = filedialog.askopenfilename(
        initialdir="/home/jakers/Desktop",
        title="Select a file"
    )
    return filename


def add_exclude(): # Add exclude.txt
    report("Adding exclude.txt file")
    path = browse_files()
    s = os.path.split(path)
    if s[1] != "exclude.txt":
        report("Not a valid exclude file: " + path)
        #! Need to report some kind of error here
        return 
    else:
        report("Set exclude file to " + path)
        archive.exclude_file = path 
        exclude_file_lbl["font"] = small_font
        exclude_file_lbl["text"] = path


def calc_size(): # Get size of all directories in archive.target_paths
    b = 0
    for p in archive.target_paths:
        b += get_size(p)
    fmt = convert_size(b)
    size_before_lbl["text"] = fmt

#-----------------------------------------------------------------------------------
#                           Update Archive Name

# Get name field, mess w it a bit
def update_name(): 
    name = arch_name_entry.get()
    if name:
        if add_dt.get():
            name += '_'
            name += get_date()
        name += '.tar.gz'
        archive.archive_name = name
        arch_name_lbl["text"] = name
        report("Changed archive name: " + name)



#===================================================================================================================
#===================================================================================================================
#===================================================================================================================
#                           Main Frame Setup 



# Header
label = tk.Label(
    master=main,
    text="Archive Manager",
    font=header_font,
    bg=main_bg
)

label.place(x=220,y=50)

#-----------------------------------------------------------------------------------
#                           Archive Name

# Label 
label = tk.Label(
    master=main,
    text="Archive name:",
    font=body_font,
    bg=main_bg
)
# Text field
arch_name_entry = tk.Entry(master=main, width=20)

# Update button
arch_name_update_button = tk.Button(
    main,
    text="Update",
    font=body_font,
    command=update_name
)

# Checkboxes
c1 = tk.Checkbutton(
    main,
    variable=add_dt,
    text="Add date",
    font=small_font,
    bd=0,
    bg=main_bg
    )

label.place(x=20,y=150)
arch_name_entry.place(x=170, y=150)
c1.place(x=350, y=150)
arch_name_update_button.place(x=475, y=145)


#-----------------------------------------------------------------------------------
#                              Add Directories

# Add directories label
label = tk.Label(
    master=main,
    text="Add folders",
    font=body_font,
    bg=main_bg
)

label.place(x=20,y=200)

# Browse directories button
sel_dir_button = tk.Button(main, text="Browse",font=body_font, command=add_dir)
sel_dir_button.place(x=475,y=200)

#-----------------------------------------------------------------------------------
#                           Add Exclude File

label = tk.Label(
    master=main,
    text="Add exclude.txt",
    font=body_font,
    bg=main_bg
)

label.place(x=20,y=250)

add_exclude_btn = tk.Button(main, text="Browse", font=body_font, command=add_exclude)
add_exclude_btn.place(x=475,y=250)


#-----------------------------------------------------------------------------------

start_archive_btn = tk.Button(
    main,
    text="Start Archive",
    command=start_archive

)

start_archive_btn.place(x=250,y=600)


#===================================================================================================================
#===================================================================================================================
#===================================================================================================================

#       Stats Page Setup

# Change this shit to adjust spacing
x_start = 10 # 1,0
x_next = 150# 2,0
y_start = 0 # 0,1
y_next = y_start + 25# 0,2

# -------------------------------------------
# Archive name

label = tk.Label(
    master=stats,
    text="Archive name:",
    font=body_font,
    bg=stats_bg
)

label.place(x=x_start,y=y_start)


arch_name_lbl = tk.Label( #?
    stats,
    text="",
    font=body_font,
    bg=stats_bg
)

arch_name_lbl.place(x=x_next, y=y_start)

# -------------------------------------------
# Paths added

label = tk.Label(
    master=stats,
    text="Paths added:",
    font=body_font,
    bg=stats_bg
)

label.place(x=x_start, y=y_next)

paths_added_lbl = tk.Label(
    stats,
    text="0",
    font=body_font,
    bg=stats_bg
)

paths_added_lbl.place(x=x_next, y=y_next)

# -------------------------------------------
# Exclude file

label = tk.Label(
    master=stats,
    text="Exclude file:",
    font=body_font,
    bg=stats_bg
)

label.place(x=x_start, y=y_next * 2)


exclude_file_lbl = tk.Label(
    stats,
    text="None",
    font=body_font,
    bg=stats_bg
)

exclude_file_lbl.place(x=x_next, y=y_next * 2)


# -------------------------------------------
# Archive size

label = tk.Label(
    master=stats,
    text="Size (before):",
    font=body_font,
    bg=stats_bg
)

label.place(x=x_start, y=y_next * 3)

size_before_lbl = tk.Label(
    master=stats,
    text="0",
    font=body_font,
    bg=stats_bg
)

size_before_lbl.place(x=x_next, y=y_next * 3)

# -------------------------------------------
# File count

label = tk.Label(
    master=stats,
    text="File count:",
    font=body_font,
    bg=stats_bg
)

label.place(x=x_start, y=y_next * 4)

file_count_lbl = tk.Label(
    master=stats,
    text="0",
    font=body_font,
    bg=stats_bg
)

file_count_lbl.place(x=x_next, y=y_next*4)

# -------------------------------------------
# Path list

label = tk.Label(
    master=stats,
    text="Paths to Archive",
    font=body_font,
    bg=stats_bg
)

label.place(x=175, y=375)

paths_box = tk.Text(
    stats,
    width = 55,
    height = 15
)

paths_box.place(x=25,y=400)

#-----------------------------------------------------------------------------------


root.mainloop()


#===================================================================================
