@echo off
echo Running tests for clay...
powershell -Command "ls *py -r | %% { py $_ }"
echo.
echo Tests for clay completed.
