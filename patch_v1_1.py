from pathlib import Path

p = Path('bad_sector.c')
s = p.read_text(encoding='utf-8')

# Replace the awkward face-on floppy insertion with a simple edge-on slide into the drive.
start = s.index('static void drawIntro(HDC dc)')
end = s.index('static void drawGame(HDC dc)', start)
intro = r'''static void drawIntro(HDC dc){float t=introTime;char b[120];
 /* computer body and screen */
 fill(dc,105,145,510,405,RGB(29,35,44));outline(dc,105,145,510,405,RGB(135,150,160),4);
 fill(dc,145,185,430,195,RGB(3,8,12));outline(dc,145,185,430,195,RGB(65,84,96),3);
 /* drive bezel and slot */
 fill(dc,300,420,270,72,RGB(45,53,63));outline(dc,300,420,270,72,RGB(110,125,135),3);
 fill(dc,325,445,205,13,RGB(2,5,8));outline(dc,325,445,205,13,RGB(85,100,110),2);
 fill(dc,535,467,17,17,t>2.35f&&((int)(t*7)&1)?RGB(75,245,170):RGB(35,62,58));
 if(t<2.6f){float q=t/2.6f;int right=(int)(870-q*345);int visible=right-530;
   center(dc,70,28,RGB(82,245,190),"INSERTING DISK INTO DRIVE A:");
   /* edge-on disk: constant thickness, aligned with the slot */
   if(visible>0){if(visible>150)visible=150;fill(dc,right-visible,438,visible,26,RGB(62,73,86));outline(dc,right-visible,438,visible,26,RGB(175,188,198),2);fill(dc,right-visible+8,443,visible>24?visible-16:visible,5,RGB(215,218,210));}
   /* bezel always covers the disk once it crosses the slot */
   fill(dc,530,432,40,40,RGB(45,53,63));
   if(q>.88f)center(dc,585,18,RGB(255,205,90),"CLICK - DISK LOCKED");
 }else if(t<4.8f){float q=(t-2.6f)/2.2f;
   center(dc,215,23,RGB(82,245,190),"READING DRIVE A:");sprintf(b,"SCANNING TRACKS%.*s",((int)(t*4))%4,"...");center(dc,265,20,RGB(205,220,228),b);
   fill(dc,190,315,580,18,RGB(20,38,45));fill(dc,190,315,(int)(580*q),18,RGB(75,225,175));
 }else{
   center(dc,205,24,RGB(255,90,80),"DISK READ ERROR");center(dc,260,20,RGB(235,240,245),"12 UNREADABLE BOOT SECTORS DETECTED");center(dc,305,18,RGB(170,195,205),"The disk cannot start until the damage is repaired.");
   fill(dc,235,365,490,110,RGB(8,18,24));outline(dc,235,365,490,110,RGB(255,190,80),2);center(dc,385,22,RGB(255,205,95),"LAUNCH BAD SECTOR RECOVERY UTILITY?");center(dc,430,21,RGB(105,255,195),"ENTER - REPAIR DISK");center(dc,465,17,RGB(150,170,180),"ESC - RETURN TO MENU");
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
print('Applied Bad Sector v1.1 clarity patch')