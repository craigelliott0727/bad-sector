from pathlib import Path
import re

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


# Animation, recently-used-tool and classic extra-life state.
replace_once(
    'static float px,py,invuln,spawnTimer,spreadTimer,stageClock,stageIntro,introTime,completeTime,screenShake,magnetPulse,overclock,sectorLock,firewallTimer;',
    'static float px,py,invuln,spawnTimer,spreadTimer,stageClock,stageIntro,introTime,completeTime,screenShake,magnetPulse,overclock,sectorLock,firewallTimer,beamFxTimer,lastToolFlash;\nstatic int beamFxRow=-1,lastToolUsed=-1,nextOneUpScore=5000;',
    'v1.9 effect state'
)
replace_once(
    'overclock=0;sectorLock=0;firewallTimer=0;',
    'overclock=0;sectorLock=0;firewallTimer=0;beamFxTimer=0;beamFxRow=-1;lastToolUsed=-1;lastToolFlash=0;',
    'stage effect reset'
)
replace_once(
    'run=(RunStats){0,1,3,100,0,0,0,0,0};',
    'run=(RunStats){0,1,3,100,0,0,0,0,0};nextOneUpScore=5000;',
    'new-game 1UP threshold'
)
replace_once(
    'if(sectorLock>0)sectorLock-=dt;if(firewallTimer>0)firewallTimer-=dt;',
    'if(sectorLock>0)sectorLock-=dt;if(firewallTimer>0)firewallTimer-=dt;if(beamFxTimer>0)beamFxTimer-=dt;if(lastToolFlash>0)lastToolFlash-=dt;',
    'effect countdowns'
)
replace_once(
    'if(statusTimer>0)statusTimer-=dt;',
    'if(statusTimer>0)statusTimer-=dt;if(run.score>=nextOneUpScore){nextOneUpScore+=10000;if(run.lives<5){run.lives++;pLives[currentPlayer]=run.lives;setStatus("1UP! EXTRA RECOVERY BOT AWARDED");particle(px,py,1,45);fx(0);}}',
    'classic 1UP award'
)

# A used tool flashes briefly. The beam now visibly fires both ways and counts the sectors it clears.
replace_once(
    'toolCharges[selectedTool]--;switch(selectedTool)',
    'toolCharges[selectedTool]--;lastToolUsed=selectedTool;lastToolFlash=.70f;switch(selectedTool)',
    'recently used tool flash'
)
replace_once(
    'case TOOL_BEAM:for(i=0;i<GW;i++){grid[y][i].type=S_CLEAN;grid[y][i].repair=0;}run.score+=250;setStatus("DEFRAG BEAM: TRACK CLEANED");break;',
    'case TOOL_BEAM:{int cleaned=0;for(i=0;i<GW;i++){if(grid[y][i].type!=S_CLEAN)cleaned++;grid[y][i].type=S_CLEAN;grid[y][i].repair=0;}run.repairs+=cleaned;run.score+=250+cleaned*40;beamFxRow=y;beamFxTimer=.85f;particle(px,py,0,45);setStatus("DEFRAG BEAM: TRACK CLEANED");}break;',
    'animated defrag beam'
)

# Readable status notifications and a two-direction beam effect.
helpers = r'''
static void drawStatusBanner(HDC dc,const char*msg){
 int blink=((int)(GetTickCount64()/180)&1);fill(dc,205,606,550,38,RGB(3,10,15));outline(dc,205,606,550,38,blink?RGB(255,215,80):RGB(105,255,195),3);fill(dc,215,616,8,18,RGB(255,205,70));center(dc,614,18,RGB(245,245,220),msg);
}
static void drawBeamFx(HDC dc,int ox,int oy){
 float progress=clampf(1.0f-beamFxTimer/.85f,0,1);int cx=GX+(int)(px*CELL)+CELL/2+ox,cy=GY+beamFxRow*CELL+CELL/2+oy;int maxL=GW*CELL,reach=(int)(progress*maxL);int left=cx-reach,right=cx+reach,k;if(left<GX+ox)left=GX+ox;if(right>GX+GW*CELL+ox)right=GX+GW*CELL+ox;
 line(dc,cx,cy,left,cy,RGB(45,145,160),9);line(dc,cx,cy,right,cy,RGB(45,145,160),9);line(dc,cx,cy,left,cy,RGB(110,255,235),5);line(dc,cx,cy,right,cy,RGB(110,255,235),5);line(dc,cx,cy,left,cy,RGB(255,250,170),2);line(dc,cx,cy,right,cy,RGB(255,250,170),2);
 fill(dc,left-4,cy-7,8,14,RGB(255,245,145));fill(dc,right-4,cy-7,8,14,RGB(255,245,145));
 for(k=0;k<GW;k++){int sx=GX+k*CELL+CELL/2+ox;if(sx>=left&&sx<=right&&((k+(int)(beamFxTimer*30))&2)==0){line(dc,sx,cy-13,sx,cy+13,RGB(105,255,220),2);fill(dc,sx-2,cy-16,4,4,RGB(255,230,95));}}
}
'''
insert_at = s.index('static void drawGame(HDC dc)')
s = s[:insert_at] + helpers + s[insert_at:]

# Show the beam after the sectors, so the player sees it sweep across the entire recovered row.
replace_once(
    'drawSectorTile(dc,sx,sy,x,y,&grid[y][x]);}',
    'drawSectorTile(dc,sx,sy,x,y,&grid[y][x]);}if(beamFxTimer>0&&beamFxRow>=0)drawBeamFx(dc,ox,oy);',
    'beam renderer call'
)

