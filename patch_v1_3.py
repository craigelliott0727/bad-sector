from pathlib import Path

p = Path('bad_sector.c')
s = p.read_text(encoding='utf-8')

# More realistic floppy artwork with the writable label in the upper half.
floppy_start = s.index('static void drawFloppy(HDC dc')
floppy_end = s.index('static void drawIntro(HDC dc)', floppy_start)
floppy = r'''static void drawFloppy(HDC dc,int x,int y,int w,int h){
 int lx=x+w*16/100,ly=y+h*39/100,lw=w*68/100,lh=h*35/100;
 fill(dc,x,y,w,h,RGB(54,65,79));outline(dc,x,y,w,h,RGB(178,192,202),3);
 line(dc,x+5,y+h-6,x+w/5,y+h-6,RGB(95,110,122),2);line(dc,x+w-5,y+h-6,x+w*4/5,y+h-6,RGB(95,110,122),2);
 /* metal shutter */
 fill(dc,x+w*25/100,y+h*5/100,w*50/100,h*29/100,RGB(17,24,32));outline(dc,x+w*25/100,y+h*5/100,w*50/100,h*29/100,RGB(85,99,110),2);
 fill(dc,x+w*30/100,y+h*7/100,w*21/100,h*23/100,RGB(170,181,189));
 line(dc,x+w*55/100,y+h*8/100,x+w*55/100,y+h*30/100,RGB(85,98,108),2);
 /* writable paper label */
 fill(dc,lx,ly,lw,lh,RGB(229,229,218));outline(dc,lx,ly,lw,lh,RGB(120,125,125),2);
 line(dc,lx+10,ly+lh*30/100,lx+lw-10,ly+lh*30/100,RGB(185,186,180),1);
 line(dc,lx+10,ly+lh*57/100,lx+lw-10,ly+lh*57/100,RGB(185,186,180),1);
 /* lower hub recess and write-protect window */
 fill(dc,x+w*39/100,y+h*82/100,w*22/100,h*12/100,RGB(18,24,31));
 fill(dc,x+w*78/100,y+h*82/100,w*10/100,h*10/100,RGB(16,23,30));outline(dc,x+w*78/100,y+h*82/100,w*10/100,h*10/100,RGB(110,122,130),1);
}
'''
s = s[:floppy_start] + floppy + s[floppy_end:]

# The firewall duration must be a real float so its countdown lasts seconds, not frames.
s = s.replace('typedef struct { int x,y,life,active; } Wall;', 'typedef struct { int x,y,active; float life; } Wall;')
s = s.replace('walls[i]=(Wall){x,y,8,1};', 'walls[i]=(Wall){x,y,1,8.0f};')

# Floppy rises in front of the drive. The drive is drawn first; only the slot lip is drawn over the disk.
intro_start = s.index('static void drawIntro(HDC dc)')
intro_end = s.index('static void drawGame(HDC dc)', intro_start)
intro = r'''static void drawIntro(HDC dc){float t=introTime;char b[120];
 int bodyX=35,bodyY=42,bodyW=890,bodyH=625;
 int screenX=100,screenY=92,screenW=760,screenH=345;
 int driveX=245,driveY=465,driveW=470,driveH=130;
 int slotX=295,slotY=520,slotW=370,slotH=20;
 fill(dc,bodyX,bodyY,bodyW,bodyH,RGB(29,35,44));outline(dc,bodyX,bodyY,bodyW,bodyH,RGB(135,150,160),5);
 fill(dc,screenX,screenY,screenW,screenH,RGB(3,8,12));outline(dc,screenX,screenY,screenW,screenH,RGB(65,84,96),4);
 /* Drive housing is behind the incoming disk. */
 fill(dc,driveX,driveY,driveW,driveH,RGB(45,53,63));outline(dc,driveX,driveY,driveW,driveH,RGB(110,125,135),4);
 fill(dc,680,552,20,20,t>2.45f&&((int)(t*7)&1)?RGB(75,245,170):RGB(35,62,58));
 if(t<3.2f){float q=t/3.2f;int diskY=(int)(740-q*420);int saved;
   /* Clip away only the part already inside the opening. Everything below stays in front. */
   saved=SaveDC(dc);IntersectClipRect(dc,0,slotY+slotH,W,H);drawFloppy(dc,370,diskY,220,220);RestoreDC(dc,saved);
   /* Only the black opening and its narrow lip cover the disk. No lower bezel is redrawn over it. */
   fill(dc,slotX,slotY,slotW,slotH,RGB(2,5,8));outline(dc,slotX,slotY,slotW,slotH,RGB(170,182,191),2);
   line(dc,slotX,slotY,slotX+slotW,slotY,RGB(212,217,222),3);
   center(dc,145,29,RGB(82,245,190),"INSERT DISK INTO DRIVE A:");
   center(dc,205,18,RGB(175,195,205),q<.47f?"WAITING FOR MEDIA...":q<.94f?"MEDIA ENTERING DRIVE...":"DISK LOCKED");
   if(q>.94f)center(dc,385,19,RGB(255,205,90),"CLICK - DRIVE A: READY");
 }else{
   fill(dc,slotX,slotY,slotW,slotH,RGB(2,5,8));outline(dc,slotX,slotY,slotW,slotH,RGB(170,182,191),2);
   if(t<5.3f){float q=(t-3.2f)/2.1f;
     center(dc,160,26,RGB(82,245,190),"READING DRIVE A:");
     sprintf(b,"SCANNING TRACKS%.*s",((int)(t*4))%4,"...");center(dc,220,19,RGB(205,220,228),b);
     fill(dc,210,300,540,20,RGB(20,38,45));fill(dc,210,300,(int)(540*q),20,RGB(75,225,175));
   }else{
     center(dc,145,28,RGB(255,90,80),"DISK READ ERROR");
     center(dc,210,19,RGB(235,240,245),"12 UNREADABLE BOOT SECTORS DETECTED");
     center(dc,255,17,RGB(170,195,205),"The disk cannot start until the damaged sectors are repaired.");
     fill(dc,190,300,580,110,RGB(8,18,24));outline(dc,190,300,580,110,RGB(255,190,80),3);
     center(dc,320,21,RGB(255,205,95),"LAUNCH BAD SECTOR RECOVERY UTILITY?");
     center(dc,362,20,RGB(105,255,195),"ENTER - REPAIR DISK");
     center(dc,397,15,RGB(150,170,180),"ESC - RETURN TO MENU");
   }
 }
}
'''
s = s[:intro_start] + intro + s[intro_end:]

