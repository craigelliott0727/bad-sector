from pathlib import Path

p = Path('bad_sector.c')
s = p.read_text(encoding='utf-8')

# 1) Floppy insertion: use a larger disk and clip it at the slot so no part can appear behind/above the drive.
start = s.index('static void drawIntro(HDC dc)')
end = s.index('static void drawGame(HDC dc)', start)
intro = r'''static void drawIntro(HDC dc){float t=introTime;char b[120];
 int bodyX=35,bodyY=42,bodyW=890,bodyH=625;
 int screenX=100,screenY=92,screenW=760,screenH=345;
 int driveX=250,driveY=475,driveW=460,driveH=125;
 int slotX=300,slotY=518,slotW=360,slotH=20;
 fill(dc,bodyX,bodyY,bodyW,bodyH,RGB(29,35,44));outline(dc,bodyX,bodyY,bodyW,bodyH,RGB(135,150,160),5);
 fill(dc,screenX,screenY,screenW,screenH,RGB(3,8,12));outline(dc,screenX,screenY,screenW,screenH,RGB(65,84,96),4);
 fill(dc,driveX,driveY,driveW,driveH,RGB(45,53,63));outline(dc,driveX,driveY,driveW,driveH,RGB(110,125,135),4);
 fill(dc,680,555,20,20,t>2.35f&&((int)(t*7)&1)?RGB(75,245,170):RGB(35,62,58));
 if(t<3.1f){float q=t/3.1f;int diskY=(int)(735-q*360);int saved;
   /* The disk is larger and visible only BELOW the slot opening. */
   saved=SaveDC(dc);IntersectClipRect(dc,0,slotY+slotH,W,H);drawFloppy(dc,385,diskY,190,190);RestoreDC(dc,saved);
   /* Draw the drive face and slot lip last so the disk clearly enters the opening. */
   fill(dc,driveX+4,driveY+4,driveW-8,slotY-driveY-4,RGB(45,53,63));
   outline(dc,driveX,driveY,driveW,driveH,RGB(110,125,135),4);
   fill(dc,slotX,slotY,slotW,slotH,RGB(2,5,8));outline(dc,slotX,slotY,slotW,slotH,RGB(165,178,188),2);
   line(dc,slotX,slotY+slotH,slotX+slotW,slotY+slotH,RGB(200,205,210),3);
   center(dc,145,29,RGB(82,245,190),"INSERT DISK INTO DRIVE A:");
   center(dc,205,18,RGB(175,195,205),q<.50f?"WAITING FOR MEDIA...":q<.91f?"MEDIA ENTERING DRIVE...":"DISK LOCKED");
   if(q>.91f)center(dc,385,19,RGB(255,205,90),"CLICK - DRIVE A: READY");
 }else{
   fill(dc,slotX,slotY,slotW,slotH,RGB(2,5,8));outline(dc,slotX,slotY,slotW,slotH,RGB(165,178,188),2);
   if(t<5.2f){float q=(t-3.1f)/2.1f;
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

# Keep the completion celebration onscreen until the player chooses to continue.
s = s.replace(
    "else if(mode==M_COMPLETE){completeTime+=dt;if(completeTime>=2.4f||(completeTime>=1.0f&&(pressed(VK_RETURN)||pressed(VK_SPACE)))){stageIndex=completedStage+1;run.level=stageIndex+1;stageSetup();mode=M_STORY;}}",
    "else if(mode==M_COMPLETE){completeTime+=dt;if(completeTime>=1.0f&&(pressed(VK_RETURN)||pressed(VK_SPACE))){stageIndex=completedStage+1;run.level=stageIndex+1;stageSetup();mode=M_STORY;}}"
)
s = s.replace('completeTime<1.0f?"RECOVERY VERIFIED...":"NEXT MISSION LOADING"',
              'completeTime<1.0f?"RECOVERY VERIFIED...":"RECOVERY COMPLETE"')
s = s.replace('"ENTER / SPACE TO CONTINUE NOW"', '"ENTER / SPACE FOR NEXT MISSION"')

# An infected sector releases its bug several cells away, instead of directly under the player.
s = s.replace('if(old==S_INFECTED)spawnEnemyType(E_VIRUS,x,y);',
              'if(old==S_INFECTED){spawnEnemyType(E_VIRUS,x<GW/2?x+3:x-3,y);setStatus("VIRUS RELEASED - MOVE AWAY");}')

# Restore small life icons next to the large life count.
s = s.replace('txt(dc,50,15,14,RGB(145,170,180),"LIVES");sprintf(b,"%d",run.lives);txt(dc,50,34,38,run.lives<=1?RGB(255,85,85):RGB(105,255,195),b);',
              'txt(dc,50,15,14,RGB(145,170,180),"LIVES");sprintf(b,"%d",run.lives);txt(dc,50,34,38,run.lives<=1?RGB(255,85,85):RGB(105,255,195),b);for(i=0;i<run.lives&&i<3;i++)drawBot(dc,92+i*28,48,0);')

# Upgrade the procedural soundtrack with melody, bass, arpeggio, kick, snare and hi-hat layers.
music_start = s.index('static void startMusic(int tense)')
music_end = s.index('static void particle(', music_start)
music = r'''static void startMusic(int tense){int rate=22050,seconds=16,n=rate*seconds,i;WAVEFORMATEX fmt={WAVE_FORMAT_PCM,1,rate,rate,1,8,0};
 static const int leadA[]={330,392,494,659,494,392,349,440,294,370,440,587,440,370,330,392};
 static const int leadB[]={147,175,220,294,220,175,165,196,131,165,196,262,196,165,147,175};
 static const int bassA[]={82,82,98,98,73,73,110,110}; static const int bassB[]={55,55,65,65,49,49,73,73};
 stopMusic();if(!musicOn)return;musicData=(uint8_t*)malloc(n);if(!musicData)return;
 for(i=0;i<n;i++){double t=(double)i/rate;double beatPos=fmod(t*4.0,1.0),barPos=fmod(t,4.0);int step=(int)(t*4)%16,bstep=(int)(t*2)%8;double lf=(tense?leadB[step]:leadA[step]);double bf=(tense?bassB[bstep]:bassA[bstep]);double lead=(fmod(t*lf,1.0)<.5?1.0:-1.0);double bass=2.0*fabs(2.0*fmod(t*bf,1.0)-1.0)-1.0;double arpF=lf*(step%3==0?2.0:step%3==1?1.5:1.25);double arp=(fmod(t*arpF,1.0)<.18?1.0:-.35);double kick=beatPos<.12?(1.0-beatPos/.12)*sin(2*PI*(78.0-35.0*beatPos/.12)*t):0.0;double snPos=fmod(t*2.0+.5,1.0);double noise=((i*1103515245u+12345u)>>24)/255.0*2.0-1.0;double snare=snPos<.10?(1.0-snPos/.10)*noise:0.0;double hat=beatPos<.045?(1.0-beatPos/.045)*noise:0.0;double pulse=(barPos<.08?1.0:0.0);int v=(int)(128+13*lead+11*bass+6*arp+19*kick+12*snare+5*hat+3*pulse);musicData[i]=(uint8_t)(v<0?0:v>255?255:v);}
 ZeroMemory(&musicHdr,sizeof(musicHdr));musicHdr.lpData=(LPSTR)musicData;musicHdr.dwBufferLength=n;if(waveOutOpen(&waveOut,WAVE_MAPPER,&fmt,0,0,CALLBACK_NULL)==MMSYSERR_NOERROR){waveOutPrepareHeader(waveOut,&musicHdr,sizeof(musicHdr));musicHdr.dwFlags|=WHDR_BEGINLOOP;musicHdr.dwLoops=0xffffffff;waveOutWrite(waveOut,&musicHdr,sizeof(musicHdr));}}

