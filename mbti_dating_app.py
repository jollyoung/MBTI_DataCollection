import streamlit as st
import gspread
import uuid
from google.oauth2.service_account import Credentials
from datetime import datetime

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
    """세션마다 고유한 UUID를 발급해서 유지"""
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = str(uuid.uuid4())
    return st.session_state["user_id"]


def save_row_to_sheet(row):
    """한 줄 데이터를 시트에 저장"""
    sheet.append_row(row)


def get_scenario_by_mbti(mbti: str):
    """
    MBTI별로 다른 시나리오 반환.
    지금은 예시용으로 4그룹 정도만 다르게 두고,
    나머지는 공용 시나리오를 쓰도록 구성해둘게.
    나중에 너가 각 MBTI에 맞게 자연스럽게 문장만 바꿔도 돼.
    """
    # 기본 템플릿 (공용)
    default = [
        {
            "npc": f"{mbti}인 상대가 살짝 긴장한 표정으로 인사를 건넵니다.",
            "choices": [
                "먼저 밝게 인사하며 분위기를 띄운다",
                "차분하게 천천히 말을 건다",
                "상대가 먼저 이야기 꺼내도록 기다린다",
            ],
        },
        {
            "npc": f"{mbti}인 상대가 취미를 물어봅니다.",
            "choices": [
                "사람 만나는 활동적인 취미를 말한다",
                "혼자서 하는 조용한 취미를 말한다",
                "상대 MBTI에 맞춰 보일 법한 취미를 말한다",
            ],
        },
        {
            "npc": f"{mbti}인 상대가 다음에 또 만날지 조심스럽게 물어봅니다.",
            "choices": [
                "솔직하게 '또 보고 싶다'고 말한다",
                "좀 더 시간을 갖고 생각해보고 싶다고 말한다",
                "상대의 반응을 먼저 떠보며 애매하게 대답한다",
            ],
        },
    ]

    # MBTI 그룹별로 조금씩 다른 느낌 줄 수도 있음 (예시)
    if mbti in ["INFP", "INFJ", "ENFP", "ENFJ"]:
        # 감성/관계 중심형 (NF)
        return [
            {
                "npc": f"{mbti}인 상대가 살짝 수줍게 웃으며 인사를 건넵니다.",
                "choices": [
                    "상대의 이름을 부르며 반갑게 인사한다",
                    "너무 부담스럽지 않게 미소 지으며 인사한다",
                    "가볍게 농담을 섞어 긴장을 풀어준다",
                ],
            },
            {
                "npc": "상대가 '요즘 마음이 꽂힌 것'이 있는지 물어봅니다.",
                "choices": [
                    "최근에 감명 깊게 본 영화나 책 이야기를 나눈다",
                    "요즘 힘들었던 이야기를 솔직하게 조금 나눈다",
                    "상대의 이야기를 먼저 더 들어보고 싶다고 말한다",
                ],
            },
            {
                "npc": "상대가 '나와 대화해보니 어떤 느낌이냐'고 조심스레 물어봅니다.",
                "choices": [
                    "함께 있으면 편안하다고 솔직하게 말한다",
                    "아직 잘 모르겠지만 알아가고 싶다고 말한다",
                    "상대가 어떻게 느끼는지 먼저 물어본다",
                ],
            },
        ]

    if mbti in ["INTJ", "INTP", "ENTJ", "ENTP"]:
        # 분석/아이디어형 (NT)
        return [
            {
                "npc": f"{mbti}인 상대가 담백하게 인사를 건넵니다.",
                "choices": [
                    "논리적으로 호기심을 자극하는 질문을 던진다",
                    "요즘 생각하고 있는 주제를 꺼내본다",
                    "가볍게 날씨 이야기 정도만 하며 탐색한다",
                ],
            },
            {
                "npc": "상대가 '요즘 가장 흥미로운 주제'가 뭐냐고 묻습니다.",
                "choices": [
                    "최근 관심 있는 지적/전문적인 주제를 얘기한다",
                    "상대가 흥미로워할 만한 주제를 골라서 얘기한다",
                    "상대에게 먼저 물어보고 거기에 맞춰 대화를 맞춘다",
                ],
            },
            {
                "npc": "상대가 '서로 아이디어를 나누며 더 만나보면 좋겠다'고 합니다.",
                "choices": [
                    "구체적인 다음 약속(전시, 행사 등)을 제안한다",
                    "대화가 더 필요하다고 느끼는 점을 솔직하게 말한다",
                    "상대의 제안에 공감만 표현하고 여지를 남긴다",
                ],
            },
        ]

    if mbti in ["ISFJ", "ISTJ", "ESFJ", "ESTJ"]:
        # 책임감/안정형 (SJ)
        return [
            {
                "npc": f"{mbti}인 상대가 예의 바르게 인사를 건넵니다.",
                "choices": [
                    "예의 바르고 단정하게 인사한다",
                    "유머를 살짝 섞되 선을 넘지 않는다",
                    "상대가 불편하지 않게 최대한 배려하며 말한다",
                ],
            },
            {
                "npc": "상대가 '휴일에는 보통 어떻게 보내냐'고 묻습니다.",
                "choices": [
                    "규칙적인 루틴과 계획적인 휴일을 말한다",
                    "가끔은 즉흥적인 하루도 즐긴다고 말한다",
                    "가족/지인과 함께 보내는 시간을 강조한다",
                ],
            },
            {
                "npc": "상대가 '앞으로도 연락 이어가고 싶다'고 말합니다.",
                "choices": [
                    "연락 빈도나 방법을 구체적으로 제안한다",
                    "부담스럽지 않게 천천히 알아가자고 말한다",
                    "당장은 바쁘지만 기회가 되면 보자고 말한다",
                ],
            },
        ]

    if mbti in ["ISFP", "ISTP", "ESFP", "ESTP"]:
        # 즉흥/체험형 (SP)
        return [
            {
                "npc": f"{mbti}인 상대가 가볍게 농담 섞인 인사를 합니다.",
                "choices": [
                    "그 분위기를 그대로 받아 장난을 섞어준다",
                    "살짝 웃으며 자연스럽게 맞장구친다",
                    "조금 진지하게 자기소개를 먼저 한다",
                ],
            },
            {
                "npc": "상대가 '바로 지금 같이 뭐 하면 좋을까?'라고 묻습니다.",
                "choices": [
                    "가볍게 할 수 있는 액티비티를 제안한다",
                    "조용한 카페에서 대화 더 나누자고 한다",
                    "상대에게 하고 싶은 걸 먼저 제안해보라고 한다",
                ],
            },
            {
                "npc": "상대가 '다음에 더 재밌는 걸 해보자'고 제안합니다.",
                "choices": [
                    "바로 다음에 할 수 있는 활동을 함께 구체적으로 정한다",
                    "재미있을 것 같다며 긍정적으로만 반응한다",
                    "서로 시간 날 때 연락하자며 여지만 남긴다",
                ],
            },
        ]

    # 위에 없는 MBTI는 default 사용
    return default


