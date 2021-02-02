if not exist settings.py (
    mkdir logs
    mkdir test_files
    copy net/settings_example.py net/settings.py
    copy settings_example.py settings.py
)
echo Setup complete
pause
