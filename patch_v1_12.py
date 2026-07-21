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


# Pending yellow-sector spread animation plus campaign reward/progression state.
replace_once(
    'static float px,py,invuln,spawnTimer,spreadTimer,stageClock,stageIntro,introTime,completeTime,screenShake,magnetPulse,overclock,sectorLock,firewallTimer,beamFxTimer,lastToolFlash,deathTimer,toolFxTimer,toolFxX,toolFxY,missionTimer;',
    'static float px,py,invuln,spawnTimer,spreadTimer,stageClock,stageIntro,introTime,completeTime,screenShake,magnetPulse,overclock,sectorLock,firewallTimer,beamFxTimer,lastToolFlash,deathTimer,toolFxTimer,toolFxX,toolFxY,missionTimer,spreadFxTimer;',
    'spread animation float state'
)
replace_once(
    'static int beamFxRow=-1,lastToolUsed=-1,nextOneUpScore=5000,gameOverHasHighScore=0,toolFxKind=-1,spreadAdded=0,spreadCap=0;',
    'static int beamFxRow=-1,lastToolUsed=-1,nextOneUpScore=5000,gameOverHasHighScore=0,toolFxKind=-1,spreadAdded=0,spreadCap=0,spreadFxActive=0,spreadFromX=-1,spreadFromY=-1,spreadToX=-1,spreadToY=-1,pendingReward=-1,activeReward=-1,trackRank=0,runStars=0,nextStarLife=8,trackStartLives=3,trackBestCombo=0,stageRepairBoost=0;',
    'spread and progression integer state'
)


# Distinct track hooks, visible progression rewards, and yellow-only spreading.
stage_hook = r'''static const char* stageHook(int stage){static const char*hooks[20]={
 "BOOT SECTOR: LEARN THE RECOVERY ROUTE",
 "FRAGMENTS TAKE LONGER - PLAN YOUR PATH",
 "PURPLE BUG TILES RELEASE VIRUSES",
 "YELLOW SECTORS TELEGRAPH AND SPREAD",
 "ENCRYPTED TILES OPEN ON GREEN PULSES",
 "PROTECTED P DATA BUILDS BONUS STARS",
 "READ-HEAD SWEEPERS CROSS ENTIRE TRACKS",
 "COMBO CACHE: EVERY 5 REPAIRS RECHARGES A TOOL",
 "MAGNET ARRAY: POLARITY PULLS THE BOT",
 "ARCHIVE CACHE: PERIODIC TOOL DROPS",
 "DECRYPTION SURGE: GLOBAL GREEN WINDOWS",
 "GHOST TRACK: DAMAGE RELOCATES",
 "SPEAKER STACK: MULTIPLE MAGNETIC FIELDS",
 "RESCUE RUN: PROTECTED DATA PAYS DOUBLE",
 "CHECKSUM STREAK: FOUR REPAIRS RECHARGE A TOOL",
 "MAGNET TUNNEL: FIREWALL LASTS LONGER",
 "MASTER INDEX: FASTER ENEMY WAVES",
 "LAST BACKUP: BACKUP RESTORE RECOVERS MORE",
 "POLARITY REVERSAL: THE FIELD FLIPS RAPIDLY",
 "FINAL BOSS: SHUT DOWN THE BIG MAGNET"};return hooks[stage<0?0:stage>19?19:stage];}'''
replace_function('static const char* lateMissionRule', stage_hook)

