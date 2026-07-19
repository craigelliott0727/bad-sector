@echo off
setlocal
where gcc >nul 2>nul || (
  echo MinGW-w64 GCC was not found in PATH.
  echo Install MSYS2/MinGW-w64 i686 and run this file from its 32-bit shell.
  pause
  exit /b 1
)
gcc -std=c99 -Os -s -mwindows -march=i686 -ffunction-sections -fdata-sections -Wl,--gc-sections -o BadSector.exe bad_sector.c -lgdi32 -lwinmm -lm
if errorlevel 1 exit /b 1
for %%A in (BadSector.exe) do echo Built BadSector.exe - %%~zA bytes
pause
