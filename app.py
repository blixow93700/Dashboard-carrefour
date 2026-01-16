import streamlit as st
import pandas as pd
import altair as alt
import os

# -----------------------
# 1. CONFIGURATION GLOBALE
# -----------------------
st.set_page_config(
    page_title="Carrefour Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CHEMIN DU LOGO UNIQUEMENT (On oublie l'image de fond) ---
IMG_LOGO_PATH = r"C:\Users\rayan.rami\Downloads\CAC40\R.jpg"
DATA_FILE = "CARREFOUR_2026-01-16.txt"

# -----------------------
# 2. DESIGN "MODERN SAAS" (CSS PUR)
# -----------------------
# C'est ici qu'on fait la magie pour avoir le look "Google Analytics"
st.markdown(
    """
    <style>
    /* IMPORT POLICE GOOGLE (Inter - Standard actuel du web) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #F8F9FA; /* Gris très très clair pour le fond global */
        color: #1F2937; /* Gris foncé pour le texte (pas noir pur pour être doux) */
    }

    /* NETTOYAGE STREAMLIT */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* STYLE DES CARTES (KPIs) - Inspiré de vos images */
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #E5E7EB;
        text-align: left;
        transition: transform 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }
    .kpi-title {
        color: #6B7280;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 5px;
    }
    .kpi-value {
        color: #111827;
        font-size: 1.875rem;
        font-weight: 800;
        margin: 0;
    }
    .kpi-delta-pos {
        color: #059669; /* Vert Emeraude */
        font-size: 0.875rem;
        font-weight: 600;
        margin-top: 5px;
    }
    .kpi-delta-neg {
        color: #DC2626; /* Rouge */
        font-size: 0.875rem;
        font-weight: 600;
        margin-top: 5px;
    }

    /* BARRE LATÉRALE */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }
    
    /* GRAPHIQUES */
    .chart-container {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------
# 3. TRAITEMENT DES DONNÉES
# -----------------------
@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE): return None
    try:
        df = pd.read_csv(DATA_FILE, sep="\t", decimal=".")
        df.columns = df.columns.str.strip()
        df = df.rename(columns={"ouv": "Open", "haut": "High", "bas": "Low", "clot": "Close", "vol": "Volume"})
        df["date"] = pd.to_datetime(df["date"], dayfirst=True)
        df = df.sort_values("date")
        
        df["Montant"] = df["Volume"] * df["Close"]
        df["Variation"] = df["Close"] - df["Open"]
        df["Variation_Pct"] = (df["Close"] - df["Open"]) / df["Open"] * 100
        
        return df
    except: return None

df = load_data()

# -----------------------
# 4. INTERFACE
# -----------------------
if df is None:
    st.error("Données introuvables.")
    st.stop()

# --- SIDEBAR (Épurée) ---
with st.sidebar:
    if os.path.exists(IMG_LOGO_PATH):
        st.image(IMG_LOGO_PATH, use_container_width=True)
        st.markdown("###") # Espace
    
    st.markdown("**Paramètres**")
    # Filtre Date simple et propre
    dates = st.date_input("Période", [df["date"].min(), df["date"].max()], label_visibility="collapsed")
    
    # Bouton de téléchargement discret
    st.markdown("---")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Exporter CSV", data=csv, file_name='export_carrefour.csv', mime='text/csv')

    # Filtre effectif
    if len(dates) == 2:
        df_filt = df[(df["date"].dt.date >= dates[0]) & (df["date"].dt.date <= dates[1])]
    else:
        df_filt = df

# --- HEADER PAGE PRINCIPALE ---
st.markdown("### 📊 Dashboard Financier")
st.markdown(f"<div style='color: #6B7280; margin-bottom: 20px;'>Vue d'ensemble des performances boursières du {dates[0].strftime('%d/%m/%Y')} au {dates[1].strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)

# --- KPI CARDS (HTML/CSS Custom pour ressembler à vos images) ---
# Calculs
last_price = df_filt["Close"].iloc[-1]
prev_price = df_filt["Close"].iloc[-2] if len(df_filt) > 1 else last_price
delta_price = last_price - prev_price
delta_pct = (delta_price / prev_price) * 100

vol_total = df_filt["Volume"].sum()
mnt_total = df_filt["Montant"].sum()
max_price = df_filt["High"].max()

# Fonction pour générer une carte HTML
def kpi_card(title, value, delta_txt, is_positive):
    color_class = "kpi-delta-pos" if is_positive else "kpi-delta-neg"
    arrow = "↗" if is_positive else "↘"
    if delta_txt == "": arrow = ""
    
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="{color_class}">{arrow} {delta_txt}</div>
    </div>
    """

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(kpi_card("Dernier Cours", f"{last_price:.2f} €", f"{delta_pct:+.2f}% (vs veille)", delta_pct >= 0), unsafe_allow_html=True)
with col2:
    st.markdown(kpi_card("Volume Période", f"{vol_total:,.0f}", "Titres échangés", True), unsafe_allow_html=True)
with col3:
    st.markdown(kpi_card("Capitaux", f"{mnt_total/1e6:.1f} M€", "Flux monétaire", True), unsafe_allow_html=True)
with col4:
    st.markdown(kpi_card("Plus Haut (Période)", f"{max_price:.2f} €", "Résistance majeure", True), unsafe_allow_html=True)

st.markdown("###") # Espace

# --- GRAPHIQUE PRINCIPAL (Style Google/Stripe) ---
# On utilise un conteneur blanc pour encadrer le graphique
with st.container():
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("##### 📈 Évolution du Prix & Tendance")
    
    # Graphique Altair : Area Chart avec Dégradé Bleu (Comme sur l'image 2)
    
    # 1. La Ligne et l'Aire (Bleu "Tech")
    base = alt.Chart(df_filt).encode(x=alt.X('date', axis=alt.Axis(format='%d %b', title=None, grid=False)))
    
    area = base.mark_area(
        line={'color':'#3B82F6'}, # Bleu Roi Moderne
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='rgba(59, 130, 246, 0.5)', offset=0), # Bleu semi-transparent
                   alt.GradientStop(color='rgba(59, 130, 246, 0.0)', offset=1)], # Vers transparent
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        y=alt.Y('Close', scale=alt.Scale(zero=False), axis=alt.Axis(title='Prix (€)', grid=True, gridColor='#F3F4F6')),
        tooltip=['date', 'Close', 'Volume']
    )
    
    st.altair_chart(area, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION 2 : VOLUMES & DONNÉES ---
c_chart, c_table = st.columns([1, 1])

with c_chart:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("##### 📊 Volumes Quotidiens")
    
    # Bar Chart simple et élégant (Gris/Bleu)
    bars = alt.Chart(df_filt).mark_bar(color='#94A3B8', cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X('date', axis=alt.Axis(labels=False, title=None, grid=False)),
        y=alt.Y('Volume', axis=alt.Axis(format='.2s', title=None, grid=True, gridColor='#F3F4F6')),
        tooltip=['date', 'Volume', 'Montant']
    ).properties(height=300)
    
    st.altair_chart(bars, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_table:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("##### 📋 Dernières Transactions")
    # On affiche juste les colonnes importantes pour faire propre
    short_df = df_filt[["date", "Close", "Variation", "Volume"]].sort_values("date", ascending=False).head(8)
    # Formatage simple
    st.dataframe(
        short_df.style.format({"Close": "{:.2f}€", "Variation": "{:+.2f}€", "Volume": "{:,.0f}"}),
        use_container_width=True,
        height=300,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)