'''
s = s[:music_start] + music + s[music_end:]

# Replace the plain title with an animated arcade attract screen.
title_start = s.index('if(mode==M_TITLE){', s.index('static void draw(void)'))
title_end = s.index('}else if(mode==M_INTRO){', title_start)
title = r'''if(mode==M_TITLE){int x,y;float tt=(float)GetTickCount64()/1000.0f;
 for(y=0;y<9;y++){int yy=150+y*52+(int)(fmod(tt*18+y*9,52));line(dc,80,yy,880,yy,RGB(10,35,42),1);}for(x=0;x<15;x++){int xx=95+x*58;line(dc,xx,145,xx,620,RGB(8,27,34),1);}
 drawFloppy(dc,385,82,190,190);drawMagnet(dc,112,175,24,RGB(235,65,75));drawMagnet(dc,798,175,24,RGB(235,65,75));
 center(dc,48,64,RGB(76,255,186),"BAD SECTOR");center(dc,112,22,RGB(185,205,215),"1.44 MB RECOVERY ARCADE");
 for(x=0;x<6;x++){int bx=178+x*115+(int)(sin(tt*1.4+x)*18),by=300+(int)(cos(tt*1.1+x)*20);fill(dc,bx,by,18,22,RGB(235,65+x*9,82));line(dc,bx,by+5,bx-8,by,RGB(235,80,90),2);line(dc,bx+18,by+5,bx+26,by,RGB(235,80,90),2);}
 fill(dc,185,350,590,205,RGB(4,11,17));outline(dc,185,350,590,205,RGB(75,225,175),3);
 center(dc,370,27,RGB(255,205,90),((int)(tt*2)&1)?"PRESS ENTER TO INSERT DISK":"PRESS ENTER TO START RECOVERY");
 center(dc,423,19,RGB(215,230,238),"C   DAILY RECOVERY DISK");sprintf(b,"2   TWO-PLAYER MODE: %s",twoPlayer?"ON":"OFF");center(dc,458,19,RGB(185,205,215),b);center(dc,493,19,RGB(185,205,215),"H   HIGH SCORES       O   OPTIONS");
 center(dc,585,17,RGB(255,115,90),"MAGNETS DISTORT. VIRUSES ATTACK. EVERY BYTE COUNTS.");center(dc,642,14,RGB(100,130,145),"NATIVE WIN32  /  PROCEDURAL GRAPHICS + AUDIO  /  NO EXTERNAL ASSETS");
 }'''
s = s[:title_start] + title + s[title_end:]

p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v1.5 polish patch')