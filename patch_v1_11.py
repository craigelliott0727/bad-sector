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


# Balance state: every source of spreading shares a strict per-track budget.
replace_once(
    'static float px,py,invuln,spawnTimer,spreadTimer,stageClock,stageIntro,introTime,completeTime,screenShake,magnetPulse,overclock,sectorLock,firewallTimer,beamFxTimer,lastToolFlash,deathTimer,toolFxTimer,toolFxX,toolFxY;',
    'static float px,py,invuln,spawnTimer,spreadTimer,stageClock,stageIntro,introTime,completeTime,screenShake,magnetPulse,overclock,sectorLock,firewallTimer,beamFxTimer,lastToolFlash,deathTimer,toolFxTimer,toolFxX,toolFxY,missionTimer;',
    'mission event timer state'
)
replace_once(
    'static int beamFxRow=-1,lastToolUsed=-1,nextOneUpScore=5000,gameOverHasHighScore=0,toolFxKind=-1;',
    'static int beamFxRow=-1,lastToolUsed=-1,nextOneUpScore=5000,gameOverHasHighScore=0,toolFxKind=-1,spreadAdded=0,spreadCap=0;',
    'spread budget state'
)


balance_helpers = r'''
static int seedExactDamage(int count){int made=0,guard=0;while(made<count&&guard++<20000){int x=irand(GW),y=irand(GH);if(grid[y][x].type==S_CLEAN){grid[y][x].type=randomSector();grid[y][x].timer=frand()*2;made++;}}return made;}
static void guaranteeSectorType(int type,int wanted){int x,y,have=0,start=irand(GW*GH),k;for(y=0;y<GH;y++)for(x=0;x<GW;x++)if(grid[y][x].type==type)have++;for(k=0;k<GW*GH&&have<wanted;k++){int n=(start+k*37)%(GW*GH);x=n%GW;y=n/GW;if(grid[y][x].type!=S_CLEAN&&grid[y][x].type!=type){grid[y][x].type=(uint8_t)type;grid[y][x].repair=0;grid[y][x].timer=0;have++;}}}
static int addSpreadAt(int x,int y,int type,const char*msg){if(sectorLock>0||spreadAdded>=spreadCap||x<0||y<0||x>=GW||y>=GH||grid[y][x].type!=S_CLEAN)return 0;grid[y][x].type=(uint8_t)type;grid[y][x].repair=0;grid[y][x].timer=0;repairedGoal++;spreadAdded++;particle((float)x,(float)y,2,8);setStatus(msg);return 1;}
static int addRandomSpread(const char*msg){int k,start=irand(GW*GH);for(k=0;k<GW*GH;k++){int n=(start+k*29)%(GW*GH);if(addSpreadAt(n%GW,n/GW,S_CORRUPT,msg))return 1;}return 0;}
static const char* lateMissionRule(int stage){switch((stage-8)&3){case 0:return "MISSION MODIFIER: MAGNETIC POLARITY SHIFTS";case 1:return "MISSION MODIFIER: ARCHIVE CACHES RECHARGE TOOLS";case 2:return "MISSION MODIFIER: GLOBAL DECRYPTION WINDOWS";default:return "MISSION MODIFIER: GHOST SECTORS RELOCATE";}}
static void runLateMissionEvent(void){int i,x,y,start;if(stageIndex<8)return;switch((stageIndex-8)&3){case 0:magnetPulse+=PI;stageClock+=4;particle(px,py,1,28);setStatus("POLARITY SHIFT: +4 SECONDS");break;case 1:{int best=0;for(i=1;i<TOOL_COUNT;i++)if(toolCharges[i]<toolCharges[best])best=i;if(toolCharges[best]<4)toolCharges[best]++;particle(px,py,0,24);setStatus("ARCHIVE CACHE: TOOL CHARGE RESTORED");}break;case 2:for(y=0;y<GH;y++)for(x=0;x<GW;x++)if(grid[y][x].type==S_ENCRYPTED)grid[y][x].timer=0;stageClock+=5;setStatus("DECRYPTION WINDOW OPEN: +5 SECONDS");break;default:start=irand(GW*GH);for(i=0;i<GW*GH;i++){int a=(start+i*17)%(GW*GH),ax=a%GW,ay=a/GW;if(grid[ay][ax].type!=S_CLEAN){int j;for(j=1;j<GW*GH;j++){int b=(a+j*31)%(GW*GH),bx=b%GW,by=b/GW;if(grid[by][bx].type==S_CLEAN){grid[by][bx]=grid[ay][ax];grid[ay][ax]=(Sector){S_CLEAN,1,0,0,0,0};particle((float)ax,(float)ay,1,10);particle((float)bx,(float)by,0,12);setStatus("GHOST SHIFT: DAMAGED SECTOR RELOCATED");i=GW*GH;j=GW*GH;break;}}}}break;}}
'''
insert_at = s.index('static void stageSetup(void)')
s = s[:insert_at] + balance_helpers + s[insert_at:]


