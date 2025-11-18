import streamlit as st
import gspread
import uuid
from google.oauth2.service_account import Credentials
from datetime import datetime

# ===========================
# Google Sheets 연결
# ===========================
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(credentials)
sheet = client.open("MBTI_Dating_Data").sheet1


# ===========================
# 함수
# ===========================
def create_uuid():
    """고유 사용자 UUID 생성"""
    return str(uuid.uuid4())


def save_to_sheet(row):
    """Google Sheets에 한 줄 저장"""
    sheet.append_row(row)


def scenario_for_mbti(style):
    """성격 선택(밝고/차갑고/차분함)에 따라 시나리오 반환"""

    return {
        "밝고 활발": [
            {
                "npc": "안녕하세요! 소개받게 되어 반갑습니다!",
                "choices": ["밝게 인사하기", "미소만 지으며 인사", "장난치며 인사"]
            },
            {
                "npc": "취미가 어떻게 되세요?",
                "choices": ["운동 좋아해요", "여행 좋아해요", "그냥 쉬는 게 좋아요"]
            },
            {
                "npc": "다음에 또 뵐까요?",
                "choices": ["좋아요!", "음… 생각해볼게요", "아직 잘 모르겠어요"]
            }
        ],

        "차갑고 이성적": [
            {
                "npc": "오늘 약속 잘 지켜서 왔네요.",
                "choices": ["예의 바르게 대답", "담백하게 '네'만 말하기", "직설적으로 말하기"]
            },
            {
                "npc": "최근 읽은 책 있으세요?",
                "choices": ["심리학 책", "경제 관련 책", "소설 책"]
            },
            {
                "npc": "다음 미팅 잡을까요?",
                "choices": ["좋습니다", "아직은 잘…", "천천히 생각하고 싶어요"]
            }
        ],

        "차분하고 안정적": [
            {
                "npc": "편하게 이야기 나눠요.",
                "choices": ["부드럽게 대답", "조용히 끄덕임", "‘긴장되네요’라고 말함"]
            },
            {
                "npc": "어떤 취미 좋아하세요?",
                "choices": ["산책", "요리", "음악 듣기"]
            },
            {
                "npc": "또 만날까요?",
                "choices": ["네, 좋아요", "글쎄요", "천천히 알아가요"]
            }
        ]
    }[style]


# ===========================
# UI
# ===========================
st.title("내 MBTI를 공략해라! ❤️‍🔥")
st.write("※ 당신의 MBTI를 공략하려면 어떤 선택이 효과적인지 데이터를 수집하는 게임입니다.")

# 유저 정보
sex = st.selectbox("성별", ["남성", "여성"])
age = st.number_input("나이", min_value=10, max_value=100, value=20)
my_mbti = st.selectbox("당신의 MBTI", [
    "INFP","INFJ","INTP","INTJ","ISFP","ISFJ","ISTP","ISTJ",
    "ENFP","ENFJ","ENTP","ENTJ","ESFP","ESFJ","ESTP","ESTJ"
])

st.write("---")

# 1단계: 첫인상 컨셉 선택
st.subheader("1단계: 첫인상을 어떻게 만들까요?")
first_style = st.radio(
    "첫인상 스타일 선택:",
    ["밝고 활발", "차갑고 이성적", "차분하고 안정적"]
)

# 시나리오 불러오기
scenario = scenario_for_mbti(first_style)

st.write("---")
st.subheader("2~4단계: 시나리오 진행")

all_choices = []

for i, step in enumerate(scenario):
    st.write(f"### 🗣 NPC: {step['npc']}")
    selected = st.radio(f"선택지 {i+1}", step["choices"], key=f"sel_{i}")
    score = st.slider(f"호감도 평가 {i+1} (0~10)", 0, 10, 5, key=f"score_{i}")
    all_choices.append((selected, score))
    st.write("---")

# 제출 버튼
if st.button("제출"):
    user_id = create_uuid()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = [
        user_id,
        sex,
        age,
        my_mbti,      # 유저 MBTI
        my_mbti,      # NPC MBTI = 유저 MBTI
        first_style   # 첫 번째 선택
    ]

    # 각 단계 선택 + 점수 저장
    for selected, score in all_choices:
        row.extend([selected, score])

    row.append(timestamp)

    save_to_sheet(row)

    st.success("🎉 데이터가 성공적으로 저장되었습니다! 참여해주셔서 감사합니다.")
