set %destination%=C:\Python37\Lib\site-packages\clay

robocopy . %destination% /mir
if exist %destination%\README.md (
    title Install complete
    cd %destination%
) else (
    title Install failed
)
pause
