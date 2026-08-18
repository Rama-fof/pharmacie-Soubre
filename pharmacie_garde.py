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
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Pharmacies de garde - Soubré", page_icon="💊", layout="centered"
)


# =========================================================
# INITIALISATION ET CONNEXION SQLITE
# =========================================================
def initialiser_base_de_donnees():
    """Crée la table et insère tes données de test si la base n'existe pas."""
    db_existe = os.path.exists("pharmacies_soubre.db")
    conn = sqlite3.connect("pharmacies_soubre.db")
    cursor = conn.cursor()

    if not db_existe:
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

        # Insertion de tes données d'exemple de Soubré
        donnees_initiales = [
            (
                "2026-08-18",
                "Pharmacie Centrale",
                "+225 07 00 00 00 00",
                "Centre-ville, Soubré",
                "08h00 - 22h00",
            ),
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
            (
                "2026-08-21",
                "Pharmacie de la Gare",
                "+225 07 33 33 33 33",
                "Près de la gare routière, Soubré",
                "08h00 - 22h00",
            ),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO gardes VALUES (?, ?, ?, ?, ?)",
            donnees_initiales,
        )
        conn.commit()

    conn.close()


def chercher_pharmacie_du_jour(date_cible):
    """Récupère les informations depuis la base SQLite."""
    conn = sqlite3.connect("pharmacies_soubre.db")
    cursor = conn.cursor()

    # SQLite stocke les dates sous forme de texte (AAAA-MM-JJ)
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


# Lancement automatique de la bdd
initialiser_base_de_donnees()

# =========================================================
# STYLE DE L'APPLICATION
# =========================================================

st.markdown(
    """
<style>
    .main { padding-top: 2rem; }
    .titre { font-size: 38px; font-weight: 700; text-align: center; margin-bottom: 5px; }
    .sous-titre { text-align: center; color: #666; font-size: 16px; margin-bottom: 30px; }
    
    /* Carte pharmacie */
    .carte-pharmacie {
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #dddddd;
        background-color: #f8fff9;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .nom-pharmacie { font-size: 25px; font-weight: 700; margin-bottom: 5px; color: #111111; }
    .statut { color: #168a35; font-weight: 600; margin-bottom: 20px; }
    .information { font-size: 16px; margin: 8px 0; color: #333333; }
    
    /* Informations importantes */
    .information-importante {
        padding: 15px;
        border-radius: 10px;
        background-color: #f5f5f5;
        margin-top: 25px;
        font-size: 14px;
        color: #444444;
    }
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# TITRE
# =========================================================

st.markdown(
    '<div class="titre">💊 Pharmacie de garde - Soubré</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sous-titre">Trouvez rapidement une pharmacie de garde</div>',
    unsafe_allow_html=True,
)

# =========================================================
# CHOIX DE LA DATE
# =========================================================

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
    "Ou choisissez une date",
    value=st.session_state["date_choisie"],
    format="DD/MM/YYYY",
)
st.session_state["date_choisie"] = date_choisie

# =========================================================
# AFFICHAGE DU RÉSULTAT (DEPUIS SQLITE)
# =========================================================

st.divider()

# Requête vers SQLite au lieu du dictionnaire en dur
pharmacie = chercher_pharmacie_du_jour(date_choisie)

if pharmacie:
    # Nettoyage et injection sécurisée du bloc HTML
    html_carte = f"""
    <div class="carte-pharmacie">
    <div class="statut">✓ Pharmacie de garde</div>
        <div class="nom-pharmacie">🟢 {pharmacie["nom"]}</div>
        <div class="information">📍 <b>Adresse :</b> {pharmacie["adresse"]}</div>
        <div class="information">🕐 <b>Horaires :</b> {pharmacie["horaires"]}</div>
        <div class="information">📞 <b>Téléphone :</b> {pharmacie["telephone"]}</div>
    </div>
    """
    # L'astuce magique : on supprime les sauts de lignes pour forcer l'affichage HTML pur
    st.markdown(html_carte.replace("\n", ""), unsafe_allow_html=True)

    # Boutons d'actions
    adresse_recherche = quote(pharmacie["adresse"] + ", Soubré")
    url_itineraire = (
        f"https://www.google.com/maps/search/?api=1&query={adresse_recherche}"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.link_button(
            "📞 Appeler", "tel:" + pharmacie["telephone"], use_container_width=True
        )
    with col2:
        st.link_button("📍 Itinéraire", url_itineraire, use_container_width=True)
else:
    st.warning(
        "Aucune pharmacie de garde n'est encore renseignée pour cette date."
    )
    
# =========================================================
# ESPACE ADMINISTRATEUR SÉCURISÉ ET MASQUÉ
# =========================================================
st.divider()

# 1. Un champ discret. Les utilisateurs ne verront que cette ligne.
mot_de_passe = st.text_input(
    "⚙️ Accès administration", 
    type="password", 
    placeholder="Entrez le code pour ajouter une pharmacie"
)

# 2. Le formulaire secret ne s'affiche QUE si le code est le bon
if mot_de_passe == "Soubre2026": 
    st.success("🔓 Accès autorisé")
    
    # Tout le formulaire est maintenant protégé ici
    with st.container():
        st.write("### ➕ Ajouter une pharmacie de garde")

        nouvelle_date = st.date_input("Date de la garde", date.today(), key="nouv_date")
        nouveau_nom = st.text_input("Nom de la pharmacie", placeholder="Pharmacie...")
        nouveau_tel = st.text_input("Téléphone", placeholder="+225...")
        nouvelle_adresse = st.text_input("Adresse", placeholder="Quartier...")
        nouveaux_horaires = st.text_input("Horaires", value="08h00 - 22h00")

        if st.button("💾 Enregistrer dans la base SQL", use_container_width=True):
            if nouveau_nom and nouveau_tel and nouvelle_adresse:
                # Écriture directe dans la base SQLite
                conn = sqlite3.connect("pharmacies_soubre.db")
                cursor = conn.cursor()
                date_str = nouvelle_date.strftime("%Y-%m-%d")
                
                cursor.execute("""
                    INSERT OR REPLACE INTO gardes (date, nom, telephone, adresse, horaires) 
                    VALUES (?, ?, ?, ?, ?)
                """, (date_str, nouveau_nom, nouveau_tel, nouvelle_adresse, nouveaux_horaires))
                
                conn.commit()
                conn.close()
                st.success(f"✅ Enregistré avec succès pour le {date_str} !")
                st.rerun() # Recharge l'écran pour afficher la nouvelle pharmacie
            else:
                st.error("⚠️ Veuillez remplir tous les champs.")


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


