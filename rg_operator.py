# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see < https://www.gnu.org/licenses/ >.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (c) 2025 Roni Raihan

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import bpy
import re
from mathutils import Matrix, Quaternion


#Catatan :  kalau bisa jangan gabung antara `snap_bone_item`
#           `dynamic_snap_bone` dan `dynamic_snap_obj`
#           biar gak pusing pas mantenc bug nya


#~~~~ Untility ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def snap_bone_item(context, obj, item_snap_bone):
    #catatan kalo kepake:
        #World Space      = Armature Matrix  ×  Bone Matrix (pose space)
        #Bone Local Space = Parent Matrix⁻¹  ×  World Space
        #                    ^pake parent matrix kalo punya parent
        #                       kalo gak ada, pake armature matrix
        
    obj_data = obj.data
    for item in item_snap_bone:
        print(f"Snap Bone {item.bone}") ####################
        snap_bone = obj.pose.bones.get(item.bone)
        #target_bone = obj.pose.bones.get(item.target)
        
        #snap hitung snap lokasi
        if item.loc:
            jml = 0
            for i in range(obj_data.rairig_snap_iteration):
                context.view_layer.update()
                depsgraph = context.evaluated_depsgraph_get()
                obj_eval = obj.evaluated_get(depsgraph)
            
                #evaluasi bone
                snap_bone_eval = obj_eval.pose.bones.get(item.bone)
                target_bone_eval = obj_eval.pose.bones.get(item.target)
                
                # Relatif target terhadap snap, dalam pose space
                relative = snap_bone_eval.matrix.inverted() @ target_bone_eval.matrix
                loc_rel = relative.to_translation()
                #print(f"location_relative: {loc_rel}") ####################
                
                #hitung threshold
                thold = abs(loc_rel.x) + abs(loc_rel.y) + abs(loc_rel.z)
                if abs(thold) <= obj_data.rairig_snap_threshold:
                    break
                
                # Terapkan ke matrix_basis
                loc_matrix = snap_bone.matrix_basis @ relative
                snap_bone.location = loc_matrix.to_translation()
                #print(f"location_vextor: {loc_matrix.to_translation()}") ####################
                jml += 1
            print(f"Step snap location iteration: {jml}")
                
        # snap hitung rotasi
        if item.rot:
            jml = 0
            for i in range(obj_data.rairig_snap_iteration):
                context.view_layer.update()
                depsgraph = context.evaluated_depsgraph_get()
                obj_eval = obj.evaluated_get(depsgraph)
            
                # evaluasi bone
                snap_bone_eval = obj_eval.pose.bones.get(item.bone)
                target_bone_eval = obj_eval.pose.bones.get(item.target)
                

                # Relatif target terhadap snap, dalam pose space
                relative = snap_bone_eval.matrix.inverted() @ target_bone_eval.matrix
                rot_rel = relative.to_quaternion()
                #print(f"rotation_relative: {rot_rel}") ####################
                
                #hitung threshold
                thold = abs(abs(rot_rel.w) - 1.0) + abs(rot_rel.x) + abs(rot_rel.y) + abs(rot_rel.z)
                if abs(thold) <= obj_data.rairig_snap_threshold:
                    break
                
                #hitung delta
                if rot_rel.w <= 1.0 and rot_rel.w >= -1.0:
                    delta_w = -obj_data.rairig_snap_threshold if rot_rel.w < 0 else obj_data.rairig_snap_threshold
                else:
                    delta_w = -obj_data.rairig_snap_threshold if rot_rel.w > 0 else obj_data.rairig_snap_threshold
                delta_x = -obj_data.rairig_snap_threshold if rot_rel.x > 0 else obj_data.rairig_snap_threshold
                delta_y = -obj_data.rairig_snap_threshold if rot_rel.y > 0 else obj_data.rairig_snap_threshold
                delta_z = -obj_data.rairig_snap_threshold if rot_rel.z > 0 else obj_data.rairig_snap_threshold
                #print(f"delta: {delta_w, delta_x, delta_y, delta_z}") ####################
                
                
                # tambahkan delta ke rotasi basis
                rot_basis_matrix = snap_bone.matrix_basis @ relative
                rot_basis = rot_basis_matrix.to_quaternion()
                
                quar_vextor = Quaternion((
                    rot_basis.w + delta_w,
                    rot_basis.x + delta_x,
                    rot_basis.y + delta_y,
                    rot_basis.z + delta_z
                ))
                quar_vextor.normalize()
                #print(f"quar_vextor: {quar_vextor}") ####################
                
                # teapkan quarternion vextor
                if snap_bone.rotation_mode == 'QUATERNION':
                    snap_bone.rotation_quaternion = quar_vextor
                elif snap_bone.rotation_mode == 'AXIS_ANGLE':
                    snap_bone.rotation_axis_angle = quar_vextor.to_axis_angle()
                else:
                    snap_bone.rotation_euler = quar_vextor.to_euler(snap_bone.rotation_mode)
                    
                jml += 1
            print(f"Step snap rotation iteration: {jml}")
            
        #snap hitung skala
        if item.scl:
            jml = 0
            for i in range(obj_data.rairig_snap_iteration):
                context.view_layer.update()
                depsgraph = context.evaluated_depsgraph_get()
                obj_eval = obj.evaluated_get(depsgraph)
                
                #evaluasi bone
                snap_bone_eval = obj_eval.pose.bones.get(item.bone)
                target_bone_eval = obj_eval.pose.bones.get(item.target)
                
                # Relatif target terhadap snap, dalam pose space
                relative = snap_bone_eval.matrix.inverted() @ target_bone_eval.matrix
                scl_rel = relative.to_scale()
                #print(f"scale_relative: {scl_rel}") ####################
                
                #hitung threshold
                thold = abs(scl_rel.x - 1.0) + abs(scl_rel.y - 1.0) + abs(scl_rel.z - 1.0)
                if abs(thold) <= obj_data.rairig_snap_threshold:
                    break
                
                #tambah data relatif ke matrix basis
                scl_matrix = snap_bone.matrix_basis @ relative
                snap_bone.scale = scl_matrix.to_scale()
                #print(f"quar_vextor: {scl_matrix.to_scale()}") ####################
                jml += 1
            print(f"Step snap scale iteration: {jml}")
        context.view_layer.update()
        
