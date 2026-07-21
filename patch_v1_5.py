from pathlib import Path

p = Path('bad_sector.c')
s = p.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Could not find {label}')
    s = s.replace(old, new, 1)


# Mobile firewall state: this is a shield attached to the repair bot, not a static wall.
replace_once(
    'static float px,py,invuln,spawnTimer,spreadTimer,stageClock,stageIntro,introTime,completeTime,screenShake,magnetPulse,overclock,sectorLock;',
    'static float px,py,invuln,spawnTimer,spreadTimer,stageClock,stageIntro,introTime,completeTime,screenShake,magnetPulse,overclock,sectorLock,firewallTimer;',
    'global timed-tool state'
)
replace_once('overclock=0;sectorLock=0;', 'overclock=0;sectorLock=0;firewallTimer=0;', 'stage timer reset')
replace_once(
    'case TOOL_FIREWALL:addWall(x,y);if(x>0)addWall(x-1,y);if(x<GW-1)addWall(x+1,y);setStatus("FIREWALL DEPLOYED");break;',
    'case TOOL_FIREWALL:firewallTimer=8.0f;particle(px,py,0,30);setStatus("MOBILE FIREWALL ENABLED");break;',
    'firewall activation'
)
replace_once('if(sectorLock>0)sectorLock-=dt;', 'if(sectorLock>0)sectorLock-=dt;if(firewallTimer>0)firewallTimer-=dt;', 'firewall countdown')
replace_once(
    'if(wallAt((int)(e->x+.5f),(int)(e->y+.5f))){e->vx=-e->vx;e->vy=-e->vy;e->x+=e->vx*.2f;e->y+=e->vy*.2f;}if(dist2(px,py,e->x,e->y)<.72f)',
    'if(wallAt((int)(e->x+.5f),(int)(e->y+.5f))){e->vx=-e->vx;e->vy=-e->vy;e->x+=e->vx*.2f;e->y+=e->vy*.2f;}if(firewallTimer>0&&dist2(px,py,e->x,e->y)<2.35f){if(e->type==E_MAGNET){e->vx=-e->vx*1.4f;e->vy=-e->vy*1.4f;e->x+=e->vx*.35f;e->y+=e->vy*.35f;}else{killEnemy(i,60);continue;}}if(dist2(px,py,e->x,e->y)<.72f)',
    'mobile firewall enemy collision'
)

# Replace the small procedural sprites with more dimensional versions.
magnet_start = s.index('static void drawMagnet(HDC dc')
bot_start = s.index('static void drawBot(HDC dc', magnet_start)
magnet = r'''static void drawMagnet(HDC dc,int x,int y,int scale,COLORREF c){
 int w=scale*3,h=scale*3;
 fill(dc,x+2,y+3,w,h,RGB(18,24,31));
 fill(dc,x,y,scale,scale*2,c);fill(dc,x+scale*2,y,scale,scale*2,c);fill(dc,x,y+scale*2,scale*3,scale,c);
 fill(dc,x+2,y+2,scale-3,scale*2-3,RGB(255,95,100));fill(dc,x+scale*2+2,y+2,scale-3,scale*2-3,RGB(255,95,100));
 fill(dc,x,y,scale,scale/2,RGB(235,240,244));fill(dc,x+scale*2,y,scale,scale/2,RGB(235,240,244));
 fill(dc,x+scale,y+scale/2,scale,scale*2,RGB(5,11,16));
 line(dc,x+scale/2,y+scale*2,x+scale*5/2,y+scale*2,RGB(120,25,35),2);
}
'''
s = s[:magnet_start] + magnet + s[bot_start:]

