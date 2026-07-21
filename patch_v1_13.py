from pathlib import Path

p = Path('bad_sector.c')
s = p.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Could not find {label}')
    s = s.replace(old, new, 1)


# Daily disks should also activate spreading whenever their board contains yellow sectors.
replace_once(
    'spreadTimer=stageUsesUnstable(stageIndex)?7.0f:999.0f;',
    'spreadTimer=(challengeMode||stageUsesUnstable(stageIndex))?7.0f:999.0f;',
    'daily yellow spread timer'
)

# Combo-cache recharges are introduced on Track 8 rather than being available from the beginning.
replace_once(
    'if(run.combo%cacheEvery==0){int i,best=0;',
    'if(stageIndex>=7&&run.combo%cacheEvery==0){int i,best=0;',
    'combo cache unlock point'
)

# Emergency Reboot may damage sectors, but it must not introduce a nonfunctional yellow tile on a no-spread track.
replace_once(
    'case TOOL_REBOOT:for(i=0;i<MAX_ENEMIES;i++)if(enemies[i].active)killEnemy(i,20);repairedGoal+=corruptRandom(5);invuln=3;setStatus("EMERGENCY REBOOT: THREATS CLEARED / 5 SECTORS DAMAGED");break;',
    'case TOOL_REBOOT:for(i=0;i<MAX_ENEMIES;i++)if(enemies[i].active)killEnemy(i,20);repairedGoal+=corruptRandom(5);if(!challengeMode&&!stageUsesUnstable(stageIndex))for(y=0;y<GH;y++)for(x=0;x<GW;x++)if(grid[y][x].type==S_UNSTABLE)grid[y][x].type=S_CORRUPT;invuln=3;setStatus("EMERGENCY REBOOT: THREATS CLEARED / 5 SECTORS DAMAGED");break;',
    'reboot yellow-sector semantics'
)

s = s.replace('PROTECTED P DATA BUILDS BONUS STARS', 'PROTECTED P DATA PAYS BONUS POINTS')

p.write_text(s, encoding='utf-8')
print('Applied Bad Sector v2.4.1 yellow-sector semantic fixes')