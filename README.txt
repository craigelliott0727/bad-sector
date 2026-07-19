BAD SECTOR v0.5 - FEATURE-COMPLETE ALPHA
========================================

A standalone native Win32 arcade game designed for the 1,474,560-byte floppy-disk limit.
No engine, installer, downloaded content, or external game assets are required.

BUILD TARGET
------------
32-bit x86 Windows. Compile from an MSYS2/MinGW-w64 32-bit shell by running build_32bit.bat.
The build links only against Windows system libraries (GDI32 and WINMM).

CONTROLS
--------
Move:              WASD or arrow keys
Repair sector:     Hold Space
Select utility:    Q / E
Quick-select:      1 through 7
Use utility:       F or Enter
Pause:             Escape

FEATURES INCLUDED
-----------------
* Twenty-stage campaign with story text and designed progression
* Daily-seeded challenge mode
* Optional two-player alternating mode
* Seven utilities: antivirus pulse, sector lock, defrag beam, backup restore,
  overclock, firewall, and emergency reboot
* Corrupt, fragmented, infected, encrypted, unstable, and protected sectors
* Virus, worm, trojan, cluster, read-head sweeper, and magnet enemies
* Magnetic-field stages with polarity changes and a final Big Magnet boss
* Combo scoring, time bonuses, protected-file bonuses, achievements, and high scores
* Procedurally generated chiptune music and code-drawn graphics
* Pause menu, options, three difficulty settings, screen shake, particles, and local save data

IMPORTANT TESTING NOTE
----------------------
This source was produced in a Linux-hosted environment without a 32-bit Windows cross-compiler.
It therefore still needs to be compiled and play-tested on Windows. v0.5 is intended as a broad,
feature-complete alpha, not a contest-ready final build. The next step is gameplay testing,
compiler-error cleanup if needed, balancing, and measuring the actual EXE size.

The save file bad_sector.sav is created beside the executable and is not required to launch the game.
