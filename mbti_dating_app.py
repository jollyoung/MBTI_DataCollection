import streamlit as st
import gspread
import uuid
from google.oauth2.service_account import Credentials
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

# ===========================
# 경로 설정
# ===========================
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

# ===========================
# CSS / HTML 로더
# ===========================
def load_css(file_path: str):
    css_file = ASSETS_DIR / file_path
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def load_html_template(file_path: str) -> str:
    html_file = ASSETS_DIR / file_path
    with open(html_file, "r", encoding="utf-8") as f:
        return f.read()


# ===========================
# 채팅 UI 헬퍼
# ===========================
def make_chat_renderer(template: str, role: str):
    def render(text: str):
        html = template.replace("{{role}}", role).replace("{{text}}", text)
        st.markdown(html, unsafe_allow_html=True)
    return render


def choice_buttons(choices, key: str):
    # 카톡 버튼 느낌은 CSS로, 실제 선택은 radio로 처리
    return st.radio("선택지", choices, key=key)


# ===========================
# Google Sheets 연결
# ===========================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
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
    except Exception:
        return False  # 에러 발생시 중복여부 알 수 없으므로 기본 False로 처리


def get_scenario_by_mbti(mbti):
    # 간단한 예시 시나리오 (기존 것 유지)
    return [
        {
            "npc": f"{mbti}인 상대가 조용히 미소 지으며 인사합니다.",
            "choices": ["밝게 먼저 인사한다", "조용히 인사한다", "상대의 리드를 기다린다"],
        },
        {
            "npc": "상대가 ‘요즘 뭐하며 지내냐’고 묻습니다.",
            "choices": ["일/학업 이야기", "취미 이야기", "요즘 생각 많은 이야기"],
        },
        {
            "npc": "상대가 ‘또 보고 싶다’고 합니다.",
            "choices": ["다음 약속을 구체적으로 잡기", "천천히 알아가자고 말하기", "부담되지 않게 여지만 남기기"],
        },
    ]


# ===========================
# 스타일 & 템플릿 로드
# ===========================
load_css("styles.css")
chat_template = load_html_template("chat_template.html")

chat_npc = make_chat_renderer(chat_template, "npc")
chat_user = make_chat_renderer(chat_template, "user")


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
    [
        "INFP",
        "INFJ",
        "INTP",
        "INTJ",
        "ISFP",
        "ISFJ",
        "ISTP",
        "ISTJ",
        "ENFP",
        "ENFJ",
        "ENTP",
        "ENTJ",
        "ESFP",
        "ESFJ",
        "ESTP",
        "ESTJ",
    ],
)

st.write("---")

# 1단계 — 공략 전략 선택
chat_npc("첫인상은 어떻게 보여야 좋을까요?")

attack_style = st.radio(
    "",
    ["밝고 활발", "차갑고 이성적", "차분하고 안정적"],
)

chat_user(attack_style.replace("", ""))  # 유저가 선택한 내용을 말풍선처럼 오른쪽에 표시

st.write("---")
st.subheader("MBTI 맞춤 시나리오 진행")

scenario_steps = get_scenario_by_mbti(my_mbti)
choices_only = []

for idx, step in enumerate(scenario_steps):
    # NPC 대사
    chat_npc(step["npc"])
    # 유저 선택
    choice = choice_buttons(step["choices"], key=f"choice_{idx}")
    chat_user(choice)
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
        my_mbti,  # NPC MBTI = 유저 MBTI
        attack_style,  # 첫인상 전략
    ]

    for c in choices_only:
        row.append(c)

    row.append(timestamp)

    save_row_to_sheet(row)
    st.success("데이터가 저장되었습니다! 참여해줘서 고마워요 🙌")