bot_start = s.index('static void drawBot(HDC dc')
floppy_start = s.index('static void drawFloppy(HDC dc', bot_start)
bot = r'''static void drawBot(HDC dc,int x,int y,int repairing){int blink=((int)(GetTickCount64()/180)&7)==0;
 /* shadow, treads and articulated arms */
 fill(dc,x+5,y+29,25,3,RGB(5,15,20));
 fill(dc,x+3,y+23,8,7,RGB(70,88,98));fill(dc,x+24,y+23,8,7,RGB(70,88,98));
 fill(dc,x+4,y+25,6,3,RGB(145,165,174));fill(dc,x+25,y+25,6,3,RGB(145,165,174));
 line(dc,x+7,y+14,x+2,y+19,RGB(130,155,165),3);line(dc,x+28,y+14,x+33,y+19,RGB(130,155,165),3);
 /* body shell and illuminated face */
 fill(dc,x+7,y+7,22,19,RGB(20,55,58));outline(dc,x+6,y+6,24,21,RGB(225,255,247),2);
 fill(dc,x+9,y+9,18,14,RGB(74,238,191));fill(dc,x+11,y+11,14,9,RGB(103,255,211));
 fill(dc,x+12,y+13,4,blink?1:4,RGB(5,35,33));fill(dc,x+21,y+13,4,blink?1:4,RGB(5,35,33));
 line(dc,x+15,y+20,x+22,y+20,RGB(10,75,66),1);
 /* antenna and status lamp */
 line(dc,x+18,y+6,x+18,y+1,RGB(215,225,230),2);fill(dc,x+16,y,5,4,repairing?RGB(255,224,80):RGB(95,215,255));
 if(repairing){line(dc,x+18,y+27,x+18,y+35,RGB(110,255,220),3);line(dc,x+15,y+33,x+21,y+33,RGB(255,245,150),3);fill(dc,x+12,y+31,3,3,RGB(255,220,70));fill(dc,x+23,y+34,3,3,RGB(255,220,70));}
}
'''
s = s[:bot_start] + bot + s[floppy_start:]

# Richer floppy used by the title, intro, and high-score screen.
floppy_start = s.index('static void drawFloppy(HDC dc')
intro_start = s.index('static void drawIntro(HDC dc)', floppy_start)
floppy = r'''static void drawFloppy(HDC dc,int x,int y,int w,int h){
 int lx=x+w*16/100,ly=y+h*39/100,lw=w*68/100,lh=h*35/100;
 /* drop shadow and layered plastic shell */
 fill(dc,x+7,y+8,w,h,RGB(10,16,22));
 fill(dc,x,y,w,h,RGB(48,59,73));outline(dc,x,y,w,h,RGB(190,203,212),3);
 fill(dc,x+5,y+5,w-10,h-10,RGB(61,73,88));
 line(dc,x+5,y+5,x+w-6,y+5,RGB(112,129,143),2);line(dc,x+5,y+5,x+5,y+h-6,RGB(112,129,143),2);
 line(dc,x+6,y+h-6,x+w-6,y+h-6,RGB(27,35,45),3);line(dc,x+w-6,y+6,x+w-6,y+h-6,RGB(27,35,45),3);
 /* shutter with rails and reflected highlight */
 fill(dc,x+w*24/100,y+h*5/100,w*52/100,h*29/100,RGB(15,22,29));outline(dc,x+w*24/100,y+h*5/100,w*52/100,h*29/100,RGB(102,116,127),2);
 fill(dc,x+w*29/100,y+h*7/100,w*23/100,h*23/100,RGB(158,171,181));
 fill(dc,x+w*31/100,y+h*8/100,w*4/100,h*21/100,RGB(207,216,222));
 line(dc,x+w*56/100,y+h*7/100,x+w*56/100,y+h*31/100,RGB(82,94,104),2);
 line(dc,x+w*60/100,y+h*7/100,x+w*60/100,y+h*31/100,RGB(82,94,104),1);
 /* writable label with stripe and ruled lines */
 fill(dc,lx,ly,lw,lh,RGB(235,234,221));outline(dc,lx,ly,lw,lh,RGB(105,110,111),2);
 fill(dc,lx,ly,lw,lh*12/100,RGB(82,220,183));
 line(dc,lx+10,ly+lh*38/100,lx+lw-10,ly+lh*38/100,RGB(180,182,176),1);
 line(dc,lx+10,ly+lh*66/100,lx+lw-10,ly+lh*66/100,RGB(180,182,176),1);
 /* hub recess, write-protect window and molded details */
 fill(dc,x+w*38/100,y+h*82/100,w*24/100,h*12/100,RGB(16,22,29));outline(dc,x+w*38/100,y+h*82/100,w*24/100,h*12/100,RGB(92,104,114),2);
 fill(dc,x+w*78/100,y+h*81/100,w*10/100,h*11/100,RGB(13,19,26));outline(dc,x+w*78/100,y+h*81/100,w*10/100,h*11/100,RGB(125,137,146),1);
 fill(dc,x+w*7/100,y+h*8/100,4,4,RGB(25,32,40));fill(dc,x+w*90/100,y+h*8/100,4,4,RGB(25,32,40));
 line(dc,x+w*8/100,y+h*95/100,x+w*24/100,y+h*95/100,RGB(94,108,119),2);line(dc,x+w*76/100,y+h*95/100,x+w*92/100,y+h*95/100,RGB(94,108,119),2);
}
'''
s = s[:floppy_start] + floppy + s[intro_start:]

