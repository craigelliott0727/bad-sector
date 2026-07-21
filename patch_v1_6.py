from pathlib import Path

p = Path('bad_sector.c')
s = p.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Could not find {label}')
    s = s.replace(old, new, 1)


def replace_function(signature, replacement):
    global s
    start = s.index(signature)
    brace = s.index('{', start)
    depth = 0
    end = None
    for i in range(brace, len(s)):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise SystemExit(f'Could not find end of {signature}')
    s = s[:start] + replacement + s[end:]


# A more authentic 3.5-inch disk: dark shell, silver shutter, and a wide ruled INDEX label.
floppy = r'''static void drawFloppy(HDC dc,int x,int y,int w,int h){
 int lx=x+w*13/100,ly=y+h*43/100,lw=w*74/100,lh=h*38/100,fs=w/36,i;
 POINT shell[8]={{x+8,y},{x+w-14,y},{x+w,y+14},{x+w,y+h-18},{x+w-18,y+h},{x+18,y+h},{x,y+h-18},{x,y+12}};
 HBRUSH br=CreateSolidBrush(RGB(34,35,38)),oldbr=(HBRUSH)SelectObject(dc,br);HPEN pn=CreatePen(PS_SOLID,3,RGB(180,188,194)),oldpn=(HPEN)SelectObject(dc,pn);
 Polygon(dc,shell,8);SelectObject(dc,oldpn);SelectObject(dc,oldbr);DeleteObject(pn);DeleteObject(br);
 /* molded shell highlights and lower shadow */
 line(dc,x+10,y+5,x+w-18,y+5,RGB(75,77,81),2);line(dc,x+5,y+14,x+5,y+h-23,RGB(68,70,74),2);
 line(dc,x+18,y+h-5,x+w-20,y+h-5,RGB(12,13,15),3);line(dc,x+w-5,y+17,x+w-5,y+h-22,RGB(12,13,15),3);
 /* silver shutter and exposed opening */
 fill(dc,x+w*28/100,y+h*2/100,w*44/100,h*28/100,RGB(118,122,126));outline(dc,x+w*28/100,y+h*2/100,w*44/100,h*28/100,RGB(35,37,40),2);
 fill(dc,x+w*30/100,y+h*3/100,w*19/100,h*25/100,RGB(200,204,207));fill(dc,x+w*32/100,y+h*4/100,w*4/100,h*23/100,RGB(238,240,241));
 fill(dc,x+w*57/100,y+h*4/100,w*10/100,h*22/100,RGB(20,22,25));line(dc,x+w*52/100,y+h*4/100,x+w*52/100,y+h*27/100,RGB(70,73,77),2);
 /* paper INDEX label matching a real floppy */
 fill(dc,lx,ly,lw,lh,RGB(247,247,244));outline(dc,lx,ly,lw,lh,RGB(95,98,100),2);
 if(fs<7)fs=7;txt(dc,lx+8,ly+3,fs,RGB(30,32,34),"INDEX");
 line(dc,lx,ly+lh*18/100,lx+lw,ly+lh*18/100,RGB(125,128,130),1);
 for(i=0;i<5;i++)line(dc,lx,ly+lh*(34+i*13)/100,lx+lw,ly+lh*(34+i*13)/100,RGB(155,157,158),1);
 /* hub opening, write-protect notch and shell details */
 fill(dc,x+w*39/100,y+h*84/100,w*22/100,h*10/100,RGB(15,17,20));outline(dc,x+w*39/100,y+h*84/100,w*22/100,h*10/100,RGB(72,75,79),2);
 fill(dc,x+w*87/100,y+h*85/100,w*6/100,h*7/100,RGB(225,226,222));outline(dc,x+w*87/100,y+h*85/100,w*6/100,h*7/100,RGB(75,77,79),1);
 fill(dc,x+w*5/100,y+h*13/100,4,4,RGB(10,11,13));fill(dc,x+w*92/100,y+h*13/100,4,4,RGB(10,11,13));
}'''
replace_function('static void drawFloppy(HDC dc', floppy)