progress_helpers = r'''
static const char* rewardName(int r){switch(r){case 0:return "TIME CACHE +15 SEC";case 1:return "BACKUP RESTORE +1";case 2:return "SECTOR LOCK +1";case 3:return "TURBO REPAIR +25%";case 4:return "FIREWALL +1";case 5:return "ANTIVIRUS PULSE +2";default:return "NO BONUS";}}
static int stageUsesUnstable(int stage){return stage==3||stage==7||stage==8||stage==11||stage==14||stage==16||stage==18||stage==19;}
static int unstableCount(void){int x,y,n=0;for(y=0;y<GH;y++)for(x=0;x<GW;x++)if(grid[y][x].type==S_UNSTABLE)n++;return n;}
static int beginUnstableSpread(int sx,int sy){static const int dx[8]={1,-1,0,0,1,1,-1,-1};static const int dy[8]={0,0,1,-1,1,-1,1,-1};int k,start=irand(8);if(spreadFxActive||sectorLock>0||spreadAdded>=spreadCap||grid[sy][sx].type!=S_UNSTABLE)return 0;for(k=0;k<8;k++){int j=(start+k)%8,tx=sx+dx[j],ty=sy+dy[j];if(tx>=0&&ty>=0&&tx<GW&&ty<GH&&grid[ty][tx].type==S_CLEAN){spreadFxActive=1;spreadFxTimer=.90f;spreadFromX=sx;spreadFromY=sy;spreadToX=tx;spreadToY=ty;grid[sy][sx].timer=0;setStatus("YELLOW SECTOR CHARGING - SPREAD INCOMING");fx(2);return 1;}}grid[sy][sx].timer=0;return 0;}
static void cancelPendingSpread(const char*msg){if(!spreadFxActive)return;spreadFxActive=0;spreadFxTimer=0;spreadFromX=spreadFromY=spreadToX=spreadToY=-1;if(msg)setStatus(msg);}
static void finishPendingSpread(float dt){if(!spreadFxActive)return;if(sectorLock>0){cancelPendingSpread("SECTOR LOCK CANCELLED THE SPREAD");return;}spreadFxTimer-=dt;if(spreadFxTimer>0)return;if(spreadFromX>=0&&spreadFromY>=0&&spreadToX>=0&&spreadToY>=0&&grid[spreadFromY][spreadFromX].type==S_UNSTABLE&&grid[spreadToY][spreadToX].type==S_CLEAN&&spreadAdded<spreadCap){grid[spreadToY][spreadToX].type=S_CORRUPT;grid[spreadToY][spreadToX].repair=0;grid[spreadToY][spreadToX].timer=0;repairedGoal++;spreadAdded++;particle((float)spreadFromX,(float)spreadFromY,1,16);particle((float)spreadToX,(float)spreadToY,2,24);screenShake=4;setStatus("YELLOW SECTOR SPREAD: +1 SECTOR");fx(1);}spreadTimer=6.0f;spreadFxActive=0;spreadFxTimer=0;spreadFromX=spreadFromY=spreadToX=spreadToY=-1;}
'''
insert_at = s.index('static void stageSetup(void)')
s = s[:insert_at] + progress_helpers + s[insert_at:]


# Later levels now have individual events rather than a four-item repeating loop.
late_events = r'''static void runLateMissionEvent(void){int i,x,y,start;if(stageIndex<8)return;switch(stageIndex){
 case 8:magnetPulse+=PI;stageClock+=4;particle(px,py,1,28);setStatus("POLARITY SHIFT: +4 SECONDS");break;
 case 9:{int best=0;for(i=1;i<6;i++)if(toolCharges[i]<toolCharges[best])best=i;if(toolCharges[best]<4)toolCharges[best]++;particle(px,py,0,24);setStatus("ARCHIVE CACHE: TOOL CHARGE RESTORED");}break;
 case 10:for(y=0;y<GH;y++)for(x=0;x<GW;x++)if(grid[y][x].type==S_ENCRYPTED)grid[y][x].timer=0;stageClock+=5;setStatus("DECRYPTION SURGE: GREEN WINDOW / +5 SEC");break;
 case 11:start=irand(GW*GH);for(i=0;i<GW*GH;i++){int a=(start+i*17)%(GW*GH),ax=a%GW,ay=a/GW;if(grid[ay][ax].type!=S_CLEAN){int j;for(j=1;j<GW*GH;j++){int b=(a+j*31)%(GW*GH),bx=b%GW,by=b/GW;if(grid[by][bx].type==S_CLEAN){grid[by][bx]=grid[ay][ax];grid[ay][ax]=(Sector){S_CLEAN,1,0,0,0,0};particle((float)ax,(float)ay,1,10);particle((float)bx,(float)by,0,12);setStatus("GHOST SHIFT: DAMAGE RELOCATED");i=GW*GH;j=GW*GH;break;}}}}break;
 case 12:if(firewallTimer<3.0f)firewallTimer=3.0f;setStatus("SPEAKER SHOCKWAVE: FIREWALL BUFFER GRANTED");break;
 case 13:stageClock+=4;run.score+=250;setStatus("PROTECTED DATA SCAN: +250 / +4 SEC");break;
 case 14:if(trackBestCombo>=8){run.score+=700;setStatus("CHECKSUM STREAK VERIFIED: +700");}else{stageClock+=4;setStatus("CHECKSUM RETRY: +4 SECONDS");}break;
 case 15:if(toolCharges[TOOL_FIREWALL]<4)toolCharges[TOOL_FIREWALL]++;setStatus("TUNNEL ANCHOR: FIREWALL RECHARGED");break;
 case 16:spawnTimer=0;stageClock+=3;setStatus("MASTER INDEX SURGE: ENEMY WAVE / +3 SEC");break;
 case 17:if(toolCharges[TOOL_BACKUP]<4)toolCharges[TOOL_BACKUP]++;setStatus("LAST BACKUP FOUND: RESTORE RECHARGED");break;
 case 18:magnetPulse+=PI;stageClock+=5;setStatus("POLARITY REVERSAL: FIELD FLIPPED / +5 SEC");break;
 default:if(firewallTimer<3.0f)firewallTimer=3.0f;stageClock+=3;setStatus("BOSS CHECKPOINT: SHIELD BUFFER / +3 SEC");break;
 }}'''
