import streamlit as st
import pickle
import pandas as pd
import os

def charger_modele(path_modele):
    """Charge le modèle à partir du fichier spécifié."""
    if not os.path.exists(path_modele):
        st.error(f"Le fichier de modèle {path_modele} est introuvable.")
        return None
    try:
        with open(path_modele, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle : {e}")
        return None

def extraire_caracteristiques(fichier):
    """Extrait les caractéristiques d'un fichier binaire et les convertit en format compatible avec le modèle."""
    try:
        contenu = fichier.read()
        # Exemple de génération de 20 caractéristiques pour correspondre à l'entraînement du modèle
        taille = len(contenu)
        signature_numerique = [byte for byte in contenu[:10]]
        padding = [0] * (10 - len(signature_numerique))  # Compléter si moins de 10 octets
        signature_numerique += padding

        # Retirer la caractéristique en surplus pour garantir 20 au total
        return {
            **{f'byte_{i}': signature_numerique[i] for i in range(10)},
            **{f'freq_{i}': contenu.count(i) / taille if taille > 0 else 0 for i in range(10)}
        }
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des caractéristiques : {e}")
        return None

# Charger le modèle
path_modele = 'modele_entraine.pkl'
modele = charger_modele(path_modele)
if modele is None:
    st.stop()

# Interface utilisateur
st.title("Détection de fichiers malveillants")
st.markdown("**Instructions :** Téléchargez un fichier exécutable (.exe, .bin) pour vérifier s'il est malveillant ou légitime.")

fichier = st.file_uploader("Uploader un fichier exécutable", type=['exe', 'bin'])
if fichier:
    # Extraire les caractéristiques
    caracteristiques = extraire_caracteristiques(fichier)
    if caracteristiques:
        try:
            # Synchronisation avec le modèle sauvegardé depuis le notebook
            caracteristiques_df = pd.DataFrame([{key: caracteristiques[key] for key in sorted(caracteristiques.keys())}])
            prediction = modele.predict(caracteristiques_df)
            resultat = "Malveillant" if prediction[0] == 1 else "Légitime"
            st.success(f"Résultat : {resultat}")
        except Exception as e:
            st.error(f"Erreur lors de la prédiction : {e}")
