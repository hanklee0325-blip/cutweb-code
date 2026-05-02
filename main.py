from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from PIL import Image
import io
import asyncio

app = FastAPI(title="AI Background Removal SaaS")

# CORS（給前端用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# 🔥 SaaS 前端頁面
# ---------------------------
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>AI 去背 SaaS</title>
    <style>
        body {
            margin: 0;
            font-family: Arial;
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: white;
            text-align: center;
        }

        .box {
            margin-top: 80px;
            padding: 30px;
        }

        .card {
            background: rgba(255,255,255,0.08);
            padding: 30px;
            border-radius: 20px;
            width: 420px;
            margin: auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }

        input {
            margin-top: 15px;
        }

        button {
            margin-top: 20px;
            padding: 12px 20px;
            border: none;
            border-radius: 10px;
            background: #22c55e;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }

        button:hover {
            background: #16a34a;
        }

        img {
            margin-top: 20px;
            max-width: 300px;
            border-radius: 10px;
        }

        .title {
            font-size: 28px;
            font-weight: bold;
        }

        .sub {
            opacity: 0.7;
            margin-top: 5px;
        }

        .ad {
            margin-top: 30px;
            font-size: 12px;
            opacity: 0.5;
        }
    </style>
</head>

<body>
<div class="box">
    <div class="card">
        <div class="title">🔥 AI 去背 SaaS</div>
        <div class="sub">Upload image → auto remove background</div>

        <input type="file" id="file"/><br>

        <button onclick="upload()">開始去背</button>

        <div id="loading"></div>

        <img id="result"/>

        <div class="ad">
            📢 Google Ads 位置（未接入）
        </div>
    </div>
</div>

<script>
async function upload() {
    const file = document.getElementById("file").files[0];
    if (!file) {
        alert("請選圖片");
        return;
    }

    const form = new FormData();
    form.append("file", file);

    document.getElementById("loading").innerText = "處理中...";

    const res = await fetch("/remove-bg", {
        method: "POST",
        body: form
    });

    if (!res.ok) {
        alert("失敗");
        return;
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    document.getElementById("result").src = url;
    document.getElementById("loading").innerText = "完成";
}
</script>

</body>
</html>
"""

# ---------------------------
# 🔥 首頁（不再 404）
# ---------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE


# ---------------------------
# 🔥 去背 API（核心）
# ---------------------------
@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    try:
        input_data = await file.read()

        loop = asyncio.get_event_loop()

        # 避免 blocking（Render 會卡的原因之一）
        result = await loop.run_in_executor(None, process_image, input_data)

        return StreamingResponse(io.BytesIO(result), media_type="image/png")

    except Exception as e:
        return JSONResponse({"error": str(e)})


# ---------------------------
# 🔥 image processing
# ---------------------------
def process_image(data):
    img = Image.open(io.BytesIO(data))
    output = remove(img)
    buf = io.BytesIO()
    output.save(buf, format="PNG")
    return buf.getvalue()