replace_function('static void runLateMissionEvent(void)', late_events)


# Exact damage counts remain, but only designated tracks contain yellow spreading sectors.
stage_setup = r'''static void stageSetup(void){
 static const int initialDamage[20]={12,14,16,18,20,22,24,26,28,30,30,32,32,34,34,36,36,38,40,44};
 static const int timeLimit[20]={150,150,145,145,145,145,150,150,155,155,160,160,165,165,170,170,175,180,185,210};
 static const int spreadLimits[20]={0,0,0,3,0,0,0,5,5,0,0,6,0,0,7,0,8,0,10,12};
 int x,y,i,made;const Stage*st=&stages[stageIndex];
 for(y=0;y<GH;y++)for(x=0;x<GW;x++)grid[y][x]=(Sector){S_CLEAN,1,0,0,0,0};
 clearEntities();made=seedExactDamage(initialDamage[stageIndex]);
 if(stageIndex==0&&!challengeMode)for(y=0;y<GH;y++)for(x=0;x<GW;x++)if(grid[y][x].type!=S_CLEAN)grid[y][x].type=S_CORRUPT;
 if(!challengeMode){
  if(stageIndex==1)guaranteeSectorType(S_FRAGMENTED,4);
  if(stageIndex==2)guaranteeSectorType(S_INFECTED,4);
  if(stageIndex==4)guaranteeSectorType(S_ENCRYPTED,4);
  if(stageIndex==5)guaranteeSectorType(S_PROTECTED,4);
  if(stageIndex>=6){guaranteeSectorType(S_ENCRYPTED,2);guaranteeSectorType(S_PROTECTED,2);}
  if(!stageUsesUnstable(stageIndex)){for(y=0;y<GH;y++)for(x=0;x<GW;x++)if(grid[y][x].type==S_UNSTABLE)grid[y][x].type=S_CORRUPT;}
  else guaranteeSectorType(S_UNSTABLE,stageIndex==3?3:2);
 }
 px=GW*.5f;py=GH*.5f;invuln=2.0f;
 spawnTimer=stageIndex<2?13.0f:stageIndex<4?11.0f:stageIndex<6?10.0f:stageIndex<9?9.0f:8.0f;
 spreadTimer=stageUsesUnstable(stageIndex)?7.0f:999.0f;
 stageClock=(float)timeLimit[stageIndex];stageIntro=5.0f;screenShake=0;magnetPulse=0;overclock=0;sectorLock=0;firewallTimer=0;beamFxTimer=0;beamFxRow=-1;lastToolUsed=-1;lastToolFlash=0;deathTimer=0;gameOverHasHighScore=0;toolFxTimer=0;toolFxKind=-1;spreadFxTimer=0;spreadFxActive=0;spreadFromX=spreadFromY=spreadToX=spreadToY=-1;
 repairedGoal=made;spreadAdded=0;spreadCap=challengeMode?10:spreadLimits[stageIndex];missionTimer=stageIndex>=8?14.0f:999.0f;
 run.repairs=0;run.combo=0;trackBestCombo=0;selectedTool=TOOL_PULSE;for(i=0;i<TOOL_COUNT;i++)toolCharges[i]=2;toolCharges[TOOL_PULSE]=4;toolCharges[TOOL_REBOOT]=1;
 activeReward=pendingReward;pendingReward=-1;stageRepairBoost=0;if(activeReward==0)stageClock+=15;else if(activeReward==1)toolCharges[TOOL_BACKUP]++;else if(activeReward==2)toolCharges[TOOL_LOCK]++;else if(activeReward==3)stageRepairBoost=1;else if(activeReward==4)toolCharges[TOOL_FIREWALL]++;else if(activeReward==5)toolCharges[TOOL_PULSE]+=2;
 trackStartLives=run.lives;
 if(st->boss)for(i=0;i<3;i++)enemies[i]=(Enemy){i?GW-3:2,2+i*5,0,0,0,0,1,E_MAGNET,8};
 startMusic(stageIndex>=12);
}'''
replace_function('static void stageSetup(void)', stage_setup)


