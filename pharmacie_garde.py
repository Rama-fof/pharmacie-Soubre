# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 2026
@author: ramat
Version finale — Supabase + esthétique responsive + sélection de date corrigée
"""

from datetime import date, timedelta
from urllib.parse import quote
import streamlit as st
from supabase import create_client, Client

# =========================================================
# CONFIGURATION (doit être la toute première commande Streamlit)
# =========================================================

st.set_page_config(
    page_title="Pharmacies de garde - Soubré", page_icon="💊", layout="centered"
)

# =========================================================
# CONNEXION SUPABASE
# =========================================================

@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

supabase = init_supabase()


def chercher_pharmacie_du_jour(date_cible):
    """Récupère les informations depuis Supabase."""
    date_str = date_cible.strftime("%Y-%m-%d")
    reponse = supabase.table("gardes").select("*").eq("date", date_str).execute()
    if reponse.data:
        ligne = reponse.data[0]
        return {
            "nom": ligne["nom"],
            "telephone": ligne["telephone"],
            "adresse": ligne["adresse"],
            "horaires": ligne["horaires"],
        }
    return None


def enregistrer_pharmacie(date_cible, nom, telephone, adresse, horaires):
    """Ajoute ou met à jour une garde dans Supabase."""
    date_str = date_cible.strftime("%Y-%m-%d")
    supabase.table("gardes").upsert({
        "date": date_str,
        "nom": nom,
        "telephone": telephone,
        "adresse": adresse,
        "horaires": horaires,
    }).execute()


# =========================================================
# STYLE — ESTHÉTIQUE + RESPONSIVE MOBILE
# =========================================================

st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(160deg, #eaf3fb 0%, #dceaf7 45%, #f5f9fd 100%);
    }

    .main { padding-top: 1.5rem; }

    .titre {
        font-size: 40px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 4px;
        color: #0b3d66;
    }
    .sous-titre {
        text-align: center;
        color: #2c5578;
        font-size: 16px;
        margin-bottom: 28px;
        font-weight: 500;
    }

    .carte-pharmacie {
        padding: 28px;
        border-radius: 18px;
        border: 1px solid #b8d4ec;
        background-color: #ffffff;
        box-shadow: 0 4px 14px rgba(11, 61, 102, 0.10);
        margin-top: 20px;
        margin-bottom: 20px;
        transition: transform 0.2s ease;
    }
    .carte-pharmacie:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(11, 61, 102, 0.16);
    }

    .nom-pharmacie {
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 6px;
        color: #0b1f33;
    }
    .statut {
        display: inline-block;
        background-color: #1565c0;
        color: #ffffff;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 18px;
    }
    .information {
        font-size: 16px;
        margin: 10px 0;
        color: #1a1a1a;
        font-weight: 500;
    }

    .information-importante {
        padding: 16px;
        border-radius: 12px;
        background-color: #ffffff;
        margin-top: 25px;
        font-size: 14px;
        color: #1a1a1a;
        border-left: 4px solid #1565c0;
    }

    @media (max-width: 640px) {
        .titre { font-size: 30px; }
        .sous-titre { font-size: 14px; }
        .carte-pharmacie { padding: 18px; border-radius: 14px; }
        .nom-pharmacie { font-size: 21px; }
        .information { font-size: 14px; }
    }

    /* ===== ÉLÉMENTS NATIFS STREAMLIT — meilleure lisibilité ===== */
    h3 {
        color: #0b3d66 !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    label, .stDateInput label, .stTextInput label {
        font-size: 17px !important;
        color: #0b1f33 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMarkdownContainer"] p {
        font-size: 17px !important;
        color: #0b1f33 !important;
    }
    button p {
        font-size: 16px !important;
        font-weight: 700 !important;
    }
    div[data-testid="stAlert"] p {
        font-size: 16px !important;
        font-weight: 500 !important;
    }
    input {
        font-size: 16px !important;
        color: #0b1f33 !important;
    }
    /* Labels des champs du formulaire admin */
    [data-testid="stWidgetLabel"] p {
        font-size: 16px !important;
        color: #0b1f33 !important;
        font-weight: 600 !important;
    }
    /* Texte des placeholders dans les champs */
    input::placeholder {
        color: #6b7f94 !important;
        opacity: 1 !important;
    }
    /* Caption en pied de page */
    [data-testid="stCaptionContainer"] p, .stCaption p {
        font-size: 13px !important;
        color: #4a6178 !important;
        font-weight: 500 !important;
    }
    /* Texte gras dans l'encadré information */
    .information-importante b {
        color: #0b3d66 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# TITRE
# =========================================================

st.markdown('<div class="titre">💊 Pharmacie de garde</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sous-titre">Soubré — Trouvez rapidement une pharmacie de garde</div>',
    unsafe_allow_html=True,
)

# =========================================================
# CHOIX DE LA DATE (version corrigée, sans conflit de session_state)
# =========================================================

st.subheader("📅 Quelle date recherchez-vous ?")

if "date_choisie" not in st.session_state:
    st.session_state.date_choisie = date.today()

col1, col2 = st.columns(2)
aujourdhui = date.today()
demain = aujourdhui + timedelta(days=1)

with col1:
    if st.button("📅 Aujourd'hui", use_container_width=True):
        st.session_state.date_choisie = aujourdhui
        st.rerun()

with col2:
    if st.button("📅 Demain", use_container_width=True):
        st.session_state.date_choisie = demain
        st.rerun()

date_choisie = st.date_input(
    "Ou choisissez une date",
    key="date_choisie",
    format="DD/MM/YYYY",
)

# =========================================================
# AFFICHAGE DU RÉSULTAT
# =========================================================

st.divider()

pharmacie = chercher_pharmacie_du_jour(date_choisie)

if pharmacie:
    html_carte = f"""
    <div class="carte-pharmacie">
        <div class="statut">✓ Pharmacie de garde</div>
        <div class="nom-pharmacie">🟢 {pharmacie["nom"]}</div>
        <div class="information">📍 <b>Adresse :</b> {pharmacie["adresse"]}</div>
        <div class="information">🕐 <b>Horaires :</b> {pharmacie["horaires"]}</div>
        <div class="information">📞 <b>Téléphone :</b> {pharmacie["telephone"]}</div>
    </div>
    """
    st.markdown(html_carte.replace("\n", ""), unsafe_allow_html=True)

    adresse_recherche = quote(pharmacie["adresse"] + ", Soubré")
    url_itineraire = f"https://www.google.com/maps/search/?api=1&query={adresse_recherche}"

    col1, col2 = st.columns(2)
    with col1:
        st.link_button("📞 Appeler", "tel:" + pharmacie["telephone"], use_container_width=True)
    with col2:
        st.link_button("📍 Itinéraire", url_itineraire, use_container_width=True)
else:
    st.warning("Aucune pharmacie de garde n'est encore renseignée pour cette date.")

# =========================================================
# ESPACE ADMINISTRATEUR SÉCURISÉ
# =========================================================

st.divider()

mot_de_passe = st.text_input(
    "⚙️ Accès administration", type="password", placeholder="Entrez le code pour ajouter une pharmacie"
)

if mot_de_passe == st.secrets["mot_de_passe_admin"]:
    st.success("🔓 Accès autorisé")

    with st.container():
        st.write("Ajoutez une nouvelle pharmacie de garde :")

        nouvelle_date = st.date_input("Date de la garde", date.today(), key="nouv_date")
        nouveau_nom = st.text_input("Nom de la pharmacie", placeholder="Pharmacie...")
        nouveau_tel = st.text_input("Téléphone", placeholder="+225...")
        nouvelle_adresse = st.text_input("Adresse", placeholder="Quartier...")
        nouveaux_horaires = st.text_input("Horaires", value="08h00 - 22h00")

        if st.button("💾 Enregistrer", use_container_width=True):
            if nouveau_nom and nouveau_tel and nouvelle_adresse:
                enregistrer_pharmacie(
                    nouvelle_date, nouveau_nom, nouveau_tel, nouvelle_adresse, nouveaux_horaires
                )
                st.success(f"✅ Enregistré avec succès pour le {nouvelle_date} !")
                st.rerun()
            else:
                st.error("⚠️ Veuillez remplir tous les champs.")
elif mot_de_passe:
    st.error("❌ Mot de passe incorrect")

# =========================================================
# INFORMATIONS & PIED DE PAGE
# =========================================================

st.markdown(
    """
    <div class="information-importante">
    ℹ️ <b>Information importante</b><br><br>
    Les informations affichées sont données à titre de prototype.
    Elles devront être vérifiées et mises à jour régulièrement avant une utilisation réelle.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")
st.caption("Prototype — Pharmacies de garde de Soubré")