# Faster insertion, followed by a clear seated-disk pause before the drive light and scan begin.
intro = r'''static void drawIntro(HDC dc){float t=introTime;char b[120];
 int bodyX=35,bodyY=42,bodyW=890,bodyH=625;
 int screenX=100,screenY=92,screenW=760,screenH=345;
 int driveX=245,driveY=465,driveW=470,driveH=130;
 int slotX=295,slotY=520,slotW=370,slotH=20;
 fill(dc,bodyX,bodyY,bodyW,bodyH,RGB(29,35,44));outline(dc,bodyX,bodyY,bodyW,bodyH,RGB(135,150,160),5);
 fill(dc,screenX,screenY,screenW,screenH,RGB(3,8,12));outline(dc,screenX,screenY,screenW,screenH,RGB(65,84,96),4);
 fill(dc,driveX,driveY,driveW,driveH,RGB(45,53,63));outline(dc,driveX,driveY,driveW,driveH,RGB(110,125,135),4);
 if(t<2.25f){float q=t/2.25f;int diskY=(int)(735-q*435);int saved;
   /* The disk stays in front of the drive until it has completely crossed the slot. */
   saved=SaveDC(dc);IntersectClipRect(dc,0,slotY+slotH,W,H);drawFloppy(dc,360,diskY,240,240);RestoreDC(dc,saved);
   fill(dc,680,552,20,20,RGB(27,49,48));
   fill(dc,slotX,slotY,slotW,slotH,RGB(2,5,8));outline(dc,slotX,slotY,slotW,slotH,RGB(170,182,191),2);line(dc,slotX,slotY,slotX+slotW,slotY,RGB(212,217,222),3);
   center(dc,145,29,RGB(82,245,190),"INSERT DISK INTO DRIVE A:");
   center(dc,205,18,RGB(175,195,205),q<.32f?"WAITING FOR MEDIA...":"MEDIA ENTERING DRIVE...");
 }else{
   int lampOn=t>2.55f&&((int)((t-2.55f)*7)&1)==0;
   fill(dc,680,552,20,20,lampOn?RGB(75,245,170):RGB(27,60,54));
   fill(dc,slotX,slotY,slotW,slotH,RGB(2,5,8));outline(dc,slotX,slotY,slotW,slotH,RGB(170,182,191),2);line(dc,slotX,slotY,slotX+slotW,slotY,RGB(212,217,222),3);
   if(t<3.45f){
     center(dc,155,27,RGB(82,245,190),"MEDIA DETECTED");
     center(dc,215,18,RGB(190,207,216),t<2.65f?"DISK LOCKED":"DRIVE SPINNING UP...");
   }else if(t<5.55f){float q=(t-3.45f)/2.10f;
     center(dc,150,26,RGB(82,245,190),"READING DRIVE A:");
     sprintf(b,"SCANNING TRACKS%.*s",((int)(t*4))%4,"...");center(dc,215,19,RGB(205,220,228),b);
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
}'''
replace_function('static void drawIntro(HDC dc)', intro)


# Put the score tag directly onto the authentic ruled label instead of drawing a second label over it.
initials_start = s.rindex('}else if(mode==M_INITIALS){')
initials_end = s.index('}else if(mode==M_SCORES){', initials_start)
initials_draw = r'''}else if(mode==M_INITIALS){int k;int fx=300,fy=215,fw=360,fh=390,lx=fx+fw*13/100,ly=fy+fh*43/100,lw=fw*74/100;center(dc,55,34,RGB(105,255,195),"NEW HIGH SCORE");sprintf(b,"SCORE %08d",highScores[initialsSlot]);center(dc,112,24,RGB(255,205,90),b);center(dc,160,18,RGB(175,195,205),"WRITE YOUR TAG ON THE FLOPPY LABEL");drawFloppy(dc,fx,fy,fw,fh);
 txt(dc,lx+67,ly+5,10,RGB(50,52,54),"/ RECOVERED BY");
 for(k=0;k<3;k++){int cx=lx+28+k*79;char n[2]={highNames[initialsSlot][k],0};if(k==initialsPos){fill(dc,cx,ly+47,58,61,RGB(255,239,190));outline(dc,cx,ly+47,58,61,RGB(255,95,75),4);}txt(dc,cx+13,ly+54,43,RGB(20,28,34),n);}
 line(dc,lx,ly+112,lx+lw,ly+112,RGB(155,157,158),1);center(dc,625,15,RGB(175,195,205),"UP/DOWN: LETTERS, NUMBERS, SPACE + SYMBOLS");center(dc,651,15,RGB(175,195,205),"TYPE A-Z / 0-9   SPACE = BLANK   LEFT/RIGHT = SELECT");center(dc,680,18,RGB(235,240,245),"ENTER CONFIRMS");'''