# A gradual campaign curve with exact initial counts and guaranteed introduced sector types.
stage_setup = r'''static void stageSetup(void){
 static const int initialDamage[20]={12,14,16,18,20,22,24,26,28,30,30,32,32,34,34,36,36,38,40,44};
 static const int timeLimit[20]={150,150,145,145,145,145,150,150,155,155,160,160,165,165,170,170,175,180,185,210};
 static const int spreadLimits[20]={0,0,0,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,12,14};
 int x,y,i,made;const Stage*st=&stages[stageIndex];
 for(y=0;y<GH;y++)for(x=0;x<GW;x++)grid[y][x]=(Sector){S_CLEAN,1,0,0,0,0};
 clearEntities();made=seedExactDamage(initialDamage[stageIndex]);
 if(stageIndex==0&&!challengeMode)for(y=0;y<GH;y++)for(x=0;x<GW;x++)if(grid[y][x].type!=S_CLEAN)grid[y][x].type=S_CORRUPT;
 if(!challengeMode){
  if(stageIndex==1)guaranteeSectorType(S_FRAGMENTED,4);
  if(stageIndex==2)guaranteeSectorType(S_INFECTED,4);
  if(stageIndex==3)guaranteeSectorType(S_UNSTABLE,3);
  if(stageIndex==4)guaranteeSectorType(S_ENCRYPTED,4);
  if(stageIndex==5)guaranteeSectorType(S_PROTECTED,4);
  if(stageIndex>=6){guaranteeSectorType(S_ENCRYPTED,2);guaranteeSectorType(S_PROTECTED,2);}
  if(stageIndex==7)guaranteeSectorType(S_UNSTABLE,4);
  if(stageIndex>=8)guaranteeSectorType(S_UNSTABLE,2);
 }
 px=GW*.5f;py=GH*.5f;invuln=2.0f;
 spawnTimer=stageIndex<2?13.0f:stageIndex<4?11.0f:stageIndex<6?10.0f:stageIndex<9?9.0f:8.0f;
 spreadTimer=stageIndex<3?999.0f:stageIndex==3?20.0f:stageIndex<8?18.0f:16.0f;
 stageClock=(float)timeLimit[stageIndex];stageIntro=5.0f;screenShake=0;magnetPulse=0;overclock=0;sectorLock=0;firewallTimer=0;beamFxTimer=0;beamFxRow=-1;lastToolUsed=-1;lastToolFlash=0;deathTimer=0;gameOverHasHighScore=0;toolFxTimer=0;toolFxKind=-1;
 repairedGoal=made;spreadAdded=0;spreadCap=challengeMode?12:spreadLimits[stageIndex];missionTimer=stageIndex>=8?14.0f:999.0f;
 run.repairs=0;run.combo=0;selectedTool=TOOL_PULSE;for(i=0;i<TOOL_COUNT;i++)toolCharges[i]=2;toolCharges[TOOL_PULSE]=4;toolCharges[TOOL_REBOOT]=1;
 if(st->boss)for(i=0;i<3;i++)enemies[i]=(Enemy){i?GW-3:2,2+i*5,0,0,0,0,1,E_MAGNET,8};
 startMusic(stageIndex>=12);
}'''
replace_function('static void stageSetup(void)', stage_setup)