# Expanded arcade character set: blank, letters, numbers and classic score-table symbols.
old_state = "static char highNames[5][4]={{'A','A','A',0},{'A','A','A',0},{'A','A','A',0},{'A','A','A',0},{'A','A','A',0}}; static int initialsSlot=-1,initialsPos=0; static Mode initialsReturnMode=M_GAMEOVER;"
new_state = old_state + '\nstatic const char initialsChars[]=" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-!?*+/@#&"; static int initialsCharIndex(char c){int i;for(i=0;initialsChars[i];i++)if(initialsChars[i]==c)return i;return 1;}'
s = s.replace(old_state, new_state)

old_initials_update = "else if(mode==M_INITIALS){char*c=&highNames[initialsSlot][initialsPos];if(pressed(VK_UP)||pressed('W')){*c=(*c>='A'&&*c<'Z')?*c+1:'A';}if(pressed(VK_DOWN)||pressed('S')){*c=(*c>'A'&&*c<='Z')?*c-1:'Z';}if(pressed(VK_LEFT)||pressed('A')){if(initialsPos>0)initialsPos--;}if(pressed(VK_RIGHT)||pressed('D')||pressed(VK_RETURN)||pressed(VK_SPACE)){if(initialsPos<2)initialsPos++;else{saveData();mode=initialsReturnMode;}}if(pressed(VK_BACK)&&initialsPos>0)initialsPos--;}"
new_initials_update = "else if(mode==M_INITIALS){int ci,k;char*c=&highNames[initialsSlot][initialsPos];ci=initialsCharIndex(*c);if(pressed(VK_UP)||pressed(VK_DOWN)||pressed('W')||pressed('S')){int n=(int)strlen(initialsChars);ci+=(pressed(VK_UP)||pressed('W'))?1:-1;if(ci<0)ci=n-1;if(ci>=n)ci=0;*c=initialsChars[ci];}for(k='A';k<='Z';k++)if(pressed(k)){*c=(char)k;if(initialsPos<2)initialsPos++;}for(k='0';k<='9';k++)if(pressed(k)){*c=(char)k;if(initialsPos<2)initialsPos++;}if(pressed(VK_SPACE)){*c=' ';if(initialsPos<2)initialsPos++;}if(pressed(VK_LEFT)||pressed('A')){if(initialsPos>0)initialsPos--;}if(pressed(VK_RIGHT)||pressed('D')){if(initialsPos<2)initialsPos++;}if(pressed(VK_RETURN)){if(initialsPos<2)initialsPos++;else{saveData();mode=initialsReturnMode;}}if(pressed(VK_BACK)&&initialsPos>0)initialsPos--; }"
s = s.replace(old_initials_update, new_initials_update)

