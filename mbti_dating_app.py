# ======================
# UI 시작 부분에 추가
# ======================
load_css("assets/styles.css")
chat_template = load_html_template("assets/chat_template.html")

st.title("내 MBTI를 공략해라 🔍")

user_id = get_or_create_user_id()

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

# 1단계
chat_npc("첫인상은 어떻게 보여야 좋을까요?")
attack_style = st.radio(
    "",
    ["밝고 활발", "차갑고 이성적", "차분하고 안정적"]
)
chat_user(attack_style)

st.write("---")

# 2~4단계: 시나리오 진행
scenario_steps = get_scenario_by_mbti(my_mbti)
choices_only = []

for idx, step in enumerate(scenario_steps):
    chat_npc(step["npc"])
    choice = choice_buttons(step["choices"], key=f"c{idx}")
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
        my_mbti,
        attack_style,
    ]

    for c in choices_only:
        row.append(c)

    row.append(timestamp)

    save_row_to_sheet(row)
    st.success("데이터가 저장되었습니다! 참여해주셔서 고마워요 🙌")