def dynamic_snap_bone(context, obj, snap_bone, matrix, atur):
    loc, rot, scl, snap_iteration, snap_threshold = atur
    
    if loc:
        jml = 0
        for i in range(snap_iteration):
            context.view_layer.update()
            depsgraph = context.evaluated_depsgraph_get()
            obj_eval = obj.evaluated_get(depsgraph)
            snap_bone_eval = obj_eval.pose.bones.get(snap_bone.name)

            snap_world = obj_eval.matrix_world @ snap_bone_eval.matrix
            relative = snap_world.inverted() @ matrix
            loc_rel = relative.to_translation()

            thold = abs(loc_rel.x) + abs(loc_rel.y) + abs(loc_rel.z)
            if thold <= snap_threshold:
                break

            loc_matrix = snap_bone.matrix_basis @ relative
            snap_bone.location = loc_matrix.to_translation()
            jml += 1
        print(f"Step snap location iteration: {jml}")

    if rot:
        jml = 0
        for i in range(snap_iteration):
            context.view_layer.update()
            depsgraph = context.evaluated_depsgraph_get()
            obj_eval = obj.evaluated_get(depsgraph)
            snap_bone_eval = obj_eval.pose.bones.get(snap_bone.name)

            snap_world = obj_eval.matrix_world @ snap_bone_eval.matrix
            relative = snap_world.inverted() @ matrix
            rot_rel = relative.to_quaternion()

            thold = abs(abs(rot_rel.w) - 1.0) + abs(rot_rel.x) + abs(rot_rel.y) + abs(rot_rel.z)
            if thold <= snap_threshold:
                break

            if rot_rel.w <= 1.0 and rot_rel.w >= -1.0:
                delta_w = -snap_threshold if rot_rel.w < 0 else snap_threshold
            else:
                delta_w = -snap_threshold if rot_rel.w > 0 else snap_threshold
            delta_x = -snap_threshold if rot_rel.x > 0 else snap_threshold
            delta_y = -snap_threshold if rot_rel.y > 0 else snap_threshold
            delta_z = -snap_threshold if rot_rel.z > 0 else snap_threshold

            rot_basis_matrix = snap_bone.matrix_basis @ relative
            rot_basis = rot_basis_matrix.to_quaternion()

            quat = Quaternion((
                rot_basis.w + delta_w,
                rot_basis.x + delta_x,
                rot_basis.y + delta_y,
                rot_basis.z + delta_z
            ))
            quat.normalize()

            if snap_bone.rotation_mode == 'QUATERNION':
                snap_bone.rotation_quaternion = quat
            elif snap_bone.rotation_mode == 'AXIS_ANGLE':
                snap_bone.rotation_axis_angle = quat.to_axis_angle()
            else:
                snap_bone.rotation_euler = quat.to_euler(snap_bone.rotation_mode)
            jml += 1
        print(f"Step snap rotation iteration: {jml}")

    if scl:
        jml = 0
        for i in range(snap_iteration):
            context.view_layer.update()
            depsgraph = context.evaluated_depsgraph_get()
            obj_eval = obj.evaluated_get(depsgraph)
            snap_bone_eval = obj_eval.pose.bones.get(snap_bone.name)

            snap_world = obj_eval.matrix_world @ snap_bone_eval.matrix
            relative = snap_world.inverted() @ matrix
            scl_rel = relative.to_scale()

            thold = abs(scl_rel.x - 1.0) + abs(scl_rel.y - 1.0) + abs(scl_rel.z - 1.0)
            if thold <= snap_threshold:
                break

            scl_matrix = snap_bone.matrix_basis @ relative
            snap_bone.scale = scl_matrix.to_scale()
            jml += 1
        print(f"Step snap scale iteration: {jml}")
    context.view_layer.update()
    
