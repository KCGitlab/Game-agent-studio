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
MIN_SECONDS_BETWEEN_CALLS = 25  # affordable & safe
if "last_api_call" not in st.session_state:
    st.session_state.last_api_call = 0

# ------------------ API KEY CHECK ------------------
if "OPENAI_API_KEY" not in st.secrets:
    st.error("❌ OPENAI_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ------------------ UI HEADER ------------------
st.title("🎮 GameMaster AI – The Ultimate Gaming Agent")
st.markdown(
    """
Your **AI Game Studio Partner**  
Concepts • Levels • NPC Logic • Strategy • Story • Avatars • Animations
"""
)

# ------------------ SIDEBAR ------------------
feature = st.sidebar.radio(
    "Select Agent Capability",
    [
        "Game Concept Generator",
        "Level & Environment Designer",
        "NPC Behavior Designer",
        "Game Strategy Assistant",
        "Dialogue & Story Scripting",
        "Avatar Creation for Games",
        "Game Animation Creation"
    ]
)

language = st.sidebar.selectbox(
    "Select Output Language",
    [
        "English",
        "Hindi",
        "Marathi",
        "Tamil",
        "Telugu",
        "Kannada",
        "Malayalam",
        "Bengali",
        "Gujarati",
        "Punjabi",
        "Spanish",
        "French",
        "German",
        "Japanese",
        "Korean",
        "Chinese"
    ]
)

user_prompt = st.text_area(
    "Enter your idea / requirement:",
    height=160,
    placeholder="Example: A cyberpunk RPG boss character with emotional AI..."
)

generate = st.button("🚀 Generate Agent Output")

# ------------------ PROMPT ENGINE ------------------
def build_prompt(feature, user_input, language):
    base = f"""
You are GameMaster AI, an expert game designer and game AI architect.
Generate the output strictly in {language} language.
Ensure clarity, structure, and professional game development terminology.
"""

    prompts = {
        "Game Concept Generator": """
Create a complete game concept including:
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
Create NPC behavior logic including:
- NPC role
- Decision rules
- Emotional states
- Behavior tree (pseudo-code)
""",
        "Game Strategy Assistant": """
Analyze and improve gameplay strategy including:
- Balance fixes
- Player engagement
- Difficulty tuning
- Retention mechanics
""",
        "Dialogue & Story Scripting": """
Write immersive game narrative including:
- Characters
- Quests
- Branching dialogue
- Story arcs
""",
        "Avatar Creation for Games": """
Design a game-ready avatar including:
- Visual appearance
- Personality traits
- Outfit & accessories
- Animation style
- Game engine notes (Unity / Unreal)
""",
        "Game Animation Creation": """
Create animation design including:
- Animation type (idle, walk, combat, emote)
- Keyframes description
- Timing & transitions
- Engine-ready animation logic
"""
    }

    return f"""
{base}

Task:
{prompts[feature]}

User Input:
{user_input}
"""

# ------------------ OPENAI CALL (SAFE) ------------------
def generate_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": "You are a professional game development AI agent."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700
        )
        return response.choices[0].message.content

    except RateLimitError:
        return "⚠️ Rate limit reached. Please wait a minute and try again."

    except OpenAIError as e:
        return f"❌ OpenAI API error: {str(e)}"

# ------------------ FILE SAVE ------------------
def save_output(feature, content, language):
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/{feature.replace(' ', '_')}_{language}_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

# ------------------ OUTPUT ------------------
if generate:
    now = time.time()
    elapsed = now - st.session_state.last_api_call

    if elapsed < MIN_SECONDS_BETWEEN_CALLS:
        st.warning(
            f"⏳ Please wait {int(MIN_SECONDS_BETWEEN_CALLS - elapsed)} seconds before generating again."
        )
        st.stop()

    if not user_prompt.strip():
        st.warning("⚠️ Please enter a prompt.")
        st.stop()

    st.session_state.last_api_call = now

    with st.spinner("GameMaster AI is working... 🎮"):
        final_prompt = build_prompt(feature, user_prompt, language)
        output = generate_response(final_prompt)

    file_path = save_output(feature, output, language)

    st.subheader(f"🧠 Agent Output ({language})")
    st.markdown(output)

    with open(file_path, "rb") as file:
        st.download_button(
            label="⬇️ Download Agent Output",
            data=file,
            file_name=os.path.basename(file_path),
            mime="text/plain"
        )
