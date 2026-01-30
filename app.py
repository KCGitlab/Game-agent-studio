import streamlit as st
from openai import OpenAI, RateLimitError, OpenAIError
from datetime import datetime
import os
import time

# ------------------ CACHE RESET ------------------
st.cache_resource.clear()

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="GameMaster AI 🎮",
    page_icon="🎮",
    layout="wide"
)

# ------------------ RATE LIMIT CONFIG ------------------
MIN_SECONDS_BETWEEN_CALLS = 20  # safe limit
if "last_api_call" not in st.session_state:
    st.session_state.last_api_call = 0

# ------------------ API KEY CHECK ------------------
if "OPENAI_API_KEY" not in st.secrets:
    st.error("❌ OPENAI_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ------------------ UI HEADER ------------------
st.title("🎮 GameMaster AI – Your AI Game Studio Partner")
st.markdown("""
Welcome! Generate **game concepts, levels, NPC logic, strategies, stories, avatars, and animations**  
all powered by GPT-5 AI.
""")

# ------------------ SIDEBAR OPTIONS ------------------
feature = st.sidebar.selectbox(
    "Select Agent Capability",
    [
        "Game Concept Generator",
        "Level & Environment Designer",
        "NPC Behavior Designer",
        "Game Strategy Assistant",
        "Dialogue & Story Scripting",
        "Avatar & Character Creation",
        "Game Animation Designer"
    ]
)

language = st.sidebar.selectbox(
    "Output Language",
    [
        "English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada",
        "Malayalam", "Bengali", "Gujarati", "Punjabi", "Spanish",
        "French", "German", "Japanese", "Korean", "Chinese"
    ]
)

user_prompt = st.text_area(
    "Enter your idea or requirement:",
    height=160,
    placeholder="Example: Create a sci-fi RPG villain with AI-driven decision-making..."
)

generate = st.button("🚀 Generate Output")

# ------------------ PROMPT ENGINE ------------------
def build_prompt(feature, user_input, language):
    base = f"""
You are GameMaster AI, a professional game designer and AI assistant.  
Respond strictly in {language}. Ensure clarity, professional terminology, and structure.
"""
    prompts = {
        "Game Concept Generator": """
Generate a full game concept including:
- Genre
- Core gameplay loop
- Story theme
- Unique mechanics
- Target audience
""",
        "Level & Environment Designer": """
Design a detailed game level including:
- Environment & terrain
- Player challenges
- Enemy placement
- Rewards & progression
""",
        "NPC Behavior Designer": """
Create NPC behavior including:
- Role
- Decision rules
- Emotional states
- Behavior tree (pseudo-code)
""",
        "Game Strategy Assistant": """
Analyze and improve gameplay strategy:
- Balance fixes
- Player engagement
- Difficulty tuning
- Retention mechanics
""",
        "Dialogue & Story Scripting": """
Write immersive narrative:
- Characters
- Quests
- Branching dialogues
- Story arcs
""",
        "Avatar & Character Creation": """
Design game avatar:
- Visual appearance
- Personality
- Outfit & accessories
- Animation notes
""",
        "Game Animation Designer": """
Design animations:
- Type (idle, walk, combat, emote)
- Keyframes & transitions
- Engine-ready animation notes
"""
    }

    return f"{base}\nTask:\n{prompts[feature]}\nUser Input:\n{user_input}"

# ------------------ OPENAI GPT-5 CALL ------------------
def generate_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": "You are a professional game development AI agent."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1200
        )

        # ✅ Correct access for GPT-5
        content = response.choices[0].message.content
        if content:
            return content
        return "⚠️ Model returned no visible text output."

    except Exception as e:
        return f"❌ OpenAI API error: {e}"


# ------------------ SAVE OUTPUT ------------------
def save_output(feature, content, language):
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/{feature.replace(' ', '_')}_{language}_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

# ------------------ STREAMLIT OUTPUT ------------------
if generate:
    now = time.time()
    elapsed = now - st.session_state.last_api_call

    if elapsed < MIN_SECONDS_BETWEEN_CALLS:
        st.warning(f"⏳ Please wait {int(MIN_SECONDS_BETWEEN_CALLS - elapsed)} seconds before generating again.")
        st.stop()

    if not user_prompt.strip():
        st.warning("⚠️ Please enter a prompt.")
        st.stop()

    st.session_state.last_api_call = now

    with st.spinner("🎮 GameMaster AI is generating..."):
        final_prompt = build_prompt(feature, user_prompt, language)
        output = generate_response(final_prompt)

    file_path = save_output(feature, output, language)

    st.subheader(f"🧠 Agent Output ({language})")
    st.markdown(output)

    with open(file_path, "rb") as file:
        st.download_button(
            label="⬇️ Download Output",
            data=file,
            file_name=os.path.basename(file_path),
            mime="text/plain"
        )
