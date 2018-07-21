robocopy . C:\Python36\Lib\site-packages\clay /mir
if exist C:\Python36\Lib\site-packages\clay\README.md (
    title Setup Complete
) else (
    title Setup Failed
)
pause