# Redraw the initials screen on the floppy's upper paper label.
initials_start = s.rindex('}else if(mode==M_INITIALS){')
initials_end = s.index('}else if(mode==M_SCORES){', initials_start)
initials_draw = r'''}else if(mode==M_INITIALS){int k;center(dc,55,34,RGB(105,255,195),"NEW HIGH SCORE");sprintf(b,"SCORE %08d",highScores[initialsSlot]);center(dc,112,24,RGB(255,205,90),b);center(dc,160,18,RGB(175,195,205),"WRITE YOUR TAG ON THE FLOPPY LABEL");drawFloppy(dc,300,215,360,390);
 fill(dc,358,367,244,130,RGB(235,234,221));outline(dc,358,367,244,130,RGB(65,70,72),3);center(dc,380,13,RGB(95,100,100),"RECOVERED BY");
 for(k=0;k<3;k++){char n[2]={highNames[initialsSlot][k],0};if(k==initialsPos){fill(dc,377+k*70,410,55,61,RGB(255,236,185));outline(dc,377+k*70,410,55,61,RGB(255,95,75),4);}txt(dc,390+k*70,417,43,RGB(20,28,34),n);}
 center(dc,625,15,RGB(175,195,205),"UP/DOWN: LETTERS, NUMBERS, SPACE + SYMBOLS");center(dc,651,15,RGB(175,195,205),"TYPE A-Z / 0-9   SPACE = BLANK   LEFT/RIGHT = SELECT");center(dc,680,18,RGB(235,240,245),"ENTER CONFIRMS");'''
s = s[:initials_start] + initials_draw + s[initials_end:]

# Graphical tool cards with charge counts and countdown bars for active timed utilities.
tool_helpers = r'''static float firewallRemaining(void){int i;float r=0;for(i=0;i<MAX_WALLS;i++)if(walls[i].active&&walls[i].life>r)r=walls[i].life;return r;}
static void drawToolIcon(HDC dc,int t,int x,int y,COLORREF c){switch(t){
 case TOOL_PULSE:outline(dc,x+3,y+3,20,20,c,2);line(dc,x+13,y,x+13,y+26,c,2);line(dc,x,y+13,x+26,y+13,c,2);break;
 case TOOL_LOCK:outline(dc,x+4,y+10,20,15,c,2);outline(dc,x+8,y+2,12,13,c,2);fill(dc,x+12,y+16,4,6,c);break;
 case TOOL_BEAM:line(dc,x+1,y+6,x+25,y+6,c,3);line(dc,x+5,y+13,x+21,y+13,c,3);line(dc,x+9,y+20,x+17,y+20,c,3);break;
 case TOOL_BACKUP:outline(dc,x+2,y+3,20,16,c,2);outline(dc,x+6,y+8,20,16,c,2);line(dc,x+11,y+16,x+20,y+16,c,2);break;
 case TOOL_OVERCLOCK:line(dc,x+15,y,x+5,y+15,c,4);line(dc,x+5,y+15,x+14,y+15,c,4);line(dc,x+14,y+15,x+8,y+27,c,4);line(dc,x+8,y+27,x+23,y+10,c,4);line(dc,x+23,y+10,x+15,y+10,c,4);break;
 case TOOL_FIREWALL:outline(dc,x+2,y+3,24,22,c,2);line(dc,x+2,y+10,x+26,y+10,c,2);line(dc,x+8,y+3,x+8,y+10,c,2);line(dc,x+19,y+10,x+19,y+25,c,2);break;
 default:outline(dc,x+3,y+3,21,21,c,2);line(dc,x+13,y+3,x+13,y+10,c,3);line(dc,x+13,y+17,x+13,y+24,c,3);line(dc,x+6,y+13,x+20,y+13,c,3);break;}}
static void drawToolBar(HDC dc){static const char*names[]={"PULSE","LOCK","BEAM","BACKUP","SPEED","WALL","REBOOT"};int i,j;char b[32];float wall=firewallRemaining();for(i=0;i<TOOL_COUNT;i++){int x=38+i*127,y=660,w=122,h=52;float rem=0,max=1;COLORREF edge=RGB(65,92,104),ink=toolCharges[i]>0?RGB(205,225,232):RGB(85,95,100);if(i==TOOL_LOCK&&sectorLock>0){rem=sectorLock;max=8;}if(i==TOOL_OVERCLOCK&&overclock>0){rem=overclock;max=10;}if(i==TOOL_FIREWALL&&wall>0){rem=wall;max=8;}if(rem>0)edge=RGB(95,255,190);else if(i==selectedTool)edge=RGB(255,205,90);fill(dc,x,y,w,h,RGB(7,15,21));outline(dc,x,y,w,h,edge,2);fill(dc,x+4,y+4,20,18,RGB(20,31,38));sprintf(b,"%d",i+1);txt(dc,x+10,y+5,13,RGB(255,205,90),b);drawToolIcon(dc,i,x+29,y+5,ink);txt(dc,x+60,y+5,11,ink,names[i]);sprintf(b,"x%d",toolCharges[i]);txt(dc,x+91,y+24,16,toolCharges[i]>0?RGB(255,225,145):RGB(110,110,110),b);for(j=0;j<toolCharges[i]&&j<4;j++)fill(dc,x+59+j*8,y+30,5,5,RGB(105,255,195));if(rem>0){int bw=(int)((w-8)*clampf(rem/max,0,1));fill(dc,x+4,y+h-9,w-8,5,RGB(25,45,50));fill(dc,x+4,y+h-9,bw,5,RGB(95,255,190));sprintf(b,"%.1fs",rem);txt(dc,x+5,y+35,10,RGB(185,255,225),b);}}}
'''
s = s.replace('static void drawGame(HDC dc){', tool_helpers + 'static void drawGame(HDC dc){', 1)

