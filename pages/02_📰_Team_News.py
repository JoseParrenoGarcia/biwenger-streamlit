import streamlit as st
import os
from io import BytesIO
from PIL import Image
from supabase_client.connection import get_supabase_client
from supabase_client.utils import (
    check_if_table_exists
)

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="News scraper")

# --- Session state initialization ---
if "clicked_team" not in st.session_state:
    st.session_state.clicked_team = None


# --- Global variables ---
TEAMS = [
    "Alaves", "Athletic Bilbao", "Atletico Madrid", "Barcelona", "Betis",
    "Celta de Vigo", "Elche", "Espanyol", "Getafe", "Girona",
    "Levante", "Mallorca", "Osasuna", "Oviedo", "Rayo Vallecano",
    "Real Madrid", "Real Sociedad", "Sevilla FC", "Valencia", "Villareal"
]

CREST_DIR = "./team_crests"

supabase = get_supabase_client()
table_name = "article_for_streamlit"
if not check_if_table_exists(supabase, table_name):
    st.warning(f"⚠️ Table '{table_name}' does not exist.")

# --- Team selector top of page ---
# clicked_team = None

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


@st.cache_data
def load_all_news_articles() -> dict:
    result = supabase.table(table_name).select("*").execute()
    if result and result.data:
        return result.data
    return {}

# First row (10 teams)
cols = st.columns(10)
for i in range(10):
    team = TEAMS[i]
    with cols[i].container(border=True):
        crest_path = os.path.join(CREST_DIR, f"{team}.png")
        data = load_rectangle_png(crest_path, width=100, height=120, transparent_bg=True)
        if data is not None:
            st.image(data, use_container_width=True)  # render with fixed width
        else:
            st.write("🛡️ [Logo missing]")
        if st.button(team, key=f"btn_{team}", use_container_width=True):
            st.session_state.clicked_team = team

# Second row (next 10 teams)
cols = st.columns(10)
for i in range(10, 20):
    team = TEAMS[i]
    with cols[i-10].container(border=True):
        crest_path = os.path.join(CREST_DIR, f"{team}.png")
        data = load_rectangle_png(crest_path, width=100, height=120, transparent_bg=True)
        if data is not None:
            st.image(data, use_container_width=True)  # render with fixed width
        else:
            st.write("🛡️ [Logo missing]")
        if st.button(team, key=f"btn_{team}", use_container_width=True):
            st.session_state.clicked_team = team

if st.session_state.clicked_team:
    with st.container(border=True):
        result = load_all_news_articles()
        team_rows = [r for r in result if r.get("team") == st.session_state.clicked_team]
        st.success(f"Has elegido: {st.session_state.clicked_team}. Encontrados {len(team_rows)} resumenes.")

        with st.container(border=True):
            with st.expander("Lesiones y sanciones..."):
                lesiones = [r for r in team_rows if r.get("tag") == '["lesiones_sanciones"]']
                st.write(lesiones[0]['markdown_document'])

        with st.container(border=True):
            with st.expander("Previa de proximos partidos..."):
                st.write("Aqui va el detalle de la previa de proximos partidos")

        with st.container(border=True):
            with st.expander("Cronicas de partidos anteriores..."):
                st.write("Aqui va el detalle de las cronicas de partidos anteriores")

        with st.container(border=True):
            with st.expander("Fichajes..."):
                st.write("Aqui va el detalle de los fichajes")




