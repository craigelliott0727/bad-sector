from pathlib import Path

p = Path('bad_sector.c')
s = p.read_text(encoding='utf-8')

# On the initials screen, arrows navigate while letter/number keys type directly.
# This avoids WASD conflicting with the letters W, A, S and D.
update_start = s.index('static void update(float dt)')
branch_start = s.index('else if(mode==M_INITIALS){', update_start)
branch_end = s.index('else if(mode==M_SCORES){', branch_start)
branch = "else if(mode==M_INITIALS){int ci,k;char*c=&highNames[initialsSlot][initialsPos];ci=initialsCharIndex(*c);if(pressed(VK_UP)||pressed(VK_DOWN)){int n=(int)strlen(initialsChars);ci+=pressed(VK_UP)?1:-1;if(ci<0)ci=n-1;if(ci>=n)ci=0;*c=initialsChars[ci];}for(k='A';k<='Z';k++)if(pressed(k)){*c=(char)k;if(initialsPos<2)initialsPos++;}for(k='0';k<='9';k++)if(pressed(k)){*c=(char)k;if(initialsPos<2)initialsPos++;}if(pressed(VK_SPACE)){*c=' ';if(initialsPos<2)initialsPos++;}if(pressed(VK_LEFT)&&initialsPos>0)initialsPos--;if(pressed(VK_RIGHT)&&initialsPos<2)initialsPos++;if(pressed(VK_RETURN)){if(initialsPos<2)initialsPos++;else{saveData();mode=initialsReturnMode;}}if(pressed(VK_BACK)&&initialsPos>0)initialsPos--; }"
s = s[:branch_start] + branch + s[branch_end:]

p.write_text(s, encoding='utf-8')
print('Applied v1.6 high-score control correction')
