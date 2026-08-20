# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 2026
@author: ramat
Espace Pharmacien — Version finale (Gestion dynamique du logo parent)
"""

import base64
import os
import streamlit as st
from supabase import create_client, Client

# =========================================================
# 1. CONFIGURATION DE LA PAGE
# =========================================================

st.set_page_config(
    page_title="Espace Pharmacien - Soubré",
    page_icon="🏥",
    layout="centered"
)

# =========================================================
# 2. CONNEXION SUPABASE
# =========================================================

supabase_url = st.secrets.get("SUPABASE_URL", "https://vjhxnajfoymazcyejxmk.supabase.co")
supabase_key = st.secrets.get("SUPABASE_KEY", "sb_publishable_Uej8awCy-KFl2_A2gco_SQ_oCxYXk0V")

@st.cache_resource
def init_supabase() -> Client:
    return create_client(supabase_url, supabase_key)

supabase = init_supabase()

# =========================================================
# 3. STYLE CSS GLOBAL & HOMOGÈNE
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(160deg, #eaf3fb 0%, #dceaf7 45%, #f5f9fd 100%);
    }

    .main { 
        padding-top: 1.5rem; 
    }

    /* En-tête flex pour aligner le logo et le titre */
    .entete-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
        margin-bottom: 8px;
    }

    .logo-cadre {
        width: 80px;
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
        font-size: 32px;
        font-weight: 800;
        color: #0b3d66;
        line-height: 1.1;
        margin: 0;
    }
    
    .sous-titre {
        text-align: center;
        color: #1a3e5c;
        font-size: 15px;
        margin-bottom: 24px;
        font-weight: 600;
    }

    /* Personnalisation des typographies Streamlit */
    h2, h3 {
        color: #0b3d66 !important;
        font-weight: 800 !important;
    }

    label, .stTextInput label, .stSelectbox label, .stDateInput label {
        font-size: 15px !important;
        color: #0b1f33 !important;
        font-weight: 700 !important;
    }

    button p {
        font-size: 16px !important;
        font-weight: 700 !important;
    }

    input {
        font-size: 15px !important;
        color: #0b1f33 !important;
    }

    @media (max-width: 640px) {
        .titre-aligne { font-size: 24px; }
        .sous-titre { font-size: 13px; }
        .logo-cadre { width: 65px; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 4. RECHERCHE ET CHARGEMENT DU LOGO (DOSSIER PARENT & ENFANT)
# =========================================================

dossier_actuel = os.path.dirname(os.path.abspath(__file__))
dossier_parent = os.path.dirname(dossier_actuel)

noms_possibles = ["logo.gif.gif", "logo.gif", "logo.GIF", "logo.png", "Design sans titre.gif"]

chemin_trouve = None

# On teste d'abord dans /pages, puis dans le dossier racine
for dossier in [dossier_actuel, dossier_parent]:
    for nom in noms_possibles:
        chemin_test = os.path.join(dossier, nom)
        if os.path.exists(chemin_test):
            chemin_trouve = chemin_test
            break
    if chemin_trouve:
        break

if chemin_trouve:
    with open(chemin_trouve, "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()
    ext = chemin_trouve.split(".")[-1].lower()
    mime = "image/gif" if "gif" in ext else "image/png"
    img_tag = f'<div class="logo-cadre"><img src="data:{mime};base64,{encoded}" class="logo-img" /></div>'
else:
    img_tag = ""

st.markdown(
    f"""
    <div class="entete-container">
        {img_tag}
        <div class="titre-aligne">Espace Pharmaciens</div>
    </div>
    <div class="sous-titre">Soubré — Gestion des gardes d'officine</div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 5. GESTION DE LA SESSION UTILISATEUR
# =========================================================

if "user" not in st.session_state:
    st.session_state.user = None

# =========================================================
# 6. INTERFACE : NON CONNECTÉ
# =========================================================