# Reset progression cleanly whenever a fresh campaign or daily disk begins.
new_game = r'''static void newGame(int challenge){int i;SYSTEMTIME st;challengeMode=challenge;GetLocalTime(&st);if(challenge){rngState=(uint32_t)(st.wYear*10000+st.wMonth*100+st.wDay)^0x1440BEEF;stageIndex=4+(int)(rngState%12);}else{rngState=0x1440BEEFu;stageIndex=0;}run=(RunStats){0,1,3,100,0,0,0,0,0};nextOneUpScore=5000;pendingReward=-1;activeReward=-1;trackRank=0;runStars=0;nextStarLife=8;trackStartLives=3;trackBestCombo=0;stageRepairBoost=0;for(i=0;i<2;i++){pScores[i]=0;pLives[i]=3;}currentPlayer=0;stageSetup();introTime=0;mode=M_INTRO;}'''
replace_function('static void newGame(int challenge)', new_game)


# Tools have clear effects; Sector Lock cancels an in-flight spread animation.
use_tool = r'''static void useTool(void){
 static const char*toolFullNames[]={"ANTIVIRUS PULSE","SECTOR LOCK","DEFRAG BEAM","BACKUP RESTORE","OVERCLOCK","FIREWALL","EMERGENCY REBOOT"};
 char msg[80];int i,x=(int)(px+.5f),y=(int)(py+.5f);
 if(toolCharges[selectedTool]<=0){sprintf(msg,"%s EMPTY",toolFullNames[selectedTool]);setStatus(msg);fx(2);return;}
 toolCharges[selectedTool]--;lastToolUsed=selectedTool;lastToolFlash=.70f;toolFxKind=selectedTool;toolFxTimer=1.10f;toolFxX=px;toolFxY=py;
 switch(selectedTool){
  case TOOL_PULSE:for(i=0;i<MAX_ENEMIES;i++)if(enemies[i].active&&dist2(px,py,enemies[i].x,enemies[i].y)<16)killEnemy(i,75);particle(px,py,0,40);setStatus("ANTIVIRUS PULSE");break;
  case TOOL_LOCK:sectorLock=10.0f;spreadTimer=10.0f;cancelPendingSpread(NULL);for(y=0;y<GH;y++)for(x=0;x<GW;x++)if(grid[y][x].type==S_UNSTABLE)grid[y][x].timer=0;setStatus("SECTOR LOCK: YELLOW SPREAD FROZEN FOR 10s");break;
  case TOOL_BEAM:{int cleaned=0;for(i=0;i<GW;i++){SectorType old=(SectorType)grid[y][i].type;if(old!=S_CLEAN){cleaned++;if(old==S_PROTECTED)run.protectedSaved++;particle((float)i,(float)y,0,8);}grid[y][i].type=S_CLEAN;grid[y][i].repair=0;}run.repairs+=cleaned;run.score+=250+cleaned*40;beamFxRow=y;beamFxTimer=.85f;sprintf(msg,"DEFRAG BEAM: %d SECTORS CLEANED",cleaned);setStatus(msg);}break;
  case TOOL_BACKUP:{int cleaned=0,limit=stageIndex==17?9:6,start=irand(GW*GH);for(i=0;i<GW*GH&&cleaned<limit;i++){int n=(start+i*37)%(GW*GH),a=n%GW,b=n/GW;SectorType old=(SectorType)grid[b][a].type;if(old!=S_CLEAN){grid[b][a].type=S_CLEAN;grid[b][a].repair=0;cleaned++;run.repairs++;run.score+=old==S_PROTECTED?220:100;if(old==S_PROTECTED)run.protectedSaved++;particle((float)a,(float)b,0,14);}}sprintf(msg,"BACKUP RESTORE: %d SECTORS RECOVERED",cleaned);setStatus(msg);}break;
  case TOOL_OVERCLOCK:overclock=10;particle(px,py,1,24);setStatus("OVERCLOCK ENABLED: 10 SECONDS");break;
  case TOOL_FIREWALL:firewallTimer=stageIndex==15?12.0f:8.0f;particle(px,py,0,30);setStatus(stageIndex==15?"TUNNEL FIREWALL: 12 SECONDS":"MOBILE FIREWALL: 8 SECONDS");break;
  case TOOL_REBOOT:for(i=0;i<MAX_ENEMIES;i++)if(enemies[i].active)killEnemy(i,20);repairedGoal+=corruptRandom(5);invuln=3;setStatus("EMERGENCY REBOOT: THREATS CLEARED / 5 SECTORS DAMAGED");break;
  default:break;
 }
 fx(0);
}'''
replace_function('static void useTool(void)', use_tool)


