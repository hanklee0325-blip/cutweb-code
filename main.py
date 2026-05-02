from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from rembg import remove
from PIL import Image
import io

app = FastAPI()

# 首頁
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# 去背API
@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    input_bytes = await file.read()

    output = remove(input_bytes)

    return StreamingResponse(
        io.BytesIO(output),
        media_type="image/png",
        headers={
            "Content-Disposition": "attachment; filename=result.png"
        }
    )