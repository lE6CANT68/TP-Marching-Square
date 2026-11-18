# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 11:58:01 2026

@author: e2001989
"""

import SimpleITK as sitk
import numpy as np
from skimage.measure import marching_cubes
import pyvista as pv

def main():
    # =========================================================================
    # ÉTAPE 1 : Lecture du volume
    # =========================================================================
    fichier_nrrd = "MrHead.nrrd"
    
    try:
        # Chargement de l'image et conversion en tableau NumPy
        image = sitk.ReadImage(fichier_nrrd)
        volume = sitk.GetArrayFromImage(image)
    except Exception as e:
        print(f"Erreur lors du chargement : {e}")
        return

    # Récupération des statistiques demandées
    dimensions = volume.shape
    nb_voxels = volume.size
    val_min = volume.min()
    val_max = volume.max()

    print("--- ÉTAPE 1 : Informations sur le volume ---")
    print(f"Dimensions du volume (Z, Y, X) : {dimensions}")
    print(f"Nombre total de voxels       : {nb_voxels:,}")
    print(f"Valeur minimale              : {val_min}")
    print(f"Valeur maximale              : {val_max}")
    print("Vérification                 : Chargement réussi. Les données sont prêtes.\n")

    # =========================================================================
    # ÉTAPE 2 : Exploration des données et choix de l'isovaleur
    # =========================================================================
    # Explication du choix :
    # Dans une IRM/Scanner classique encodée sur cette plage (0 à ~279) :
    # - Le fond (air) est à 0.
    # - Les tissus mous (peau, graisse) commencent généralement autour de 30-50.
    # - Les structures denses (os, crâne) se situent vers les valeurs plus hautes (> 100).
    # Nous fixons l'isovaleur par défaut à 45.0 pour extraire l'enveloppe faciale (peau).
    
    isovalue_defaut = 45.0
    print("--- ÉTAPE 2 : Isovaleur ---")
    print(f"Isovaleur par défaut choisie : {isovalue_defaut} (Cible : contours du visage / peau)\n")

    # =========================================================================
    # ÉTAPE 3, 4 & 5 : Extraction Marching Cubes, Visualisation 3D et Slider
    # =========================================================================
    print("--- ÉTAPE 3, 4 & 5 : Lancement de l'interface 3D ---")
    print("L'extraction Marching Cubes est calculée en temps réel via le curseur.")

    # Initialisation de la fenêtre de rendu PyVista
    plotter = pv.Plotter(title="Extraction 3D - Marching Cubes")

    def update_surface(isovalue):
        """
        Fonction de rappel (callback) déclenchée par le curseur.
        Recalcule le Marching Cubes et met à jour le maillage 3D affiché.
        """
        try:
            # ÉTAPE 3 : Algorithme Marching Cubes
            # Retourne les sommets (verts) et les triangles (faces)
            verts, faces, normals, values = marching_cubes(volume, level=isovalue)
            
            # Formatage spécifique des faces pour PyVista : 
            # Il faut insérer le nombre de sommets par face (3) avant chaque triangle
            # Ex: [3, v0, v1, v2, 3, v3, v4, v5, ...]
            faces_pv = np.column_stack((np.full(len(faces), 3), faces)).flatten()
            
            # Création de l'objet 3D
            mesh = pv.PolyData(verts, faces_pv)
            
            # ÉTAPE 4 : Affichage et mise à jour du modèle
            plotter.add_mesh(
                mesh, 
                name='isosurface',     # Le nom permet d'écraser l'ancien maillage au lieu d'en rajouter un
                color='bisque',        # Couleur chair claire
                smooth_shading=True,   # Lissage des normales pour un beau rendu
                specular=0.5           # Reflets de lumière pour mieux voir les reliefs
            )
        except ValueError:
            # Gère le cas où l'isovaleur ne génère aucune surface (ex: valeurs extrêmes)
            pass

    # Génération du premier maillage avec la valeur par défaut
    update_surface(isovalue_defaut)

    # ÉTAPE 5 : Interaction avec l'isovaleur
    # Ajout du curseur interactif en bas de l'écran
    plotter.add_slider_widget(
        callback=update_surface,
        rng=[val_min + 1, val_max - 1], # Plage de valeurs du curseur
        value=isovalue_defaut,
        title="Isovaleur (Glisser pour mettre a jour)",
        pointa=(0.2, 0.1),
        pointb=(0.8, 0.1),
        style='modern'
    )

    # Configuration de la caméra et affichage de la fenêtre (permet zoom, rotation, pan)
    plotter.view_isometric()
    plotter.add_axes()
    plotter.show()

if __name__ == "__main__":
    main()