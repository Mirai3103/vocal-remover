from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
import os
from queue import Queue
import asyncio
import uvicorn
import subprocess
app = FastAPI()
import sqlite3
import uuid
from enum import Enum
from fastapi.staticfiles import StaticFiles

app.mount("/output", StaticFiles(directory="output"), name="output")
con = sqlite3.connect("database.db")
#  make sure the table is created
con.execute("CREATE TABLE IF NOT EXISTS uploads (id text, filename text,music_path text,vocals_path text,status text)")
con.commit()

class Status(str, Enum):
    PENDING = "PENDING"
    DONE = "DONE"
    FAILED = "FAILED"


UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

queue = Queue()
    #     print('done')
    # sf.write('{}{}_Instruments.wav'.format(output_dir, basename), wave.T, sr)

    # print('inverse stft of vocals...', end=' ')
    # wave = spec_utils.spectrogram_to_wave(v_spec, hop_length=args.hop_length)
    # print('done')
    # sf.write('{}{}_Vocals.wav'.format(output_dir, basename), wave.T, sr)
def get_out_file(input_file):
    output_dir = OUTPUT_FOLDER
    basename = os.path.splitext(os.path.basename(input_file))[0]
    outMusic= os.path.join(output_dir, f"{basename}_Instruments.wav")
    outVocals= os.path.join(output_dir, f"{basename}_Vocals.wav")
    return outMusic, outVocals

async def process_queue():
    while True:
        if not queue.empty():
            file_path = queue.get()
            # move the file to the output folder
            output_file_path = os.path.join(OUTPUT_FOLDER, os.path.basename(file_path))
            # insert the file into the database
            id = str(uuid.uuid4())
            outMusic, outVocals = get_out_file(file_path)
            con.execute("INSERT INTO uploads (id, filename, music_path, vocals_path, status) VALUES (?, ?, ?, ?, ?)", (id, output_file_path, outMusic, outVocals, Status.PENDING))
            os.rename(file_path, output_file_path)
            process = subprocess.Popen(["python", "inference.py", "--input", output_file_path, "--output_dir", OUTPUT_FOLDER], stdout=subprocess.PIPE)
            process.wait()
            if process.returncode == 0:
                os.rename
                con.execute("UPDATE uploads SET status = ? WHERE id = ?", (Status.DONE, id))
            else:
                con.execute("UPDATE uploads SET status = ? WHERE id = ?", (Status.FAILED, id))
            con.commit()
        else:
            await asyncio.sleep(1)

@app.post("/upload")
async def upload_mp3(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(".mp3"):
        return JSONResponse(content={"error": "Only MP3 files are allowed"}, status_code=400)

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    queue.put(file_path)
    background_tasks.add_task(process_queue)

    return {"filename": file.filename}

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)