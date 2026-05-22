import bpy
import math
import random
import os

# ============================================================
#  PARAMÈTRES
# ============================================================
scale        = 0.5
nb_moutons_a = 6
nb_moutons_b = 6
rayon_parc   = (290 / 2) * scale
marge_bord   = 10
random.seed(42)

z_min_par_type = {
    "A": -41.994576,
    "B": -42.292244,
}

# ============================================================
#  CHEMINS
# ============================================================
blend_dir    = bpy.path.abspath("//")
mouton_a_stl = os.path.join(blend_dir, "moutonA.stl")
mouton_b_stl = os.path.join(blend_dir, "moutonB.stl")

print(f"MoutonA : {os.path.exists(mouton_a_stl)}")
print(f"MoutonB : {os.path.exists(mouton_b_stl)}")

# ============================================================
#  FONCTIONS
# ============================================================
def import_stl(filepath):
    bpy.ops.object.select_all(action='DESELECT')
    try:
        bpy.ops.wm.stl_import(filepath=filepath)
    except AttributeError:
        bpy.ops.import_mesh.stl(filepath=filepath)
    return bpy.context.selected_objects[0]

def move_to_collection(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

def position_aleatoire(rayon_max, marge, positions_prises):
    taille_mouton = 90 * scale
    for _ in range(500):
        angle = random.uniform(0, 2 * math.pi)
        r     = random.uniform(0, rayon_max - marge)
        x     = r * math.cos(angle)
        y     = r * math.sin(angle)
        ok = all(math.sqrt((x-px)**2 + (y-py)**2) > taille_mouton for px, py, _ in positions_prises)
        if ok:
            return (x, y, angle)
    return (0, 0, 0)

def make_material(name, color):
    if name in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[name])
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value  = 0.9
    out  = nodes.new("ShaderNodeOutputMaterial")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    mat.diffuse_color = color
    return mat

# ============================================================
#  NETTOYAGE
# ============================================================
# Supprimer la collection Personnages et tout son contenu
if "Personnages" in bpy.data.collections:
    col_existing = bpy.data.collections["Personnages"]
    for obj in list(col_existing.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(col_existing)

# Supprimer le berger si existe
if "BonBerger" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["BonBerger"], do_unlink=True)

# Purge meshes orphelins
for mesh in list(bpy.data.meshes):
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)

print("🧹 Nettoyage OK")

# ============================================================
#  COLLECTION
# ============================================================
col = bpy.data.collections.new("Personnages")
if "Bon Berger" in bpy.data.collections:
    bpy.data.collections["Bon Berger"].children.link(col)
else:
    bpy.context.scene.collection.children.link(col)
col_moutons = col

# ============================================================
#  MATÉRIAUX
# ============================================================
mat_a = make_material("Mouton_A_Mat", (0.9, 0.9, 0.85, 1.0))
mat_b = make_material("Mouton_B_Mat", (0.75, 0.65, 0.5, 1.0))

# ============================================================
#  IMPORT MOUTONS
# ============================================================
types = (
    [(mouton_a_stl, "A", mat_a)] * nb_moutons_a +
    [(mouton_b_stl, "B", mat_b)] * nb_moutons_b
)
random.shuffle(types)

positions_prises = []
for idx, (stl_path, typ, mat) in enumerate(types):
    x, y, angle_pos = position_aleatoire(rayon_parc, marge_bord, positions_prises)
    positions_prises.append((x, y, 0))

    obj = import_stl(stl_path)
    obj.name = f"Mouton{typ}_{idx+1:02d}"
    move_to_collection(obj, col_moutons)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    obj.scale = (scale, scale, scale)
    bpy.ops.object.transform_apply(scale=True, rotation=False, location=False)

    z_min_mesh = z_min_par_type[typ]
    obj.location = (x, y, 6 + (-z_min_mesh * scale))
    obj.lock_location[2] = True
    obj.rotation_euler = (0, 0, random.uniform(0, 2 * math.pi))

    print(f"✅ Mouton{typ}_{idx+1:02d} — pos ({x:.1f}, {y:.1f}) mm")

print(f"🐑 {len(types)} moutons placés !")

# ============================================================
#  BERGER
# ============================================================
scale_berger = 0.5

berger_stl    = os.path.join(blend_dir, "BonBerger.stl")
bb_min_berger = (-37.486137, 32.943996, -42.212002)
bb_max_berger = ( 21.476265, 101.096001, 101.279602)
cx_berger     = (bb_min_berger[0] + bb_max_berger[0]) / 2
cy_berger     = (bb_min_berger[1] + bb_max_berger[1]) / 2
z_min_berger  = bb_min_berger[2]

berger = import_stl(berger_stl)
berger.name = "BonBerger"
move_to_collection(berger, col_moutons)

bpy.context.view_layer.objects.active = berger
berger.select_set(True)

berger.scale = (scale_berger, scale_berger, scale_berger)
bpy.ops.object.transform_apply(scale=True, rotation=False, location=False)

berger.location = (
    -cx_berger * scale_berger,
    -cy_berger * scale_berger,
    6 + (-z_min_berger * scale_berger)
)
berger.lock_location[2] = True

print(f"✅ BonBerger posé — Z={6 + (-z_min_berger * scale_berger):.2f}")
print("🎉 Terminé !")