# New board tile, enemy, shield, and toolbar renderers.
helpers = r'''static void drawSectorTile(HDC dc,int sx,int sy,int gx,int gy,Sector*s){COLORREF c=sectorColor(s->type,s->timer);int pulse=((int)(GetTickCount64()/120)+gx+gy)&3;
 fill(dc,sx+2,sy+3,CELL-3,CELL-3,RGB(5,17,23));
 fill(dc,sx+1,sy+1,CELL-3,CELL-3,c);
 line(dc,sx+2,sy+2,sx+CELL-4,sy+2,RGB(78,126,135),1);line(dc,sx+2,sy+2,sx+2,sy+CELL-4,RGB(78,126,135),1);
 line(dc,sx+3,sy+CELL-3,sx+CELL-3,sy+CELL-3,RGB(3,16,22),2);line(dc,sx+CELL-3,sy+3,sx+CELL-3,sy+CELL-3,RGB(3,16,22),2);
 if(s->type==S_CLEAN){if(((gx*3+gy*5)&3)==0){fill(dc,sx+9,sy+9,4,4,RGB(45,112,117));line(dc,sx+13,sy+11,sx+25,sy+11,RGB(35,80,88),1);line(dc,sx+25,sy+11,sx+25,sy+22,RGB(35,80,88),1);}if(pulse==0)fill(dc,sx+26,sy+26,3,3,RGB(55,135,136));return;}
 outline(dc,sx+5,sy+5,24,22,RGB(255,238,190),1);
 if(s->type==S_CORRUPT){line(dc,sx+9,sy+8,sx+24,sy+24,RGB(72,12,22),3);line(dc,sx+24,sy+8,sx+11,sy+24,RGB(72,12,22),2);}
 else if(s->type==S_FRAGMENTED){fill(dc,sx+8,sy+8,18,4,RGB(75,40,20));fill(dc,sx+12,sy+15,14,4,RGB(75,40,20));fill(dc,sx+8,sy+22,11,3,RGB(75,40,20));}
 else if(s->type==S_INFECTED){fill(dc,sx+12,sy+10,10,13,RGB(35,10,45));fill(dc,sx+14,sy+7,6,5,RGB(35,10,45));line(dc,sx+12,sy+12,sx+7,sy+9,RGB(35,10,45),2);line(dc,sx+22,sy+12,sx+27,sy+9,RGB(35,10,45),2);line(dc,sx+12,sy+19,sx+7,sy+23,RGB(35,10,45),2);line(dc,sx+22,sy+19,sx+27,sy+23,RGB(35,10,45),2);fill(dc,sx+14,sy+12,2,2,RGB(255,225,90));fill(dc,sx+19,sy+12,2,2,RGB(255,225,90));}
 else if(s->type==S_ENCRYPTED){outline(dc,sx+10,sy+14,14,11,RGB(225,255,235),2);outline(dc,sx+13,sy+8,8,10,RGB(225,255,235),2);fill(dc,sx+16,sy+18,3,5,RGB(225,255,235));}
 else if(s->type==S_UNSTABLE){line(dc,sx+19,sy+7,sx+11,sy+18,RGB(75,55,5),4);line(dc,sx+11,sy+18,sx+18,sy+18,RGB(75,55,5),4);line(dc,sx+18,sy+18,sx+14,sy+27,RGB(75,55,5),4);line(dc,sx+14,sy+27,sx+25,sy+14,RGB(75,55,5),4);}
 else if(s->type==S_PROTECTED){outline(dc,sx+9,sy+8,16,18,RGB(235,250,255),2);line(dc,sx+9,sy+8,sx+17,sy+5,RGB(235,250,255),2);line(dc,sx+25,sy+8,sx+17,sy+5,RGB(235,250,255),2);txt(dc,sx+13,sy+10,13,RGB(255,255,255),"P");}
 {float need=repairNeed(s->type),p=s->repair/need;int bw=(int)((CELL-8)*clampf(p,0,1));fill(dc,sx+4,sy+CELL-7,CELL-8,4,RGB(15,31,36));fill(dc,sx+4,sy+CELL-7,bw,4,RGB(105,255,200));if(bw>2)fill(dc,sx+4+bw-2,sy+CELL-8,3,6,RGB(255,245,165));}
}
static void drawEnemySprite(HDC dc,Enemy*e,int sx,int sy){int bob=(int)(sin(e->timer*7)*2);COLORREF c=e->type==E_VIRUS?RGB(255,72,68):e->type==E_WORM?RGB(250,205,55):e->type==E_TROJAN?RGB(195,82,240):e->type==E_CLUSTER?RGB(255,132,45):e->type==E_SWEEPER?RGB(80,185,255):RGB(235,235,240);
 fill(dc,sx+7,sy+27,22,3,RGB(5,14,18));
 if(e->type==E_MAGNET){drawMagnet(dc,sx+3,sy+1,7,c);return;}
 if(e->type==E_VIRUS){fill(dc,sx+10,sy+9+bob,14,16,c);outline(dc,sx+9,sy+8+bob,16,18,RGB(35,6,12),2);fill(dc,sx+12,sy+5+bob,10,6,c);line(dc,sx+11,sy+8+bob,sx+5,sy+3+bob,c,2);line(dc,sx+23,sy+8+bob,sx+29,sy+3+bob,c,2);line(dc,sx+10,sy+13+bob,sx+4,sy+10+bob,c,2);line(dc,sx+10,sy+19+bob,sx+4,sy+23+bob,c,2);line(dc,sx+24,sy+13+bob,sx+30,sy+10+bob,c,2);line(dc,sx+24,sy+19+bob,sx+30,sy+23+bob,c,2);fill(dc,sx+13,sy+11+bob,3,3,RGB(255,240,130));fill(dc,sx+20,sy+11+bob,3,3,RGB(255,240,130));}
 else if(e->type==E_WORM){int k;for(k=0;k<4;k++){fill(dc,sx+4+k*7,sy+12+(k&1)*4,8,10,c);outline(dc,sx+4+k*7,sy+12+(k&1)*4,8,10,RGB(70,52,8),1);}fill(dc,sx+27,sy+11,3,3,RGB(20,25,20));}
 else if(e->type==E_TROJAN){fill(dc,sx+8,sy+7,18,20,c);outline(dc,sx+7,sy+6,20,22,RGB(38,10,55),2);line(dc,sx+8,sy+7,sx+17,sy+2,c,3);line(dc,sx+26,sy+7,sx+17,sy+2,c,3);fill(dc,sx+12,sy+12,10,4,RGB(35,10,50));fill(dc,sx+15,sy+19,4,7,RGB(245,215,255));}
 else if(e->type==E_CLUSTER){fill(dc,sx+4,sy+8,12,12,c);fill(dc,sx+18,sy+6,12,12,c);fill(dc,sx+11,sy+19,13,12,c);outline(dc,sx+3,sy+7,13,13,RGB(75,32,5),1);outline(dc,sx+17,sy+5,13,13,RGB(75,32,5),1);outline(dc,sx+10,sy+18,14,13,RGB(75,32,5),1);}
 else{fill(dc,sx+4,sy+12,27,9,c);outline(dc,sx+3,sy+11,29,11,RGB(8,35,55),2);fill(dc,sx+8,sy+9,4,16,RGB(190,235,255));fill(dc,sx+22,sy+9,4,16,RGB(190,235,255));}
}
static void drawFirewallShield(HDC dc,int sx,int sy,float left){int phase=(int)(GetTickCount64()/90)%8;COLORREF c=left<2.0f?RGB(255,180,70):RGB(85,245,225);int x1=sx-7,y1=sy-7,x2=sx+41,y2=sy+41;
 line(dc,x1+8,y1,x2-8,y1,c,2);line(dc,x2-8,y1,x2,y1+8,c,2);line(dc,x2,y1+8,x2,y2-8,c,2);line(dc,x2,y2-8,x2-8,y2,c,2);line(dc,x2-8,y2,x1+8,y2,c,2);line(dc,x1+8,y2,x1,y2-8,c,2);line(dc,x1,y2-8,x1,y1+8,c,2);line(dc,x1,y1+8,x1+8,y1,c,2);
 if(phase<2)fill(dc,x1+6+phase*12,y1-2,6,6,RGB(245,255,210));else if(phase<4)fill(dc,x2-2,y1+6+(phase-2)*12,6,6,RGB(245,255,210));else if(phase<6)fill(dc,x2-12-(phase-4)*12,y2-2,6,6,RGB(245,255,210));else fill(dc,x1-2,y2-12-(phase-6)*12,6,6,RGB(245,255,210));
}
'''
insert_at = s.index('static void drawGame(HDC dc)')
s = s[:insert_at] + helpers + s[insert_at:]

