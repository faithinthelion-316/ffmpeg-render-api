from fastapi import FastAPI
import subprocess
app = FastAPI ()
@app.get ("/")
def root ():
  return {"status": "running"}
