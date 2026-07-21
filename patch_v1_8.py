from pathlib import Path

p = Path('bad_sector.c')
s = p.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Could not find {label}')
    s = s.replace(old, new, 1)


# Add a dedicated death state so the board can remain visible during the failure sequence.
replace_once(
    'M_SETTINGS, M_INITIALS } Mode;',
    'M_SETTINGS, M_INITIALS, M_DYING } Mode;',
    'dying mode enum'
)
replace_once(
    'static float px,py,invuln,spawnTimer,spreadTimer,stageClock,stageIntro,introTime,completeTime,screenShake,magnetPulse,overclock,sectorLock,firewallTimer,beamFxTimer,lastToolFlash;',
    'static float px,py,invuln,spawnTimer,spreadTimer,stageClock,stageIntro,introTime,completeTime,screenShake,magnetPulse,overclock,sectorLock,firewallTimer,beamFxTimer,lastToolFlash,deathTimer;',
    'death animation timer'
)
replace_once(
    'static int beamFxRow=-1,lastToolUsed=-1,nextOneUpScore=5000;',
    'static int beamFxRow=-1,lastToolUsed=-1,nextOneUpScore=5000,gameOverHasHighScore=0;',
    'game-over score state'
)
replace_once(
    'overclock=0;sectorLock=0;firewallTimer=0;beamFxTimer=0;beamFxRow=-1;lastToolUsed=-1;lastToolFlash=0;',
    'overclock=0;sectorLock=0;firewallTimer=0;beamFxTimer=0;beamFxRow=-1;lastToolUsed=-1;lastToolFlash=0;deathTimer=0;gameOverHasHighScore=0;',
    'death state reset'
)

# The final life now starts an on-board animation instead of immediately changing screens.
replace_once(
    'if(submitScore(run.score+pScores[1-currentPlayer],M_GAMEOVER))mode=M_INITIALS;else mode=M_GAMEOVER;stopMusic();',
    'deathTimer=0;gameOverHasHighScore=0;mode=M_DYING;setStatus("RECOVERY BOT OFFLINE");',
    'final-death transition'
)

# Keep similarly important tool names at a consistent readable size.
replace_once(
    'static const char*line1[]={"ANTIVIRUS","SECTOR","DEFRAG","BACKUP","OVERCLOCK","FIREWALL","EMERGENCY"};',
    'static const char*line1[]={"A-VIRUS","SECTOR","DEFRAG","BACKUP","OVER","FIRE","EMERGENCY"};',
    'tool label first lines'
)
replace_once(
    'static const char*line2[]={"PULSE","LOCK","BEAM","RESTORE","","","REBOOT"};',
    'static const char*line2[]={"PULSE","LOCK","BEAM","RESTORE","CLOCK","WALL","REBOOT"};',
    'tool label second lines'
)
replace_once(
    ';int nsz=(int)strlen(line1[i])>8?8:10;',
    ';',
    'variable-size tool text'
)
replace_once(
    'txt(dc,x+70,y+5,nsz,ink,line1[i]);',
    'txt(dc,x+70,y+5,10,ink,line1[i]);',
    'uniform tool text size'
)

# Do not leave a normal, still-repairing bot underneath the death animation or failure overlay.
s = s.replace(
    'repairing=grid[ry][rx].type!=S_CLEAN',
    'repairing=(mode==M_PLAY||mode==M_PAUSE)&&grid[ry][rx].type!=S_CLEAN'
)
replace_once(
    'if(firewallTimer>0)drawFirewallShield(dc,sx,sy,firewallTimer);if(invuln<=0||((int)(invuln*14)&1)==0)drawBot(dc,sx,sy,repairing);',
    'if(mode!=M_DYING&&mode!=M_GAMEOVER){if(firewallTimer>0)drawFirewallShield(dc,sx,sy,firewallTimer);if(invuln<=0||((int)(invuln*14)&1)==0)drawBot(dc,sx,sy,repairing);}',
    'hide bot during final failure'
)

