from pathlib import Path

p = Path('bad_sector.c')
s = p.read_text(encoding='utf-8')

# Tool-guide state.
s = s.replace('static char statusLine[160]="SYSTEM READY"; static float statusTimer;',
              'static char statusLine[160]="SYSTEM READY"; static float statusTimer; static int toolGuide=0;')

# Larger computer and a true front-layer floppy insertion:
# body/drive first, floppy in front, then only the upper drive mask and slot lip cover it.
start = s.index('static void drawIntro(HDC dc)')
end = s.index('static void drawGame(HDC dc)', start)
intro = r'''static void drawIntro(HDC dc){float t=introTime;char b[120];
 int bodyX=35,bodyY=42,bodyW=890,bodyH=625;
 int screenX=100,screenY=92,screenW=760,screenH=345;
 int driveX=250,driveY=475,driveW=460,driveH=125;
 int slotX=310,slotY=520,slotW=340,slotH=18;
 /* Large computer body and screen. */
 fill(dc,bodyX,bodyY,bodyW,bodyH,RGB(29,35,44));outline(dc,bodyX,bodyY,bodyW,bodyH,RGB(135,150,160),5);
 fill(dc,screenX,screenY,screenW,screenH,RGB(3,8,12));outline(dc,screenX,screenY,screenW,screenH,RGB(65,84,96),4);
 /* Drive face exists behind the approaching disk. */
 fill(dc,driveX,driveY,driveW,driveH,RGB(45,53,63));outline(dc,driveX,driveY,driveW,driveH,RGB(110,125,135),4);
 fill(dc,680,555,20,20,t>2.35f&&((int)(t*7)&1)?RGB(75,245,170):RGB(35,62,58));
 if(t<2.9f){float q=t/2.9f;int diskY=(int)(720-q*330);
   /* Disk is drawn in FRONT of the computer and drive face. */
   drawFloppy(dc,405,diskY,150,150);
   /* Only the portion that has crossed above the slot is hidden inside the drive. */
   fill(dc,driveX+4,driveY+4,driveW-8,slotY-driveY-4,RGB(45,53,63));
   outline(dc,driveX,driveY,driveW,driveH,RGB(110,125,135),4);
   fill(dc,slotX,slotY,slotW,slotH,RGB(2,5,8));outline(dc,slotX,slotY,slotW,slotH,RGB(150,165,175),2);
   line(dc,slotX,slotY+slotH,slotX+slotW,slotY+slotH,RGB(185,195,202),3);
   center(dc,145,29,RGB(82,245,190),"INSERT DISK INTO DRIVE A:");
   center(dc,205,18,RGB(175,195,205),q<.54f?"WAITING FOR MEDIA...":q<.88f?"MEDIA ENTERING DRIVE...":"DISK LOCKED");
   if(q>.90f)center(dc,385,19,RGB(255,205,90),"CLICK - DRIVE A: READY");
 }else{
   fill(dc,slotX,slotY,slotW,slotH,RGB(2,5,8));outline(dc,slotX,slotY,slotW,slotH,RGB(150,165,175),2);
   if(t<5.0f){float q=(t-2.9f)/2.1f;
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
s = s[:start] + intro + s[end:]

# Direct-use number keys and a pausing tool guide.
old_controls = "if(pressed(VK_ESCAPE)){mode=M_PAUSE;return;}if(pressed('Q')){selectedTool=(selectedTool+TOOL_COUNT-1)%TOOL_COUNT;}if(pressed('E')){selectedTool=(selectedTool+1)%TOOL_COUNT;}for(i=0;i<TOOL_COUNT;i++)if(pressed('1'+i))selectedTool=i;if(pressed(VK_RETURN)||pressed('F'))useTool();"
new_controls = "if(pressed('T')){toolGuide=!toolGuide;return;}if(toolGuide){if(pressed(VK_ESCAPE)||pressed(VK_RETURN))toolGuide=0;return;}if(pressed(VK_ESCAPE)){mode=M_PAUSE;return;}if(pressed('Q')){selectedTool=(selectedTool+TOOL_COUNT-1)%TOOL_COUNT;}if(pressed('E')){selectedTool=(selectedTool+1)%TOOL_COUNT;}for(i=0;i<TOOL_COUNT;i++)if(pressed('1'+i)){selectedTool=i;useTool();}if(pressed(VK_RETURN)||pressed('F'))useTool();"
s = s.replace(old_controls, new_controls)

# Completion now remains on the board briefly, then advances to the next black mission briefing.
old_complete_update = "else if(mode==M_COMPLETE){completeTime+=dt;if(pressed(VK_RETURN)||pressed(VK_SPACE)){stageIndex=completedStage+1;run.level=stageIndex+1;stageSetup();mode=M_STORY;}}"
new_complete_update = "else if(mode==M_COMPLETE){completeTime+=dt;if(completeTime>=2.4f||(completeTime>=1.0f&&(pressed(VK_RETURN)||pressed(VK_SPACE)))){stageIndex=completedStage+1;run.level=stageIndex+1;stageSetup();mode=M_STORY;}}"
s = s.replace(old_complete_update, new_complete_update)

# Replace the gameplay HUD with larger score/time panels.
hud_start = s.index('/* HUD hierarchy:', s.index('static void drawGame(HDC dc)'))
grid_start = s.index('fill(dc,GX-6+ox', hud_start)
new_hud = r'''/* Large glanceable HUD panels. */
 fill(dc,35,8,155,86,RGB(9,20,27));outline(dc,35,8,155,86,run.lives<=1?RGB(255,80,80):RGB(95,245,190),3);
 txt(dc,50,15,14,RGB(145,170,180),"LIVES");sprintf(b,"%d",run.lives);txt(dc,50,34,38,run.lives<=1?RGB(255,85,85):RGB(105,255,195),b);
 fill(dc,205,8,230,86,RGB(8,18,25));outline(dc,205,8,230,86,RGB(90,180,230),3);
 txt(dc,220,15,14,RGB(145,180,205),"SCORE");sprintf(b,"%07d",run.score);txt(dc,220,39,30,RGB(225,242,250),b);
 fill(dc,450,8,145,86,RGB(15,17,24));outline(dc,450,8,145,86,stageClock<20?RGB(255,85,75):RGB(200,190,255),3);
 txt(dc,465,15,14,RGB(165,160,195),"TIME");sprintf(b,"%03d",(int)stageClock);txt(dc,465,36,34,stageClock<20?RGB(255,95,80):RGB(235,225,255),b);
 sprintf(b,"TRACK %02d/20",stageIndex+1);txt(dc,465,72,12,RGB(135,145,165),b);
 fill(dc,610,8,315,86,RGB(22,18,10));outline(dc,610,8,315,86,sectorsRemaining()<=3?RGB(255,90,70):RGB(255,190,80),3);
 txt(dc,625,15,14,RGB(205,170,105),"SECTORS LEFT");sprintf(b,"%d",sectorsRemaining());txt(dc,625,34,38,sectorsRemaining()<=3?RGB(255,105,75):RGB(255,205,90),b);
 sprintf(b,"COMBO x%d",run.combo);txt(dc,780,50,18,RGB(255,220,145),b);
 '''
s = s[:hud_start] + new_hud + s[grid_start:]

# Replace the footer with a visible numbered toolbar and clear activation wording.
old_footer = 'txt(dc,72,672,15,RGB(125,150,160),"MOVE WASD / ARROWS   REPAIR IS AUTOMATIC   1-7 USE TOOL   ESC PAUSE");'
new_footer = '''sprintf(b,"1 PULSE:%d   2 LOCK:%d   3 BEAM:%d   4 BACKUP:%d",toolCharges[0],toolCharges[1],toolCharges[2],toolCharges[3]);txt(dc,72,661,13,RGB(145,190,195),b);sprintf(b,"5 OVERCLOCK:%d   6 FIREWALL:%d   7 REBOOT:%d     T TOOL GUIDE",toolCharges[4],toolCharges[5],toolCharges[6]);txt(dc,72,681,13,RGB(145,190,195),b);'''
s = s.replace(old_footer, new_footer)

# Add the in-game strategy guide overlay.
end_marker = 'else if(statusTimer>0)center(dc,638,18,RGB(255,225,100),statusLine);}'
guide = '''else if(statusTimer>0)center(dc,638,18,RGB(255,225,100),statusLine);if(toolGuide){fill(dc,105,100,750,520,RGB(4,9,14));outline(dc,105,100,750,520,RGB(95,245,190),3);center(dc,120,31,RGB(95,245,190),"UTILITY GUIDE - GAME PAUSED");txt(dc,145,180,18,RGB(255,205,90),"1  ANTIVIRUS PULSE");txt(dc,415,180,16,RGB(200,215,225),"Destroys moving threats near the bot.");txt(dc,145,230,18,RGB(255,205,90),"2  SECTOR LOCK");txt(dc,415,230,16,RGB(200,215,225),"Temporarily stops corruption from spreading.");txt(dc,145,280,18,RGB(255,205,90),"3  DEFRAG BEAM");txt(dc,415,280,16,RGB(200,215,225),"Instantly cleans the entire current row.");txt(dc,145,330,18,RGB(255,205,90),"4  BACKUP RESTORE");txt(dc,415,330,16,RGB(200,215,225),"Repairs several random damaged sectors.");txt(dc,145,380,18,RGB(255,205,90),"5  OVERCLOCK");txt(dc,415,380,16,RGB(200,215,225),"Temporarily increases movement and repair speed.");txt(dc,145,430,18,RGB(255,205,90),"6  FIREWALL");txt(dc,415,430,16,RGB(200,215,225),"Places a temporary barrier around your position.");txt(dc,145,480,18,RGB(255,205,90),"7  EMERGENCY REBOOT");txt(dc,415,480,16,RGB(200,215,225),"Clears enemies, but damages five new sectors.");center(dc,545,17,RGB(175,195,205),"PRESS 1-7 TO USE A TOOL IMMEDIATELY");center(dc,580,16,RGB(235,240,245),"T / ENTER / ESC TO RETURN");}}'''
s = s.replace(end_marker, guide)

# Replace the separate completion screen with an animated overlay on the finished board.
branch_start = s.index('}else if(mode==M_COMPLETE){')
branch_end = s.index('}else if(mode==M_PLAY||mode==M_PAUSE){', branch_start)
complete_branch = r'''}else if(mode==M_COMPLETE){int k;drawGame(dc);fill(dc,150,205,660,300,RGB(5,12,18));outline(dc,150,205,660,300,((int)(completeTime*8)&1)?RGB(95,255,190):RGB(255,205,80),4);for(k=0;k<18;k++){int sx=175+((k*97+(int)(completeTime*190))%610),sy=225+((k*53+(int)(completeTime*110))%255);fill(dc,sx,sy,4+(k%3)*2,4+(k%3)*2,k%2?RGB(95,255,190):RGB(255,205,80));}center(dc,235,29,RGB(105,255,195),"TRACK RECOVERED!");sprintf(b,"%s COMPLETE",stages[completedStage].name);center(dc,285,34,RGB(235,245,245),b);sprintf(b,"BONUS +%d",stageBonus);center(dc,345,22,RGB(255,205,90),b);sprintf(b,"TOTAL SCORE %d",run.score);center(dc,380,22,RGB(255,205,90),b);center(dc,440,17,RGB(185,205,215),completeTime<1.0f?"RECOVERY VERIFIED...":"NEXT MISSION LOADING");if(completeTime>=1.0f)center(dc,470,14,RGB(135,155,170),"ENTER / SPACE TO CONTINUE NOW");'''
s = s[:branch_start] + complete_branch + s[branch_end:]

# Make infected-sector wording explicit.
s = s.replace('Purple. Finishing the repair releases a virus.',
              'Purple bug tile. Repair it, then move away: it releases a hostile moving bug.')
s = s.replace('PURPLE = infected. Completing it releases a virus.',
              'PURPLE BUG TILE = repair it, then move away. Never touch the released moving bug.')
s = s.replace('Infected sectors introduce the next threat, but corruption still cannot spread.',
              'Repair purple bug tiles, then move away. The released moving bug cannot be repaired.')

# Add a bug icon inside purple infected sectors.
needle = 'if(s->type==S_FRAGMENTED){line(dc,sx+7,sy+10,sx+26,sy+10,RGB(30,30,30),2);line(dc,sx+10,sy+22,sx+27,sy+22,RGB(30,30,30),2);}if(s->type==S_PROTECTED)'
replacement = '''if(s->type==S_FRAGMENTED){line(dc,sx+7,sy+10,sx+26,sy+10,RGB(30,30,30),2);line(dc,sx+10,sy+22,sx+27,sy+22,RGB(30,30,30),2);}if(s->type==S_INFECTED){fill(dc,sx+12,sy+10,10,13,RGB(245,205,255));fill(dc,sx+14,sy+7,6,5,RGB(245,205,255));line(dc,sx+12,sy+12,sx+7,sy+9,RGB(245,205,255),2);line(dc,sx+22,sy+12,sx+27,sy+9,RGB(245,205,255),2);line(dc,sx+12,sy+19,sx+7,sy+23,RGB(245,205,255),2);line(dc,sx+22,sy+19,sx+27,sy+23,RGB(245,205,255),2);}if(s->type==S_PROTECTED)'''
s = s.replace(needle, replacement)

old = 'if(nt==S_INFECTED){fill(dc,204,330,10,10,RGB(245,180,255));fill(dc,238,358,9,9,RGB(245,180,255));}'
new = '''if(nt==S_INFECTED){fill(dc,214,333,24,30,RGB(245,205,255));fill(dc,219,324,14,11,RGB(245,205,255));line(dc,214,338,200,330,RGB(245,205,255),4);line(dc,238,338,252,330,RGB(245,205,255),4);line(dc,214,355,200,366,RGB(245,205,255),4);line(dc,238,355,252,366,RGB(245,205,255),4);}'''
s = s.replace(old, new)

p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v1.4 gameplay clarity patch')