# Repair streaks now generate frequent rewards and meaningful track ratings.
repair_cell = r'''static void repairCell(float dt){int x=(int)(px+.5f),y=(int)(py+.5f);Sector*cell=&grid[y][x];float need=repairNeed(cell->type),rate=(overclock>0?2.2f:1.0f)*(stageRepairBoost?1.25f:1.0f);if(cell->type==S_CLEAN)return;if(cell->type==S_ENCRYPTED&&fmod(cell->timer,2.0f)>0.75f){setStatus("ENCRYPTED: WAIT FOR GREEN PULSE");return;}cell->repair+=dt*rate;if(cell->repair>=need){SectorType old=(SectorType)cell->type;int cacheEvery=stageIndex==14?4:5,cacheAward=0;cell->type=S_CLEAN;cell->repair=0;run.repairs++;run.combo++;if(run.combo>run.maxCombo)run.maxCombo=run.combo;if(run.combo>trackBestCombo)trackBestCombo=run.combo;run.score+=100+run.combo*12+(old==S_PROTECTED?(stageIndex==13?600:300):0);run.energy=run.energy<100?run.energy+3:100;if(old==S_INFECTED){spawnEnemyType(E_VIRUS,x<GW/2?x+3:x-3,y);setStatus("VIRUS RELEASED - MOVE AWAY");}if(old==S_PROTECTED)run.protectedSaved++;if(run.combo%cacheEvery==0){int i,best=0;for(i=1;i<6;i++)if(toolCharges[i]<toolCharges[best])best=i;if(toolCharges[best]<4){toolCharges[best]++;cacheAward=1;}}particle(x,y,0,14);fx(0);if(old==S_UNSTABLE&&unstableCount()==0){cancelPendingSpread(NULL);setStatus("SPREAD CONTAINED: NO YELLOW SECTORS REMAIN");}else if(run.combo==10){achievements|=1;setStatus("ACHIEVEMENT: TEN-SECTOR COMBO");}else if(cacheAward)setStatus(stageIndex==14?"CHECKSUM CACHE: TOOL RECHARGED":"COMBO CACHE: TOOL RECHARGED");else if(old!=S_INFECTED)setStatus("SECTOR RECOVERED");}}'''
replace_function('static void repairCell(float dt)', repair_cell)

complete_stage = r'''static void completeStage(void){int lost=trackStartLives-run.lives;if(lost<0)lost=0;trackRank=(lost==0&&stageClock>=40&&trackBestCombo>=8)?3:(lost==0||stageClock>=25||trackBestCombo>=10)?2:1;runStars+=trackRank;if(runStars>=nextStarLife){nextStarLife+=8;if(run.lives<5){run.lives++;pLives[currentPlayer]=run.lives;setStatus("STAR MILESTONE: EXTRA RECOVERY BOT");}}pendingReward=(stageIndex+trackRank+runStars)%6;stageBonus=(int)(stageClock*25)+1000+run.combo*20+trackRank*500;run.score+=stageBonus;if(run.protectedSaved>=10)achievements|=2;if(challengeMode){if(submitScore(run.score,M_VICTORY))mode=M_INITIALS;else mode=M_VICTORY;stopMusic();saveData();return;}if(stageIndex==19){achievements|=4;if(submitScore(run.score+pScores[1-currentPlayer],M_VICTORY))mode=M_INITIALS;else mode=M_VICTORY;stopMusic();saveData();return;}completedStage=stageIndex;completeTime=0;mode=M_COMPLETE;fx(0);}'''
replace_function('static void completeStage(void)', complete_stage)