# Procedural collapse: warning flash, expanding shock rings, sparks and falling bot fragments.
death_fx = r'''
static void drawDeathFx(HDC dc){
 float p=clampf(deathTimer/1.80f,0,1),burst=clampf(p/.45f,0,1);int cx=GX+(int)(px*CELL)+CELL/2,cy=GY+(int)(py*CELL)+CELL/2,k;COLORREF red=((int)(deathTimer*18)&1)?RGB(255,65,65):RGB(255,205,95);
 if(p<.32f){int r=10+(int)(p*95);outline(dc,cx-r,cy-r,r*2,r*2,red,3);outline(dc,cx-r/2,cy-r/2,r,r,RGB(245,255,235),2);line(dc,cx-22,cy,cx+22,cy,RGB(255,245,210),4);line(dc,cx,cy-22,cx,cy+22,RGB(255,245,210),4);}
 for(k=0;k<14;k++){float a=k*.73f+.25f,v=22+(k%5)*7;int x=cx+(int)(cos(a)*v*burst),y=cy+(int)(sin(a)*v*burst+p*p*(28+(k%4)*8));COLORREF c=(k%3)==0?RGB(105,255,205):(k%3)==1?RGB(255,220,75):RGB(255,75,70);fill(dc,x-2,y-2,5+(k&1)*2,5,c);if((k&1)==0)line(dc,x,y,x-(int)(cos(a)*10),y-(int)(sin(a)*10),c,2);}
 if(p>.22f){int drop=(int)((p-.22f)*72);fill(dc,cx-14,cy-7+drop,10,8,RGB(55,82,88));fill(dc,cx+5,cy-10+drop,12,10,RGB(70,235,190));fill(dc,cx-4,cy+5+drop,9,7,RGB(205,225,230));}
 if(p>.58f){outline(dc,cx-27,cy-27,54,54,RGB(255,75,70),3);line(dc,cx-18,cy-18,cx+18,cy+18,RGB(255,75,70),4);line(dc,cx+18,cy-18,cx-18,cy+18,RGB(255,75,70),4);drawStatusBanner(dc,"RECOVERY BOT SIGNAL LOST");}
}
'''
insert_at = s.index('static void draw(void)')
s = s[:insert_at] + death_fx + s[insert_at:]

# Draw the death sequence over the unchanged board.
replace_once(
    '}else if(mode==M_PLAY||mode==M_PAUSE){',
    '}else if(mode==M_PLAY||mode==M_PAUSE||mode==M_DYING){',
    'dying draw route'
)
replace_once(
    'drawGame(dc);if(mode==M_PAUSE)',
    'drawGame(dc);if(mode==M_DYING)drawDeathFx(dc);if(mode==M_PAUSE)',
    'death effect draw call'
)

# After the animation, freeze the same board and present DISK FAILURE in a centered overlay.
draw_start = s.index('static void draw(void)')
gameover_start = s.index('}else if(mode==M_GAMEOVER){', draw_start)
gameover_end = s.index('}else if(mode==M_VICTORY){', gameover_start)
gameover = r'''}else if(mode==M_GAMEOVER){drawGame(dc);
 fill(dc,177,165,606,365,RGB(3,8,12));outline(dc,177,165,606,365,RGB(255,75,75),4);
 fill(dc,195,185,570,7,RGB(92,20,27));fill(dc,195,504,570,7,RGB(92,20,27));
 center(dc,210,48,RGB(255,75,80),"DISK FAILURE");
 center(dc,278,20,RGB(255,210,105),"RECOVERY BOT DESTROYED");
 sprintf(b,"FINAL SCORE %d",run.score+pScores[1-currentPlayer]);center(dc,326,29,RGB(240,245,248),b);
 center(dc,380,18,RGB(175,195,205),"The board remains exactly where the final read error occurred.");
 center(dc,418,18,RGB(175,195,205),gameOverHasHighScore?"NEW HIGH SCORE DETECTED":"No recovery bots remain.");
 center(dc,474,21,RGB(105,255,195),gameOverHasHighScore?"ENTER TO RECORD YOUR TAG":"ENTER TO RETURN TO BOOT MENU");'''
s = s[:gameover_start] + gameover + s[gameover_end:]

replace_once(
    'updateEnemies(dt);if(run.repairs>=repairedGoal||damagedSectorCount()==0)completeStage();',
    'updateEnemies(dt);if(mode==M_DYING)return;if(run.repairs>=repairedGoal||damagedSectorCount()==0)completeStage();',
    'prevent completion after final death'
)

# Death animation finishes first; score handling waits behind the failure overlay.
replace_once(
    'else if(mode==M_PLAY)updateWorld(dt);else if(mode==M_COMPLETE)',
    'else if(mode==M_PLAY)updateWorld(dt);else if(mode==M_DYING){deathTimer+=dt;if(deathTimer>=1.80f){gameOverHasHighScore=submitScore(run.score+pScores[1-currentPlayer],M_TITLE);statusTimer=0;mode=M_GAMEOVER;stopMusic();}}else if(mode==M_COMPLETE)',
    'dying update route'
)
replace_once(
    'else if(mode==M_GAMEOVER||mode==M_VICTORY){if(pressed(VK_RETURN)){mode=M_TITLE;startMusic(0);}}',
    'else if(mode==M_GAMEOVER){if(pressed(VK_RETURN)){startMusic(0);if(gameOverHasHighScore)mode=M_INITIALS;else mode=M_TITLE;}}else if(mode==M_VICTORY){if(pressed(VK_RETURN)){mode=M_TITLE;startMusic(0);}}',
    'game-over confirmation flow'
)

p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v2.0 tool labels and death sequence')