def dynamic_snap_obj(context, obj, matrix, atur):
    loc, rot, scl, snap_iteration, snap_threshold = atur
    
    if loc:
        jml = 0
        for i in range(snap_iteration):
            context.view_layer.update()
            depsgraph = context.evaluated_depsgraph_get()
            obj_eval = obj.evaluated_get(depsgraph)

            relative = obj_eval.matrix_world.inverted() @ matrix
            loc_rel = relative.to_translation()

            thold = abs(loc_rel.x) + abs(loc_rel.y) + abs(loc_rel.z)
            if thold <= snap_threshold:
                break

            loc_matrix = obj.matrix_basis @ relative
            obj.location = loc_matrix.to_translation()
            jml += 1
        print(f"Step snap location iteration: {jml}")

    if rot:
        jml = 0
        for i in range(snap_iteration):
            context.view_layer.update()
            depsgraph = context.evaluated_depsgraph_get()
            obj_eval = obj.evaluated_get(depsgraph)

            relative = obj_eval.matrix_world.inverted() @ matrix
            rot_rel = relative.to_quaternion()

            thold = abs(abs(rot_rel.w) - 1.0) + abs(rot_rel.x) + abs(rot_rel.y) + abs(rot_rel.z)
            if thold <= snap_threshold:
                break

            if rot_rel.w <= 1.0 and rot_rel.w >= -1.0:
                delta_w = -snap_threshold if rot_rel.w < 0 else snap_threshold
            else:
                delta_w = -snap_threshold if rot_rel.w > 0 else snap_threshold
            delta_x = -snap_threshold if rot_rel.x > 0 else snap_threshold
            delta_y = -snap_threshold if rot_rel.y > 0 else snap_threshold
            delta_z = -snap_threshold if rot_rel.z > 0 else snap_threshold

            rot_basis_matrix = obj.matrix_basis @ relative
            rot_basis = rot_basis_matrix.to_quaternion()

            quat = Quaternion((
                rot_basis.w + delta_w,
                rot_basis.x + delta_x,
                rot_basis.y + delta_y,
                rot_basis.z + delta_z
            ))
            quat.normalize()

            if obj.rotation_mode == 'QUATERNION':
                obj.rotation_quaternion = quat
            elif obj.rotation_mode == 'AXIS_ANGLE':
                obj.rotation_axis_angle = quat.to_axis_angle()
            else:
                obj.rotation_euler = quat.to_euler(obj.rotation_mode)
            jml += 1
        print(f"Step snap rotation iteration: {jml}")

    if scl:
        jml = 0
        for i in range(snap_iteration):
            context.view_layer.update()
            depsgraph = context.evaluated_depsgraph_get()
            obj_eval = obj.evaluated_get(depsgraph)

            relative = obj_eval.matrix_world.inverted() @ matrix
            scl_rel = relative.to_scale()

            thold = abs(scl_rel.x - 1.0) + abs(scl_rel.y - 1.0) + abs(scl_rel.z - 1.0)
            if thold <= snap_threshold:
                break

            scl_matrix = obj.matrix_basis @ relative
            obj.scale = scl_matrix.to_scale()
            jml += 1
        print(f"Step snap scale iteration: {jml}")
    context.view_layer.update()
        
def rapikan_lct_bone(context, lct_bone):
    jml_inv = 0
    jml_dup = 0
    if len(lct_bone) > 0:
        obj_bones = get_bones_collection(context.active_object)
        
        hapus_list = []
        ada = set()
        for i, lct in enumerate(lct_bone):
            
            if lct.name and lct.name in obj_bones:
                if lct.name in ada:
                    hapus_list.append(i)
                    jml_dup += 1
                else:
                    ada.add(lct.name)
            else:
                hapus_list.append(i)
                jml_inv += 1
        
        for i in reversed(hapus_list):
            lct_bone.remove(i)
            
    return jml_inv, jml_dup

