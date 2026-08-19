# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:11:48 2026

@author: ramat
"""

import os
import sqlite3
from datetime import date, datetime, timedelta
from urllib.parse import quote
import streamlit as st

# =========================================================
# CONFIGURATION ET THÈME DE LA PAGE
# =========================================================
st.set_page_config(
    page_title="Pharmacies de garde - Soubré", page_icon="💊", layout="centered"
)

# Injection CSS globale : Force le fond bleu/gris et nettoie le design
st.markdown(
    """
<style>
    .stApp {
        background-color: #eef5f9 !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# INITIALISATION BASE DE DONNÉES SQLite
# =========================================================
def initialiser_base_de_donnees():
    conn = sqlite3.connect("pharmacies_soubre.db")
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS gardes (
        date TEXT PRIMARY KEY,
        nom TEXT NOT NULL,
        telephone TEXT NOT NULL,
        adresse TEXT NOT NULL,
        horaires TEXT NOT NULL
    )
    """
    )

    # Données par défaut initiales pour Soubré
    donnees_initiales = [
        (
            "2026-08-19",
            "Pharmacie du Marché",
            "+225 07 11 11 11 11",
            "Marché de Soubré",
            "08h00 - 22h00",
        ),
        (
            "2026-08-20",
            "Pharmacie Saint-Michel",
            "+225 07 22 22 22 22",
            "Quartier Saint-Michel, Soubré",
            "08h00 - 22h00",
        ),
    ]
    # Correction ici : Utilisation de la bonne variable pour l'insertion
    cursor.executemany(
        "INSERT OR IGNORE INTO gardes VALUES (?, ?, ?, ?, ?)", donnees_initiales
    )
    conn.commit()
    conn.close()


def chercher_pharmacie_du_jour(date_cible):
    conn = sqlite3.connect("pharmacies_soubre.db")
    cursor = conn.cursor()
    date_str = date_cible.strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT nom, telephone, adresse, horaires FROM gardes WHERE date = ?",
        (date_str,),
    )
    ligne = cursor.fetchone()
    conn.close()

    if ligne:
        return {
            "nom": ligne[0],
            "telephone": ligne[1],
            "adresse": ligne[2],
            "horaires": ligne[3],
        }
    return None


# Lancement automatique de la BDD
initialiser_base_de_donnees()

# =========================================================
# INTERFACE EN-TÊTE
# =========================================================
st.markdown(
    """
    <div style="text-align:center; padding:10px;">
        <h1 style="color:#1e3d59; font-size:36px; margin-bottom:0px; font-weight:700;">💊 Pharmacie de garde</h1>
        <p style="color:#17b978; font-size:24px; font-weight:bold; margin-top:5px;">Soubré</p>
        <p style="color:#555555; font-size:15px;">Trouvez rapidement votre officine ouverte</p>
    </div>
""",
    unsafe_allow_html=True,
)

st.write("---")
st.subheader("📅 Quelle date recherchez-vous ?")

col1, col2 = st.columns(2)
aujourdhui = date.today()
demain = aujourdhui + timedelta(days=1)

if "date_choisie" not in st.session_state:
    st.session_state["date_choisie"] = aujourdhui

with col1:
    if st.button("📅 Aujourd'hui", use_container_width=True):
        st.session_state["date_choisie"] = aujourdhui
with col2:
    if st.button("📅 Demain", use_container_width=True):
        st.session_state["date_choisie"] = demain

date_choisie = st.date_input(
    "Ou sélectionnez un jour précis :",
    value=st.session_state["date_choisie"],
    format="DD/MM/YYYY",
)
st.session_state["date_choisie"] = date_choisie

# =========================================================
# AFFICHAGE DE LA CARTE DE GARDE
# =========================================================
st.write("---")
pharmacie = chercher_pharmacie_du_jour(date_choisie)

if pharmacie:
    # Conteneur HTML au design épuré, pro et lisible
    card_html = f"""
    <div style="background-color: #ffffff; border: 1px solid #dddddd; padding: 25px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h2 style="color: #168a35; margin-top: 0px; font-size: 26px; font-weight:700;">🟢 {pharmacie["nom"]}</h2>
        <p style="color: #168a35; font-weight: 600; font-size: 15px; margin-bottom: 20px;">✓ Officine de garde active</p>
        <p style="color: #2c3e50; font-size: 16px; margin: 8px 0;">📍 <b>Adresse :</b> {pharmacie["adresse"]}</p>
        <p style="color: #2c3e50; font-size: 16px; margin: 8px 0;">🕐 <b>Horaires :</b> {pharmacie["horaires"]}</p>
        <p style="color: #2c3e50; font-size: 16px; margin: 8px 0;">📞 <b>Téléphone :</b> {pharmacie["telephone"]}</p>
    </div>
    """
    st.markdown(card_html.replace("\n", ""), unsafe_allow_html=True)

    # Paramétrage des boutons d'actions mobiles
    adresse_recherche = quote(pharmacie["adresse"] + ", Soubré")
    url_itineraire = (
        f"https://google.com{adresse_recherche}"
    )

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.link_button(
            "📞 Appeler l'officine",
            f"tel:{pharmacie['telephone']}",
            use_container_width=True,
        )
    with btn_col2:
        st.link_button(
            "📍 Lancer l'itinéraire", url_itineraire, use_container_width=True
        )
else:
    st.warning(
        "⚠️ Aucune pharmacie de garde enregistrée pour cette date spécifique dans la base."
    )

# =========================================================
# ESPACE ADMINISTRATION SECRÈTE
# =========================================================
st.write("---")
mot_de_passe = st.text_input(
    "⚙️ Accès administration",
    type="password",
    placeholder="Entrez le code secret pour ajouter une garde",
)

if mot_de_passe == "Soubre2026":
    st.success("🔓 Mode éditeur actif")
    with st.form("ajout_pharmacie", clear_on_submit=True):
        st.write("### ➕ Ajouter un créneau de garde")
        n_date = st.date_input("Date de la garde", date.today())
        n_nom = st.text_input("Nom de la pharmacie")
        n_tel = st.text_input("Téléphone")
        n_adr = st.text_input("Adresse")
        n_hor = st.text_input("Horaires d'ouverture", value="08h00 - 22h00")

        if st.form_submit_button(
            "💾 Sauvegarder dans la base de données", use_container_width=True
        ):
            if n_nom and n_tel and n_adr:
                conn = sqlite3.connect("pharmacies_soubre.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO gardes VALUES (?, ?, ?, ?, ?)",
                    (n_date.strftime("%Y-%m-%d"), n_nom, n_tel, n_adr, n_hor),
                )
                conn.commit()
                conn.close()
                st.success("🎉 Données enregistrées avec succès !")
                st.rerun()
            else:
                st.error("Veuillez remplir tous les champs.")

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


