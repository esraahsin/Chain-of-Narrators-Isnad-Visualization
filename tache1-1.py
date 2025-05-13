import pandas as pd
import re
import pygraphviz as pgv
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image

# Utilisation de la police DejaVu Sans
from matplotlib import rcParams
rcParams['font.family'] = 'DejaVu Sans'

# Fonction pour reformater le texte arabe
def reshape_text_arabic(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# Fonction pour nettoyer le texte
def clean_text(text):
    if isinstance(text, str):
        text = re.sub(r'\s+', ' ', text)  # Supprimer les espaces multiples
        text = text.strip()  # Supprimer les espaces au début et à la fin
        return text
    return text

# Fonction pour normaliser le nom
def normalize_name(name):
    if isinstance(name, str):
        name = clean_text(name)
        name = re.sub(r'\s+', ' ', name)  # Supprimer les espaces multiples
        name = name.replace('.', '')  # Supprimer les points
    else:
        name = ''
    return name

# Charger les narrateurs depuis le fichier Excel
file_path = 'annexe2_2hadith2.xlsx'
df = pd.read_excel(file_path, header=None)

# Charger les chaînes depuis un autre fichier Excel
file_path1 = 'anexe2_1_hadith1.xlsx'
df_chains = pd.read_excel(file_path1, header=None, usecols=[0])  # Colonne A

# Dictionnaire des narrateurs
narrators_dict = {}

def charger_narrateurs():
    for _, row in df.iloc[1:].iterrows():
        nom_narrateur = normalize_name(row[2])  # Nom du narrateur
        rawi = clean_text(row[1])  # Identité
        annee_naissance = clean_text(row[3])  # Date de naissance
        annee_deces = clean_text(row[4])  # Date de décès
        
        narrators_dict[nom_narrateur] = {
            'الراوي': rawi,
            'تاريخ الميلاد': annee_naissance,
            'تاريخ الوفاة': annee_deces
        }

# Charger les chaînes de narrateurs
def charger_chaines():
    chaine1 = {}
    current_chain = []
    current_key = 1

    for _, row in df_chains.iterrows():
        text = row[0]
        if isinstance(text, str):
            text = clean_text(text)  
            if "سلسلة رواة الحديث عدد" in text:
                if current_chain:
                    chaine1[current_key] = current_chain
                    current_chain = []
                    current_key += 1
            else:
                cleaned_text = re.sub(r'\d+', '', text).strip()
                normalized_narrator = normalize_name(cleaned_text)  
                current_chain.append(clean_text(normalized_narrator))  

    if current_chain:
        chaine1[current_key] = current_chain

    return chaine1

# Fonction pour visualiser les chaînes de narrateurs
def visualiser_chaine_pygraphviz(chaine1):
    G = pgv.AGraph(directed=True)
    G.graph_attr['rankdir'] = "RL"  # De droite à gauche

    # Ajouter les chaînes au graphe
    for key, chaine in chaine1.items():
        previous_narrator = None
        for narrator in chaine:  # On garde l'ordre original
            normalized_narrator = normalize_name(narrator)

            # Vérifier si le narrateur existe dans le dictionnaire
            rawi_info = narrators_dict.get(normalized_narrator, {})
            label_text = f"{narrator}\n({rawi_info.get('تاريخ الميلاد', '')} - {rawi_info.get('تاريخ الوفاة', '')})"

            if not G.has_node(normalized_narrator):
                reshaped_label = label_text
                G.add_node(normalized_narrator, label=reshaped_label, shape="rect")

            if previous_narrator is not None:
                G.add_edge(narrator, previous_narrator)  # Les flèches pointent vers le précédent

            previous_narrator = normalized_narrator

    G.node_attr['fontname'] = 'DejaVu Sans'
    G.edge_attr['fontname'] = 'DejaVu Sans'
    G.node_attr['fontsize'] = '12'

    G.layout(prog='dot')  # Utiliser 'dot' pour une disposition hiérarchique
    G.draw('graphe.png')

    img = Image.open('graphe.png')
    img.show()

# Fonction principale
def main():
    charger_narrateurs()
    chaine1 = charger_chaines()
    visualiser_chaine_pygraphviz(chaine1)

if __name__ == "__main__":
    main()
