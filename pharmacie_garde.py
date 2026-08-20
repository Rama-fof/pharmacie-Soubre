# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 2026
@author: ramat
Version finale — Supabase + Logo GIF Intégral + Interface Propre
"""

import base64
from datetime import date, timedelta
import os
from urllib.parse import quote
import streamlit as st
from supabase import create_client, Client

# =========================================================
# CONFIGURATION DE LA PAGE
# =========================================================

st.set_page_config(
    page_title="Pharmacies de garde - Soubré", page_icon="💊", layout="centered"
)

# =========================================================
# CONNEXION SUPABASE (Flexible pour éviter les erreurs de clés)
# =========================================================

@st.cache_resource
def init_supabase() -> Client:
    # Récupère les clés qu'elles soient en majuscules ou en minuscules
    url = st.secrets.get("SUPABASE_URL", st.secrets.get("supabase_url"))
    key = st.secrets.get("SUPABASE_KEY", st.secrets.get("supabase_key"))
    return create_client(url, key)

supabase = init_supabase()


def chercher_pharmacies_du_jour(date_cible):
    """Récupère les gardes du jour via jointure Supabase."""
    date_str = date_cible.strftime("%Y-%m-%d")
    try:
        reponse = (
            supabase.table("gardes")
            .select("*, pharmacies(nom, telephone, adresse)")
            .eq("date", date_str)
            .execute()
        )
        
        gardes = []
        if reponse.data:
            for ligne in reponse.data:
                pharma_info = ligne.get("pharmacies") or {}
                gardes.append({
                    "nom": pharma_info.get("nom", "Pharmacie sans nom"),
                    "telephone": pharma_info.get("telephone", "N/C"),
                    "adresse": pharma_info.get("adresse", "Soubré"),
                    "horaires": ligne.get("horaires", "08h00 - 22h00"),
                    "type_garde": ligne.get("type_garde", "Garde de Nuit"),
                })
        return gardes
    except Exception as e:
        st.error(f"Erreur lors de la recherche des gardes : {e}")
        return []


# =========================================================
# STYLE ET DESIGN RESPONSIVE
# =========================================================

st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(160deg, #eaf3fb 0%, #dceaf7 45%, #f5f9fd 100%);
    }

    .main { padding-top: 1.5rem; }

    /* En-tête avec logo entier */
    .entete-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
        margin-bottom: 10px;
    }

    .logo-cadre {
        width: 100px;
        height: auto;
        border-radius: 12px;
        overflow: hidden;
        background-color: #ffffff;
        padding: 4px;
        box-shadow: 0 4px 12px rgba(11, 61, 102, 0.12);
        flex-shrink: 0;
    }

    .logo-img {
        width: 100%;
        height: auto;
        display: block;
        object-fit: contain;
    }

    .titre-aligne {
        font-size: 38px;
        font-weight: 800;
        color: #0b3d66;
        line-height: 1.1;
        margin: 0;
    }
    
    .sous-titre {
        text-align: center;
        color: #1a3e5c;
        font-size: 17px;
        margin-bottom: 28px;
        font-weight: 600;
    }

    /* Cartes pharmacies */
    .carte-pharmacie {
        padding: 26px;
        border-radius: 18px;
        border: 1px solid #b8d4ec;
        background-color: #ffffff;
        box-shadow: 0 5px 16px rgba(11, 61, 102, 0.08);
        margin-top: 18px;
        margin-bottom: 18px;
    }

    .nom-pharmacie {
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 8px;
        color: #0b1f33;
    }
    .statut {
        display: inline-block;
        background-color: #1565c0;
        color: #ffffff;
        padding: 5px 14px;
        border-radius: 16px;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 16px;
    }
    .information {
        font-size: 16px;
        margin: 8px 0;
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
        border-left: 5px solid #1565c0;
    }

    /* Streamlit overrides */
    h3 {
        color: #0b3d66 !important;
        font-size: 22px !important;
        font-weight: 800 !important;
    }
    label, .stDateInput label, .stTextInput label {
        font-size: 17px !important;
        color: #0b1f33 !important;
        font-weight: 700 !important;
    }
    button p {
        font-size: 16px !important;
        font-weight: 700 !important;
    }
    input {
        font-size: 16px !important;
        color: #0b1f33 !important;
    }

    @media (max-width: 640px) {
        .titre-aligne { font-size: 28px; }
        .sous-titre { font-size: 14px; }
        .logo-cadre { width: 75px; }
        .carte-pharmacie { padding: 18px; }
        .nom-pharmacie { font-size: 21px; }
        .information { font-size: 14px; }
    }
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# EN-TÊTE ET LOGO INTEGRAL
# =========================================================

dossier_script = os.path.dirname(os.path.abspath(__file__))

noms_possibles = [
    "logo.gif", 
    "logo.GIF", 
    "logo.png", 
    "Design sans titre.gif"
]

chemin_trouve = None
for nom in noms_possibles:
    chemin_test = os.path.join(dossier_script, nom)
    if os.path.exists(chemin_test):
        chemin_trouve = chemin_test
        break

if chemin_trouve:
    with open(chemin_trouve, "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()
    ext = chemin_trouve.split(".")[-1].lower()
    mime = "image/gif" if "gif" in ext else "image/png"
    img_html = f'<div class="logo-cadre"><img src="data:{mime};base64,{encoded}" class="logo-img" /></div>'
else:
    img_html = ""

st.markdown(
    f"""
    <div class="entete-container">
        {img_html}
        <h1 class="titre-aligne">Pharmacie de garde</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="sous-titre">Soubré — Trouvez rapidement une pharmacie de garde</div>',
    unsafe_allow_html=True,
)

