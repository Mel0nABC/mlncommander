MLNCommander

MLNCommander is a dual-window file explorer

<img width="1774" height="1429" alt="imagen" src="https://github.com/user-attachments/assets/73258a6e-77fc-404d-8e37-056c2d1cc9dc" />

Filtered by name:

It has filtering to search the beginning of files and directories, just type.

<img width="888" height="289" alt="imagen" src="https://github.com/user-attachments/assets/bd16cfec-100f-4f5d-ab7d-ecf853280d50" />


After 5 seconds, pressing Escape or switching focus to the other browser cancels the search and returns to the normal window.

Rename:

Rename files or directorys.

<img width="712" height="341" alt="imagen" src="https://github.com/user-attachments/assets/636761c2-1e84-4f27-abb9-8a3a7a968b84" />


New file:

Create office application files

<img width="440" height="428" alt="imagen" src="https://github.com/user-attachments/assets/760c48a8-66f9-415b-8c10-49d3da4ec2b5" />

Copy:

You can copy files and entire directories; it will determine whether they exist or not.


<img width="536" height="277" alt="image-4" src="https://github.com/user-attachments/assets/f368eda0-d983-4052-a1d6-fc7c8e29cb85" />

<img width="697" height="602" alt="image-5" src="https://github.com/user-attachments/assets/d896680e-3898-48ce-acb4-95fa682400a5" />


Move:

Move one or more locations. A dialog box will also appear if it finds a file that already exists, asking you what to do.

<img width="697" height="602" alt="image-6" src="https://github.com/user-attachments/assets/f58f7d50-61e3-4891-99fd-38de07f8bac2" />


Create durectirues:

<img width="714" height="229" alt="image-7" src="https://github.com/user-attachments/assets/e87085ce-5715-40a0-a16e-afc372188c35" />


Delete:

Delete one or multiple options


<img width="696" height="586" alt="image-8" src="https://github.com/user-attachments/assets/b94f4c74-a0cd-49b1-9c81-9c591c010c71" />


Hotkeys:

F2 > Rename
F5 > Copy
F6 > Move
F7 > Create Directory
F8 > Delete
F9 > Generate duplicate (copy)
F10 > Opens File menu, the Yes button closes it.
Tab > Switch Browser
Ctrl+O > In the opposite explorer, open the selected folder or, if you are in a file, the same folder

Enable search:

Just type and it will search the beginning of directories and files.

Compatible:

It's built with Gtk+Python, uses symbolic icons, and is compatible with AdWita or Gnome themes.

<img width="138" height="245" alt="imagen" src="https://github.com/user-attachments/assets/9c1fa5bd-63ca-4ea9-80df-2e6d79638861" />


Installation:

1) git clone https://github.com/Mel0nABC/mlncommander
2) cd mlncommander
3) python -m venv venv
4) source venv/bin/activate.fish | source venv/bin/activate.csh | source venv/bin/activate
5) pip install -r requirements.txt
6) ./venv/bin/python App.py

Requirements:

- python
- tk

Issues:

If your screen is blank when using a theme in dark mode, add "GTK_THEME=Adwaita-dark" to /etc/environment


