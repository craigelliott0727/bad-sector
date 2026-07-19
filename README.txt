BAD SECTOR v0.7 - USER-FEEDBACK BUILD
=====================================

A native Win32 arcade game designed to fit on a 1.44 MB floppy disk.
No engine, no external art, no downloaded content, and no installer.

WHAT CHANGED IN v0.7
--------------------
* New skippable opening animation: floppy insertion, disk scan, zoom to the
  magnetic surface, and Recovery Bot deployment.
* Level 1 now starts with exactly 12 damaged sectors and ends when all 12 are
  repaired. No new corruption spreads during the first two tutorial stages.
* Level 1 has only one very slow virus, arriving after a generous delay.
* Enemy spawning and speed now ramp more gradually across the campaign.
* Damaged sectors visibly clear from the bottom upward while being repaired.
* A percentage indicator and repair beam show that holding SPACE is working.
* Partial repair progress remains when the player moves away and returns.
* Player is now a recognizable Recovery Bot rather than a square.
* HUD says SECTORS REMAINING instead of showing an arbitrary recovered target.
* Daily-Seed Challenge renamed TODAY'S DISK and explained on the title screen.
* TODAY'S DISK uses the local calendar date, creates a repeatable fixed run,
  and ends after one score-attack stage.

CONTROLS
--------
WASD / Arrow keys  Move
Hold SPACE          Repair the sector beneath the Recovery Bot
Q / E               Select utility
F / ENTER           Use selected utility
1 through 7         Select utility directly
ESC                  Pause / skip intro

BUILD
-----
Run build_32bit.bat from a MinGW 32-bit command prompt, or use:

gcc -m32 -Os -s -ffunction-sections -fdata-sections bad_sector.c \
    -o bad_sector.exe -mwindows -lwinmm -lgdi32 \
    -Wl,--gc-sections

The source has not been compiled in this Linux environment because a 32-bit
Windows cross-compiler is unavailable here. Compile and play-test on Windows.


V0.7 PLAYTEST FOCUS
- Test the transition from Track 1 through Track 4.
- Confirm each new sector briefing makes its color and behavior understandable.
- Confirm the new intro reads as: disk inserted -> magnetic surface scanned -> zoom to sectors -> bot deployed.
