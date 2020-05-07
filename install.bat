set %destination%=C:\Python37\Lib\site-packages\clay

robocopy . %destination% /mir
if exist %destination%\README.md (
    title Install complete
    title Installing dependencies...
    pip install bs4 requests
    title Done
    cd %destination%
) else (
    title Install failed
)
pause