# Full tool names, clear PRESS placement, no unexplained initial selected border.
toolbar = r'''static void drawToolBar(HDC dc){
 static const char*line1[]={"ANTIVIRUS","SECTOR","DEFRAG","BACKUP","OVERCLOCK","FIREWALL","EMERGENCY"};
 static const char*line2[]={"PULSE","LOCK","BEAM","RESTORE","","","REBOOT"};
 int i,j;char b[32];float wall=firewallRemaining();
 for(i=0;i<TOOL_COUNT;i++){int x=18+i*133,y=652,w=126,h=64;float rem=0,max=1;COLORREF edge=RGB(56,82,94),ink=toolCharges[i]>0?RGB(215,233,239):RGB(80,91,96);int nsz=(int)strlen(line1[i])>8?8:10;
  if(i==TOOL_LOCK&&sectorLock>0){rem=sectorLock;max=8;}if(i==TOOL_OVERCLOCK&&overclock>0){rem=overclock;max=10;}if(i==TOOL_FIREWALL&&wall>0){rem=wall;max=8;}
  if(rem>0)edge=RGB(80,255,215);else if(i==lastToolUsed&&lastToolFlash>0)edge=RGB(255,205,75);
  fill(dc,x+3,y+3,w,h,RGB(2,7,10));fill(dc,x,y,w,h,RGB(8,18,25));outline(dc,x,y,w,h,edge,2);
  txt(dc,x+7,y+2,8,RGB(170,185,192),"PRESS");
  fill(dc,x+5,y+14,32,32,toolCharges[i]>0?RGB(47,37,16):RGB(25,27,29));outline(dc,x+5,y+14,32,32,RGB(255,205,75),2);sprintf(b,"%d",i+1);txt(dc,x+13,y+15,24,RGB(255,225,115),b);
  drawToolIcon(dc,i,x+42,y+15,ink);txt(dc,x+70,y+5,nsz,ink,line1[i]);if(line2[i][0])txt(dc,x+70,y+17,10,ink,line2[i]);
  sprintf(b,"x%d",toolCharges[i]);txt(dc,x+72,y+31,18,toolCharges[i]>0?RGB(255,230,145):RGB(105,110,112),b);
  for(j=0;j<toolCharges[i]&&j<4;j++)fill(dc,x+42+j*8,y+50,6,6,RGB(105,255,195));
  if(rem>0){int bw=(int)((w-76)*clampf(rem/max,0,1));fill(dc,x+72,y+52,w-77,6,RGB(20,42,48));fill(dc,x+72,y+52,bw,6,rem<2?RGB(255,170,65):RGB(85,255,210));sprintf(b,"%.1fs",rem);txt(dc,x+92,y+42,10,RGB(205,255,235),b);}
 }
}'''
replace_function('static void drawToolBar(HDC dc)', toolbar)

# Replace difficult-to-read board text with an opaque notification banner.
s = s.replace('center(dc,638,18,RGB(255,225,100),"RED = standard damage. Repair all 12; no new damage will appear.");', 'drawStatusBanner(dc,"RED = standard damage. Repair all 12; no new damage will appear.");')
s = s.replace('center(dc,638,18,RGB(255,225,100),"ORANGE = fragmented. It keeps progress, but needs about twice as much repair time.");', 'drawStatusBanner(dc,"ORANGE = fragmented. Progress is saved, but repair takes about twice as long.");')
s = s.replace('center(dc,638,18,RGB(255,225,100),"PURPLE BUG TILE = repair it, then move away. Never touch the released moving bug.");', 'drawStatusBanner(dc,"PURPLE BUG TILE: repair it, then move away from the released bug.");')
s = s.replace('center(dc,638,18,RGB(255,225,100),statusLine);', 'drawStatusBanner(dc,statusLine);')

# Near-zero sectors are positive progress, while low time flashes as an urgent warning.
s = s.replace('fill(dc,610,8,315,86,RGB(22,18,10));', 'fill(dc,610,8,315,86,sectorsRemaining()<=3?RGB(6,27,22):RGB(22,18,10));')
s = s.replace('sectorsRemaining()<=3?RGB(255,90,70):RGB(255,190,80)', 'sectorsRemaining()<=3?RGB(80,245,170):RGB(255,190,80)')
s = s.replace('sectorsRemaining()<=3?RGB(255,105,75):RGB(255,205,90)', 'sectorsRemaining()<=3?RGB(105,255,195):RGB(255,205,90)')
s = s.replace('stageClock<20?RGB(255,85,75):RGB(200,190,255)', 'stageClock<20?(((int)(GetTickCount64()/220)&1)?RGB(255,65,55):RGB(95,25,25)):RGB(200,190,255)')
s = s.replace('stageClock<20?RGB(255,95,80):RGB(235,225,255)', 'stageClock<20?(((int)(GetTickCount64()/220)&1)?RGB(255,235,225):RGB(255,70,60)):RGB(235,225,255)')

# Put the upcoming extra-life milestone in the score panel.
replace_once(
    'sprintf(b,"%07d",run.score);txt(dc,220,39,30,RGB(225,242,250),b);',
    'sprintf(b,"%07d",run.score);txt(dc,220,35,30,RGB(225,242,250),b);sprintf(b,"NEXT 1UP %05d",nextOneUpScore);txt(dc,220,70,11,RGB(115,190,210),b);',
    'next 1UP HUD'
)

p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v1.9 HUD, toolbar, beam and 1UP update')
