// ============================================================
//  Plateau "Parabole du Bon Berger" pour découpe Laser sur Contreplaqué 6 mm
//  Fichier OpenSCAD — tous les paramètres sont en tête de fichier
// ============================================================

/* ---- PARAMÈTRES PLATEAU ---- */
plateau_diametre   = 290;   // mm  — diamètre du plateau - un seul morceau dans XTools PS2
plateau_epaisseur  = 6;     // mm  — épaisseur du panneau de contreplaqué

/* ---- PARAMÈTRES POTEAUX ---- */
poteau_hauteur      = 45;   // mm  — hauteur totale du poteau 
poteau_section     = plateau_epaisseur;   // mm  — poteau à section carrée
trou_ficelle        = 1.1;  // mm  — diamètre du trou pour la ficelle
emplacement_trou = 10; // mm emplacement du centre du trou en partant du haut du poteau
emplacement_trou_2 = 30; // mm — deuxième trou, à ajuster


// jeu pour l'emboîtement poteau dans le plateau
jeu = 0.3; // mm

// Positions des poteaux sur le pourtour
retrait_poteau = 40;  // mm  — retrait par rapport au bord
nb_poteaux   = 11;   // nombre de poteaux équirépartis
epsilon = 1; // mm marge pour bien voir le trou dans OpenScad

// Calculs intermédiaires //
rayon         = plateau_diametre / 2;
rayon_poteaux = rayon - retrait_poteau;

/* --- Pièces en 3D pour voir --- */
module plateau() {
    cylinder(h=plateau_epaisseur,r=rayon,$fn=64);
    }

    
module trou() {
 cube([poteau_section+jeu,poteau_section+jeu,plateau_epaisseur+2*epsilon]);
    } 

    
module plateau_troue() {
    difference() {
        plateau();    
 // Trous carrés d'emboîtement pour les poteaux
        for (i = [0 : nb_poteaux - 1]) {
            angle = i * (360 / nb_poteaux);
            translate([rayon_poteaux * cos(angle),rayon_poteaux * sin(angle),-epsilon])
            rotate([0, 0, angle + 90])   // ← alignement tangentiel
            translate([-poteau_section/2, -poteau_section/2, 0])  // ← centrage
            trou();
        } 
    } 
} 
//plateau_troue();

module poteau() {
    cube([poteau_section,poteau_section,poteau_hauteur]);
     } 
     
//poteau();

     
module poteau_troue() {
    difference() {
        poteau();
        // Trou du haut
        rotate ([90,0,0])
        translate ([poteau_section/2, poteau_hauteur-emplacement_trou, -(poteau_section+epsilon)])  
        cylinder(h=poteau_section+2*epsilon, r=trou_ficelle, $fn=64);
        // Trou du bas
        rotate ([90,0,0])
        translate ([poteau_section/2, poteau_hauteur-emplacement_trou_2, -(poteau_section+epsilon)])  
        cylinder(h=poteau_section+2*epsilon, r=trou_ficelle, $fn=64);
    } 
}
     
//poteau_troue();
    
    // Export pour svg
    //projection(cut = true)
    //translate([0, 0, -plateau_epaisseur/2])  // on coupe au milieu de l'épaisseur
    //plateau_troue();
    
     // Export pour svg
    
    module poteau_couche(){
    rotate([90,0,0])
    poteau_troue();
      } 
        //poteau_couche();
        
   projection(cut = true)  
         poteau_couche();
        