s = s[:initials_start] + initials_draw + s[initials_end:]


# Return how many new sectors were actually created so dynamic corruption can increase the mission target.
replace_once(
    'static void corruptRandom(int count){while(count--){int x=irand(GW),y=irand(GH);if(grid[y][x].type==S_CLEAN){grid[y][x].type=randomSector();grid[y][x].timer=frand()*2;}}}',
    'static int corruptRandom(int count){int made=0;while(count--){int x=irand(GW),y=irand(GH);if(grid[y][x].type==S_CLEAN){grid[y][x].type=randomSector();grid[y][x].timer=frand()*2;made++;}}return made;}',
    'counted random corruption'
)

# Emergency reboot creates five obligations as well as five damaged sectors.
replace_once('corruptRandom(5);invuln=3;', 'repairedGoal+=corruptRandom(5);invuln=3;', 'reboot sector goal')

# Worm trails are now visible additions to SECTORS LEFT.
replace_once(
    'if(x>=0&&y>=0&&x<GW&&y<GH&&grid[y][x].type==S_CLEAN)grid[y][x].type=S_CORRUPT;e->timer=0;',
    'if(x>=0&&y>=0&&x<GW&&y<GH&&grid[y][x].type==S_CLEAN){grid[y][x].type=S_CORRUPT;repairedGoal++;setStatus("WORM SPREAD: +1 SECTOR");}e->timer=0;',
    'worm spread goal'
)

# Slow the automatic spread cadence, especially on the first yellow-sector mission.
replace_once(
    'spreadTimer=!challengeMode&&stageIndex<3?999.0f:!challengeMode&&stageIndex==3?6.0f:3.5f;',
    'spreadTimer=!challengeMode&&stageIndex<3?999.0f:!challengeMode&&stageIndex==3?12.0f:7.0f;',
    'initial spread cadence'
)
replace_once(
    'spreadTimer=!challengeMode&&stageIndex==3?7.0f:clampf(4.8f-stageIndex*.07f,1.1f,4.8f);',
    'spreadTimer=!challengeMode&&stageIndex==3?14.0f:clampf(8.5f-stageIndex*.15f,3.0f,8.5f);',
    'repeat spread cadence'
)

# Automatic spread now raises the goal by the exact number of sectors created.
replace_once(
    'if(spreadTimer<=0&&sectorLock<=0&&(!challengeMode?stageIndex>=3:1)){corruptRandom(stageIndex>11?2:1);spreadTimer=',
    'if(spreadTimer<=0&&sectorLock<=0&&(!challengeMode?stageIndex>=3:1)){int added=corruptRandom(stageIndex>11?2:1);repairedGoal+=added;if(added)setStatus("CORRUPTION SPREAD: SECTORS ADDED");spreadTimer=',
    'automatic spread goal'
)

# Each yellow sector spreads much less frequently, and every successful spread is added to SECTORS LEFT.
replace_once('c->type==S_UNSTABLE&&sectorLock<=0&&c->timer>1.8f', 'c->type==S_UNSTABLE&&sectorLock<=0&&c->timer>(!challengeMode&&stageIndex==3?8.0f:5.5f)', 'unstable spread speed')
replace_once(
    'if(nx>=0&&ny>=0&&nx<GW&&ny<GH&&grid[ny][nx].type==S_CLEAN)grid[ny][nx].type=S_CORRUPT;c->timer=0;',
    'if(nx>=0&&ny>=0&&nx<GW&&ny<GH&&grid[ny][nx].type==S_CLEAN){grid[ny][nx].type=S_CORRUPT;repairedGoal++;setStatus("UNSTABLE SECTOR SPREAD: +1");}c->timer=0;',
    'unstable spread goal'
)

p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v1.8 intro, floppy label and spread-goal update')