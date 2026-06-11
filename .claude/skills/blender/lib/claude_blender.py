# claude_blender — Blender 無頭建模共用函式庫
# 由 blender --background --python build.py -- --out xxx.blend 執行
import bpy
import math
import os
import sys

_OUT_PATH = None


def parse_args():
    """讀取 '--' 之後的 --out 參數，決定 .blend 輸出路徑。"""
    global _OUT_PATH
    argv = sys.argv
    if "--" in argv:
        args = argv[argv.index("--") + 1:]
        if "--out" in args:
            _OUT_PATH = os.path.abspath(args[args.index("--out") + 1])
    if not _OUT_PATH:
        _OUT_PATH = os.path.abspath("output.blend")
    return _OUT_PATH


def reset_scene():
    """清空場景（物件、材質、網格），保留乾淨世界。"""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block_list in (bpy.data.meshes, bpy.data.materials, bpy.data.curves,
                       bpy.data.lights, bpy.data.cameras):
        for block in list(block_list):
            if block.users == 0:
                block_list.remove(block)


def _finish(obj, name, location, rotation, scale):
    if name:
        obj.name = name
    if location:
        obj.location = location
    if rotation:
        obj.rotation_euler = rotation
    if scale:
        obj.scale = scale
    return obj


# ---------- 基礎物件 ----------

def add_cube(size=2, location=None, rotation=None, scale=None, name=None):
    bpy.ops.mesh.primitive_cube_add(size=size)
    return _finish(bpy.context.active_object, name, location, rotation, scale)


def add_plane(size=10, location=None, rotation=None, scale=None, name=None):
    bpy.ops.mesh.primitive_plane_add(size=size)
    return _finish(bpy.context.active_object, name, location, rotation, scale)


def add_sphere(radius=1, segments=32, location=None, rotation=None, scale=None, name=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segments)
    return _finish(bpy.context.active_object, name, location, rotation, scale)


def add_cylinder(radius=1, depth=2, vertices=32, location=None, rotation=None, scale=None, name=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=vertices)
    return _finish(bpy.context.active_object, name, location, rotation, scale)


def add_cone(radius=1, depth=2, location=None, rotation=None, scale=None, name=None):
    bpy.ops.mesh.primitive_cone_add(radius1=radius, depth=depth)
    return _finish(bpy.context.active_object, name, location, rotation, scale)


def add_torus(major_radius=1, minor_radius=0.25, location=None, rotation=None, scale=None, name=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major_radius, minor_radius=minor_radius)
    return _finish(bpy.context.active_object, name, location, rotation, scale)


def add_text(body, size=1, extrude=0.1, location=None, rotation=None, name=None):
    bpy.ops.object.text_add()
    obj = bpy.context.active_object
    obj.data.body = body
    obj.data.size = size
    obj.data.extrude = extrude
    return _finish(obj, name, location, rotation, None)


# ---------- 材質 ----------

def set_material(obj, name, color=(0.8, 0.8, 0.8), metallic=0.0, roughness=0.5, emission=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None:
        # Blender 4.x 改名為 Emission Color / Emission Strength
        for key in ("Emission Color", "Emission"):
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = (*emission, 1.0)
                break
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 2.0
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return mat


# ---------- 修改器 ----------

def add_subsurf(obj, levels=2):
    m = obj.modifiers.new("Subsurf", "SUBSURF")
    m.levels = levels
    m.render_levels = levels
    return m


def add_array(obj, count=3, offset=(2.5, 0, 0)):
    m = obj.modifiers.new("Array", "ARRAY")
    m.count = count
    m.use_relative_offset = False
    m.use_constant_offset = True
    m.constant_offset_displace = offset
    return m


def add_mirror(obj, axis="X"):
    m = obj.modifiers.new("Mirror", "MIRROR")
    m.use_axis = ("X" in axis, "Y" in axis, "Z" in axis)
    return m


def add_bevel(obj, width=0.05, segments=3):
    m = obj.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segments
    return m


def add_solidify(obj, thickness=0.1):
    m = obj.modifiers.new("Solidify", "SOLIDIFY")
    m.thickness = thickness
    return m


def add_boolean(obj, cutter, op="DIFFERENCE", hide_cutter=True):
    m = obj.modifiers.new("Boolean", "BOOLEAN")
    m.operation = op
    m.object = cutter
    if hide_cutter:
        cutter.hide_render = True
        cutter.hide_viewport = True
    return m


# ---------- 物理 / 機制 ----------

def add_rigidbody(obj, type="ACTIVE", mass=1.0):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = type
    obj.rigid_body.mass = mass
    return obj.rigid_body


def add_cloth(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_add(type="CLOTH")
    return obj.modifiers["Cloth"]


def set_constraint_follow_path(obj, curve):
    c = obj.constraints.new("FOLLOW_PATH")
    c.target = curve
    c.use_curve_follow = True
    return c


def bake_physics(frame_end=250):
    bpy.context.scene.frame_end = frame_end
    bpy.ops.ptcache.bake_all(bake=True)


# ---------- 動畫 ----------

def set_frame_range(start=1, end=250):
    bpy.context.scene.frame_start = start
    bpy.context.scene.frame_end = end


def keyframe(obj, frame, location=None, rotation=None, scale=None):
    if location:
        obj.location = location
        obj.keyframe_insert("location", frame=frame)
    if rotation:
        obj.rotation_euler = rotation
        obj.keyframe_insert("rotation_euler", frame=frame)
    if scale:
        obj.scale = scale
        obj.keyframe_insert("scale", frame=frame)


# ---------- 燈光 / 環境 / 相機 ----------

def add_sun(energy=3.0, rotation=(0.7, 0, 0.5), name="Sun"):
    bpy.ops.object.light_add(type="SUN", rotation=rotation)
    light = bpy.context.active_object
    light.name = name
    light.data.energy = energy
    return light


def add_point_light(location=(0, 0, 5), energy=500, name="Point"):
    bpy.ops.object.light_add(type="POINT", location=location)
    light = bpy.context.active_object
    light.name = name
    light.data.energy = energy
    return light


def add_area_light(location=(0, 0, 5), energy=200, size=5, name="Area"):
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.active_object
    light.name = name
    light.data.energy = energy
    light.data.size = size
    return light


def set_world_sky(strength=1.0, color=(0.05, 0.08, 0.15)):
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (*color, 1.0)
    bg.inputs["Strength"].default_value = strength


def add_camera(location=(12, -12, 8), look_at=(0, 0, 0), name="Camera"):
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.active_object
    cam.name = name
    direction = [look_at[i] - location[i] for i in range(3)]
    rot_z = math.atan2(direction[1], direction[0]) + math.pi / 2
    dist_xy = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
    rot_x = math.atan2(dist_xy, -direction[2])
    cam.rotation_euler = (rot_x, 0, rot_z)
    bpy.context.scene.camera = cam
    return cam


# ---------- 收尾 ----------

def save(filepath=None):
    path = os.path.abspath(filepath or _OUT_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print(f"[claude_blender] saved: {path}")
    return path


def render_preview(filepath=None, samples=16, resolution=(960, 540)):
    scene = bpy.context.scene
    if not scene.camera:
        add_camera()
    path = os.path.abspath(filepath or os.path.join(os.path.dirname(_OUT_PATH), "preview.png"))
    scene.render.engine = "BLENDER_EEVEE_NEXT" if hasattr(scene, "eevee") and bpy.app.version >= (4, 2, 0) else "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f"[claude_blender] preview: {path}")
    return path
