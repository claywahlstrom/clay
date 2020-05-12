if not exist settings.py (
    mkdir logs
    mkdir test_files
    copy settings_example.py settings.py
)
echo Setup complete
pause
