

#===================================================================================================================
#===================================================================================================================
#===================================================================================================================


# PROGRAM:        Archiver
app_vers = "0.1.5"
# PROGAMMER:      Jake Springer
# DATE:           6/11/23
# PYTHON VERS:    3.10.6

#-----------------------------------------------------------------------------------


import json
# from archive import Archive
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
app_name = "Archiver"
app_title = app_name, app_vers

# Fonts/Window stuff
font_family = "Hack"
header_font = (font_family, "18","bold","underline")
body_font = (font_family, "12")
small_font = (font_family, "10")
main_bg = "grey90"
stats_bg = "grey80"

add_dt = tk.IntVar()


#       Load JSON config file
with open(config_file, 'r') as file:
    config = json.load(file)
    start_dir = config["start_dir"]
    save_dir = config["save_dir"]
    verbose = config["verbose"]
    full_paths = config["preserve_paths"]
    clean_names = config["clean_names"]
    date_fmt = config["date_fmt"]

archive.archive_path = save_dir


#===================================================================================================================
#===================================================================================================================
#===================================================================================================================
#                                  Functions

# ----- JSON Functions ------

def load_json():
    with open(config_file, 'r') as file:
        return json.load(file)
    

def save_json(data):
    with open(config_file, 'w') as file:
        file.write(json.dumps(data, indent=4))

# ----- Utilities ------

def report(msg):
    if verbose:
        print("[>] " + msg)


def get_date():
    now = datetime.now()
    return now.strftime(date_fmt)


def display_loop(lbl_list, val_list, pos_list):
    # pos_list = (label x position, value x position, row gap)
    lbl_xpos = pos_list[0] # Label placement 
    val_xpos = pos_list[1] # Value placement
    row_ypos = pos_list[2] # Gap between rows
    for l in lbl_list:
        # Get matching value from val_list
        i = lbl_list.index(l)
        v = val_list[i]
        # Calculate row
        y = (row_ypos * i ) + row_ypos
        l.place(x=lbl_xpos,y=y)
        v.place(x=val_xpos, y=y)

# ------ File data ------

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

#TODO rename this mf
def calc_size(): # Get size of all directories in archive.target_paths
    b = 0
    for p in archive.target_paths:
        b += get_size(p)
    fmt = convert_size(b)
    size_before_val["text"] = fmt


def count_files(path):
    num=0
    for i in os.walk(path, topdown=True):
        num += len(i[2]) 
    archive.total_files = num


# ----- File broswers ------

def add_dir(): # For adding directories to archive.target_paths
    report("Opened directory browser")

    path = filedialog.askdirectory(
        initialdir = start_dir,
        title = "Select a folder"
    )
    if not path:
        report("File browser closed")
        return    
    archive.target_paths.append(path)
    paths_added_val["text"] = str(len(archive.target_paths))
    #update_path_box()
    paths_box.config(state="normal")
    paths_box.insert(tk.END, path + '\n')
    paths_box.config(state="disabled")
    # Get the estimated size of paths added to the target paths list
    calc_size()
    # Total files to be archived
    count_files(path)
    file_count_val["text"] = archive.total_files
    report("Added directory to target path: " + path)