def split_last_attr(path):
        """Ambil nama atribut terakhir dari path (setelah titik terakhir di luar brackets)."""
        depth = 0
        for i in range(len(path) - 1, -1, -1):
            c = path[i]
            if c in (']', ')'):
                depth += 1
            elif c in ('[', '('):
                depth -= 1
            elif c == '.' and depth == 0:
                return path[i + 1:]
        return None
    
def perbaharui_validasi_data_path(item):
    item.key = ""
    item.owner = ""
    item.i_key = -1
    custom_prop_match = re.search(r'\["([^"]+)"\]$', item.data_path)
    attr = split_last_attr(item.data_path)
    
    if custom_prop_match:
        #print(f"1 {item.name}") ##########
        key = custom_prop_match.group(1)
        item.key = f'["{key}"]'
        item.owner = item.data_path[:custom_prop_match.start()]
        item.sah_data_path = True
    elif attr:
        #print(f"2 {item.name}") ##########
        item.owner = item.data_path[:-(len(attr) + 1)]
        index_match = re.search(r'^(.+)\[(\d+)\]$', attr)
        if index_match:
            item.key = index_match.group(1)
            item.i_key = int(index_match.group(2))
        else:
            item.i_key = -1
            item.key = attr
        item.sah_data_path = True
    elif item.data_path:
        #print(f"3 {item.name}") ##########
        index_match = re.search(r'^(.+)\[(\d+)\]$', item.data_path)
        custom_prop_match = re.search(r'\["([^"]+)"\]$', index_match.group(1))
        if index_match:
            if custom_prop_match:
                key = custom_prop_match.group(1)
                item.owner = item.data_path[:custom_prop_match.start()]
                item.key = f'["{key}"]'
                item.i_key = int(index_match.group(2))
            else:
                item.key = index_match.group(1)
                item.i_key = int(index_match.group(2))
        else:
            item.key = item.data_path
        item.sah_data_path = True
    else:
        item.sah_data_path = False
        
def get_bones_collection(obj):
    if obj.mode == 'POSE':
        return obj.pose.bones
    elif obj.mode == 'EDIT':
        return obj.data.edit_bones
    else:
        return obj.data.bones
        
def perbaharui_validasi_snap_bone(obj, itemnya):
    if len(itemnya.snap_bone) <1:
        return False
    
    obj_bones = get_bones_collection(obj)
    for item in itemnya.snap_bone:
        if not item.bone or not item.target or item.bone == item.target:
            return False

        if not item.bone in obj_bones or not item.target in obj_bones:
            return False

    return True

def perbaharui_validasi_lct_bone(obj, itemnya):
    if len(itemnya.lct_bone) <1:
        return False
    
    obj_bones = get_bones_collection(obj)
    for item in itemnya.lct_bone:
        if not item.name:
            return False

        if not item.name in obj_bones:
            return False

    return True

#~~~~ Edit dan apply ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class edit_grup(bpy.types.Operator):
    bl_idname = "data.edit_group"
    bl_label = "Edit group"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        data = context.active_object.data
        
        #lakukan tindakan ke mode edit di sini
        
        data.rairig_edit = True
        return {'FINISHED'}
    
class apply_grup(bpy.types.Operator):
    bl_idname = "data.apply_group"
    bl_label = "Apply Edit group"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        data = obj.data
        
        for grup in data.rairig_grup:
            for item in grup.itemnya:
                
                if item.type == 'PROP':
                    perbaharui_validasi_data_path(item)
                    
                elif item.type == 'SNP':
                    item.sah_snap_bone = perbaharui_validasi_snap_bone(obj, item)
                    
                    if item.sah_snap_bone and item.snap_lct_bone and item.snap_tambahan_lct_bone:
                        if len(item.lct_bone) > 0:
                            item.sah_snap_bone = perbaharui_validasi_lct_bone(obj, item)
                    
                elif item.type == 'LCT':
                    item.sah_snap_bone = perbaharui_validasi_lct_bone(obj, item)
        
        data.rairig_edit = False
        return {'FINISHED'}
    
#~~~~ grub operator ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class tambah_grup(bpy.types.Operator):
    bl_idname = "data.add_group"
    bl_label = "Add Group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        data = context.active_object.data
        
        item = data.rairig_grup.add()
        item.name = "group"
        data.rairig_pilih_grup = len(data.rairig_grup) - 1
        return {'FINISHED'}
    
