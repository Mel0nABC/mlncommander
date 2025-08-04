MLNCommander

MLNCommander is a dual-window file explorer

<img width="128" height="128" alt="mlncommander_transparente" src="https://github.com/user-attachments/assets/0ddcce0e-50ec-4efe-8015-0984bc8e785e" />


<img width="1743" height="1429" alt="image" src="https://github.com/user-attachments/assets/9fdc75f6-8f12-45d3-8a1d-f11fe3414d97" />



Filtered by name:

It has filtering to search the beginning of files and directories, just type.

<img width="887" height="291" alt="image-2" src="https://github.com/user-attachments/assets/348ffcef-68b9-4dca-9301-3b081b048a30" />


Indicate below what you are looking for

<img width="418" height="166" alt="image-3" src="https://github.com/user-attachments/assets/1a080b4b-b646-4729-9957-36f7b3ea2342" />


After 5 seconds, pressing Escape or switching focus to the other browser cancels the search and returns to the normal window.

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
F10 > Opens File menu, the Yes button closes it.
Tab > Switch Browser

Enable search:

Just type and it will search the beginning of directories and files.

Compatible:

It's built with Gtk+Python, uses symbolic icons, and is compatible with AdWita or Gnome themes.

Installation:

1) git clone https://github.com/Mel0nABC/mlncommander
2) cd mlncommander
3) python -m venv venv
4) source venv/bin/activate.fish
5) pip install -r requirements.txt
6) ./venv/bin/python App.py

Requirements:

- python
- tk

Issues:

If your screen is blank when using a theme in dark mode, add "GTK_THEME=Adwaita-dark" to /etc/environment


