import pandas as pd
import re
import pygraphviz as pgv
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image
from matplotlib import rcParams

# Utilisation de la police DejaVu Sans
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

# Définir les positions des nœuds
def definir_positions():
    positions = {
        'ابن أبي حاتم': (0, 0),
        'أبو سعيد بن يحيى بْنِ سَعِيدٍ الْقَطَّانُ': (1, 0),
        'أَبُو أَحْمَدَ الزُّبَيْرِيُّ': (2, 0),
        'سُفْيَانَ': (3, 0),
        'عَمَّارٍالدُّهْنِيِّ': (4, 0),
        'مُسْلِمٍ الْبَطِينِ': (5, 0),
        'سَعِيدِ بْنِ جُبَيْرٍ': (6, 0),
        'ابْنِ عَبَّاسٍ': (7, 0),
        'الطبري': (0, 1),
        'أَحْمَدُ بْنُ إِسْحَاقَ': (1, 1),
        'أَبُو عَاصِمٍ الضَّحاك بْنُ مَخْلَدٍ': (2, 1),
        'الدارقطني': (3, 1),
        'مُحَمَّدُ بْنُ مَخْلَدٍ': (4, 1),
        'أَحْمَدُ بْنُ مَنْصُورٍ الرَّمَادِيُّ': (5, 1),
        'مُحَمَّدُ بْنُ الْحَسَّانِيِّ': (6, 1),
        'وكيع': (7, 1),
        'الطبراني': (0, 2),
        'أَبُو مُسْلِمٍ الْكَشِّيُّ': (1, 2),
        'البيهقي': (2, 2),
        'أَبُو نَصْرِ بْنُ قَتَادَةَ': (3, 2),
        'أَبُو عَمْرِو بْنُ نُجَيْدٍ السُّلَمِيُّ': (4, 2),
        'أَبُو مُسْلِمٍ الْكِجِّيُّ': (5, 2),
        'أبو عبد الله الحاكم': (6, 2),
        'أَبُو الْعَبَّاسِ مُحَمَّدُ بْنُ أَحْمَدَ الْمَحْبُوبِيُّ': (7, 2),
        'مُحَمَّدُ بْنُ مُعَاذٍ': (0, 3),
        'ابن خزيمة': (1, 3),
        'بُنْدَارٌ مُحَمَّدُ بْنُ بَشَّارٍ': (2, 3),
        'عبد الرزاق صاحب التفسير': (3, 3),
        'عبد الله ابن أحمد': (4, 3),
        'أحمد ابن حنبل': (5, 3),
        'ابْنُ مَهْدِيٍّ': (6, 3),
    }
    return positions

# Fonction pour visualiser les chaînes de narrateurs avec positions
def visualiser_chaine_pygraphviz(chaine1, positions):
    G = pgv.AGraph(directed=True)
    G.graph_attr['rankdir'] = "RL"  # De droite à gauche

    # Ajouter les chaînes au graphe avec les positions
    for key, chaine in chaine1.items():
        previous_narrator = None
        for narrator in chaine:  # On garde l'ordre original
            normalized_narrator = normalize_name(narrator)

            # Vérifier si le narrateur existe dans le dictionnaire
            rawi_info = narrators_dict.get(normalized_narrator, {})
            label_text = f"{narrator}\n({rawi_info.get('تاريخ الميلاد', '')} - {rawi_info.get('تاريخ الوفاة', '')})"

            if not G.has_node(normalized_narrator):
                reshaped_label = label_text
                node_position = positions.get(normalized_narrator, None)
                if node_position:
                    x, y = node_position
                    G.add_node(normalized_narrator, label=reshaped_label, shape="rect", pos=f"{x},{y}!")
                

            if previous_narrator is not None:
                G.add_edge(normalized_narrator, previous_narrator)  

            previous_narrator = normalized_narrator

    G.node_attr['fontname'] = 'DejaVu Sans'
    G.edge_attr['fontname'] = 'DejaVu Sans'
    G.node_attr['fontsize'] = '12'


    G.layout(prog='dot')  # Utiliser 'dot' pour une disposition hiérarchique
    G.draw('Ised_Tree.png')

    img = Image.open('graphe.png')
    img.show()

# Fonction principale
def main():
    charger_narrateurs()
    chaine1 = charger_chaines()
    positions = definir_positions()
    visualiser_chaine_pygraphviz(chaine1, positions)

if __name__ == "__main__":
    main()
