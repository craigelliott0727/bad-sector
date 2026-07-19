from pathlib import Path
import re

p = Path('bad_sector.c')
s = p.read_text(encoding='utf-8')

# Modes and high-score state
s = s.replace('M_GAMEOVER, M_VICTORY, M_SCORES, M_SETTINGS } Mode;',
              'M_GAMEOVER, M_VICTORY, M_SCORES, M_SETTINGS, M_INITIALS } Mode;')
s = s.replace('static int repairedGoal, stageIndex, completedStage, stageBonus, selectedTool, toolCharges[TOOL_COUNT], highScores[5], achievements, challengeMode;',
              'static int repairedGoal, stageIndex, completedStage, stageBonus, selectedTool, toolCharges[TOOL_COUNT], highScores[5], achievements, challengeMode;\nstatic char highNames[5][4]={{\'A\',\'A\',\'A\',0},{\'A\',\'A\',\'A\',0},{\'A\',\'A\',\'A\',0},{\'A\',\'A\',\'A\',0},{\'A\',\'A\',\'A\',0}}; static int initialsSlot=-1,initialsPos=0; static Mode initialsReturnMode=M_GAMEOVER;')

# Save/load initials while remaining tolerant of older save files.
s = s.replace('fwrite(highScores,sizeof(highScores),1,f);fwrite(&achievements',
              'fwrite(highScores,sizeof(highScores),1,f);fwrite(highNames,sizeof(highNames),1,f);fwrite(&achievements')
s = s.replace('fread(highScores,sizeof(highScores),1,f);fread(&achievements',
              'fread(highScores,sizeof(highScores),1,f);if(fread(highNames,sizeof(highNames),1,f)!=1){int z;for(z=0;z<5;z++)lstrcpyA(highNames[z],"AAA");}fread(&achievements')

old_submit = 'static void submitScore(int s){int i,j;for(i=0;i<5;i++)if(s>highScores[i]){for(j=4;j>i;j--)highScores[j]=highScores[j-1];highScores[i]=s;break;}saveData();}'
new_submit = '''static int submitScore(int s,Mode after){int i,j;for(i=0;i<5;i++)if(s>highScores[i]){for(j=4;j>i;j--){highScores[j]=highScores[j-1];lstrcpyA(highNames[j],highNames[j-1]);}highScores[i]=s;lstrcpyA(highNames[i],"AAA");initialsSlot=i;initialsPos=0;initialsReturnMode=after;return 1;}saveData();return 0;}'''
s = s.replace(old_submit, new_submit)

# Score-flow callers
s = s.replace('submitScore(run.score+pScores[1-currentPlayer]);mode=M_GAMEOVER;stopMusic();',
              'if(submitScore(run.score+pScores[1-currentPlayer],M_GAMEOVER))mode=M_INITIALS;else mode=M_GAMEOVER;stopMusic();')
s = s.replace('submitScore(run.score);mode=M_VICTORY;stopMusic();saveData();return;',
              'if(submitScore(run.score,M_VICTORY))mode=M_INITIALS;else mode=M_VICTORY;stopMusic();saveData();return;')
s = s.replace('submitScore(run.score+pScores[1-currentPlayer]);mode=M_VICTORY;stopMusic();saveData();return;',
              'if(submitScore(run.score+pScores[1-currentPlayer],M_VICTORY))mode=M_INITIALS;else mode=M_VICTORY;stopMusic();saveData();return;')

# Automatic repair: simply standing on a damaged sector repairs it.
s = s.replace('if(keys[VK_SPACE])repairCell(dt);', 'repairCell(dt);')
s = s.replace('repairing=keys[VK_SPACE]&&grid[ry][rx].type!=S_CLEAN', 'repairing=grid[ry][rx].type!=S_CLEAN')
s = s.replace('Standard damage. Hold SPACE for one second.', 'Standard damage. Move onto it to repair automatically.')
s = s.replace('MOVE WASD/ARROWS   HOLD SPACE REPAIR   1-7 USE TOOL   ESC PAUSE',
              'MOVE WASD / ARROWS   REPAIR IS AUTOMATIC   1-7 USE TOOL   ESC PAUSE')

