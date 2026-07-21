from pathlib import Path

p = Path('bad_sector.c')
s = p.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Could not find {label}')
    s = s.replace(old, new, 1)


# Use the backslash key for the test-only instant level completion.
replace_once(
    'if(pressed(VK_F10)){debugCompleteStage();return;}',
    'if(pressed(VK_OEM_5)){debugCompleteStage();return;}',
    'test completion hotkey'
)
replace_once(
    'setStatus("F10 TEST: TRACK COMPLETED");',
    'setStatus("TEST MODE: TRACK COMPLETED");',
    'test completion status'
)


# Draw the black drive opening first and then the floppy in front of it.
# The clipping edge is the top of the opening, so the portion that has entered
# the drive disappears while the remaining disk visibly covers the slot.
old_intro = r'''if(t<2.25f){float q=t/2.25f;int diskY=(int)(735-q*435);int saved;
   /* The disk stays in front of the drive until it has completely crossed the slot. */
   saved=SaveDC(dc);IntersectClipRect(dc,0,slotY+slotH,W,H);drawFloppy(dc,360,diskY,240,240);RestoreDC(dc,saved);
   fill(dc,680,552,20,20,RGB(27,49,48));
   fill(dc,slotX,slotY,slotW,slotH,RGB(2,5,8));outline(dc,slotX,slotY,slotW,slotH,RGB(170,182,191),2);line(dc,slotX,slotY,slotX+slotW,slotY,RGB(212,217,222),3);'''

new_intro = r'''if(t<2.25f){float q=t/2.25f;int diskY=(int)(735-q*460);int saved;
   /* The slot is behind the disk; only the portion already inside the drive is hidden. */
   fill(dc,680,552,20,20,RGB(27,49,48));
   fill(dc,slotX,slotY,slotW,slotH,RGB(2,5,8));outline(dc,slotX,slotY,slotW,slotH,RGB(170,182,191),2);line(dc,slotX,slotY,slotX+slotW,slotY,RGB(212,217,222),3);
   saved=SaveDC(dc);IntersectClipRect(dc,0,slotY,W,H);drawFloppy(dc,360,diskY,240,240);RestoreDC(dc,saved);'''

replace_once(old_intro, new_intro, 'front-layer disk insertion animation')

p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v2.2 backslash test key and disk insertion layering fix')
