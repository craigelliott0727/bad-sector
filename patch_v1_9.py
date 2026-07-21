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


# Shared state for the one-shot procedural animation shown whenever a utility is activated.
replace_once(
    'static float px,py,invuln,spawnTimer,spreadTimer,stageClock,stageIntro,introTime,completeTime,screenShake,magnetPulse,overclock,sectorLock,firewallTimer,beamFxTimer,lastToolFlash,deathTimer;',
    'static float px,py,invuln,spawnTimer,spreadTimer,stageClock,stageIntro,introTime,completeTime,screenShake,magnetPulse,overclock,sectorLock,firewallTimer,beamFxTimer,lastToolFlash,deathTimer,toolFxTimer,toolFxX,toolFxY;',
    'tool animation float state'
)
replace_once(
    'static int beamFxRow=-1,lastToolUsed=-1,nextOneUpScore=5000,gameOverHasHighScore=0;',
    'static int beamFxRow=-1,lastToolUsed=-1,nextOneUpScore=5000,gameOverHasHighScore=0,toolFxKind=-1;',
    'tool animation kind state'
)
replace_once(
    'overclock=0;sectorLock=0;firewallTimer=0;beamFxTimer=0;beamFxRow=-1;lastToolUsed=-1;lastToolFlash=0;deathTimer=0;gameOverHasHighScore=0;',
    'overclock=0;sectorLock=0;firewallTimer=0;beamFxTimer=0;beamFxRow=-1;lastToolUsed=-1;lastToolFlash=0;deathTimer=0;gameOverHasHighScore=0;toolFxTimer=0;toolFxKind=-1;',
    'tool animation reset'
)
replace_once(
    'if(sectorLock>0)sectorLock-=dt;if(firewallTimer>0)firewallTimer-=dt;if(beamFxTimer>0)beamFxTimer-=dt;if(lastToolFlash>0)lastToolFlash-=dt;',
    'if(sectorLock>0)sectorLock-=dt;if(firewallTimer>0)firewallTimer-=dt;if(beamFxTimer>0)beamFxTimer-=dt;if(lastToolFlash>0)lastToolFlash-=dt;if(toolFxTimer>0)toolFxTimer-=dt;',
    'tool animation countdown'
)

# Status messages now occupy the narrow strip between the HUD and board instead of covering sectors.
status_banner = r'''static void drawStatusBanner(HDC dc,const char*msg){
 int blink=((int)(GetTickCount64()/180)&1);fill(dc,73,95,814,17,RGB(3,10,15));outline(dc,73,95,814,17,blink?RGB(255,215,80):RGB(105,255,195),1);center(dc,96,13,RGB(245,245,220),msg);
}'''
replace_function('static void drawStatusBanner(HDC dc,const char*msg)', status_banner)

# Restore the full names and keep them at the same size as their second lines.
replace_once(
    'static const char*line1[]={"A-VIRUS","SECTOR","DEFRAG","BACKUP","OVER","FIRE","EMERGENCY"};',
    'static const char*line1[]={"ANTIVIRUS","SECTOR","DEFRAG","BACKUP","OVERCLOCK","FIREWALL","EMERGENCY"};',
    'full toolbar names'
)
replace_once(
    'static const char*line2[]={"PULSE","LOCK","BEAM","RESTORE","CLOCK","WALL","REBOOT"};',
    'static const char*line2[]={"PULSE","LOCK","BEAM","RESTORE","","","REBOOT"};',
    'toolbar second lines'
)
replace_once(
    'drawToolIcon(dc,i,x+42,y+15,ink);txt(dc,x+70,y+5,10,ink,line1[i]);if(line2[i][0])txt(dc,x+70,y+17,10,ink,line2[i]);',
    'drawToolIcon(dc,i,x+40,y+15,ink);txt(dc,x+66,y+5,10,ink,line1[i]);if(line2[i][0])txt(dc,x+66,y+17,10,ink,line2[i]);',
    'toolbar label positioning'
)