class hapus_grup(bpy.types.Operator):
    bl_idname = "data.remove_group"
    bl_label = "Remove Group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        data = context.active_object.data

        grup = data.rairig_grup
        index = data.rairig_pilih_grup

        if index < 0 or index >= len(grup):
            return {'CANCELLED'}

        grup.remove(index)
        data.rairig_pilih_grup = max(0, index - 1)
        return {'FINISHED'}

class pindah_grup_atas(bpy.types.Operator):
    bl_idname = "data.move_group_up"
    bl_label = "Move Group Up"
    bl_description = "Move Group Up"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        data = context.active_object.data

        index = data.rairig_pilih_grup
        if index <= 0:
            return {'CANCELLED'}

        data.rairig_grup.move(index, index - 1)
        data.rairig_pilih_grup -= 1
        return {'FINISHED'}
    
class pindah_grup_bawah(bpy.types.Operator):
    bl_idname = "data.move_group_down"
    bl_label = "Move Group Down"
    bl_description = "Move Group Down"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        data = context.active_object.data

        index = data.rairig_pilih_grup
        if index >= len(data.rairig_grup) - 1:
            data.rairig_pilih_grup = len(data.rairig_grup) - 1
            return {'CANCELLED'}

        data.rairig_grup.move(index, index + 1)
        data.rairig_pilih_grup += 1
        return {'FINISHED'}
    
#~~~~ itemnya operator ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class tambah_itemnya(bpy.types.Operator):
    bl_idname = "data.add_itemnya"
    bl_label = "Add Property"
    bl_options = {'REGISTER', 'UNDO'}
    
    type: bpy.props.EnumProperty(name='Type', default='PROP',
            items=(
                ('LAB', "Label", "Type Label Text"),
                ('PROP', "Property", "Type Property"),
                ('SNP', "Snap Operator", "Type Snap Operator"),
                ('LCT', "Selection Operator", "Type Selection Operator")
                    )
                )

    def execute(self, context):
        data = context.active_object.data
        grup = data.rairig_grup[data.rairig_pilih_grup]
        
        item = grup.itemnya.add()
        if self.type == 'PROP':
            item.type = 'PROP'
            item.name = "Property"
            
        elif self.type == 'SNP':
            item.type = 'SNP'
            item.name = "Snap to"
            sb = item.snap_bone.add()
            
        elif self.type == 'LCT':
            item.type = 'LCT'
            item.name = "Select Bones"
            lct = item.lct_bone.add()
            
        else:
            item.type = 'LAB'
            item.name = "Label Text"
            
        grup.itemnya_pilih = len(grup.itemnya) - 1
        return {'FINISHED'}
    
class hapus_itemnya(bpy.types.Operator):
    bl_idname = "data.remove_itemnya"
    bl_label = "Remove Property"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        data = context.active_object.data
        grup = data.rairig_grup[data.rairig_pilih_grup]

        item = grup.itemnya
        index = grup.itemnya_pilih

        if index < 0 or index >= len(item):
            return {'CANCELLED'}

        item.remove(index)
        grup.itemnya_pilih = max(0, index - 1)
        return {'FINISHED'}

class pindah_itemnya_atas(bpy.types.Operator):
    bl_idname = "data.move_itemnya_up"
    bl_label = "Move Property Up"
    bl_description = "Move Property Up"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        data = context.active_object.data
        grup = data.rairig_grup[data.rairig_pilih_grup]

        index = grup.itemnya_pilih
        if index <= 0:
            return {'CANCELLED'}

        grup.itemnya.move(index, index - 1)
        grup.itemnya_pilih -= 1
        return {'FINISHED'}
    
class pindah_itemnya_bawah(bpy.types.Operator):
    bl_idname = "data.move_itemnya_down"
    bl_label = "Move Property Down"
    bl_description = "Move Property Down"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        data = context.active_object.data
        grup = data.rairig_grup[data.rairig_pilih_grup]

        index = grup.itemnya_pilih
        if index >= len(grup.itemnya) - 1:
            grup.itemnya_pilih = len(grup.itemnya) - 1
            return {'CANCELLED'}

        grup.itemnya.move(index, index + 1)
        grup.itemnya_pilih += 1
        return {'FINISHED'}
    