# Worms remain threats but can no longer manufacture damaged sectors; yellow sectors are the sole spread source.
update_enemies = r'''static void updateEnemies(float dt){int i;for(i=0;i<MAX_ENEMIES;i++)if(enemies[i].active){Enemy*e=&enemies[i];float dx=px-e->x,dy=py-e->y,d=(float)sqrt(dx*dx+dy*dy)+.001f;e->timer+=dt;switch(e->type){case E_VIRUS:e->vx+=dx/d*dt*1.4f;e->vy+=dy/d*dt*1.4f;break;case E_WORM:e->vx+=dx/d*dt*.35f;e->vy+=dy/d*dt*.35f;if(e->timer>.8f){particle(e->x,e->y,1,2);e->timer=0;}break;case E_TROJAN:if(d<3.2f){e->vx+=dx/d*dt*2.8f;e->vy+=dy/d*dt*2.8f;}else{e->vx*=.97f;e->vy*=.97f;}break;case E_CLUSTER:e->vx+=dx/d*dt*.8f;e->vy+=dy/d*dt*.8f;break;case E_SWEEPER:if(e->aux<3.14f){e->vx=2.8f;e->vy=0;}else{e->vx=0;e->vy=2.8f;}break;case E_MAGNET:{float pull=(stages[stageIndex].boss?2.4f:1.4f)/(d+.5f);px+=(-dx/d)*pull*dt;py+=(-dy/d)*pull*dt;e->vx+=(float)sin(e->timer)*dt;e->vy+=(float)cos(e->timer*.8f)*dt;}break;}e->vx=clampf(e->vx,-3.7f,3.7f);e->vy=clampf(e->vy,-3.7f,3.7f);e->x+=e->vx*dt;e->y+=e->vy*dt;if(e->x<0)e->x=GW-1;if(e->x>GW-1)e->x=0;if(e->y<0)e->y=GH-1;if(e->y>GH-1)e->y=0;if(wallAt((int)(e->x+.5f),(int)(e->y+.5f))){e->vx=-e->vx;e->vy=-e->vy;e->x+=e->vx*.2f;e->y+=e->vy*.2f;}if(firewallTimer>0&&dist2(px,py,e->x,e->y)<2.35f){if(e->type==E_MAGNET){e->vx=-e->vx*1.4f;e->vy=-e->vy*1.4f;e->x+=e->vx*.35f;e->y+=e->vy*.35f;}else{killEnemy(i,60);continue;}}if(dist2(px,py,e->x,e->y)<.72f){if(e->type==E_CLUSTER&&e->hp>1){e->hp=1;spawnEnemyType(E_VIRUS,e->x+.4f,e->y);spawnEnemyType(E_VIRUS,e->x-.4f,e->y);killEnemy(i,100);}else if(e->type!=E_MAGNET)killEnemy(i,25);damage();}}}'''
replace_function('static void updateEnemies(float dt)', update_enemies)