def browse_files(): # return a single file path
    report("Opened file browser")
    filename = filedialog.askopenfilename(
        initialdir=start_dir,
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
        exclude_file_val["font"] = small_font
        exclude_file_val["text"] = path

# ----- archive object data ------

# Get name field, mess w it a bit
def update_name(): 
    name = arch_name_entry.get()
    if clean_names:
        name = clean_archive_name(name)
    if name:
        if add_dt.get():
            name += '_'
            name += get_date()
        name += '.tar.gz'
        archive.archive_name = name
        arch_name_val["text"] = name
        report("Changed archive name: " + name)

# ----- Clean Archive Names ------

def clean_archive_name(name):
    # Remove spaces
    # Convert to lowercase
    clean_name = name.replace(" ", "_")
    return clean_name.lower()


#===================================================================================================================
#===================================================================================================================
#===================================================================================================================
#                                  Archive Pane

def start_archive():
    report("Starting archive")
    global root, archive
    # Window Setup ------------------
    win = tk.Toplevel(root)
    win.title("Progress")
    frame = tk.Frame(
        master=win,
        width=800,
        height=400
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
    
    # ----- text box ------
    

    file_box = tk.Text(
        win,
        state="disabled",
        width = 55,
        height = 5)

    scroll = tk.Scrollbar(win, orient="vertical", command=file_box.yview)
    file_box.configure(yscrollcommand=scroll.set)
    # scroll.pack(side=tk.RIGHT,fill='y')
    

    file_box.place(relx=.5, y=300,anchor=tk.CENTER)

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
                    file_box.config(state="normal")
                    file_box.insert(tk.END, f + '\n')
                    file_box.config(state="disabled")
                    win.update_idletasks() # Updates labels/pb during loop
                    tarhandle.add(os.path.join(root, f))
    done_lbl["text"] = "Finished"
    report("Finished archive")


#===================================================================================================================
#===================================================================================================================
#===================================================================================================================
#                                  Window Setup

report("Launching window")
root.title(app_title)

main = tk.Frame(
    master=root,
    width=600,
    height=500,
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

def update_json_config():
    data = load_json()
    data["start_dir"] = start_dir
    data["save_dir"] = save_dir
    data["preserve_paths"] = full_paths
    data["clean_names"] = clean_names
    save_json(data)
    report("Updated " + config_file)


def settings_window():
    def update():
        global save_dir, start_dir, clean_names, full_paths
        save_dir = save_dir_setting_val.get()
        start_dir = start_dir_setting_val.get()
        clean_names = bool(clean_names_cb.get())
        full_paths = bool(preserve_paths_cb.get())
        save_dir_val["text"] = save_dir
        update_json_config()
        win.destroy()

    # ----- ui ------
    settings_bg = None
    settings_font = (font_family, "12")
    entry_width = 30
    # ----- window setup ------
    report("Opened settings")
    win = tk.Toplevel(root)
    win.title("Settings")
    # ----- frame setup ------
    frame = tk.Frame(
        master=win,
        width=500,
        height=600,
        bg=settings_bg
        )
    frame.pack()

    # ----- save directory ------
    save_dir_setting_lbl = tk.Label(
        win,
        text="Directory for archives",
        font=settings_font,
        bg=settings_bg
        )

    save_dir_setting_val = tk.Entry(
        win, 
        width = entry_width,
        font=settings_font,
        bg=settings_bg
        )

    # ----- start directory ------
    start_dir_setting_lbl = tk.Label(
        win,
        text="Start directory",
        font=settings_font,
        bg=settings_bg
        )

    start_dir_setting_val = tk.Entry(
        win, 
        width = entry_width,
        font=settings_font,
        bg=settings_bg
        )
    # ----- clean names ------
    clean_names_cb = tk.IntVar()

    clean_names_setting_lbl = tk.Label(
        win,
        text="Clean archive names",
        font=settings_font,
        bg=settings_bg
        )

    clean_names_setting_val = tk.Checkbutton(
        win,
        variable=clean_names_cb,
        bg=settings_bg)

    # ----- preserve paths ------
    preserve_paths_cb = tk.IntVar()
    preserve_paths_setting_lbl = tk.Label(
        win,
        text="Preserve file paths",
        font=settings_font,
        bg=settings_bg
        )

    preserve_paths_setting_val = tk.Checkbutton(
        win,
        variable=preserve_paths_cb,
        bg=settings_bg)

    # ----- buttons ------
    about_btn = tk.Button(
        win,
        text="About " + app_name
    )

    update_settings_btn = tk.Button(
        win,
        text="Update",
        command=update
    )

    # ----- placements ------
    lbl_list = [
        save_dir_setting_lbl,
        start_dir_setting_lbl,
        clean_names_setting_lbl,
        preserve_paths_setting_lbl
    ]

    val_list = [
        save_dir_setting_val,
        start_dir_setting_val,
        clean_names_setting_val,
        preserve_paths_setting_val
    ]

    display_loop(lbl_list, val_list, (10,200,50))
    
    # ----- set values ------
    if clean_names:
        clean_names_setting_val.select()
    if full_paths:
        preserve_paths_setting_val.select()

    about_btn.place(relx=.5, y=500,anchor=tk.CENTER)
    update_settings_btn.place(relx=.5, y=550,anchor=tk.CENTER)

    # ----- fill entry widgets ------
    start_dir_setting_val.insert(tk.END, start_dir)
    save_dir_setting_val.insert(tk.END, save_dir)

#===================================================================================================================
#===================================================================================================================
#===================================================================================================================
#                           Main Frame Setup 

# Header
label = tk.Label(
    master=main,
    text=app_title,
    font=header_font,
    bg=main_bg)

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
    command=update_name)

# Checkboxes
c1 = tk.Checkbutton(
    main,
    variable=add_dt,
    text="Add date",
    font=small_font,
    bd=0,
    bg=main_bg)

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
    bg=main_bg)

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
    bg=main_bg)