# Replace system beeps with short generated arcade sounds. Damage is a distinct two-part ERR-ERR.
sfx = r'''static void put16le(unsigned char*p,int v){p[0]=(unsigned char)(v&255);p[1]=(unsigned char)((v>>8)&255);}
static void put32le(unsigned char*p,unsigned int v){p[0]=(unsigned char)(v&255);p[1]=(unsigned char)((v>>8)&255);p[2]=(unsigned char)((v>>16)&255);p[3]=(unsigned char)((v>>24)&255);}
static void fx(int kind){
 static unsigned char banks[4][44144];static int nextBank;int rate=22050,frames=kind==1?7600:kind==2?4200:4600,i,slot=nextBank++&3;unsigned char*b=banks[slot];int16_t*pcm=(int16_t*)(b+44);double t,u,f,env,v=0;
 if(!soundOn)return;memcpy(b,"RIFF",4);put32le(b+4,36+frames*2);memcpy(b+8,"WAVEfmt ",8);put32le(b+16,16);put16le(b+20,1);put16le(b+22,1);put32le(b+24,rate);put32le(b+28,rate*2);put16le(b+32,2);put16le(b+34,16);memcpy(b+36,"data",4);put32le(b+40,frames*2);
 for(i=0;i<frames;i++){t=(double)i/rate;v=0;
  if(kind==1){
   if(t<.125){u=t/.125;f=225-95*u;env=sin(PI*u);v=(sin(2*PI*f*t)+.42*sin(2*PI*f*2.03*t)+.22*sin(2*PI*f*3.91*t))*env;}
   else if(t>.175&&t<.325){u=(t-.175)/.150;f=205-100*u;env=sin(PI*u);v=(sin(2*PI*f*t)+.48*sin(2*PI*f*2.07*t)+.20*sin(2*PI*f*4.13*t))*env;}
   pcm[i]=(int16_t)(v*7600);
  }else if(kind==2){
   int pulse=(int)(t/.085);u=fmod(t,.085)/.085;env=(pulse<2)?(1-u):0;f=pulse?105:135;v=(sin(2*PI*f*t)+.45*sin(2*PI*f*2.5*t))*env;pcm[i]=(int16_t)(v*5200);
  }else{
   static const int tones[4]={523,659,784,1047};int note=(int)(t/.065);u=fmod(t,.065)/.065;env=note<4?(1-u):0;f=tones[note<4?note:3];v=(sin(2*PI*f*t)+.24*sin(2*PI*f*2*t))*env;pcm[i]=(int16_t)(v*6200);
  }
 }
 PlaySoundA((LPCSTR)b,NULL,SND_MEMORY|SND_ASYNC|SND_NODEFAULT);
}'''
replace_function('static void fx(int kind)', sfx)

# Richer procedural soundtrack: stereo melody, harmony, bass and percussion instead of one square note.
music = r'''static double triOsc(double phase){phase-=floor(phase);return 1.0-4.0*fabs(phase-.5);}
static void startMusic(int tense){
 int rate=22050,seconds=16,frames=rate*seconds,i;WAVEFORMATEX fmt={WAVE_FORMAT_PCM,2,rate,rate*4,4,16,0};
 static const int melodyA[32]={330,392,440,523,0,440,392,330,294,349,392,494,0,392,349,294,330,392,440,587,523,440,392,349,294,330,349,440,392,349,294,262};
 static const int melodyB[32]={220,262,277,330,0,277,247,220,196,233,262,311,0,262,233,196,220,247,277,349,330,277,247,220,185,220,233,294,262,233,220,196};
 static const int rootsA[8]={110,98,87,82,110,98,73,82};static const int rootsB[8]={73,65,62,55,73,65,58,55};
 int16_t*pcm;stopMusic();if(!musicOn)return;musicData=(uint8_t*)malloc(frames*4);if(!musicData)return;pcm=(int16_t*)musicData;
 for(i=0;i<frames;i++){double t=(double)i/rate,sps=tense?5.0:4.0,stepPos=t*sps,stepFrac=stepPos-floor(stepPos),env=(1-stepFrac)*.82+.18;int step=((int)stepPos)&31,bar=((int)(t/2.0))&7;double mf=(tense?melodyB[step]:melodyA[step]);double root=(tense?rootsB[bar]:rootsA[bar]);double mel=0,chord,bass,kick=0,snare=0,hat=0,beat=fmod(t,0.5),quarter=fmod(t,1.0);unsigned int nz=(unsigned int)i*1664525u+1013904223u;double noise=((double)((nz>>16)&255)/127.5)-1.0;double left,right;
  if(mf>0)mel=(sin(2*PI*mf*t)+.28*sin(2*PI*mf*2*t)+.18*triOsc(mf*t))*env;
  chord=(sin(2*PI*root*2*t)+sin(2*PI*root*2*1.259921*t)+sin(2*PI*root*2*1.498307*t))/3.0;
  bass=.70*triOsc(root*t)+.30*sin(2*PI*root*.5*t);
  if(beat<.115)kick=sin(2*PI*(75-38*(beat/.115))*t)*exp(-beat*24);
  if(quarter>.48&&quarter<.62)snare=noise*exp(-(quarter-.48)*24);
  if(fmod(t,.25)<.035)hat=noise*exp(-fmod(t,.25)*70);
  left=mel*(step&1?.19:.29)+chord*.12+bass*.20+kick*.18+snare*.075+hat*.035;
  right=mel*(step&1?.29:.19)+chord*.12+bass*.20+kick*.18+snare*.075-hat*.035;
  if(left>1)left=1;if(left<-1)left=-1;if(right>1)right=1;if(right<-1)right=-1;pcm[i*2]=(int16_t)(left*23000);pcm[i*2+1]=(int16_t)(right*23000);
 }
 ZeroMemory(&musicHdr,sizeof(musicHdr));musicHdr.lpData=(LPSTR)musicData;musicHdr.dwBufferLength=frames*4;if(waveOutOpen(&waveOut,WAVE_MAPPER,&fmt,0,0,CALLBACK_NULL)==MMSYSERR_NOERROR){waveOutPrepareHeader(waveOut,&musicHdr,sizeof(musicHdr));musicHdr.dwFlags|=WHDR_BEGINLOOP;musicHdr.dwLoops=0xffffffff;waveOutWrite(waveOut,&musicHdr,sizeof(musicHdr));}
}'''
replace_function('static void startMusic(int tense)', music)

