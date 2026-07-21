from pathlib import Path

p = Path('bad_sector.c')
s = p.read_text(encoding='utf-8')

# Larger computer and corrected insertion layering:
# body first, floppy in front, then drive bezel/slot over the inserted portion.
start = s.index('static void drawIntro(HDC dc)')
end = s.index('static void drawGame(HDC dc)', start)
intro = r'''static void drawIntro(HDC dc){float t=introTime;char b[120];
 int bodyX=55,bodyY=70,bodyW=850,bodyH=585;
 int screenX=115,screenY=120,screenW=730,screenH=330;
 int driveX=280,driveY=490,driveW=400,driveH=105;
 int slotX=325,slotY=520,slotW=310,slotH=15;
 /* Main computer fills most of the screen. */
 fill(dc,bodyX,bodyY,bodyW,bodyH,RGB(29,35,44));outline(dc,bodyX,bodyY,bodyW,bodyH,RGB(135,150,160),5);
 fill(dc,screenX,screenY,screenW,screenH,RGB(3,8,12));outline(dc,screenX,screenY,screenW,screenH,RGB(65,84,96),4);

 /* Draw the floppy AFTER the computer body so it remains visibly in front. */
 if(t<2.9f){float q=t/2.9f;int diskY=(int)(760-q*255);drawFloppy(dc,405,diskY,150,150);}

 /* Drive face is drawn over the floppy, hiding only the portion entering the slot. */
 fill(dc,driveX,driveY,driveW,driveH,RGB(45,53,63));outline(dc,driveX,driveY,driveW,driveH,RGB(110,125,135),4);
 fill(dc,slotX,slotY,slotW,slotH,RGB(2,5,8));outline(dc,slotX,slotY,slotW,slotH,RGB(85,100,110),2);
 fill(dc,645,555,20,20,t>2.45f&&((int)(t*7)&1)?RGB(75,245,170):RGB(35,62,58));

 if(t<2.9f){float q=t/2.9f;
   center(dc,160,29,RGB(82,245,190),"INSERT DISK INTO DRIVE A:");
   center(dc,215,18,RGB(175,195,205),q<.72f?"WAITING FOR MEDIA...":q<.92f?"MEDIA DETECTED":"DISK LOCKED");
   /* Slot lip overlays the disk as it enters, creating a true insertion effect. */
   if(q>.66f){fill(dc,slotX,slotY,slotW,8,RGB(2,5,8));line(dc,slotX,slotY+8,slotX+slotW,slotY+8,RGB(150,165,175),2);}
   if(q>.91f)center(dc,360,19,RGB(255,205,90),"CLICK - DRIVE A: READY");
 }else if(t<5.0f){float q=(t-2.9f)/2.1f;
   center(dc,175,26,RGB(82,245,190),"READING DRIVE A:");
   sprintf(b,"SCANNING TRACKS%.*s",((int)(t*4))%4,"...");center(dc,230,19,RGB(205,220,228),b);
   fill(dc,220,300,520,20,RGB(20,38,45));fill(dc,220,300,(int)(520*q),20,RGB(75,225,175));
 }else{
   center(dc,165,28,RGB(255,90,80),"DISK READ ERROR");
   center(dc,225,19,RGB(235,240,245),"12 UNREADABLE BOOT SECTORS DETECTED");
   center(dc,270,17,RGB(170,195,205),"The disk cannot start until the damaged sectors are repaired.");
   fill(dc,210,315,540,105,RGB(8,18,24));outline(dc,210,315,540,105,RGB(255,190,80),3);
   center(dc,335,21,RGB(255,205,95),"LAUNCH BAD SECTOR RECOVERY UTILITY?");
   center(dc,375,20,RGB(105,255,195),"ENTER - REPAIR DISK");
   center(dc,412,15,RGB(150,170,180),"ESC - RETURN TO MENU");
 }
}
'''
s = s[:start] + intro + s[end:]

# Make the infected-sector rule explicit.
s = s.replace('Purple. Finishing the repair releases a virus.',
              'Purple tile with a bug. Repair it, then move away: it releases a hostile virus.')
s = s.replace('PURPLE = infected. Completing it releases a virus.',
              'PURPLE BUG TILE = repair it, then move away. The released moving bug cannot be repaired.')
s = s.replace('Infected sectors introduce the next threat, but corruption still cannot spread.',
              'Repair purple bug tiles, then move away. Never touch the moving bug it releases.')

# Add an unmistakable bug icon inside every purple infected sector on the board.
needle = 'if(s->type==S_FRAGMENTED){line(dc,sx+7,sy+10,sx+26,sy+10,RGB(30,30,30),2);line(dc,sx+10,sy+22,sx+27,sy+22,RGB(30,30,30),2);}if(s->type==S_PROTECTED)'
replacement = '''if(s->type==S_FRAGMENTED){line(dc,sx+7,sy+10,sx+26,sy+10,RGB(30,30,30),2);line(dc,sx+10,sy+22,sx+27,sy+22,RGB(30,30,30),2);}if(s->type==S_INFECTED){fill(dc,sx+12,sy+10,10,13,RGB(245,205,255));fill(dc,sx+14,sy+7,6,5,RGB(245,205,255));line(dc,sx+12,sy+12,sx+7,sy+9,RGB(245,205,255),2);line(dc,sx+22,sy+12,sx+27,sy+9,RGB(245,205,255),2);line(dc,sx+12,sy+19,sx+7,sy+23,RGB(245,205,255),2);line(dc,sx+22,sy+19,sx+27,sy+23,RGB(245,205,255),2);}if(s->type==S_PROTECTED)'''
s = s.replace(needle, replacement)

# Improve the large infected-sector example in the mission briefing.
old = 'if(nt==S_INFECTED){fill(dc,204,330,10,10,RGB(245,180,255));fill(dc,238,358,9,9,RGB(245,180,255));}'
new = '''if(nt==S_INFECTED){fill(dc,214,333,24,30,RGB(245,205,255));fill(dc,219,324,14,11,RGB(245,205,255));line(dc,214,338,200,330,RGB(245,205,255),4);line(dc,238,338,252,330,RGB(245,205,255),4);line(dc,214,355,200,366,RGB(245,205,255),4);line(dc,238,355,252,366,RGB(245,205,255),4);}'''
s = s.replace(old, new)

p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v1.3 intro and clarity patch')