# Tools now always have an obvious gameplay result. Backup Restore repairs actual damaged sectors.
use_tool = r'''static void useTool(void){
 static const char*toolFullNames[]={"ANTIVIRUS PULSE","SECTOR LOCK","DEFRAG BEAM","BACKUP RESTORE","OVERCLOCK","FIREWALL","EMERGENCY REBOOT"};
 char msg[80];int i,x=(int)(px+.5f),y=(int)(py+.5f);
 if(toolCharges[selectedTool]<=0){sprintf(msg,"%s EMPTY",toolFullNames[selectedTool]);setStatus(msg);fx(2);return;}
 toolCharges[selectedTool]--;lastToolUsed=selectedTool;lastToolFlash=.70f;toolFxKind=selectedTool;toolFxTimer=1.10f;toolFxX=px;toolFxY=py;
 switch(selectedTool){
  case TOOL_PULSE:for(i=0;i<MAX_ENEMIES;i++)if(enemies[i].active&&dist2(px,py,enemies[i].x,enemies[i].y)<16)killEnemy(i,75);particle(px,py,0,40);setStatus("ANTIVIRUS PULSE");break;
  case TOOL_LOCK:sectorLock=10.0f;spreadTimer+=10.0f;for(i=0;i<MAX_ENEMIES;i++)if(enemies[i].active&&enemies[i].type==E_WORM)enemies[i].timer=0;for(y=0;y<GH;y++)for(x=0;x<GW;x++)if(grid[y][x].type==S_UNSTABLE)grid[y][x].timer=0;setStatus("SECTOR LOCK: ALL SPREAD FROZEN FOR 10s");break;
  case TOOL_BEAM:{int cleaned=0;for(i=0;i<GW;i++){SectorType old=(SectorType)grid[y][i].type;if(old!=S_CLEAN){cleaned++;if(old==S_PROTECTED)run.protectedSaved++;particle((float)i,(float)y,0,8);}grid[y][i].type=S_CLEAN;grid[y][i].repair=0;}run.repairs+=cleaned;run.score+=250+cleaned*40;beamFxRow=y;beamFxTimer=.85f;sprintf(msg,"DEFRAG BEAM: %d SECTORS CLEANED",cleaned);setStatus(msg);}break;
  case TOOL_BACKUP:{int cleaned=0,start=irand(GW*GH);for(i=0;i<GW*GH&&cleaned<6;i++){int n=(start+i*37)%(GW*GH),a=n%GW,b=n/GW;SectorType old=(SectorType)grid[b][a].type;if(old!=S_CLEAN){grid[b][a].type=S_CLEAN;grid[b][a].repair=0;cleaned++;run.repairs++;run.score+=old==S_PROTECTED?220:100;if(old==S_PROTECTED)run.protectedSaved++;particle((float)a,(float)b,0,14);}}sprintf(msg,"BACKUP RESTORE: %d SECTORS RECOVERED",cleaned);setStatus(msg);}break;
  case TOOL_OVERCLOCK:overclock=10;particle(px,py,1,24);setStatus("OVERCLOCK ENABLED: 10 SECONDS");break;
  case TOOL_FIREWALL:firewallTimer=8.0f;particle(px,py,0,30);setStatus("MOBILE FIREWALL ENABLED: 8 SECONDS");break;
  case TOOL_REBOOT:for(i=0;i<MAX_ENEMIES;i++)if(enemies[i].active)killEnemy(i,20);repairedGoal+=corruptRandom(5);invuln=3;setStatus("EMERGENCY REBOOT: THREATS CLEARED / 5 SECTORS DAMAGED");break;
  default:break;
 }
 fx(0);
}'''
replace_function('static void useTool(void)', use_tool)