if not st.session_state.user:
    tab_login, tab_signup = st.tabs(["🔑 Se connecter", "📝 Créer un compte"])

    with tab_login:
        st.subheader("Connexion Officine")
        email = st.text_input("Adresse Email", key="login_email")
        password = st.text_input("Mot de passe", type="password", key="login_pass")
        
        if st.button("Se connecter", type="primary", use_container_width=True):
            if not email or not password:
                st.warning("Veuillez remplir tous les champs.")
            else:
                try:
                    res = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    st.session_state.user = res.user
                    st.success("Connexion réussie !")
                    st.rerun()
                except Exception:
                    st.error("Identifiants incorrects ou compte non confirmé.")

    with tab_signup:
        st.subheader("Créer un compte pour votre Pharmacie")
        new_email = st.text_input("Email professionnel", key="signup_email")
        new_password = st.text_input("Mot de passe", type="password", key="signup_pass")
        nom_pharma = st.text_input("Nom de la Pharmacie (ex: Pharmacie du Centre)")
        adresse = st.text_input("Adresse (ex: Quartier Résidentiel, Soubré)")
        telephone = st.text_input("Téléphone (ex: +225 07 00 00 00 00)")

        if st.button("Enregistrer mon officine", use_container_width=True):
            if not new_email or not new_password or not nom_pharma:
                st.warning("Veuillez remplir tous les champs obligatoires.")
            elif len(new_password) < 6:
                st.warning("Le mot de passe doit contenir au moins 6 caractères.")
            else:
                try:
                    res = supabase.auth.sign_up({
                        "email": new_email,
                        "password": new_password,
                        "options": {
                            "data": {
                                "nom_pharma": nom_pharma,
                                "adresse": adresse,
                                "telephone": telephone
                            }
                        }
                    })
                    
                    if res.user:
                        supabase.table("pharmacies").insert({
                            "user_id": res.user.id,
                            "nom": nom_pharma,
                            "email": new_email,
                            "adresse": adresse,
                            "telephone": telephone
                        }).execute()
                        st.success("Compte créé avec succès ! Connectez-vous.")
                except Exception as e:
                    st.error(f"Erreur d'inscription : {e}")

# =========================================================
# 7. INTERFACE : CONNECTÉ
# =========================================================

else:
    with st.sidebar:
        st.write(f"Connecté : **{st.session_state.user.email}**")
        if st.button("Se déconnecter", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

    try:
        pharma_query = supabase.table("pharmacies").select("*").eq("user_id", st.session_state.user.id).execute()
        
        if pharma_query.data:
            pharmacie = pharma_query.data[0]
            
            st.markdown(f"### 🟢 {pharmacie['nom']}")
            st.caption(f"📍 {pharmacie.get('adresse', 'N/C')} | 📞 {pharmacie.get('telephone', 'N/C')}")
            st.divider()

            st.subheader("➕ Indiquer une nouvelle garde")
            with st.form("form_garde", clear_on_submit=True):
                date_garde = st.date_input("Date de la garde")
                horaires = st.text_input("Horaires d'ouverture", value="08h00 - 22h00")
                type_garde = st.selectbox("Type de service", ["Garde de Nuit", "Dimanche & Jours Fériés", "24h/24"])
                
                if st.form_submit_button("Enregistrer la date de garde", type="primary", use_container_width=True):
                    supabase.table("gardes").insert({
                        "pharmacie_id": pharmacie["id"],
                        "date": str(date_garde),
                        "horaires": horaires,
                        "type_garde": type_garde
                    }).execute()
                    st.success("Garde enregistrée avec succès !")
                    st.rerun()

            st.divider()

            st.subheader("📅 Vos prochaines gardes")
            gardes_query = supabase.table("gardes").select("date, horaires, type_garde").eq("pharmacie_id", pharmacie["id"]).order("date", desc=False).execute()
            
            if gardes_query.data:
                st.dataframe(
                    gardes_query.data,
                    column_config={
                        "date": "Date",
                        "horaires": "Horaires",
                        "type_garde": "Type de Garde"
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Aucune garde enregistrée pour le moment.")
        else:
            st.warning("Aucune information de pharmacie associée à ce compte.")

    except Exception as e:
        st.error(f"Erreur de chargement : {e}")

st.markdown("---")
st.caption("Espace Professionnel — Pharmacies de garde de Soubré")
