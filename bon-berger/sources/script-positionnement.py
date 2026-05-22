import bpy
import math
import os

# ---- PARAMÈTRES ----
plateau_epaisseur = 6
poteau_section    = 6
retrait_poteau    = 40
nb_poteaux        = 11
rayon_poteaux     = (290 / 2) - retrait_poteau  # = 105
scale             = 1.0

# ---- CHEMINS ----
blend_dir   = bpy.path.abspath("//")
plateau_stl = os.path.join(blend_dir, "plateau.stl")
poteau_stl  = os.path.join(blend_dir, "poteau.stl")

print(f"Dossier : {blend_dir}")
print(f"Plateau : {os.path.exists(plateau_stl)}")
print(f"Poteau  : {os.path.exists(poteau_stl)}")

# ============================================================
#  CLEAR TOTAL
# ============================================================
# 1. Supprimer tous les objets
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=True)

# 2. Supprimer les collections par nom (snapshot de la liste d'abord)
noms_a_supprimer = {"Bon Berger", "Plateau", "Poteaux"}
cols_a_supprimer = [c for c in bpy.data.collections if c.name in noms_a_supprimer]
for col in cols_a_supprimer:
    bpy.data.collections.remove(col)

# 3. Purger les meshes orphelins
bpy.ops.outliner.orphans_purge(do_recursive=True)

print("🧹 Scène nettoyée")

# ============================================================
#  COLLECTIONS
# ============================================================
def make_collection(name, parent=None):
    col = bpy.data.collections.new(name)
    target = parent if parent else bpy.context.scene.collection
    target.children.link(col)
    return col

col_scene   = make_collection("Bon Berger")
col_plateau = make_collection("Plateau", col_scene)
col_poteaux = make_collection("Poteaux",  col_scene)

def move_to_collection(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

def import_stl(filepath):
    bpy.ops.object.select_all(action='DESELECT')
    try:
        bpy.ops.wm.stl_import(filepath=filepath)
    except AttributeError:
        bpy.ops.import_mesh.stl(filepath=filepath)
    return bpy.context.selected_objects[0]

# ============================================================
#  IMPORT PLATEAU
# ============================================================
obj_plateau = import_stl(plateau_stl)
obj_plateau.name = "Plateau"
move_to_collection(obj_plateau, col_plateau)
obj_plateau.location = (0, 0, 0)
# Matériau vert plateau
mat_plateau = bpy.data.materials.new(name="Herbe_Plateau")
mat_plateau.use_nodes = True
nodes = mat_plateau.node_tree.nodes
links = mat_plateau.node_tree.links
nodes.clear()
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Base Color"].default_value = (0.15, 0.55, 0.15, 1.0)  # vert herbe
bsdf.inputs["Roughness"].default_value = 0.9
out = nodes.new("ShaderNodeOutputMaterial")
links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
mat_plateau.diffuse_color = (0.15, 0.55, 0.15, 1.0)  # ← viewport
obj_plateau.data.materials.append(mat_plateau)
print(f"✅ Plateau — dimensions : {obj_plateau.dimensions}")

# ============================================================
#  IMPORT POTEAUX
# ============================================================
s = poteau_section

for i in range(nb_poteaux):
    angle_deg = i * (360 / nb_poteaux)
    angle_rad = math.radians(angle_deg)

    cx = rayon_poteaux * math.cos(angle_rad)
    cy = rayon_poteaux * math.sin(angle_rad)

    obj = import_stl(poteau_stl)
    obj.name = f"Poteau_{i+1:02d}"
    move_to_collection(obj, col_poteaux)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # 1. Centrage local (translate[-s/2, -s/2, 0] d'OpenSCAD)
    obj.location = (-s/2, -s/2, 0)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    # 2. Rotation tangentielle
    obj.rotation_euler = (0, 0, math.radians(angle_deg + 180))
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    # 3. Position finale
    obj.location = (cx, cy, 0)
    
    # Matériau bois
    if "Bois_Contreplaque" not in bpy.data.materials:
        mat = bpy.data.materials.new(name="Bois_Contreplaque")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        # Principled BSDF
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = (0.65, 0.45, 0.25, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.8
        mat.diffuse_color = (0.65, 0.45, 0.25, 1.0)  # ← ajouter cette ligne
        # Output
        out = nodes.new("ShaderNodeOutputMaterial")
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    else:
        mat = bpy.data.materials["Bois_Contreplaque"]

    obj.data.materials.append(mat)

    print(f"✅ Poteau {i+1:02d} — angle {angle_deg:.1f}° — pos ({cx:.1f}, {cy:.1f}) mm")

print("🎉 Terminé !")