label.place(x=20,y=250)

add_exclude_btn = tk.Button(main, text="Browse", font=body_font, command=add_exclude)
add_exclude_btn.place(x=475,y=250)

#-----------------------------------------------------------------------------------

start_archive_btn = tk.Button(
    main,
    text="Start Archive",
    command=start_archive)

start_archive_btn.place(x=250,y=400)

settings_btn = tk.Button(
    main,
    text="Settings",
    command=settings_window)

settings_btn.place(x=175, y=400)

#===================================================================================================================
#===================================================================================================================
#===================================================================================================================
#       Stats Page Setup

# -------------------------------------------
# Archive name

arch_name_lbl = tk.Label(
    master=stats,
    text="Archive name:",
    font=body_font,
    bg=stats_bg)

arch_name_val = tk.Label( #?
    stats,
    text="",
    font=body_font,
    bg=stats_bg)

# -------------------------------------------
# Display save directory path

save_dir_lbl = tk.Label(
    stats,
    text="Save folder:",
    font=body_font,
    bg=stats_bg)


save_dir_val = tk.Label(
    stats, 
    text=save_dir,
    font=body_font,
    bg = stats_bg)

# -------------------------------------------
# Paths added

paths_added_lbl = tk.Label(
    master=stats,
    text="Paths added:",
    font=body_font,
    bg=stats_bg
)

paths_added_val = tk.Label(
    stats,
    text="0",
    font=body_font,
    bg=stats_bg
)

# -------------------------------------------
# Exclude file

exclude_file_lbl = tk.Label(
    master=stats,
    text="Exclude file:",
    font=body_font,
    bg=stats_bg)

exclude_file_val = tk.Label(
    stats,
    text="None",
    font=body_font,
    bg=stats_bg)

# -------------------------------------------
# Archive size

size_before_lbl = tk.Label(
    master=stats,
    text="Size (before):",
    font=body_font,
    bg=stats_bg)

size_before_val = tk.Label(
    master=stats,
    text="0",
    font=body_font,
    bg=stats_bg)

# -------------------------------------------
# File count

file_count_lbl = tk.Label(
    master=stats,
    text="File count:",
    font=body_font,
    bg=stats_bg)

file_count_val = tk.Label(
    master=stats,
    text="0",
    font=body_font,
    bg=stats_bg)

# -------------------------------------------
# Path list

paths_box_lbl = tk.Label(
    master=stats,
    text="Paths to Archive",
    font=body_font,
    bg=stats_bg)

paths_box = tk.Text(
    stats,
    state="disabled",
    width = 55,
    height = 15)

paths_box_lbl.place(x=175, y=175)
paths_box.place(x=25,y=200)

#-----------------------------------------------------------------------------------
    # Displaying Stats Labels and Values#


lbl_list = [
    arch_name_lbl,
    save_dir_lbl,
    paths_added_lbl,
    #exclude_file_lbl,
    file_count_lbl,
    size_before_lbl]

val_list = [
    arch_name_val,
    save_dir_val,
    paths_added_val,
    #exclude_file_val,
    file_count_val,
    size_before_val]

pos_list = (10,150,25)

display_loop(lbl_list, val_list, pos_list) 

#-----------------------------------------------------------------------------------


root.mainloop()


#===================================================================================
