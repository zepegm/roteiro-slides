@echo off
"C:\Python310\pythonw.exe" "C:\Users\giuseppe.manzella\Desktop\Projetos Python\roteiroslides\app.py"
wmic Path win32_process Where "Caption Like 'cmd%.exe'" Call Terminate