# Worms are no longer sector-printing machines, and Sector Lock blocks their trails too.
update_enemies = r'''static void updateEnemies(float dt){int i;for(i=0;i<MAX_ENEMIES;i++)if(enemies[i].active){Enemy*e=&enemies[i];float dx=px-e->x,dy=py-e->y,d=(float)sqrt(dx*dx+dy*dy)+.001f;e->timer+=dt;switch(e->type){case E_VIRUS:e->vx+=dx/d*dt*1.4f;e->vy+=dy/d*dt*1.4f;break;case E_WORM:e->vx+=dx/d*dt*.35f;e->vy+=dy/d*dt*.35f;if(e->timer>(challengeMode?3.0f:stageIndex<8?5.5f:4.5f)){int x=(int)e->x,y=(int)e->y;if(sectorLock<=0)addSpreadAt(x,y,S_CORRUPT,"WORM TRAIL: +1 SECTOR");e->timer=0;}break;case E_TROJAN:if(d<3.2f){e->vx+=dx/d*dt*2.8f;e->vy+=dy/d*dt*2.8f;}else{e->vx*=.97f;e->vy*=.97f;}break;case E_CLUSTER:e->vx+=dx/d*dt*.8f;e->vy+=dy/d*dt*.8f;break;case E_SWEEPER:if(e->aux<3.14f){e->vx=2.8f;e->vy=0;}else{e->vx=0;e->vy=2.8f;}break;case E_MAGNET:{float pull=(stages[stageIndex].boss?2.4f:1.4f)/(d+.5f);px+=(-dx/d)*pull*dt;py+=(-dy/d)*pull*dt;e->vx+=(float)sin(e->timer)*dt;e->vy+=(float)cos(e->timer*.8f)*dt;}break;}e->vx=clampf(e->vx,-3.7f,3.7f);e->vy=clampf(e->vy,-3.7f,3.7f);e->x+=e->vx*dt;e->y+=e->vy*dt;if(e->x<0)e->x=GW-1;if(e->x>GW-1)e->x=0;if(e->y<0)e->y=GH-1;if(e->y>GH-1)e->y=0;if(wallAt((int)(e->x+.5f),(int)(e->y+.5f))){e->vx=-e->vx;e->vy=-e->vy;e->x+=e->vx*.2f;e->y+=e->vy*.2f;}if(firewallTimer>0&&dist2(px,py,e->x,e->y)<2.35f){if(e->type==E_MAGNET){e->vx=-e->vx*1.4f;e->vy=-e->vy*1.4f;e->x+=e->vx*.35f;e->y+=e->vy*.35f;}else{killEnemy(i,60);continue;}}if(dist2(px,py,e->x,e->y)<.72f){if(e->type==E_CLUSTER&&e->hp>1){e->hp=1;spawnEnemyType(E_VIRUS,e->x+.4f,e->y);spawnEnemyType(E_VIRUS,e->x-.4f,e->y);killEnemy(i,100);}else if(e->type!=E_MAGNET)killEnemy(i,25);damage();}}}'''
replace_function('static void updateEnemies(float dt)', update_enemies)