# Every utility now triggers a named empty warning and a unique visible effect.
replace_once(
    'static void useTool(void){int i,x=(int)(px+.5f),y=(int)(py+.5f);if(toolCharges[selectedTool]<=0){setStatus("UTILITY EMPTY");return;}toolCharges[selectedTool]--;lastToolUsed=selectedTool;lastToolFlash=.70f;switch(selectedTool)',
    'static void useTool(void){static const char*toolFullNames[]={"ANTIVIRUS PULSE","SECTOR LOCK","DEFRAG BEAM","BACKUP RESTORE","OVERCLOCK","FIREWALL","EMERGENCY REBOOT"};char empty[64];int i,x=(int)(px+.5f),y=(int)(py+.5f);if(toolCharges[selectedTool]<=0){sprintf(empty,"%s EMPTY",toolFullNames[selectedTool]);setStatus(empty);fx(2);return;}toolCharges[selectedTool]--;lastToolUsed=selectedTool;lastToolFlash=.70f;toolFxKind=selectedTool;toolFxTimer=1.10f;toolFxX=px;toolFxY=py;switch(selectedTool)',
    'named empty tool and animation trigger'
)

tool_fx = r'''
static void fxRing(HDC dc,int cx,int cy,int r,COLORREF c,int thick){HPEN p=CreatePen(PS_SOLID,thick,c);HPEN op=(HPEN)SelectObject(dc,p);HBRUSH ob=(HBRUSH)SelectObject(dc,GetStockObject(NULL_BRUSH));Ellipse(dc,cx-r,cy-r,cx+r,cy+r);SelectObject(dc,ob);SelectObject(dc,op);DeleteObject(p);}
static void drawToolFx(HDC dc){
 float p;if(toolFxTimer<=0||toolFxKind<0)return;p=clampf(1.0f-toolFxTimer/1.10f,0,1);{int cx=GX+(int)(toolFxX*CELL)+CELL/2,cy=GY+(int)(toolFxY*CELL)+CELL/2,k;
  switch(toolFxKind){
   case TOOL_PULSE:for(k=0;k<3;k++){float q=fmod(p+k*.24f,1.0f);fxRing(dc,cx,cy,12+(int)(q*130),q>.72f?RGB(255,230,95):RGB(90,255,220),q>.72f?2:4);}for(k=0;k<12;k++){double a=k*PI/6;int r=28+(int)(p*85);line(dc,cx+(int)(cos(a)*12),cy+(int)(sin(a)*12),cx+(int)(cos(a)*r),cy+(int)(sin(a)*r),RGB(105,255,215),2);}break;
   case TOOL_LOCK:{int sy=GY+(int)(p*GH*CELL);COLORREF c=((int)(p*18)&1)?RGB(255,215,75):RGB(105,255,195);outline(dc,GX-5,GY-5,GW*CELL+10,GH*CELL+10,c,3);line(dc,GX,sy,GX+GW*CELL,sy,c,3);for(k=0;k<8;k++){int xx=GX+(k%4)*(GW*CELL/3),yy=k<4?GY:GY+GH*CELL;line(dc,xx-8,yy,xx+8,yy,c,3);}}break;
   case TOOL_BEAM:fxRing(dc,cx,cy,15+(int)(p*34),RGB(255,245,145),3);break;
   case TOOL_BACKUP:for(k=0;k<7;k++){int sx=GX+35+((k*113)%730),sy=GY+25+((k*71)%470)-(int)((1-p)*45);COLORREF c=(k&1)?RGB(95,210,255):RGB(105,255,195);outline(dc,sx,sy,22,18,c,2);fill(dc,sx+5,sy+4,12,6,c);line(dc,sx+11,sy+18,cx,cy,RGB(45,115,135),1);}fxRing(dc,cx,cy,18+(int)(p*52),RGB(105,255,195),2);break;
   case TOOL_OVERCLOCK:{int pcx=GX+(int)(px*CELL)+CELL/2,pcy=GY+(int)(py*CELL)+CELL/2;for(k=0;k<6;k++){double a=k*PI/3+p*5;int r=24+(k&1)*10;line(dc,pcx,pcy,pcx+(int)(cos(a)*r),pcy+(int)(sin(a)*r),k&1?RGB(255,235,90):RGB(105,255,230),3);}line(dc,pcx-30,pcy+18,pcx-12,pcy+8,RGB(105,255,220),2);line(dc,pcx-42,pcy+25,pcx-18,pcy+14,RGB(255,220,75),2);}break;
   case TOOL_FIREWALL:{int pcx=GX+(int)(px*CELL)+CELL/2,pcy=GY+(int)(py*CELL)+CELL/2,r=25+(int)(p*18);COLORREF c=RGB(105,255,195);line(dc,pcx,pcy-r,pcx+r,pcy-r/2,c,3);line(dc,pcx+r,pcy-r/2,pcx+r,pcy+r/2,c,3);line(dc,pcx+r,pcy+r/2,pcx,pcy+r,c,3);line(dc,pcx,pcy+r,pcx-r,pcy+r/2,c,3);line(dc,pcx-r,pcy+r/2,pcx-r,pcy-r/2,c,3);line(dc,pcx-r,pcy-r/2,pcx,pcy-r,c,3);for(k=-2;k<=2;k++)line(dc,pcx-r+5,pcy+k*7,pcx+r-5,pcy+k*7,RGB(55,140,130),1);}break;
   case TOOL_REBOOT:{int sy=GY+(int)(p*GH*CELL);outline(dc,GX-7,GY-7,GW*CELL+14,GH*CELL+14,((int)(p*20)&1)?RGB(255,225,100):RGB(105,255,195),4);fill(dc,GX,sy,GW*CELL,7,RGB(225,255,235));for(k=0;k<12;k++){int gy=GY+((k*47+(int)(p*300))%(GH*CELL));fill(dc,GX+((k*83)%700),gy,35+(k%4)*18,3,k&1?RGB(255,95,80):RGB(95,255,210));}}break;
  }
 }
}
'''
insert_at = s.index('static void drawGame(HDC dc)')
s = s[:insert_at] + tool_fx + s[insert_at:]
replace_once('drawToolBar(dc);', 'drawToolFx(dc);drawToolBar(dc);', 'tool animation draw call')

