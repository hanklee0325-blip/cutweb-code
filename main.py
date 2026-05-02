from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from io import BytesIO

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return HTMLResponse("""
    <h1>AI 去背 SaaS</h1>
    <form action="/remove-bg" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">去背</button>
    </form>
    """)

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    input_data = await file.read()
    output = remove(input_data)

    return HTMLResponse(
        content=f"<h3>完成</h3><a download='output.png' href='data:image/png;base64,{output}'>下載</a>"
    )