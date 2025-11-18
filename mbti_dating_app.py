import streamlit as st
import pandas as pd
import gspread
import uuid
from google.oauth2.service_account import Credentials

# ===========================
# Google Sheets 연결
# ===========================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(credentials)
sheet = client.open("MBTI_Dating_Data").sheet1

# ===========================
# 유저 UUID 생성 (세션당 1회)
# ===========================
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())  # 랜덤 고유 ID 생성

user_id = st.session_state.user_id

# ===========================
# UI
# ===========================
st.title("MBTI 데이트 시뮬레이션")
st.write("간단한 소개팅 시뮬레이션을 통해 MBTI별 선호 행동 데이터를 수집합니다.")

# 유저 정보 입력
sex = st.selectbox("성별 선택", ["남성", "여성"])
age = st.number_input("나이 입력", min_value=10, max_value=100, value=20)
my_mbti = st.selectbox("자신의 MBTI 선택", [
    "INFP","INFJ","INTP","INTJ","ISFP","ISFJ","ISTP","ISTJ",
    "ENFP","ENFJ","ENTP","ENTJ","ESFP","ESFJ","ESTP","ESTJ"
])

npc_mbti_options = ["밝고 활발", "차갑고 이성적", "차분하고 안정적"]
npc_mbti = st.selectbox("데이트 상대 유형 선택", npc_mbti_options)

st.write("---")

st.write(f"{npc_mbti} 상대와 첫 만남, 어떻게 행동할까요?")

choice = st.radio("선택지:",
                  ["자신감 있게 먼저 대화 시작", 
                   "조용히 상대 말 듣기", 
                   "장난스럽게 분위기 끌기"])

score = st.slider("상대의 호감도(0~10)", 0, 10, 5)

# ===========================
# 제출 버튼
# ===========================
if st.button("제출"):

    # Google Sheets에서 기존 user_id 목록 가져오기
    rows = sheet.get_all_records()
    existing_ids = [r["user_id"] for r in rows]

    if user_id in existing_ids:
        st.warning("이미 제출한 기록이 있습니다! (중복 제출 방지)")
    else:
        sheet.append_row([user_id, sex, age, my_mbti, npc_mbti, choice, score])
        st.success("데이터가 저장되었습니다! 참여해주셔서 감사합니다.")




