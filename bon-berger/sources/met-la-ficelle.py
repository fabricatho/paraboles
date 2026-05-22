import bpy
import math

# ---- PARAMÈTRES ----
plateau_epaisseur  = 5
poteau_section     = 5
poteau_hauteur     = 45
emplacement_trou   = 10
emplacement_trou_2 = 30
retrait_poteau     = 40
nb_poteaux         = 11
rayon_poteaux      = (290 / 2) - retrait_poteau  # = 105

z_ficelle   = poteau_hauteur - emplacement_trou   # = 35 mm
z_ficelle_2 = poteau_hauteur - emplacement_trou_2 # = 25 mm

pendance = 8
nb_inter = 8

# ---- Supprimer les anciennes ficelles ----
for nom in ("Ficelle", "Ficelle_2"):
    if nom in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[nom], do_unlink=True)
for nom in ("Ficelle_curve", "Ficelle_2_curve"):
    if nom in bpy.data.curves:
        bpy.data.curves.remove(bpy.data.curves[nom])
for nom in ("Ficelle_Mat",):
    if nom in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[nom])

# ---- Caténaire ----
def segment_catenaire(p1, p2, flèche, nb_points):
    pts = []
    for k in range(1, nb_points + 1):
        t = k / (nb_points + 1)
        x = p1[0] + t * (p2[0] - p1[0])
        y = p1[1] + t * (p2[1] - p1[1])
        z = p1[2] + t * (p2[2] - p1[2]) - flèche * math.sin(math.pi * t)
        pts.append((x, y, z))
    return pts

# ---- Matériau (partagé) ----
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

# ---- Fonction création courbe ----
def creer_ficelle(nom, z_trou):
    # Points de trou
    trous = []
    for i in range(nb_poteaux):
        angle_rad = math.radians(i * (360 / nb_poteaux))
        cx = rayon_poteaux * math.cos(angle_rad)
        cy = rayon_poteaux * math.sin(angle_rad)
        trous.append((cx, cy, z_trou))

    # Tous les points avec caténaire
    tous_les_points = []
    for i in range(nb_poteaux):
        p1 = trous[i]
        p2 = trous[(i + 1) % nb_poteaux]
        tous_les_points.append(p1)
        tous_les_points.extend(segment_catenaire(p1, p2, pendance, nb_inter))
    tous_les_points.append(trous[0])

    # Courbe
    curve_data = bpy.data.curves.new(f"{nom}_curve", type='CURVE')
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

    # Objet
    obj = bpy.data.objects.new(nom, curve_data)
    bpy.context.scene.collection.objects.link(obj)
    if "Bon Berger" in bpy.data.collections:
        bpy.context.scene.collection.objects.unlink(obj)
        bpy.data.collections["Bon Berger"].objects.link(obj)
    obj.data.materials.append(mat)
    print(f"✅ {nom} créée à Z={z_trou} mm")

# ---- Créer les deux ficelles ----
creer_ficelle("Ficelle",   z_ficelle)
creer_ficelle("Ficelle_2", z_ficelle_2)

print("🎉 Terminé !")