# F10 is a test-only level-complete key. It awards each remaining repair and then the normal stage bonus.
debug_complete = r'''
static void debugCompleteStage(void){int x,y;for(y=0;y<GH;y++)for(x=0;x<GW;x++)if(grid[y][x].type!=S_CLEAN){SectorType old=(SectorType)grid[y][x].type;grid[y][x].type=S_CLEAN;grid[y][x].repair=0;run.repairs++;run.combo++;if(run.combo>run.maxCombo)run.maxCombo=run.combo;run.score+=100+run.combo*12+(old==S_PROTECTED?300:0);if(old==S_PROTECTED)run.protectedSaved++;if(run.energy<100)run.energy=run.energy+3>100?100:run.energy+3;}particle(px,py,0,70);setStatus("F10 TEST: TRACK COMPLETED");completeStage();}
'''
insert_at = s.index('static void updateEnemies(float dt)')
s = s[:insert_at] + debug_complete + s[insert_at:]
replace_once(
    'if(pressed(VK_ESCAPE)){mode=M_PAUSE;return;}',
    'if(pressed(VK_ESCAPE)){mode=M_PAUSE;return;}if(pressed(VK_F10)){debugCompleteStage();return;}',
    'F10 test completion hotkey'
)

p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v2.1 audio, utility effects, status strip and test hotkey')