#~~~~ lct bone operator ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class lct_bone_menu_operator(bpy.types.Operator):
    bl_idname = "data.lct_bone_menu"
    bl_label = "Select Bones"
    bl_description = "Snap Bone"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(name='Pilih', default=0, min=0)
    shift: bpy.props.BoolProperty(default=False)
    
    def invoke(self, context, event):
        self.shift = event.shift
        return self.execute(context)

    def execute(self, context):
        obj = context.active_object
        data = obj.data
        grup = data.rairig_grup[data.rairig_pilih_grup]
        item = grup.itemnya[self.index]
        
        if not obj.mode in ('POSE', 'EDIT'):
            self.report({'ERROR'}, "Only in 'Pose Mode' or 'Edit Mode'")
            return {'CANCELLED'}
        
        #cek validasi bone
        if item.type == 'SNP':
            item.sah_snap_bone = perbaharui_validasi_snap_bone(obj, item)
            if item.sah_snap_bone and item.snap_tambahan_lct_bone:
                if len(item.lct_bone) > 0:
                    item.sah_snap_bone = perbaharui_validasi_lct_bone(obj, item)
        else:
            item.sah_snap_bone = perbaharui_validasi_lct_bone(obj, item)
        
        #batal jika tidak valid
        if not item.sah_snap_bone:
            return {'CANCELLED'}
        
        #kumpulkan lct_bone_list
        lct_bone_list = []
        lct_aktif = ''
        if item.type == 'SNP':
            for sp in item.snap_bone:
                if sp.pilih_bone and not sp.bone in lct_bone_list:
                    if sp.bone == item.lct_bone_active:
                        lct_aktif = item.lct_bone_active
                    else:
                        lct_bone_list.append(sp.bone)
                        
            if item.snap_tambahan_lct_bone and len(item.lct_bone) > 0:
                for lct in item.lct_bone:
                    if not lct.name in lct_bone_list:
                        if lct.name == item.lct_bone_active:
                            lct_aktif = item.lct_bone_active
                        else:
                            lct_bone_list.append(lct.name)
        else:
            for lct in item.lct_bone:
                if not lct.name in lct_bone_list:
                    if lct.name == item.lct_bone_active:
                        lct_aktif = item.lct_bone_active
                    else:
                        lct_bone_list.append(lct.name)
                        
        if lct_aktif:
            lct_bone_list.append(lct_aktif)
            
        #batalkan jika gak ada satupun bone
        if not lct_bone_list:
            return {'CANCELLED'}
        
        #exsekusi
        if not self.shift:
            if obj.mode == 'POSE':
                bpy.ops.pose.select_all(action='DESELECT')
            elif obj.mode == 'EDIT':
                bpy.ops.armature.select_all(action='DESELECT')
        
        obj_bones = get_bones_collection(obj)
        gagal = []
        for b in lct_bone_list:
            try:
                bone = obj_bones.get(b)
            
                bone.select = True
                if obj.mode == 'EDIT':
                    bone.select_head = True
                    bone.select_tail = True
                    obj_bones.active = bone
                else:
                    obj.data.bones.active = obj.data.bones[b]
                    
            except Exception as e:
                print(e)
                gagal.append(b)
                
        #kasih tau kalo ada yang gagal
        if gagal:
            self.report({'WARNING'}, f"Can't select {gagal}")
                
        return {'FINISHED'}
    
class tambah_lct_bone(bpy.types.Operator):
    bl_idname = "data.add_lct_bone"
    bl_label = "Add Selection Bone List"
    bl_options = {'REGISTER', 'UNDO'}
    
    mode: bpy.props.EnumProperty(name='Mode', default='ADD',
            items=(
                ('ADD', "Add", "Add Selection Bone List"),
                ('FILL', "Add Selected Bone", "Add Selected Bone to Selection Bone List")
            )
        )

    def execute(self, context):
        data = context.active_object.data
        grup = data.rairig_grup[data.rairig_pilih_grup]
        itemnya = grup.itemnya[grup.itemnya_pilih]
        
        if self.mode == 'FILL':
            obj = context.active_object
            
            if obj.mode == 'EDIT':
                active = obj.data.edit_bones.active
                selected_bones = [b.name for b in obj.data.edit_bones if b.select or (active and b.name == active.name)]
            elif obj.mode == 'POSE':
                active = obj.data.bones.active
                selected_bones = [b.name for b in obj.pose.bones if b.select or (active and b.name == active.name)]
            else:
                self.report({'ERROR'}, "Only in 'Pose Mode' or 'Edit Mode'")
                return {'CANCELLED'}
            
            ada_list = [a.name for a in itemnya.lct_bone]
            ada_bone = False
            for b in selected_bones:
                if not b in ada_list:
                    lct = itemnya.lct_bone.add()
                    lct.name = b
                else:
                    ada_bone = True
            
            if ada_bone:
                self.report({'INFO'}, "Some bones are already on the list")
            else:
                self.report({'INFO'}, "Successfully added bones to the list")
            
        else:
            lct = itemnya.lct_bone.add()
            lct.name = ""
            
        itemnya.lct_pilih = len(itemnya.lct_bone) - 1
        return {'FINISHED'}
    
