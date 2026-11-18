import matplotlib.pyplot as plt
import math


"""
Permet de comparer les valeurs de v0,v1,v2,v3 a l'isovaleur isovalue.
Renvoie un nombre binaire <16 avec 1 pour chaque vx >= a isovalue
"""
def calculer_index_cellule(v0, v1, v2, v3, isovalue):
    index = 0
    
    # On utilise l'opérateur OU bit-à-bit (|=) pour construire l'index de 0 à 15
    if v0 >= isovalue:
        index |= 1  # Active le bit 0 (0001 en binaire)
    if v1 >= isovalue:
        index |= 2  # Active le bit 1 (0010 en binaire)
    if v2 >= isovalue:
        index |= 4  # Active le bit 2 (0100 en binaire)
    if v3 >= isovalue:
        index |= 8  # Active le bit 3 (1000 en binaire)
        
    return index

# Table de correspondance : Index -> [(Arête A, Arête B), ...]
# Un index de 0 signifie que tous les sommets sont en dessous de l'isovaleur.
# Un index de 15 signifie que tous les sommets sont au-dessus.
# Dans ces deux cas, la courbe ne passe pas par ce carré.

LIGNES_MARCHING_SQUARES = {
    0: [],                           # 0000 : Vide
    1: [(0, 3)],                     # 0001 : v0 seul -> coupe Haut et Gauche
    2: [(0, 1)],                     # 0010 : v1 seul -> coupe Haut et Droite
    3: [(1, 3)],                     # 0011 : v0, v1 -> coupe Droite et Gauche
    4: [(1, 2)],                     # 0100 : v2 seul -> coupe Droite et Bas
    5: [(0, 1), (2, 3)],             # 0101 : Cas ambigu (v0 et v2) -> deux segments
    6: [(0, 2)],                     # 0110 : v1, v2 -> coupe Haut et Bas
    7: [(2, 3)],                     # 0111 : v0, v1, v2 -> coupe Bas et Gauche
    8: [(2, 3)],                     # 1000 : v3 seul -> coupe Bas et Gauche
    9: [(0, 2)],                     # 1001 : v0, v3 -> coupe Haut et Bas
    10: [(0, 3), (1, 2)],            # 1010 : Cas ambigu (v1 et v3) -> deux segments
    11: [(1, 2)],                    # 1011 : v0, v1, v3 -> coupe Droite et Bas
    12: [(1, 3)],                    # 1100 : v2, v3 -> coupe Droite et Gauche
    13: [(0, 1)],                    # 1101 : v0, v2, v3 -> coupe Haut et Droite
    14: [(0, 3)],                    # 1110 : v1, v2, v3 -> coupe Haut et Gauche
    15: []                           # 1111 : Plein (pas de ligne)
}

def interpoler_point(p1, p2, v1, v2, isovalue):
    """
    Calcule les coordonnées exactes (x, y) de l'intersection sur une arête.
    p1, p2 : tuples (x, y) des coordonnées des deux sommets de l'arête
    v1, v2 : valeurs scalaires aux sommets p1 et p2
    """
    
    # Sécurité : éviter une division par zéro si les valeurs sont identiques
    if abs(v2 - v1) < 1e-5:
        return p1
        
    # Calcul du ratio t (où se trouve l'isovaleur entre v1 et v2)
    t = (isovalue - v1) / (v2 - v1)
    
    # Application du ratio aux coordonnées spatiales
    x = p1[0] + t * (p2[0] - p1[0])
    y = p1[1] + t * (p2[1] - p1[1])
    
    return (x, y)

def obtenir_point_sur_arete(num_arete, p0, p1, p2, p3, v0, v1, v2, v3, isovalue):
    """
    Fonction utilitaire qui fait le lien entre le numéro de l'arête (0 à 3) 
    et les deux sommets correspondants pour lancer l'interpolation.
    """
    if num_arete == 0:   # Haut (v0 -> v1)
        return interpoler_point(p0, p1, v0, v1, isovalue)
    elif num_arete == 1: # Droite (v1 -> v2)
        return interpoler_point(p1, p2, v1, v2, isovalue)
    elif num_arete == 2: # Bas (v2 -> v3)
        return interpoler_point(p2, p3, v2, v3, isovalue)
    elif num_arete == 3: # Gauche (v3 -> v0)
        return interpoler_point(p3, p0, v3, v0, isovalue)

