import streamlit as st
import gspread
import uuid
from google.oauth2.service_account import Credentials
from datetime import datetime
from zoneinfo import ZoneInfo

# ===========================
# Google Sheets 연결
# ===========================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(credentials)
sheet = client.open("MBTI_Dating_Data").sheet1


# ===========================
# 헬퍼 함수들
# ===========================
def get_or_create_user_id():
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = str(uuid.uuid4())
    return st.session_state["user_id"]


def save_row_to_sheet(row):
    sheet.append_row(row)


def has_submitted_before(user_id):
    """이미 이 user_id로 제출한 적 있는지 확인"""
    try:
        data = sheet.col_values(1)  # 1열 = user_id
        return user_id in data
    except:
        return False  # 에러 발생시 중복여부 알 수 없으므로 기본 False로 처리


# 간단한 시나리오 템플릿 (예시)
def get_scenario_by_mbti(mbti):
    return [
        {
            "npc": f"{mbti}인 상대가 조용히 미소 지으며 인사합니다.",
            "choices": ["밝게 먼저 인사한다", "조용히 인사한다", "상대의 리드를 기다린다"]
        },
        {
            "npc": "상대가 ‘요즘 뭐하며 지내냐’고 묻습니다.",
            "choices": ["일/학업 이야기", "취미 이야기", "요즘 생각 많은 이야기"]
        },
        {
            "npc": "상대가 ‘또 보고 싶다’고 합니다.",
            "choices": ["다음 약속을 구체적으로 잡기", "천천히 알아가자고 말하기", "부담되지 않게 여지만 남기기"]
        }
    ]


# ===========================
# UI
# ===========================
st.title("내 MBTI를 공략해라 🔍")
st.write("당신의 MBTI를 공략하려면 어떤 행동이 효과적인지 알아보는 익명 데이터 수집 게임입니다.")

user_id = get_or_create_user_id()

# 중복 제출 여부 체크
already_submitted = has_submitted_before(user_id)

if already_submitted:
    st.error("⚠ 이미 참여한 기록이 있습니다. 한 번만 참여할 수 있어요!")
    st.stop()


sex = st.selectbox("성별", ["남성", "여성"])
age = st.number_input("나이", min_value=10, max_value=100, value=20)
my_mbti = st.selectbox(
    "당신의 MBTI",
    ["INFP","INFJ","INTP","INTJ","ISFP","ISFJ","ISTP","ISTJ",
     "ENFP","ENFJ","ENTP","ENTJ","ESFP","ESFJ","ESTP","ESTJ"]
)

st.write("---")

# 1단계 — 공략 전략 선택
st.subheader("1단계: 어떤 첫인상을 주고 싶나요?")
attack_style = st.radio(
    "보여주고 싶은 첫인상",
    ["밝고 활발", "차갑고 이성적", "차분하고 안정적"]
)

st.write("---")
st.subheader("2~4단계: MBTI 맞춤 시나리오 진행")

scenario_steps = get_scenario_by_mbti(my_mbti)

choices_only = []

for idx, step in enumerate(scenario_steps):
    st.markdown(f"### 🗣 NPC: {step['npc']}")
    choice = st.radio(
        f"선택지 {idx+1}",
        step["choices"],
        key=f"choice_{idx}"
    )
    choices_only.append(choice)
    st.write("---")

# 제출
if st.button("제출"):
    timestamp = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")

    row = [
        user_id,
        sex,
        age,
        my_mbti,
        my_mbti,         # NPC MBTI = 유저 MBTI
        attack_style,    # 첫인상 전략
    ]

    for c in choices_only:
        row.append(c)

    row.append(timestamp)

    save_row_to_sheet(row)
    st.success("데이터가 저장되었습니다! 참여해주셔서 고마워요 🙌")
