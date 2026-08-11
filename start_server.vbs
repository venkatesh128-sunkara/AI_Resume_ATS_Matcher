Set ws = CreateObject("WScript.Shell")
ws.Run "cmd /c cd /d ""C:\Users\S Venkatesh\Desktop\new\resume-ats"" && python -m streamlit run app.py --server.port=8501 --server.headless=true >> ""C:\Users\SVENKA~1\AppData\Local\Temp\opencode\ats_server.log"" 2>&1", 0, False