class hapus_lct_bone(bpy.types.Operator):
    bl_idname = "data.remove_lct_bone"
    bl_label = "Remove Selection Bone List"
    bl_options = {'REGISTER', 'UNDO'}
    
    mode: bpy.props.EnumProperty(name='Mode', default='NRM',
            items=(
                ('NRM', "Normal", "Remove Selection Bone List"),
                ('CLN', "Add Selected Bone", "Remove Invalid Bone List")
            )
        )

    def execute(self, context):
        data = context.active_object.data
        grup = data.rairig_grup[data.rairig_pilih_grup]
        itemnya = grup.itemnya[grup.itemnya_pilih]
        
        lct = itemnya.lct_bone
        if self.mode == 'CLN':
            jml_inv, jml_dup = rapikan_lct_bone(context, lct)
            self.report({'INFO'}, f"{jml_inv} invalid bone and {jml_dup} duplicate bone removed from list")
        else:
            index = itemnya.lct_pilih
            if index < 0 or index >= len(lct):
                return {'CANCELLED'}
            
            lct.remove(index)
            itemnya.lct_pilih = max(0, index - 1)
        return {'FINISHED'}
    
class set_aktif_lct_bone(bpy.types.Operator):
    bl_idname = "data.set_aktif_lct_bone"
    bl_label = "Set Active Selection Bone List"
    bl_options = {'REGISTER', 'UNDO'}
    
    aktif: bpy.props.StringProperty(name='Set', default='')
    
    def execute(self, context):
        data = context.active_object.data
        grup = data.rairig_grup[data.rairig_pilih_grup]
        itemnya = grup.itemnya[grup.itemnya_pilih]
        
        itemnya.lct_bone_active = self.aktif
        return {'FINISHED'}

#~~~~ snap operator ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class snap_menu_operator(bpy.types.Operator):
    bl_idname = "data.snap_menu"
    bl_label = "Snap Bone"
    bl_description = "Snap Bone"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(name='Pilih', default=0, min=0)

    def execute(self, context):
        obj = context.active_object
        data = obj.data
        grup = data.rairig_grup[data.rairig_pilih_grup]
        item = grup.itemnya[self.index]
        
        if not obj.mode == 'POSE' or not item.type == 'SNP' or data.pose_position == 'REST':
            return {'CANCELLED'}
        
        item.sah_snap_bone = perbaharui_validasi_snap_bone(obj, item)
        
        if not item.sah_snap_bone:
            return {'CANCELLED'}
        
        snap_bone = item.snap_bone
        snap_bone_item(context, obj, snap_bone)
        return {'FINISHED'}
    
class refresh_snap_bone(bpy.types.Operator):
    bl_idname = "data.refresh_snap_bone"
    bl_label = "Refresh"
    bl_description = "Refresh Snap Bone"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(name='Pilih', default=0, min=0)

    def execute(self, context):
        obj = context.active_object
        data = obj.data
        grup = data.rairig_grup[data.rairig_pilih_grup]
        item = grup.itemnya[self.index]
        
        if not item.type in ('SNP', 'LCT'):
            return {'CANCELLED'}
        
        if item.type == 'SNP':
            item.sah_snap_bone = perbaharui_validasi_snap_bone(obj, item)
            if item.sah_snap_bone and item.snap_lct_bone and item.snap_tambahan_lct_bone:
                if len(item.lct_bone) > 0:
                    item.sah_snap_bone = perbaharui_validasi_lct_bone(obj, item)
        else:
            item.sah_snap_bone = perbaharui_validasi_lct_bone(obj, item)
            
        return {'FINISHED'}
    
class tambah_snap_bone(bpy.types.Operator):
    bl_idname = "data.add_snap_bone"
    bl_label = "Add Snap Bone"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        data = context.active_object.data
        grup = data.rairig_grup[data.rairig_pilih_grup]
        itemnya = grup.itemnya[grup.itemnya_pilih]
        
        sb = itemnya.snap_bone.add()
        sb.bone = ""
        sb.target = ""
        return {'FINISHED'}
    
