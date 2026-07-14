from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse  # تم إضافة هذا السطر
from pydantic import BaseModel
import google.generativeai as genai
import os

# ==========================================
# 1. إعداد الـ API Key
# ==========================================
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# ==========================================
# 2. قراءة ملف معلومات المشروع بشكل ديناميكي صح على Vercel
# ==========================================
base_dir = os.path.dirname(os.path.dirname(__file__))
txt_path = os.path.join(base_dir, "WATHIGZ.txt")

try:
    with open(txt_path, "r", encoding="utf-8") as file:
        knowledge_base = file.read()
except FileNotFoundError:
    knowledge_base = "Project information file not found."

# ==========================================
# 3. إعداد الذكاء الاصطناعي (Gemini)
# ==========================================
system_instruction = f"""
You are 'WattZilla AI', the official AI assistant for the WattZilla Power Analyzer project.
Use the following project documentation to answer user questions accurately.
If the user asks something outside this documentation, answer using your general engineering knowledge but clarify that it's a general concept.
Always format mathematical equations using LaTeX (e.g., $$equation$$).

Project Documentation:
{knowledge_base}
"""

model = genai.GenerativeModel(
    model_name="gemini-3.5-flash",
    system_instruction=system_instruction
)

# ==========================================
# 4. إعداد السيرفر (FastAPI)
# ==========================================
app = FastAPI()

# تفعيل الـ CORS عشان الموقع (HTML) يقدر يكلم السيرفر بدون مشاكل أمنية
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# هيكل الرسالة اللي جاية من الموقع
class ChatRequest(BaseModel):
    message: str

# ==========================================
# 5. المسار الرئيسي لعرض صفحة الـ HTML (تمت إضافته)
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html_path = os.path.join(base_dir, "WATTZILA2.HTML")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>HTML file not found! Please make sure WATTZILA2.HTML is in the root directory.</h1>", 
            status_code=404
        )

# المسار (Endpoint) اللي الموقع بيبعت عليه الأسئلة
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # إرسال السؤال للذكاء الاصطناعي
        response = model.generate_content(request.message)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Sorry, a system error occurred: {str(e)}"}