# World update: no invisible/global spread. A yellow source visibly charges, arcs to an adjacent tile, then converts it.
update_world = r'''static void updateWorld(float dt){int x,y,i;const Stage*st=&stages[stageIndex];float dx=0,dy=0,speed=6.5f+(overclock>0?3.2f:0);
 if(pressed('T')){toolGuide=!toolGuide;return;}if(toolGuide){if(pressed(VK_ESCAPE)||pressed(VK_RETURN)||pressed('T'))toolGuide=0;return;}
 if(pressed(VK_ESCAPE)){mode=M_PAUSE;return;}if(pressed(VK_OEM_5)){debugCompleteStage();return;}
 if(pressed('Q'))selectedTool=(selectedTool+TOOL_COUNT-1)%TOOL_COUNT;if(pressed('E'))selectedTool=(selectedTool+1)%TOOL_COUNT;for(i=0;i<TOOL_COUNT;i++)if(pressed('1'+i)){selectedTool=i;useTool();}if(pressed(VK_RETURN)||pressed('F'))useTool();
 if(keys['A']||keys[VK_LEFT])dx--;if(keys['D']||keys[VK_RIGHT])dx++;if(keys['W']||keys[VK_UP])dy--;if(keys['S']||keys[VK_DOWN])dy++;if(dx&&dy){dx*=.7071f;dy*=.7071f;}px=clampf(px+dx*speed*dt,0,GW-1);py=clampf(py+dy*speed*dt,0,GH-1);repairCell(dt);
 stageClock-=dt*(difficulty==0?.85f:difficulty==2?1.15f:1);if(stageClock<=0){damage();stageClock=12;if(mode==M_DYING)return;}
 if(invuln>0)invuln-=dt;if(overclock>0)overclock-=dt;if(sectorLock>0){sectorLock-=dt;if(sectorLock<0)sectorLock=0;}if(firewallTimer>0)firewallTimer-=dt;if(beamFxTimer>0)beamFxTimer-=dt;if(lastToolFlash>0)lastToolFlash-=dt;if(toolFxTimer>0)toolFxTimer-=dt;if(statusTimer>0)statusTimer-=dt;
 if(run.score>=nextOneUpScore){nextOneUpScore+=10000;if(run.lives<5){run.lives++;pLives[currentPlayer]=run.lives;setStatus("1UP! EXTRA RECOVERY BOT AWARDED");particle(px,py,1,45);fx(0);}}
 spawnTimer-=dt;if(spawnTimer<=0){int cap=stageIndex<1?1:stageIndex<3?2:stageIndex<6?3:stageIndex<9?4:stageIndex<14?5:stageIndex==16?7:st->boss?8:6;if(activeEnemyCount()<cap)spawnEnemy();spawnTimer=stageIndex<2?12.0f:stageIndex<4?10.5f:stageIndex<7?9.5f:stageIndex<10?8.5f:7.5f;}
 if(sectorLock<=0&&spreadTimer>0)spreadTimer-=dt;finishPendingSpread(dt);
 missionTimer-=dt;if(missionTimer<=0){runLateMissionEvent();missionTimer=20.0f;}
 magnetPulse+=dt;if(st->magnet){float polarity=(float)sin(magnetPulse*1.7f),cx=GW*.5f,cy=GH*.5f,mdx=cx-px,mdy=cy-py,dd=(float)sqrt(mdx*mdx+mdy*mdy)+.1f;px+=mdx/dd*polarity*dt*(.45f+stageIndex*.018f);py+=mdy/dd*polarity*dt*(.45f+stageIndex*.018f);}
 for(y=0;y<GH;y++)for(x=0;x<GW;x++){Sector*c=&grid[y][x];if(c->type==S_UNSTABLE){if(sectorLock<=0)c->timer+=dt;if(!spreadFxActive&&sectorLock<=0&&spreadTimer<=0&&spreadAdded<spreadCap&&c->timer>(stageIndex==3?12.0f:9.0f))beginUnstableSpread(x,y);}else c->timer+=dt;}
 for(i=0;i<MAX_WALLS;i++)if(walls[i].active){walls[i].life-=dt;if(walls[i].life<=0)walls[i].active=0;}for(i=0;i<MAX_PARTICLES;i++)if(particles[i].active){particles[i].x+=particles[i].vx*dt;particles[i].y+=particles[i].vy*dt;particles[i].life-=dt;if(particles[i].life<=0)particles[i].active=0;}
 updateEnemies(dt);if(mode==M_DYING)return;if(run.repairs>=repairedGoal||damagedSectorCount()==0)completeStage();
}'''
replace_function('static void updateWorld(float dt)', update_world)


# Preserve the earned track reward when restarting a track or switching players.
replace_once(
    "if(pressed('R')){stageSetup();mode=M_STORY;}",
    "if(pressed('R')){pendingReward=activeReward;stageSetup();mode=M_STORY;}",
    'restart reward preservation'
)
replace_once(
    'run.lives=pLives[currentPlayer];stageSetup();mode=M_STORY;setStatus("PLAYER SWITCH");',
    'run.lives=pLives[currentPlayer];pendingReward=activeReward;stageSetup();mode=M_STORY;setStatus("PLAYER SWITCH");',
    'player switch reward preservation'
)

# A clear source-to-target electrical arc makes every spread event readable before the new red sector appears.
spread_draw = r'''
static void drawSpreadFx(HDC dc,int ox,int oy){float p;if(!spreadFxActive)return;p=clampf(1.0f-spreadFxTimer/.90f,0,1);{int sx=GX+spreadFromX*CELL+CELL/2+ox,sy=GY+spreadFromY*CELL+CELL/2+oy,tx=GX+spreadToX*CELL+CELL/2+ox,ty=GY+spreadToY*CELL+CELL/2+oy,k;COLORREF c=((int)(spreadFxTimer*18)&1)?RGB(255,235,70):RGB(255,110,55);int hx=sx+(int)((tx-sx)*p),hy=sy+(int)((ty-sy)*p);outline(dc,sx-13-(int)(p*5),sy-13-(int)(p*5),26+(int)(p*10),26+(int)(p*10),RGB(255,235,70),3);line(dc,sx,sy,hx,hy,RGB(95,70,5),8);line(dc,sx,sy,hx,hy,c,4);for(k=1;k<6;k++){float q=k/6.0f;int bx=sx+(int)((hx-sx)*q),by=sy+(int)((hy-sy)*q)+((k&1)?-3:3);fill(dc,bx-2,by-2,5,5,k&1?RGB(255,245,150):RGB(255,120,55));}outline(dc,tx-12,ty-12,24,24,p>.60f?RGB(255,75,65):RGB(255,220,75),p>.60f?4:2);if(p>.72f){fill(dc,tx-8,ty-8,16,16,((int)(p*20)&1)?RGB(255,75,65):RGB(255,220,75));txt(dc,tx-4,ty-7,12,RGB(30,10,10),"!");}}}
'''
insert_at = s.index('static void drawGame(HDC dc)')
s = s[:insert_at] + spread_draw + s[insert_at:]
replace_once(
    'if(beamFxTimer>0&&beamFxRow>=0)drawBeamFx(dc,ox,oy);',
    'if(beamFxTimer>0&&beamFxRow>=0)drawBeamFx(dc,ox,oy);if(spreadFxActive)drawSpreadFx(dc,ox,oy);',
    'spread animation draw call'
)