footer_start = s.index('sprintf(b,"1 PULSE:%d', s.index('static void drawGame(HDC dc)'))
footer_end = s.index('if(stageIndex==0', footer_start)
s = s[:footer_start] + 'drawToolBar(dc);' + s[footer_end:]

# Keep the title readable and use the available space for a richer attract screen.
title_start = s.index('if(mode==M_TITLE){', s.index('static void draw(void)'))
title_end = s.index('}else if(mode==M_INTRO){', title_start)
title = r'''if(mode==M_TITLE){int x,y;float tt=(float)GetTickCount64()/1000.0f;
 for(y=0;y<11;y++){int yy=125+y*50+(int)fmod(tt*13+y*7,50);line(dc,45,yy,915,yy,RGB(8,30,38),1);}for(x=0;x<17;x++){int xx=55+x*54;line(dc,xx,120,xx,680,RGB(7,25,32),1);}
 /* Glitch-shadowed title stays clear of every graphic. */
 center(dc,42,64,RGB(95,28,55),"BAD SECTOR");center(dc,34,64,RGB(76,255,186),"BAD SECTOR");center(dc,102,21,RGB(185,205,215),"1.44 MB RECOVERY ARCADE");
 /* Hero disk and animated diagnostic panel. */
 drawFloppy(dc,82,160,235,255);fill(dc,120,260,158,72,RGB(236,234,218));outline(dc,120,260,158,72,RGB(80,85,85),2);txt(dc,142,275,17,RGB(35,42,45),"DRIVE A:");txt(dc,142,302,15,RGB(35,42,45),"RECOVERY");
 fill(dc,350,155,530,300,RGB(4,11,17));outline(dc,350,155,530,300,RGB(75,225,175),3);txt(dc,375,175,16,RGB(105,255,195),"SYSTEM STATUS");txt(dc,375,208,15,RGB(175,195,205),"MEDIA: 1.44 MB FLOPPY");txt(dc,375,236,15,RGB(175,195,205),"FAULTS: BAD SECTORS / VIRUSES / MAGNETIC DAMAGE");
 for(y=0;y<4;y++)for(x=0;x<9;x++){int bx=382+x*50,by=278+y*34;COLORREF c=((x*3+y*5+(int)(tt*2))%13==0)?RGB(235,65,80):RGB(18,55,64);fill(dc,bx,by,40,25,c);outline(dc,bx,by,40,25,RGB(30,75,82),1);}drawMagnet(dc,795,365,17,RGB(235,65,75));
 fill(dc,160,485,640,175,RGB(4,11,17));outline(dc,160,485,640,175,RGB(75,225,175),3);
 center(dc,505,27,RGB(255,205,90),((int)(tt*2)&1)?"PRESS ENTER TO INSERT DISK":"PRESS ENTER TO START RECOVERY");
 center(dc,552,18,RGB(215,230,238),"C  DAILY RECOVERY DISK");sprintf(b,"2  TWO-PLAYER MODE: %s",twoPlayer?"ON":"OFF");center(dc,585,18,RGB(185,205,215),b);center(dc,618,18,RGB(185,205,215),"H  HIGH SCORES       O  OPTIONS");
 for(x=0;x<5;x++){int bx=335+x*86+(int)(sin(tt*1.7+x)*9),by=445+(int)(cos(tt*1.4+x)*7);fill(dc,bx+7,by+7,14,17,RGB(245,70+x*8,80));line(dc,bx+7,by+11,bx,by+6,RGB(245,90,95),2);line(dc,bx+21,by+11,bx+28,by+6,RGB(245,90,95),2);}
 center(dc,685,13,RGB(100,130,145),"NATIVE WIN32 / PROCEDURAL GRAPHICS + AUDIO / NO EXTERNAL ASSETS");
 '''
s = s[:title_start] + title + s[title_end:]

p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v1.6 interface and graphics patch')