# Viruses hurt immediately on contact and are visually distinct bugs floating above the grid.
s = s.replace('if(dist2(px,py,e->x,e->y)<.42f)', 'if(dist2(px,py,e->x,e->y)<.72f)')
old_enemy = 'if(e->type==E_MAGNET)drawMagnet(dc,sx+3,sy+1,7,c);else{fill(dc,sx+6,sy+6,22,22,c);outline(dc,sx+5,sy+5,24,24,RGB(25,10,20),2);fill(dc,sx+10,sy+11,4,4,RGB(15,15,20));fill(dc,sx+20,sy+11,4,4,RGB(15,15,20));if(e->type==E_WORM)line(dc,sx+5,sy+29,sx+28,sy+29,c,4);}'
new_enemy = '''if(e->type==E_MAGNET)drawMagnet(dc,sx+3,sy+1,7,c);else if(e->type==E_VIRUS){int bob=(int)(sin(e->timer*8)*2);fill(dc,sx+10,sy+9+bob,14,17,c);outline(dc,sx+9,sy+8+bob,16,19,RGB(20,8,14),2);fill(dc,sx+12,sy+5+bob,10,6,c);line(dc,sx+11,sy+7+bob,sx+6,sy+3+bob,c,2);line(dc,sx+22,sy+7+bob,sx+27,sy+3+bob,c,2);line(dc,sx+10,sy+13+bob,sx+4,sy+10+bob,c,2);line(dc,sx+10,sy+18+bob,sx+4,sy+21+bob,c,2);line(dc,sx+24,sy+13+bob,sx+30,sy+10+bob,c,2);line(dc,sx+24,sy+18+bob,sx+30,sy+21+bob,c,2);fill(dc,sx+13,sy+11+bob,3,3,RGB(255,235,120));fill(dc,sx+19,sy+11+bob,3,3,RGB(255,235,120));}else{fill(dc,sx+6,sy+6,22,22,c);outline(dc,sx+5,sy+5,24,24,RGB(25,10,20),2);if(e->type==E_WORM)line(dc,sx+5,sy+29,sx+28,sy+29,c,4);}'''
s = s.replace(old_enemy, new_enemy)

s = s.replace('The disk starts with exactly 12 damaged sectors. No new damage will appear.',
              'Repair starts automatically. A red BUG is a virus: avoid contact or use Antivirus Pulse.')
s = s.replace('RED = standard damage. Repair all 12; no new damage will appear.',
              'SECTORS stay in the grid. Moving red BUGS are viruses - touching one costs a life.')

start = s.index('static void drawIntro(HDC dc)')
end = s.index('static void drawGame(HDC dc)', start)
intro = r'''static void drawIntro(HDC dc){float t=introTime;float q=t<2.6f?t/2.6f:1.0f;int diskX=(int)(760-q*335),diskY=300;char b[120];
 fill(dc,100,145,520,405,RGB(29,35,44));outline(dc,100,145,520,405,RGB(135,150,160),4);
 fill(dc,140,185,440,195,RGB(3,8,12));outline(dc,140,185,440,195,RGB(65,84,96),3);
 fill(dc,310,416,250,42,RGB(3,6,9));outline(dc,310,416,250,42,RGB(105,120,130),3);
 fill(dc,520,475,17,17,t>2.4f&&((int)(t*6)&1)?RGB(75,245,170):RGB(40,58,62));
 if(t<2.6f){center(dc,67,28,RGB(82,245,190),"INSERTING DISK INTO DRIVE A:");if(q<.80f)drawFloppy(dc,diskX,diskY,150,150);else{int shown=(int)(150*(1-(q-.80f)/.20f));if(shown>0)drawFloppy(dc,425,diskY,shown,150);fill(dc,425,416,135,39,RGB(42,52,62));}}
 else if(t<4.8f){center(dc,220,23,RGB(82,245,190),"READING DRIVE A:");sprintf(b,"SCANNING TRACKS%.*s",((int)(t*4))%4,"...");center(dc,270,20,RGB(205,220,228),b);fill(dc,190,325,580,18,RGB(20,38,45));fill(dc,190,325,(int)(580*((t-2.6f)/2.2f)),18,RGB(75,225,175));}
 else{center(dc,205,24,RGB(255,90,80),"DISK READ ERROR");center(dc,260,20,RGB(235,240,245),"12 UNREADABLE BOOT SECTORS DETECTED");center(dc,305,18,RGB(170,195,205),"The disk cannot start until the damage is repaired.");fill(dc,235,365,490,110,RGB(8,18,24));outline(dc,235,365,490,110,RGB(255,190,80),2);center(dc,385,22,RGB(255,205,95),"LAUNCH BAD SECTOR RECOVERY UTILITY?");center(dc,430,21,RGB(105,255,195),"ENTER - REPAIR DISK");center(dc,465,17,RGB(150,170,180),"ESC - RETURN TO MENU");}
}
'''
s = s[:start] + intro + s[end:]