def marching_squares(grille, isovalue):
    """
    Fonction principale qui parcourt la grille et retourne la liste de tous les segments.
    'grille' est un tableau 2D (liste de listes ou un array NumPy) contenant les valeurs scalaires.
    """
    segments_finaux = []
    hauteur = len(grille)
    largeur = len(grille[0])
    
    # On parcourt chaque cellule (carré 2x2) de la grille.
    # On s'arrête à -1 pour ne pas déborder, car chaque carré a besoin du point (x+1, y+1).
    for y in range(hauteur - 1):
        for x in range(largeur - 1):
            
            # 1. Coordonnées spatiales (géométrie) des 4 sommets
            p0 = (x, y)           # Haut-Gauche
            p1 = (x + 1, y)       # Haut-Droite
            p2 = (x + 1, y + 1)   # Bas-Droite
            p3 = (x, y + 1)       # Bas-Gauche
            
            # 2. Valeurs scalaires associées extraites de la grille
            v0 = grille[y][x]
            v1 = grille[y][x+1]
            v2 = grille[y+1][x+1]
            v3 = grille[y+1][x]
            
            # 3. Calcul de l'index (Étape 1)
            index = calculer_index_cellule(v0, v1, v2, v3, isovalue)
            
            # 4. Récupération des paires d'arêtes à relier depuis la Lookup Table (Étape 2)
            aretes_a_relier = LIGNES_MARCHING_SQUARES[index]
            
            # 5. Calcul des intersections exactes et stockage des lignes (Étape 3)
            for arete_A, arete_B in aretes_a_relier:
                pt_A = obtenir_point_sur_arete(arete_A, p0, p1, p2, p3, v0, v1, v2, v3, isovalue)
                pt_B = obtenir_point_sur_arete(arete_B, p0, p1, p2, p3, v0, v1, v2, v3, isovalue)
                
                # On ajoute ce segment à la liste globale pour pouvoir l'afficher plus tard
                segments_finaux.append((pt_A, pt_B))
                
    return segments_finaux

def tracer_marching_squares(segments, grille, isovalue):
    """
    Dessine la grille, les valeurs des sommets et les segments de contour.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    hauteur = len(grille)
    largeur = len(grille[0])
    
    # 1. Dessiner la grille et les sommets
    for y in range(hauteur):
        for x in range(largeur):
            valeur = grille[y][x]
            # Point noir si >= isovalue (intérieur), gris clair sinon (extérieur)
            couleur = 'black' if valeur >= isovalue else 'lightgray'
            ax.plot(x, y, marker='o', color=couleur, markersize=8)
            
            # Afficher la valeur scalaire légèrement décalée pour vérifier les calculs
            ax.text(x + 0.1, y + 0.1, f'{valeur:.1f}', fontsize=8, color='blue')
            
    # 2. Tracer les segments de l'isosurface
    for pt_A, pt_B in segments:
        x_coords = [pt_A[0], pt_B[0]]
        y_coords = [pt_A[1], pt_B[1]]
        ax.plot(x_coords, y_coords, color='red', linewidth=2)
        
    # Configuration esthétique de la fenêtre
    ax.set_aspect('equal') # Garder des proportions carrées
    ax.set_title(f"Marching Squares (Isovaleur = {isovalue})")
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.show()

def test_marching_squares():
    """
    Génère un champ scalaire de test (un cercle), lance l'algorithme et affiche le résultat.
    """
    # 1. Création d'une grille 6x6 remplie de zéros
    largeur, hauteur = 6, 6
    grille = [[0.0 for _ in range(largeur)] for _ in range(hauteur)]
    
    # Centre géométrique de notre "colline" de données
    centre_x, centre_y = 2.5, 2.5
    
    # 2. Remplissage de la grille avec des valeurs scalaires
    for y in range(hauteur):
        for x in range(largeur):
            # Calcul de la distance euclidienne par rapport au centre
            distance = math.sqrt((x - centre_x)**2 + (y - centre_y)**2)
            # Plus on est près du centre, plus la valeur est haute (max ~4.0)
            grille[y][x] = max(0.0, 4.0 - distance)
            
    # 3. Choix de l'isovaleur que l'on veut extraire
    isovalue = 2.5
    
    # 4. Appel de la fonction principale (l'Étape 4 précédente)
    segments = marching_squares(grille, isovalue)
    print(f"Succès : {len(segments)} segments générés.")
    
    # 5. Rendu graphique
    tracer_marching_squares(segments, grille, isovalue)

# Exécution du script




def generer_grille_rastrigin(largeur, hauteur, scale=0.15):
    """
    Génère un champ de données 2D très accidenté basé sur la fonction de Rastrigin.
    Le paramètre scale gère le niveau de "zoom" sur la topologie.
    """
    grille = [[0.0 for _ in range(largeur)] for _ in range(hauteur)]
    
    for y in range(hauteur):
        for x in range(largeur):
            # Centrage de la grille sur (0,0) pour capter le minimum global
            X = (x - largeur / 2.0) * scale
            Y = (y - hauteur / 2.0) * scale
            
            # Rastrigin 2D : Z = 20 + X^2 - 10*cos(2*pi*X) + Y^2 - 10*cos(2*pi*Y)
            Z = 20.0 + (X**2 - 10.0 * math.cos(2 * math.pi * X)) + (Y**2 - 10.0 * math.cos(2 * math.pi * Y))
            grille[y][x] = Z
            
    return grille

def test_marching_squares_rastrigin():
    # On monte en résolution pour bien voir les reliefs (40x40 = 1600 cellules)
    largeur, hauteur = 40, 40
    grille = generer_grille_rastrigin(largeur, hauteur, scale=0.12)
    
    # Le fond absolu de Rastrigin est à 0. 
    # Avec une isovaleur à 15 ou 20, tu vas couper les "collines" de la fonction 
    # et obtenir une grille d'îlots parfaitement symétriques.
    isovalue = 15.0 
    
    print("Extraction de l'isosurface sur Rastrigin...")
    segments = marching_squares(grille, isovalue)
    print(f"Terminé : {len(segments)} segments générés.")
    
    tracer_marching_squares(segments, grille, isovalue)

if __name__ == "__main__":
    test_marching_squares_rastrigin()