# Put the ongoing star progression in the score panel.
replace_once(
    'sprintf(b,"NEXT 1UP %05d",nextOneUpScore);txt(dc,220,70,11,RGB(115,190,210),b);',
    'sprintf(b,"1UP %05d",nextOneUpScore);txt(dc,220,70,11,RGB(115,190,210),b);sprintf(b,"STARS %02d",runStars);txt(dc,352,70,11,RGB(255,205,90),b);',
    'star HUD'
)


# Every briefing names its actual twist and shows the reward carried in from the previous track.
replace_once(
    'if(stageIndex>=8)center(dc,548,16,RGB(105,255,195),lateMissionRule(stageIndex));center(dc,610,19,RGB(225,235,240),"PRESS ENTER / SPACE WHEN READY");',
    'center(dc,530,16,RGB(105,255,195),stageHook(stageIndex));if(activeReward>=0){sprintf(b,"RUN REWARD: %s",rewardName(activeReward));center(dc,560,15,RGB(255,205,90),b);}center(dc,610,19,RGB(225,235,240),"PRESS ENTER / SPACE WHEN READY");',
    'unique mission hook and reward briefing'
)


# Completion is now a reward/teaser screen designed to create a clear one-more-track loop.
draw_start = s.index('static void draw(void)')
branch_start = s.index('}else if(mode==M_COMPLETE){', draw_start)
branch_end = s.index('}else if(mode==M_PLAY||mode==M_PAUSE||mode==M_DYING){', branch_start)
complete_branch = r'''}else if(mode==M_COMPLETE){int k,next=completedStage+1;char rank=trackRank==3?'S':trackRank==2?'A':'B';drawGame(dc);fill(dc,115,125,730,465,RGB(4,10,15));outline(dc,115,125,730,465,((int)(completeTime*8)&1)?RGB(95,255,190):RGB(255,205,80),4);for(k=0;k<20;k++){int sx=140+((k*97+(int)(completeTime*190))%680),sy=145+((k*53+(int)(completeTime*110))%420);fill(dc,sx,sy,4+(k%3)*2,4+(k%3)*2,k%2?RGB(95,255,190):RGB(255,205,80));}center(dc,155,29,RGB(105,255,195),"TRACK RECOVERED!");sprintf(b,"%s COMPLETE",stages[completedStage].name);center(dc,200,32,RGB(235,245,245),b);sprintf(b,"RATING %c     +%d DATA STARS",rank,trackRank);center(dc,252,23,trackRank==3?RGB(105,255,195):RGB(255,205,90),b);sprintf(b,"RUN TOTAL: %d STARS     SCORE %d",runStars,run.score);center(dc,292,18,RGB(200,220,228),b);sprintf(b,"REWARD LOADED: %s",rewardName(pendingReward));center(dc,335,19,RGB(255,205,90),b);fill(dc,155,380,650,125,RGB(7,18,24));outline(dc,155,380,650,125,RGB(80,175,205),2);sprintf(b,"NEXT TRACK %02d: %s",next+1,stages[next].name);center(dc,398,23,RGB(130,220,255),b);center(dc,440,17,RGB(105,255,195),stageHook(next));center(dc,478,15,RGB(165,185,195),"New enemy mixes, rewards and track rules build through all 20 missions.");if(completeTime>=1.0f)center(dc,535,19,RGB(235,245,245),"ENTER / SPACE - LOAD NEXT TRACK");'''
s = s[:branch_start] + complete_branch + s[branch_end:]


p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v2.4 yellow-only spread animation and progression loop')