# ===========================
# UI 시작
# ===========================
st.title("내 MBTI를 공략해라 🔍")
st.write("당신의 MBTI를 공략하려면 어떤 행동이 효과적인지 알아보는 익명 데이터 수집 게임입니다.")

user_id = get_or_create_user_id()

sex = st.selectbox("성별", ["남성", "여성"])
age = st.number_input("나이", min_value=10, max_value=100, value=20)
my_mbti = st.selectbox(
    "당신의 MBTI",
    [
        "INFP","INFJ","INTP","INTJ","ISFP","ISFJ","ISTP","ISTJ",
        "ENFP","ENFJ","ENTP","ENTJ","ESFP","ESFJ","ESTP","ESTJ",
    ],
)

st.write("---")

# 1단계: 공략 전략 선택 (데이터로만 기록, 시나리오는 MBTI 기준)
st.subheader("1단계: 처음에 어떤 성격으로 보여야 호감도가 올라갈까요?")

attack_style = st.radio(
    "상대에게 보여주고 싶은 첫인상",
    ["밝고 활발", "차갑고 이성적", "차분하고 안정적"],
)

st.write("※ 아래 시나리오는 당신의 MBTI에 맞춰 구성됩니다. (위 선택지는 '공략 전략' 데이터로만 사용)")

st.write("---")

# MBTI 기준 시나리오 가져오기
scenario_steps = get_scenario_by_mbti(my_mbti)

st.subheader("2~4단계: MBTI 맞춤 시나리오 진행")

choices_and_scores = []

for idx, step in enumerate(scenario_steps):
    st.markdown(f"### 🗣 NPC: {step['npc']}")
    choice = st.radio(
        f"선택지 {idx+1}",
        step["choices"],
        key=f"choice_{idx}",
    )
    score = st.slider(
        f"이 선택이 {my_mbti}인 상대에게 얼마나 효과적일 것 같나요? (0~10)",
        0,
        10,
        5,
        key=f"score_{idx}",
    )
    choices_and_scores.append((choice, score))
    st.write("---")

if st.button("제출"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 시트에 저장할 한 줄 구성
    # 시트 헤더 예시:
    # user_id, sex, age, my_mbti, npc_mbti, attack_style,
    # step1_choice, step1_score, step2_choice, step2_score, step3_choice, step3_score, timestamp
    row = [
        user_id,
        sex,
        age,
        my_mbti,
        my_mbti,        # NPC MBTI = 내 MBTI
        attack_style,   # 공략 전략
    ]
    for choice, score in choices_and_scores:
        row.extend([choice, score])
    row.append(timestamp)

    save_row_to_sheet(row)

    st.success("데이터가 저장되었습니다! 참여해줘서 고마워요 🙌")