# Replace the flat sector grid with beveled, type-specific tiles.
game_start = s.index('static void drawGame(HDC dc)')
grid_start = s.index('fill(dc,GX-6+ox', game_start)
wall_start = s.index('for(i=0;i<MAX_WALLS', grid_start)
new_grid = 'fill(dc,GX-8+ox,GY-8+oy,GW*CELL+16,GH*CELL+16,RGB(5,14,20));outline(dc,GX-8+ox,GY-8+oy,GW*CELL+16,GH*CELL+16,RGB(60,110,120),3);for(y=0;y<GH;y++)for(x=0;x<GW;x++){int sx=GX+x*CELL+ox,sy=GY+y*CELL+oy;drawSectorTile(dc,sx,sy,x,y,&grid[y][x]);}'
s = s[:grid_start] + new_grid + s[wall_start:]

# Use the new differentiated enemy sprites.
game_start = s.index('static void drawGame(HDC dc)')
enemy_start = s.index('for(i=0;i<MAX_ENEMIES', game_start)
particle_start = s.index('for(i=0;i<MAX_PARTICLES', enemy_start)
new_enemy_loop = 'for(i=0;i<MAX_ENEMIES;i++)if(enemies[i].active){Enemy*e=&enemies[i];int sx=GX+(int)(e->x*CELL)+ox,sy=GY+(int)(e->y*CELL)+oy;drawEnemySprite(dc,e,sx,sy);}'
s = s[:enemy_start] + new_enemy_loop + s[particle_start:]

