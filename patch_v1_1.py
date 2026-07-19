from pathlib import Path

p = Path('bad_sector.c')
s = p.read_text(encoding='utf-8')

# Clear intro: a full floppy rises from below and enters the horizontal drive slot.
# All status/error text is confined to the monitor screen.
start = s.index('static void drawIntro(HDC dc)')
end = s.index('static void drawGame(HDC dc)', start)
intro = r'''static void drawIntro(HDC dc){float t=introTime;char b[120];
 int bodyX=105,bodyY=145,bodyW=510,bodyH=405;
 int screenX=145,screenY=185,screenW=430,screenH=195;
 int slotX=325,slotY=445,slotW=205;
 /* During insertion, draw the floppy first so the computer casing naturally hides the part already inside. */
 if(t<2.8f){float q=t/2.8f;int diskY=(int)(650-q*220);drawFloppy(dc,352,diskY,150,150);}
 /* computer body and monitor */
 fill(dc,bodyX,bodyY,bodyW,bodyH,RGB(29,35,44));outline(dc,bodyX,bodyY,bodyW,bodyH,RGB(135,150,160),4);
 fill(dc,screenX,screenY,screenW,screenH,RGB(3,8,12));outline(dc,screenX,screenY,screenW,screenH,RGB(65,84,96),3);
 /* drive bezel, horizontal slot and activity light */
 fill(dc,300,420,270,72,RGB(45,53,63));outline(dc,300,420,270,72,RGB(110,125,135),3);
 fill(dc,slotX,slotY,slotW,13,RGB(2,5,8));outline(dc,slotX,slotY,slotW,13,RGB(85,100,110),2);
 fill(dc,535,467,17,17,t>2.45f&&((int)(t*7)&1)?RGB(75,245,170):RGB(35,62,58));
 if(t<2.8f){float q=t/2.8f;
   txt(dc,205,214,25,RGB(82,245,190),"INSERT DISK INTO DRIVE A:");
   txt(dc,230,258,17,RGB(175,195,205),q<.82f?"WAITING FOR MEDIA...":"MEDIA DETECTED");
   /* show a thin portion in the slot once the disk reaches it */
   if(q>.72f)fill(dc,353,447,149,7,RGB(175,185,185));
   if(q>.90f)txt(dc,285,320,18,RGB(255,205,90),"CLICK - DISK LOCKED");
 }else if(t<4.9f){float q=(t-2.8f)/2.1f;
   txt(dc,250,215,24,RGB(82,245,190),"READING DRIVE A:");
   sprintf(b,"SCANNING TRACKS%.*s",((int)(t*4))%4,"...");txt(dc,255,258,18,RGB(205,220,228),b);
   fill(dc,190,312,340,16,RGB(20,38,45));fill(dc,190,312,(int)(340*q),16,RGB(75,225,175));
 }else{
   txt(dc,276,205,25,RGB(255,90,80),"DISK READ ERROR");
   txt(dc,188,246,17,RGB(235,240,245),"12 UNREADABLE BOOT SECTORS DETECTED");
   txt(dc,182,278,15,RGB(170,195,205),"The disk cannot start until repaired.");
   fill(dc,178,310,364,58,RGB(8,18,24));outline(dc,178,310,364,58,RGB(255,190,80),2);
   txt(dc,205,319,17,RGB(255,205,95),"LAUNCH RECOVERY UTILITY?");
   txt(dc,225,344,17,RGB(105,255,195),"ENTER - REPAIR DISK");
   txt(dc,386,370,13,RGB(150,170,180),"ESC - MENU");
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
print('Applied Bad Sector v1.2 intro and clarity patch')