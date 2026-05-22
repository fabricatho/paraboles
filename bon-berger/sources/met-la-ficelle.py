import bpy
import math

# ---- PARAMÈTRES ----
plateau_epaisseur = 6
poteau_section    = 6
poteau_hauteur    = 45
emplacement_trou  = 10
retrait_poteau    = 40
nb_poteaux        = 11
rayon_poteaux     = (290 / 2) - retrait_poteau  # = 105

z_ficelle    = poteau_hauteur - emplacement_trou  # = 60 mm
rayon_boucle = poteau_section * 2.5               # = 15 mm
nb_boucle    = 8

# ---- PARAMÈTRE CATÉNAIRE ----
# 0 = ficelle tendue, 5 = légèrement pendante, 15 = bien molle
pendance = 8       # mm — flèche max au milieu entre deux poteaux
nb_inter  = 8      # points intermédiaires entre chaque poteau

# ---- Supprimer l'ancienne ficelle ----
if "Ficelle" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Ficelle"], do_unlink=True)
if "Ficelle_curve" in bpy.data.curves:
    bpy.data.curves.remove(bpy.data.curves["Ficelle_curve"])
if "Ficelle_Mat" in bpy.data.materials:
    bpy.data.materials.remove(bpy.data.materials["Ficelle_Mat"])

# ---- Calcul des points de trou ----
trous = []
for i in range(nb_poteaux):
    angle_rad = math.radians(i * (360 / nb_poteaux))
    cx = rayon_poteaux * math.cos(angle_rad)
    cy = rayon_poteaux * math.sin(angle_rad)
    trous.append((cx, cy, z_ficelle))

# ---- Caténaire entre deux points ----
def segment_catenaire(p1, p2, flèche, nb_points):
    """Retourne nb_points intermédiaires entre p1 et p2 avec une courbe caténaire."""
    pts = []
    for k in range(1, nb_points + 1):
        t = k / (nb_points + 1)           # 0..1 entre les deux poteaux
        # interpolation linéaire XY
        x = p1[0] + t * (p2[0] - p1[0])
        y = p1[1] + t * (p2[1] - p1[1])
        # caténaire en Z : parabole symétrique, max au milieu
        # sin(π*t) vaut 0 aux extrémités, 1 au milieu
        z = p1[2] + t * (p2[2] - p1[2]) - flèche * math.sin(math.pi * t)
        pts.append((x, y, z))
    return pts

# ---- Construire tous les points ficelle + caténaires ----
tous_les_points = []
for i in range(nb_poteaux):
    p1 = trous[i]
    p2 = trous[(i + 1) % nb_poteaux]
    tous_les_points.append(p1)
    tous_les_points.extend(segment_catenaire(p1, p2, pendance, nb_inter))

# Fermer sur le premier trou avant la boucle
tous_les_points.append(trous[0])

# ---- Boucle finale autour du DERNIER poteau ----
rayon_boucle = poteau_section * 0.6

cx0, cy0 = trous[-1][0], trous[-1][1]   # ← trous[-1] au lieu de trous[0]

z_bas_boucle = 20

for j in range(nb_boucle + 1):
    t = j / nb_boucle
    a = math.radians(j * (360 / nb_boucle))
    z = z_ficelle - z_bas_boucle * math.sin(math.pi * t) * 0.5
    

# ---- Créer la courbe ----
curve_data = bpy.data.curves.new("Ficelle_curve", type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = 12
curve_data.bevel_depth = 0.5
curve_data.bevel_resolution = 8
curve_data.use_fill_caps = True

spline = curve_data.splines.new('NURBS')
spline.use_endpoint_u = True
spline.points.add(len(tous_les_points) - 1)

for idx, (x, y, z) in enumerate(tous_les_points):
    spline.points[idx].co = (x, y, z, 1.0)

# ---- Objet ----
obj_ficelle = bpy.data.objects.new("Ficelle", curve_data)
bpy.context.scene.collection.objects.link(obj_ficelle)

if "Bon Berger" in bpy.data.collections:
    bpy.context.scene.collection.objects.unlink(obj_ficelle)
    bpy.data.collections["Bon Berger"].objects.link(obj_ficelle)

# ---- Matériau beige corde ----
mat = bpy.data.materials.new(name="Ficelle_Mat")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Base Color"].default_value = (0.85, 0.75, 0.55, 1.0)
bsdf.inputs["Roughness"].default_value = 0.9
out = nodes.new("ShaderNodeOutputMaterial")
links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
mat.diffuse_color = (0.85, 0.75, 0.55, 1.0)
obj_ficelle.data.materials.append(mat)

print(f"✅ Ficelle créée — pendance {pendance} mm")