robocopy . C:\Python37\Lib\site-packages\clay /mir
if exist C:\Python37\Lib\site-packages\clay\README.md (
    title Install complete
) else (
    title Install failed
)
pause
