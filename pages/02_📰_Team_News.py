import streamlit as st
import os
from io import BytesIO
from PIL import Image

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="News scraper")

# --- Global variables ---
TEAMS = [
    "Alaves", "Athletic Bilbao", "Atletico Madrid", "Barcelona", "Betis",
    "Celta de Vigo", "Elche", "Espanyol", "Getafe", "Girona",
    "Levante", "Mallorca", "Osasuna", "Oviedo", "Rayo Vallecano",
    "Real Madrid", "Real Sociedad", "Sevilla FC", "Valencia", "Villareal"
]

CREST_DIR = "./team_crests"

# --- Team selector top of page ---
clicked_team = None

@st.cache_data
def load_rectangle_png(path: str, width: int = 100, height: int = 120, transparent_bg: bool = True) -> bytes | None:
    """
    Open image, scale it down to fit inside (width, height),
    then center it with padding so the final size is exactly (width x height).
    """
    if not os.path.exists(path):
        return None

    img = Image.open(path).convert("RGBA")
    # Scale down preserving aspect ratio
    img.thumbnail((width, height), Image.LANCZOS)
    w, h = img.size

    bg = (255, 255, 255, 0) if transparent_bg else (255, 255, 255, 255)
    canvas = Image.new("RGBA", (width, height), bg)
    canvas.paste(img, ((width - w) // 2, (height - h) // 2), img)

    buf = BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue()

# First row (10 teams)
cols = st.columns(10)
for i in range(10):
    team = TEAMS[i]
    with cols[i].container(border=True):
        crest_path = os.path.join(CREST_DIR, f"{team}.png")
        data = load_rectangle_png(crest_path, width=100, height=120, transparent_bg=True)
        if data is not None:
            st.image(data, width=100, use_container_width=True)  # render with fixed width
        else:
            st.write("🛡️ [Logo missing]")
        if st.button(team, key=f"btn_{team}", use_container_width=True):
            clicked = team

# Second row (next 10 teams)
cols = st.columns(10)
for i in range(10, 20):
    team = TEAMS[i]
    with cols[i-10].container(border=True):
        crest_path = os.path.join(CREST_DIR, f"{team}.png")
        data = load_rectangle_png(crest_path, width=100, height=120, transparent_bg=True)
        if data is not None:
            st.image(data, width=100, use_container_width=True)  # render with fixed width
        else:
            st.write("🛡️ [Logo missing]")
        if st.button(team, key=f"btn_{team}", use_container_width=True):
            clicked = team

if clicked_team:
    st.success(f"You clicked: {clicked_team}")

