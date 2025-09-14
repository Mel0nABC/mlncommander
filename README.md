<!-- SPDX-FileCopyrightText: 2025 Mel0nABC

 SPDX-License-Identifier: MIT -->
# MlnCommander: Your file manager to increment your limits

<img src="/images/banner.jpg" alt="Main banner" width="100%" height="auto">

MlnCommander is a dual-window file explorer that uses hotkeys to perform actions and save time from tedious double-clicking. It offers customizable colors and directory options. You can copy, move, create directories, create office files, and duplicate the current directory in the other explorer.

## Features

#### v1.00
- Copy, move, duplicate and rename actions
- Create a new directory
- Create office files: *.docx, *.odt, *.xlsx, *.ods, *.txt, and *.csv
- Duplicate files or folders with a different name
- Preview images
- Hotkeys and shortcuts
- Different native icons of the symbolic type
- Managing connection loss to network drives, preventing application crashes
- Compress and decompress with 7zip system
- Watchdog, monitors changes in browsers, both local and external
- Favorite directories for each browser
- Settings to automatically minimize copy, move, duplicate, compress and decompress options

#### V1.01

- Managing permissions, owners, and groups of files and folders.
- Options on the right button, on files or explorers
- Select themes, new ones should go to /usr/share/themes

## Motivation

This started as a project to learn Python. Then, I searched for a native graphical environment for Linux and found Gtk. I realized I could adapt it to my needs, since despite excellent similar programs, I had specific needs, such as image previews.


## Requeriments

- python >= 3.13.7
- tk >= 8.6.16
- gtk4  > 4.10
- pango >= 1:1.56.4
- mailcap >= 2.1.54
- 7zip >= 25.01


## Installation

- git clone https://github.com/Mel0nABC/mlncommander
- cd mlncommander
- python -m venv venv
- source venv/bin/activate.fish | source venv/bin/activate.csh | source venv/bin/activate
- pip install -r requirements.txt
- ./venv/bin/python App.py

## Licenses

MlnCommander attempts to comply with the SPDX specifications and generally uses the MIT license.

In the LICENSES folder, you'll find several types of licenses, depending on whether you're using a third-party utility.



## Download

[Download AppImage v1.01](https://github.com/Mel0nABC/mlncommander/releases/download/v1.01/mlnCommander_v1.01.AppImage)