# Draw the mobile shield around the player sprite.
replace_once(
    'if(invuln<=0||((int)(invuln*14)&1)==0)drawBot(dc,sx,sy,repairing);',
    'if(firewallTimer>0)drawFirewallShield(dc,sx,sy,firewallTimer);if(invuln<=0||((int)(invuln*14)&1)==0)drawBot(dc,sx,sy,repairing);',
    'player firewall rendering'
)

# Replace the compact toolbar with larger keycaps, clearer names, stronger counts, and timers.
bar_start = s.index('static float firewallRemaining(void)')
bar_end = s.index("'''", bar_start) if False else -1
# Locate the existing helper block by the drawGame function that follows it.
draw_game_after_bar = s.index('static void drawGame(HDC dc)', bar_start)
new_bar = r'''static float firewallRemaining(void){return firewallTimer;}
static void drawToolIcon(HDC dc,int t,int x,int y,COLORREF c){switch(t){
 case TOOL_PULSE:outline(dc,x+3,y+3,20,20,c,2);line(dc,x+13,y,x+13,y+26,c,2);line(dc,x,y+13,x+26,y+13,c,2);fill(dc,x+10,y+10,7,7,c);break;
 case TOOL_LOCK:outline(dc,x+4,y+10,20,15,c,2);outline(dc,x+8,y+2,12,13,c,2);fill(dc,x+12,y+16,4,6,c);break;
 case TOOL_BEAM:line(dc,x+1,y+6,x+25,y+6,c,3);line(dc,x+5,y+13,x+21,y+13,c,3);line(dc,x+9,y+20,x+17,y+20,c,3);break;
 case TOOL_BACKUP:outline(dc,x+2,y+3,20,16,c,2);outline(dc,x+6,y+8,20,16,c,2);line(dc,x+11,y+16,x+20,y+16,c,2);break;
 case TOOL_OVERCLOCK:line(dc,x+15,y,x+5,y+15,c,4);line(dc,x+5,y+15,x+14,y+15,c,4);line(dc,x+14,y+15,x+8,y+27,c,4);line(dc,x+8,y+27,x+23,y+10,c,4);line(dc,x+23,y+10,x+15,y+10,c,4);break;
 case TOOL_FIREWALL:line(dc,x+13,y+1,x+3,y+6,c,3);line(dc,x+3,y+6,x+5,y+20,c,3);line(dc,x+5,y+20,x+13,y+27,c,3);line(dc,x+13,y+27,x+21,y+20,c,3);line(dc,x+21,y+20,x+23,y+6,c,3);line(dc,x+23,y+6,x+13,y+1,c,3);line(dc,x+8,y+13,x+12,y+17,c,2);line(dc,x+12,y+17,x+19,y+9,c,2);break;
 default:outline(dc,x+3,y+3,21,21,c,2);line(dc,x+13,y+3,x+13,y+10,c,3);line(dc,x+13,y+17,x+13,y+24,c,3);line(dc,x+6,y+13,x+20,y+13,c,3);break;}}
static void drawToolBar(HDC dc){static const char*names[]={"PULSE","LOCK","BEAM","BACKUP","OVERCLOCK","FIREWALL","REBOOT"};int i,j;char b[32];float wall=firewallRemaining();for(i=0;i<TOOL_COUNT;i++){int x=18+i*133,y=649,w=126,h=66;float rem=0,max=1;COLORREF edge=RGB(56,82,94),ink=toolCharges[i]>0?RGB(215,233,239):RGB(80,91,96);if(i==TOOL_LOCK&&sectorLock>0){rem=sectorLock;max=8;}if(i==TOOL_OVERCLOCK&&overclock>0){rem=overclock;max=10;}if(i==TOOL_FIREWALL&&wall>0){rem=wall;max=8;}if(rem>0)edge=RGB(80,255,215);else if(i==selectedTool)edge=RGB(255,205,75);fill(dc,x+3,y+4,w,h,RGB(3,9,13));fill(dc,x,y,w,h,RGB(8,18,25));outline(dc,x,y,w,h,edge,2);
 /* Large illuminated keycap makes the 1-7 control unmistakable. */
 fill(dc,x+5,y+6,31,31,toolCharges[i]>0?RGB(47,37,16):RGB(25,27,29));outline(dc,x+5,y+6,31,31,RGB(255,205,75),2);sprintf(b,"%d",i+1);txt(dc,x+13,y+8,23,RGB(255,225,115),b);
 drawToolIcon(dc,i,x+40,y+7,ink);txt(dc,x+69,y+7,(i==TOOL_OVERCLOCK||i==TOOL_FIREWALL)?9:10,ink,names[i]);sprintf(b,"x%d",toolCharges[i]);txt(dc,x+72,y+26,19,toolCharges[i]>0?RGB(255,230,145):RGB(105,110,112),b);
 for(j=0;j<toolCharges[i]&&j<4;j++)fill(dc,x+42+j*8,y+43,6,6,RGB(105,255,195));
 if(rem>0){int bw=(int)((w-10)*clampf(rem/max,0,1));fill(dc,x+5,y+h-10,w-10,6,RGB(20,42,48));fill(dc,x+5,y+h-10,bw,6,rem<2?RGB(255,170,65):RGB(85,255,210));sprintf(b,"%.1fs",rem);txt(dc,x+82,y+43,11,RGB(205,255,235),b);}else txt(dc,x+82,y+45,9,RGB(105,130,140),"PRESS");}}
'''
s = s[:bar_start] + new_bar + s[draw_game_after_bar:]

# Guide wording now matches the moving shield behavior.
s = s.replace('Places a temporary barrier around your position.', 'A moving shield follows the bot and destroys nearby threats.')

p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v1.7 mobile firewall and graphics polish')