# Rebuild the world update around the gentler curve and shared spread budget.
update_world = r'''static void updateWorld(float dt){int x,y,i;const Stage*st=&stages[stageIndex];float dx=0,dy=0,speed=6.5f+(overclock>0?3.2f:0);
 if(pressed('T')){toolGuide=!toolGuide;return;}if(toolGuide){if(pressed(VK_ESCAPE)||pressed(VK_RETURN)||pressed('T'))toolGuide=0;return;}
 if(pressed(VK_ESCAPE)){mode=M_PAUSE;return;}if(pressed(VK_OEM_5)){debugCompleteStage();return;}
 if(pressed('Q'))selectedTool=(selectedTool+TOOL_COUNT-1)%TOOL_COUNT;if(pressed('E'))selectedTool=(selectedTool+1)%TOOL_COUNT;for(i=0;i<TOOL_COUNT;i++)if(pressed('1'+i)){selectedTool=i;useTool();}if(pressed(VK_RETURN)||pressed('F'))useTool();
 if(keys['A']||keys[VK_LEFT])dx--;if(keys['D']||keys[VK_RIGHT])dx++;if(keys['W']||keys[VK_UP])dy--;if(keys['S']||keys[VK_DOWN])dy++;if(dx&&dy){dx*=.7071f;dy*=.7071f;}px=clampf(px+dx*speed*dt,0,GW-1);py=clampf(py+dy*speed*dt,0,GH-1);repairCell(dt);
 stageClock-=dt*(difficulty==0?.85f:difficulty==2?1.15f:1);if(stageClock<=0){damage();stageClock=12;if(mode==M_DYING)return;}
 if(invuln>0)invuln-=dt;if(overclock>0)overclock-=dt;if(sectorLock>0)sectorLock-=dt;if(firewallTimer>0)firewallTimer-=dt;if(beamFxTimer>0)beamFxTimer-=dt;if(lastToolFlash>0)lastToolFlash-=dt;if(toolFxTimer>0)toolFxTimer-=dt;if(statusTimer>0)statusTimer-=dt;
 if(run.score>=nextOneUpScore){nextOneUpScore+=10000;if(run.lives<5){run.lives++;pLives[currentPlayer]=run.lives;setStatus("1UP! EXTRA RECOVERY BOT AWARDED");particle(px,py,1,45);fx(0);}}
 spawnTimer-=dt;if(spawnTimer<=0){int cap=stageIndex<1?1:stageIndex<3?2:stageIndex<6?3:stageIndex<9?4:stageIndex<14?5:st->boss?8:6;if(activeEnemyCount()<cap)spawnEnemy();spawnTimer=stageIndex<2?12.0f:stageIndex<4?10.5f:stageIndex<7?9.5f:stageIndex<10?8.5f:7.5f;}
 if(sectorLock<=0)spreadTimer-=dt;if(spreadTimer<=0&&sectorLock<=0&&(!challengeMode?stageIndex>=3:1)){addRandomSpread("CORRUPTION SPREAD: +1 SECTOR");spreadTimer=challengeMode?9.0f:stageIndex==3?20.0f:stageIndex<8?18.0f:16.0f;}
 missionTimer-=dt;if(missionTimer<=0){runLateMissionEvent();missionTimer=20.0f;}
 magnetPulse+=dt;if(st->magnet){float polarity=(float)sin(magnetPulse*1.7f),cx=GW*.5f,cy=GH*.5f,mdx=cx-px,mdy=cy-py,dd=(float)sqrt(mdx*mdx+mdy*mdy)+.1f;px+=mdx/dd*polarity*dt*(.45f+stageIndex*.018f);py+=mdy/dd*polarity*dt*(.45f+stageIndex*.018f);}
 for(y=0;y<GH;y++)for(x=0;x<GW;x++){Sector*c=&grid[y][x];if(c->type!=S_UNSTABLE||sectorLock<=0)c->timer+=dt;if(c->type==S_UNSTABLE&&sectorLock<=0&&c->timer>(stageIndex==3?16.0f:12.0f)){int tries;for(tries=0;tries<8;tries++){int nx=x+(irand(3)-1),ny=y+(irand(3)-1);if(addSpreadAt(nx,ny,S_CORRUPT,"UNSTABLE SECTOR SPREAD: +1"))break;}c->timer=0;}}
 for(i=0;i<MAX_WALLS;i++)if(walls[i].active){walls[i].life-=dt;if(walls[i].life<=0)walls[i].active=0;}for(i=0;i<MAX_PARTICLES;i++)if(particles[i].active){particles[i].x+=particles[i].vx*dt;particles[i].y+=particles[i].vy*dt;particles[i].life-=dt;if(particles[i].life<=0)particles[i].active=0;}
 updateEnemies(dt);if(mode==M_DYING)return;if(run.repairs>=repairedGoal||damagedSectorCount()==0)completeStage();
}'''
replace_function('static void updateWorld(float dt)', update_world)


# Fit all five possible recovery-bot lives inside the HUD panel.
life_icon = r'''
static void drawLifeIcon(HDC dc,int x,int y){fill(dc,x+2,y+3,13,11,RGB(35,78,79));outline(dc,x+1,y+2,15,13,RGB(215,255,245),1);fill(dc,x+4,y+5,9,7,RGB(82,240,194));fill(dc,x+5,y+7,2,2,RGB(5,35,33));fill(dc,x+10,y+7,2,2,RGB(5,35,33));line(dc,x+8,y+2,x+8,y-1,RGB(255,220,75),1);fill(dc,x+7,y-2,3,2,RGB(255,220,75));}
'''
insert_at = s.index('static void drawGame(HDC dc)')
s = s[:insert_at] + life_icon + s[insert_at:]
old_lives = 'for(i=0;i<run.lives&&i<3;i++)drawBot(dc,92+i*28,48,0);'
if old_lives not in s:
    raise SystemExit('Could not find three-icon lives HUD')
s = s.replace(old_lives, 'for(i=0;i<run.lives&&i<5;i++)drawLifeIcon(dc,92+i*18,54);', 1)


# Explain the rotating late-game modifiers on the black mission briefing screen.
story_prompt = 'center(dc,610,19,RGB(225,235,240),"PRESS ENTER / SPACE WHEN READY");'
replace_once(
    story_prompt,
    'if(stageIndex>=8)center(dc,548,16,RGB(105,255,195),lateMissionRule(stageIndex));center(dc,610,19,RGB(225,235,240),"PRESS ENTER / SPACE WHEN READY");',
    'late mission briefing rule'
)

p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v2.3 balance, guaranteed sectors, functional tools and late-game mission update')