old_intro_update = "else if(mode==M_INTRO){introTime+=dt;if(pressed(VK_SPACE)||pressed(VK_ESCAPE)||pressed(VK_RETURN)||introTime>=9.2f)mode=M_STORY;}"
new_intro_update = "else if(mode==M_INTRO){introTime+=dt;if(introTime>=4.8f&&pressed(VK_RETURN))mode=M_STORY;else if(pressed(VK_ESCAPE))mode=M_TITLE;}"
s = s.replace(old_intro_update, new_intro_update)

needle = "else if(mode==M_SCORES){if(pressed(VK_ESCAPE)||pressed(VK_RETURN))mode=M_TITLE;}"
replacement = "else if(mode==M_INITIALS){char*c=&highNames[initialsSlot][initialsPos];if(pressed(VK_UP)||pressed('W')){*c=(*c>='A'&&*c<'Z')?*c+1:'A';}if(pressed(VK_DOWN)||pressed('S')){*c=(*c>'A'&&*c<='Z')?*c-1:'Z';}if(pressed(VK_LEFT)||pressed('A')){if(initialsPos>0)initialsPos--;}if(pressed(VK_RIGHT)||pressed('D')||pressed(VK_RETURN)||pressed(VK_SPACE)){if(initialsPos<2)initialsPos++;else{saveData();mode=initialsReturnMode;}}if(pressed(VK_BACK)&&initialsPos>0)initialsPos--;}else if(mode==M_SCORES){if(pressed(VK_ESCAPE)||pressed(VK_RETURN))mode=M_TITLE;}"
s = s.replace(needle, replacement)

s = s.replace('sprintf(b,"%d.  %08d",i+1,highScores[i]);', 'sprintf(b,"%d.  %s   %08d",i+1,highNames[i],highScores[i]);')
insert_at = s.rindex('}else if(mode==M_SCORES){')
initials_draw = '''}else if(mode==M_INITIALS){int k;center(dc,75,34,RGB(105,255,195),"NEW HIGH SCORE");sprintf(b,"SCORE %08d",highScores[initialsSlot]);center(dc,145,24,RGB(255,205,90),b);center(dc,205,18,RGB(175,195,205),"WRITE YOUR INITIALS ON THE DISK LABEL");drawFloppy(dc,300,260,360,330);fill(dc,350,440,260,92,RGB(225,226,215));outline(dc,350,440,260,92,RGB(35,40,45),2);for(k=0;k<3;k++){char n[2]={highNames[initialsSlot][k],0};if(k==initialsPos)outline(dc,382+k*70,452,55,62,RGB(255,95,75),4);txt(dc,394+k*70,458,44,RGB(20,28,34),n);}center(dc,600,17,RGB(175,195,205),"UP/DOWN CHANGE LETTER   LEFT/RIGHT SELECT");center(dc,632,18,RGB(235,240,245),"ENTER CONFIRMS");}'''
s = s[:insert_at] + initials_draw + s[insert_at+1:]

p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v1.0 patch')