# =========================================================
# SÉLECTION DE LA DATE
# =========================================================

st.subheader("📅 Quelle date recherchez-vous ?")

col1, col2 = st.columns(2)
aujourdhui = date.today()
demain = aujourdhui + timedelta(days=1)

if "date_choisie" not in st.session_state:
    st.session_state.date_choisie = aujourdhui

with col1:
    if st.button("📅 Aujourd'hui", use_container_width=True):
        st.session_state.date_choisie = aujourdhui
        st.rerun()

with col2:
    if st.button("📅 Demain", use_container_width=True):
        st.session_state.date_choisie = demain
        st.rerun()

date_selectionnee = st.date_input(
    "Ou choisissez une date",
    value=st.session_state.date_choisie,
    format="DD/MM/YYYY",
)

# =========================================================
# AFFICHAGE DES PHARMACIES
# =========================================================

st.divider()

liste_pharmacies = chercher_pharmacies_du_jour(date_selectionnee)

if liste_pharmacies:
    for pharma in liste_pharmacies:
        html_carte = f"""
        <div class="carte-pharmacie">
            <div class="statut">✓ {pharma["type_garde"]}</div>
            <div class="nom-pharmacie">🟢 {pharma["nom"]}</div>
            <div class="information">📍 <b>Adresse :</b> {pharma["adresse"]}</div>
            <div class="information">🕐 <b>Horaires :</b> {pharma["horaires"]}</div>
            <div class="information">📞 <b>Téléphone :</b> {pharma["telephone"]}</div>
        </div>
        """
        st.markdown(html_carte, unsafe_allow_html=True)

        adresse_recherche = quote(f"{pharma['nom']}, {pharma['adresse']}, Soubré")
        url_itineraire = f"https://www.google.com/maps/search/?api=1&query={adresse_recherche}"

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.link_button("📞 Appeler", "tel:" + pharma["telephone"], use_container_width=True)
        with col_btn2:
            st.link_button("📍 Itinéraire", url_itineraire, use_container_width=True)
        st.write("")
else:
    st.warning("Aucune pharmacie de garde n'est encore renseignée pour cette date.")

# =========================================================
# ACCÈS ADMIN
# =========================================================

st.divider()

with st.expander("⚙️ Accès administration"):
    mot_de_passe = st.text_input(
        "Mot de passe admin", type="password", placeholder="Entrez le code administrateur"
    )

    if mot_de_passe == st.secrets.get("mot_de_passe_admin", ""):
        st.success("🔓 Accès autorisé")

        res_pharmacies = supabase.table("pharmacies").select("id, nom").execute()
        options_pharmacies = {p["nom"]: p["id"] for p in (res_pharmacies.data or [])}

        if options_pharmacies:
            with st.form("form_admin_garde"):
                st.write("Ajouter une garde pour une pharmacie existante :")
                pharma_nom_choisi = st.selectbox("Pharmacie", list(options_pharmacies.keys()))
                nouvelle_date = st.date_input("Date de la garde", date.today())
                horaires = st.text_input("Horaires", value="08h00 - 22h00")
                type_garde = st.selectbox("Type de service", ["Garde de Nuit", "Dimanche & Jours Fériés", "24h/24"])

                if st.form_submit_button("💾 Enregistrer la garde", use_container_width=True):
                    pharma_id = options_pharmacies[pharma_nom_choisi]
                    supabase.table("gardes").insert({
                        "pharmacie_id": pharma_id,
                        "date": str(nouvelle_date),
                        "horaires": horaires,
                        "type_garde": type_garde
                    }).execute()
                    st.success(f"✅ Garde enregistrée avec succès pour le {nouvelle_date} !")
                    st.rerun()
        else:
            st.info("Aucune pharmacie enregistrée dans la base de données.")
    elif mot_de_passe:
        st.error("❌ Mot de passe incorrect")

# =========================================================
# PIED DE PAGE
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