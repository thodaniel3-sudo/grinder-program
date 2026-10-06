@echo off
echo Backing up database...
set BACKUP_DIR=backup_%date:~10,4%%date:~4,2%%date:~7,2%
mkdir %BACKUP_DIR%
copy data\grinding_polisher.db %BACKUP_DIR%\
echo Backup created in %BACKUP_DIR%
pause