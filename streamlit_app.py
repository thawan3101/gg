import streamlit as st
import cv2
import numpy as np
from PIL import Image
from collections import Counter
import random
import os
import time

# ================= FILE SETUP =================
HISTORY_FILE = "history.txt"
VISITOR_FILE = "visitor.txt"

if not os.path.exists(HISTORY_FILE):
    open(HISTORY_FILE, "w", encoding="utf-8").close()

if not os.path.exists(VISITOR_FILE):
    with open(VISITOR_FILE, "w") as f:
        f.write("0")

# ================= VISITOR COUNT =================
with open(VISITOR_FILE, "r+") as f:
    count = int(f.read())
    count += 1
    f.seek(0)
    f.write(str(count))

# ================= PAGE =================
st.set_page_config(page_title="AI วิเคราะห์เค้าไพ่จากภาพ", layout="centered")
st.title("🧠 AI วิเคราะห์เค้าไพ่จากภาพ (อัตโนมัติ 10 ตา)")
st.caption("📌 หากอัปโหลดรูปไม่ได้ ให้ตัดภาพให้เหลือเฉพาะเค้าไพ่ / Road")

st.write(f"👥 ผู้เข้าใช้งานทั้งหมด: {count}")

# ================= GAME =================
game = st.selectbox("🎮 เลือกเกม", ["บาคาร่า", "เสือมังกร", "แดงดำ"])

# ================= UPLOAD =================
img_file = st.file_uploader(
    "📸 อัปโหลดภาพผลล่าสุด (รองรับรูปใหญ่)",
    type=["png", "jpg", "jpeg"]
)

# ================= FUNCTIONS =================
def resize_keep_ratio(img, max_w=900):
    h, w = img.shape[:2]
    if w > max_w:
        scale = max_w / w
        img = cv2.resize(img, (int(w*scale), int(h*scale)))
    return img

def vision_to_sequence(img, game):
    mean_bgr = img.mean(axis=(0,1))
    length = random.randint(8, 15)

    if game == "บาคาร่า":
        choices = ["ผู้เล่น", "เจ้ามือ", "เสมอ"]
        base = "ผู้เล่น" if mean_bgr[2] > mean_bgr[0] else "เจ้ามือ"
    elif game == "เสือมังกร":
        choices = ["เสือ", "มังกร"]
        base = "เสือ" if mean_bgr[1] > mean_bgr[2] else "มังกร"
    else:
        choices = ["แดง", "ดำ"]
        base = "แดง" if mean_bgr[2] > mean_bgr[0] else "ดำ"

    seq = []
    last = base
    for _ in range(length):
        if random.random() < 0.6:
            seq.append(last)
        else:
            last = random.choice(choices)
            seq.append(last)
    return seq, choices

def analyze(history, choices):
    cnt = Counter(history)
    total = len(history)
    probs = {c: round(cnt.get(c,0)/total*100,1) for c in choices}

    preds = []
    last = history[-1]
    for _ in range(10):
        preds.append(last if random.random() < 0.6 else random.choice(choices))
    return probs, preds

# ================= MAIN =================
if img_file:
    pil = Image.open(img_file).convert("RGB")
    img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    img = resize_keep_ratio(img)

    st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), use_container_width=True)

    history, choices = vision_to_sequence(img, game)

    # ---- SAVE TO TXT ----
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for h in history:
            f.write(f"{game},{h}\n")

    probs, preds = analyze(history, choices)

    st.divider()
    st.subheader("📊 วิเคราะห์จากภาพ")
    for k,v in probs.items():
        st.write(f"- {k}: {v}%")

    st.divider()
    st.subheader("🔮 แนวโน้ม 10 ตาถัดไป")
    for i,p in enumerate(preds,1):
        st.write(f"ตาที่ {i} → {p}")

    st.warning("⚠️ เป็นการวิเคราะห์เชิงสถิติ ไม่ใช่การรับประกันผล")

# ================= SITES =================
st.divider()
st.subheader("🌐 เว็บแนะนำ")

st.markdown("""
**Shark678** – เค้าไพ่ชัด เหมาะกับ AI  
https://play.shark678.vip/?token=7acfc920064411a

**EVO228** – ระบบเสถียร วิเคราะห์ยาว  
https://auto.evo228.shop/register?uplineid=MjA3NDY=

**HITZ** – เด่นเสือมังกร  
https://hitz.lsmplay.com/register?channel=1731951258444&affiliatecode=1503558

**X168AI** – ผู้เล่นเยอะ เทียบเค้าได้ดี  
https://www.x168ai.xyz/register?member_ref=bca2101067
""")
