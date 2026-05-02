from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
import requests
import io

app = FastAPI()

API_KEY = "5HZyFZtXdM8Tdawsrhj1Z5bi"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>AI 去背 SaaS</title>
<style>
body {
    font-family: Arial;
    background: #0f172a;
    color: white;
    text-align: center;
}
.card {
    margin: 80px auto;
    padding: 30px;
    width: 400px;
    background: rgba(255,255,255,0.08);
    border-radius: 20px;
}
button {
    margin-top: 20px;
    padding: 10px 20px;
    background: #22c55e;
    border: none;
    border-radius: 10px;
    color: white;
}
img { margin-top: 20px; max-width: 300px; }
</style>
</head>
<body>
<div class="card">
<h2>🔥 AI 去背 SaaS</h2>
<input type="file" id="file"/>
<br>
<button onclick="upload()">開始去背</button>
<p id="status"></p>
<img id="result"/>
</div>

<script>
async function upload() {
    const file = document.getElementById("file").files[0];
    if (!file) return alert("請選圖片");

    const form = new FormData();
    form.append("file", file);

    document.getElementById("status").innerText = "處理中...";

    const res = await fetch("/remove-bg", {
        method: "POST",
        body: form
    });

    if (!res.ok) {
        alert("失敗");
        return;
    }

    const blob = await res.blob();
    document.getElementById("result").src = URL.createObjectURL(blob);
    document.getElementById("status").innerText = "完成";
}
</script>

</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE


@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()

        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": image_bytes},
            data={"size": "auto"},
            headers={"X-Api-Key": API_KEY},
        )

        if response.status_code != 200:
            return JSONResponse({"error": response.text})

        return StreamingResponse(io.BytesIO(response.content), media_type="image/png")

    except Exception as e:
        return JSONResponse({"error": str(e)})