class hapus_snap_bone(bpy.types.Operator):
    bl_idname = "data.remove_snap_bone"
    bl_label = "Remove Snap Bone"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(name='Pilih', default=0, min=0)
        
    def execute(self, context):
        data = context.active_object.data
        grup = data.rairig_grup[data.rairig_pilih_grup]
        itemnya = grup.itemnya[grup.itemnya_pilih]
        
        sb = itemnya.snap_bone
        sb.remove(self.index)
        return {'FINISHED'}
    
class pindah_snap_bone_atas(bpy.types.Operator):
    bl_idname = "data.move_snap_bone_up"
    bl_label = "Move Snap Bone Up"
    bl_description = "Move Snap Bone Up"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(name='Pilih', default=0, min=0)

    def execute(self, context):
        data = context.active_object.data
        grup = data.rairig_grup[data.rairig_pilih_grup]
        itemnya = grup.itemnya[grup.itemnya_pilih]

        if self.index <= 0:
            return {'CANCELLED'}

        itemnya.snap_bone.move(self.index, self.index - 1)
        return {'FINISHED'}
    
class pindah_snap_bone_bawah(bpy.types.Operator):
    bl_idname = "data.move_snap_bone_down"
    bl_label = "Move Snap Bone Down"
    bl_description = "Move Snap Bone Down"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(name='Pilih', default=0, min=0)

    def execute(self, context):
        data = context.active_object.data
        grup = data.rairig_grup[data.rairig_pilih_grup]
        itemnya = grup.itemnya[grup.itemnya_pilih]

        if self.index >= len(itemnya.snap_bone) - 1:
            return {'CANCELLED'}

        itemnya.snap_bone.move(self.index, self.index + 1)
        return {'FINISHED'}
    
#~~~~ dinamis snap operator ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class dinamis_snap_operator(bpy.types.Operator):
    bl_idname = "scene.dinamis_snap_menu"
    bl_label = "Dynamic Snap"
    bl_description = "Dynamic Snap From Clipboard"
    bl_options = {'REGISTER', 'UNDO'}
    
    loc: bpy.props.BoolProperty(name='Location', default=True)
    rot: bpy.props.BoolProperty(name='Rotation', default=True)
    scl: bpy.props.BoolProperty(name='Scale', default=True)
    snap_iteration: bpy.props.IntProperty(name='Snap Max Step', default=100, min=2)
    snap_threshold: bpy.props.FloatProperty(name='Threshold', default=0.0001, min=0.00001, max=1.000, step=1, precision=5)

    def parse_matrix_from_clipboard(self, context):
        clipboard = context.window_manager.clipboard
    
        # Ambil semua angka dari string
        numbers = re.findall(r'[-+]?\d*\.?\d+(?:e[-+]?\d+)?', clipboard)
    
        if len(numbers) != 16:
            return None
    
        values = [float(n) for n in numbers]
    
        # Susun jadi 4x4 matrix (row-major)
        matrix = Matrix([
            values[0:4],
            values[4:8],
            values[8:12],
            values[12:16]
        ])
        return matrix

    def execute(self, context):
        scene = context.scene
        obj = context.active_object
        
        self.snap_iteration = scene.rairig_snap_iteration
        self.snap_threshold = scene.rairig_snap_threshold
        
        #if not obj.mode == 'POSE' or not item.type == 'SNP' or data.pose_position == 'REST':
            #return {'CANCELLED'}
            
        matrix = self.parse_matrix_from_clipboard(context)
        if matrix is None:
            self.report({'ERROR'}, "Clipboard does not contain a valid matrix")
            return {'CANCELLED'}
        
        atur = (self.loc, self.rot, self.scl, self.snap_iteration, self.snap_threshold)
        
        if obj.type == "ARMATURE" and obj.mode == 'POSE':
            snap_bone = context.active_pose_bone
            if not snap_bone:
                self.report({'ERROR'}, "Mising active bone")
                return {'CANCELLED'}
            dynamic_snap_bone(context, obj, snap_bone, matrix, atur)
        else:
            dynamic_snap_obj(context, obj, matrix, atur)
        return {'FINISHED'}


classes = [
    edit_grup,
    apply_grup,
    tambah_grup,
    hapus_grup,
    pindah_grup_atas,
    pindah_grup_bawah,
    
    tambah_itemnya,
    hapus_itemnya,
    pindah_itemnya_atas,
    pindah_itemnya_bawah,
    
    lct_bone_menu_operator,
    tambah_lct_bone,
    hapus_lct_bone,
    set_aktif_lct_bone,
    
    snap_menu_operator,
    refresh_snap_bone,
    tambah_snap_bone,
    hapus_snap_bone,
    pindah_snap_bone_atas,
    pindah_snap_bone_bawah,
    
    dinamis_snap_operator
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()