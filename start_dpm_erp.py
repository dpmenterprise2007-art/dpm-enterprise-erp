from pathlib import Path
import os, secrets, sys, threading, time, webbrowser
ROOT=Path(__file__).resolve().parent
BACKEND=ROOT/"backend"
os.chdir(BACKEND)
env=BACKEND/".env"
if not env.exists():
    env.write_text("APP_ENV=local\nAPP_NAME=DPM ENTERPRISE ERP\nDATABASE_URL=sqlite:///./dpm_erp.db\nCORS_ORIGINS=http://127.0.0.1:8000\nJWT_SECRET_KEY="+secrets.token_urlsafe(48)+"\nJWT_ALGORITHM=HS256\nACCESS_TOKEN_EXPIRE_MINUTES=480\n",encoding="utf-8")
sys.path.insert(0,str(BACKEND))
from app.db import Base, engine
from app import models
from app.main import app
import uvicorn
def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000/login")
if __name__=="__main__":
    Base.metadata.create_all(bind=engine)
    threading.Thread(target=open_browser,daemon=True).start()
    print("DPM ERP: http://127.0.0.1:8000  |  Stop: Ctrl+C")
    uvicorn.run(app,host="127.0.0.1",port=8000,reload=False,access_log=False)
