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
#

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import bpy
        
        
def search_data_mode(context):
    obj = context.active_object
    if obj.mode == 'POSE':
        return (obj.pose, "bones")
    elif obj.mode == 'EDIT':
        return (obj.data, "edit_bones")
    else:
        return (obj.data, "bones")
    
def get_bones_collection(obj):
    if obj.mode == 'POSE':
        return obj.pose.bones
    elif obj.mode == 'EDIT':
        return obj.data.edit_bones
    else:
        return obj.data.bones
    
def get_lct_bone_list(itemnya):
    lct_bone_list =[]
    if itemnya.type == 'SNP':
        for sp in itemnya.snap_bone:
            if sp.bone and sp.pilih_bone and not sp.bone in lct_bone_list:
                lct_bone_list.append(sp.bone)
                
        if itemnya.snap_tambahan_lct_bone and len(itemnya.lct_bone) > 0:
            for lct in itemnya.lct_bone:
                if lct.name and not lct.name in lct_bone_list:
                    lct_bone_list.append(lct.name)
    else:
        for lct in itemnya.lct_bone:
            if lct.name and not lct.name in lct_bone_list:
                lct_bone_list.append(lct.name)
    return lct_bone_list

class grup_list_UI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                row = layout.row()
                row.prop(item, "name", text='', emboss=False)
                
class itemnya_list_UI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                row = layout.row()
                if item.type == 'LAB':
                    row.prop(item, "name", text='', icon='FILE_TEXT', emboss=False)
                elif item.type == 'PROP':
                    row.prop(item, "name", text='', icon='RNA', emboss=False)
                elif item.type == 'SNP':
                    row.prop(item, "name", text='', icon='SNAP_ON', emboss=False)
                elif item.type == 'LCT':
                    row.prop(item, "name", text='', icon='RESTRICT_SELECT_OFF', emboss=False)
                else:
                    row.prop(item, "name", text='', icon='BLANK1', emboss=False)
                    
class lct_bone_operator_list_UI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        search_data, search_property = search_data_mode(context)
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                bones = get_bones_collection(context.active_object)
                index = list(data.lct_bone).index(item)
                
                row = layout.row()
                row.alert = not item.name in bones
                if index == data.lct_pilih:
                    row.prop_search(item, "name", search_data, search_property, text="", icon='BONE_DATA')
                else:
                    row.prop(item, "name", text='', icon='BONE_DATA', emboss=False)
                    
class menu_tambah_itemnya(bpy.types.Menu):
    bl_label = "Add"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("data.add_itemnya", text="Label", icon='FILE_TEXT').type = 'LAB'
        layout.operator("data.add_itemnya", text="Property", icon='RNA').type = 'PROP'
        layout.operator("data.add_itemnya", text="Snap Operator", icon='SNAP_ON').type = 'SNP'
        layout.operator("data.add_itemnya", text="Selection Operator", icon='RESTRICT_SELECT_OFF').type = 'LCT'
        
class menu_lct_bone_active(bpy.types.Menu):
    bl_label = "Set Active"
    
    def draw(self, context):
        data = context.active_object.data
        grup = data.rairig_grup[data.rairig_pilih_grup]
        itemnya = grup.itemnya[grup.itemnya_pilih]
        layout = self.layout
            
        lct_bone_list = get_lct_bone_list(itemnya)
        layout.operator("data.set_aktif_lct_bone", text="Selected Last Bone In List").aktif = ''
        if len(lct_bone_list) > 0:
            for lct in lct_bone_list:
                layout.operator("data.set_aktif_lct_bone", text=f"{lct}", icon='BONE_DATA').aktif = f"{lct}"
        

class rairig_panel(bpy.types.Panel):
    bl_label = ""
    bl_idname = "DATA_PT_rairig"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        if context.active_object.type == "ARMATURE" and context.armature:
            return True
        
    def draw_header(self, context):
        data = context.active_object.data
        layout = self.layout
        
        if not data.rairig_header_name == "":
            nahedr = data.rairig_header_name
        else:
            nahedr = "Rai - Rig"
            
        if data.rairig_edit:
            layout.prop(data, "rairig_header_name", text="")
        else:
            layout.label(text=nahedr)
    
    def draw(self, context):
        data = context.active_object.data
        layout = self.layout
        
        layout.use_property_decorate = False
        layout.use_property_split = True
        
        row = layout.row()
        row.template_list("grup_list_UI", "", data, "rairig_grup", data, "rairig_pilih_grup")
        
        col = row.column(align=True)
        if data.rairig_edit:
            col.operator("data.add_group", text="", icon='ADD')
            col.operator("data.remove_group", text="", icon='REMOVE')
            col.separator()
            
        col.operator("data.move_group_up", text="", icon='TRIA_UP')
        col.operator("data.move_group_down", text="", icon='TRIA_DOWN')
        
        col.separator()
        if data.rairig_edit:
            col.operator("data.apply_group", text="", icon='MODIFIER', depress=True)
            
            if len(data.rairig_grup) > 0 and not data.rairig_pilih_grup > len(data.rairig_grup)-1 and not data.rairig_pilih_grup < 0:
                grup = data.rairig_grup[data.rairig_pilih_grup]
                self.rairig_edit_ui(context, layout, grup)
        else:
            col.separator()
            col.separator()
            col.separator()
            col.operator("data.edit_group", text="", icon='MODIFIER')
            
            if len(data.rairig_grup) > 0 and not data.rairig_pilih_grup > len(data.rairig_grup)-1 and not data.rairig_pilih_grup < 0:
                grup = data.rairig_grup[data.rairig_pilih_grup]
                self.rairig_menu_rig_ui(context, layout, grup)
            
    def rairig_edit_ui(self, context, layout, data):
        layout.label(text="Property Group")
        
        row = layout.row()
        row.template_list("itemnya_list_UI", "", data, "itemnya", data, "itemnya_pilih")
        
        col = row.column(align=True)
        #col.operator("data.add_itemnya", text="", icon='ADD')
        col.menu("menu_tambah_itemnya", text="", icon='ADD')
        col.operator("data.remove_itemnya", text="", icon='REMOVE')
        col.separator()
        col.operator("data.move_itemnya_up", text="", icon='TRIA_UP')
        col.operator("data.move_itemnya_down", text="", icon='TRIA_DOWN')
        
        if len(data.itemnya) > 0 and not data.itemnya_pilih > len(data.itemnya)-1 and not data.itemnya_pilih < 0:
            item = data.itemnya[data.itemnya_pilih]
            
            layout.label(text="Property Data")
            col = layout.column()
            col.prop(item, "type")
            
            if item.type == 'LAB':
                col.label(text="Text")
                col.prop(item, "name", text = "")
                
            elif item.type == 'PROP':
                col.prop(item, "data_path", icon='RNA')
                #col.prop(item, "owner", icon='RNA') ###################
                #col.prop(item, "key", icon='RNA') ###################
                #col.prop(item, "i_key", icon='RNA') ###################
            
            elif item.type == 'SNP':
                obj_data = context.active_object.data
                
                col.prop(obj_data, "rairig_snap_iteration")
                col.prop(obj_data, "rairig_snap_threshold")
                
                col.prop(item, "snap_lct_bone")
                row = col.row()
                row.active = item.snap_lct_bone
                col_tam_lct = row.column()
                col_tam_lct.prop(item, "snap_tambahan_lct_bone")
                self.lct_bone_active_ui_edit(context, col_tam_lct, item, item.snap_lct_bone)
                #col_lct_bone_active.prop(item, "lct_bone_active") ###################
                
                col.label(text="Snap Bone")
                box = col.box()
                col_sb = box.column(align=True)
                self.property_snap_edit_ui(context, col_sb, item)
                
                if item.snap_lct_bone and item.snap_tambahan_lct_bone:
                    col.label(text="Additional Selections Bones List")
                    box = col.box()
                    col_lct = box.column(align=True)
                    self.property_lct_edit_ui(context, col_lct, item)
                
            elif item.type == 'LCT':
                self.lct_bone_active_ui_edit(context, col, item, True)
                #col.prop(item, "lct_bone_active") ###################
                
                col.label(text="Selections Bones List")
                box = col.box()
                col_lct = box.column()
                self.property_lct_edit_ui(context, col_lct, item)
                
    def lct_bone_active_ui_edit(self, context, layout, item, enab):
        lct_list = get_lct_bone_list(item)
        row = layout.row()
        if enab and item.lct_bone_active and not item.lct_bone_active in lct_list:
            prtn = True
        else:
            prtn = False
            
        row.alert = prtn
        row.enabled = enab
        row.alignment = 'RIGHT'
        row.label(text="Set Active")
        
        col = row.column()
        col.menu("menu_lct_bone_active",
                    text=f"{item.lct_bone_active if item.lct_bone_active else 'Selected Last Bone In List'}",
                    icon=f"{'BONE_DATA' if item.lct_bone_active else 'NONE'}")
        
        if prtn:
            col = layout.column()
            col.alert = True
            col.label(text="Bone is not in the selection list", icon='ERROR')
            col.label(text="Will Set Active on last bone in list", icon='BLANK1')
            
    def property_snap_edit_ui(self, context, layout, data):
        search_data, search_property = search_data_mode(context)
        
        layout.use_property_split = False
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Bone")
        row.label(text="Snap To")
        row.label(text="Target")
        
        box = layout.box()
        if len(data.snap_bone) > 0:
            for i, item in enumerate(data.snap_bone):
                box_2 = box.box()
                row = box_2.row()
                
                col = row.column(align=True)
                col.operator("data.move_snap_bone_up", text="", icon='TRIA_UP').index = i
                col.operator("data.move_snap_bone_down", text="", icon='TRIA_DOWN').index = i
                
                col = row.column()
                row_bone = col.row()
                row_bone.alignment = 'CENTER'
                row_bone.prop_search(item, "bone", search_data, search_property, text="", icon='BONE_DATA')
                row_bone.prop_search(item, "target", search_data, search_property, text="", icon='SNAP_ON')
                
                row_set = col.row(align=True)
                row_selc = row_set.column()
                row_selc.active = data.snap_lct_bone
                if item.pilih_bone:
                    row_selc.prop(item, "pilih_bone", text="", icon='RESTRICT_SELECT_OFF', expand=True, toggle=1)
                else:
                    row_selc.prop(item, "pilih_bone", text="", icon='RESTRICT_SELECT_ON', expand=True, toggle=1)
                
                row_set.separator()
                row_set.prop(item, "loc", expand=True, toggle=1)
                row_set.prop(item, "rot", expand=True, toggle=1)
                row_set.prop(item, "scl", expand=True, toggle=1)
                
                col = row.column()
                col.operator("data.remove_snap_bone", text="", icon='REMOVE').index = i
        
        box.operator("data.add_snap_bone", text="Add Bone", icon='ADD')
        
    def property_lct_edit_ui(self, context, layout, data):
        layout.use_property_split = False
        
        row = layout.row()
        row.template_list("lct_bone_operator_list_UI", "", data, "lct_bone", data, "lct_pilih")
        row = layout.row()
        
        col_add = row.column(align=True)
        col_add.operator("data.add_lct_bone", text="Add", icon='ADD').mode = 'ADD'
        col_add.operator("data.add_lct_bone", text="Add Selected Bone", icon='BLANK1').mode = 'FILL'
        
        col_remove = row.column(align=True)
        col_remove.operator("data.remove_lct_bone", text="Remove", icon='REMOVE').mode = 'NRM'
        col_remove.operator("data.remove_lct_bone", text="Remove Invalid Bone List", icon='BLANK1').mode = 'CLN'
        
    def rairig_menu_rig_ui(self, context, layout, data):
        obj = context.active_object
         
        layout.label(text=f"{data.name}")
        col = layout.column()
        col.use_property_decorate = True
        
        for i, item in enumerate(data.itemnya):
            
            if item.type == 'LAB':
                col.label(text=f"{item.name}")
                
            elif item.type == 'PROP':
                self.property_data_path_menu_ui(context, col, item)
                
            elif item.type == 'SNP':
                row = col.row(align=True)
                row_snap = row.row(align=True)
                row_snap.enabled = obj.mode == 'POSE' and not obj.data.pose_position == 'REST'
                
                #row.prop(item, "sah_snap_bone") ###################
                if item.sah_snap_bone:
                    row_snap.operator("data.snap_menu", text=f"{item.name}", icon='SNAP_ON').index = i
                    
                    if item.snap_lct_bone:
                        row_lct = row.row(align=True)
                        row_lct.enabled = obj.mode in ('POSE', 'EDIT')
                        row_lct.operator("data.lct_bone_menu", text="", icon='RESTRICT_SELECT_OFF').index = i
                else:
                    row.alert = True
                    row.operator("data.refresh_snap_bone", text=f'Missing bone for "{item.name}"', icon='FILE_REFRESH').index = i
            
            elif item.type == 'LCT':
                row = col.row(align=True)
                row_lct = row.row(align=True)
                #row.prop(item, "sah_snap_bone") ###################
                
                row_lct.enabled =obj.mode in ('POSE', 'EDIT')
                    
                if item.sah_snap_bone:
                    row_lct.operator("data.lct_bone_menu", text=f"{item.name}", icon='RESTRICT_SELECT_OFF').index = i
                else:
                    row.alert = True
                    row.operator("data.refresh_snap_bone", text=f'Missing bone for "{item.name}"', icon='FILE_REFRESH').index = i
                
    def property_data_path_menu_ui(self, context, col, data):
        if data.sah_data_path:
            try:
                owner = self.resolve_owner(data, context)
                if data.i_key > -1:
                    col.prop(owner, data.key, index=data.i_key, text=data.name)
                else:
                    col.prop(owner, data.key, text=f"{data.name}")
            except Exception: # as e:
                #print(e)
                box = col.box()
                box.alert = True
                box.label(text=f"Invalid Data Path For {data.name}", icon='ERROR')
        else:
            box = col.box()
            box.alert = True
            box.label(text=f"Invalid Data Path For {data.name}", icon='ERROR')
            
    def resolve_owner(self, data, context):
        """Coba resolve owner dari Object, fallback ke Object.data"""
        for source in [context.active_object, context.active_object.data]:
            try:
                owner = source.path_resolve(data.owner) if data.owner else source
                # validasi key-nya ada di owner ini
                if data.key.startswith('["'):
                    owner[data.key[2:-2]]  # akses custom prop
                else:
                    getattr(owner, data.key.split("[")[0])  # akses built-in attr
                return owner
            except Exception:
                continue
        return None

class rairig_dinamis_snap_panel(bpy.types.Panel):
    bl_label = "Dynamic Snap"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animation"
    bl_parent_id = "VIEW3D_PT_copy_global_transform"
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        
        layout.use_property_decorate = False
        layout.use_property_split = True
        
        col = layout.column()
        col.operator("scene.dinamis_snap_menu", text='Paste Dynamic Snap', icon='PASTEDOWN')
        col.prop(scene, "rairig_snap_iteration")
        col.prop(scene, "rairig_snap_threshold")

            
classes = [
    grup_list_UI,
    itemnya_list_UI,
    lct_bone_operator_list_UI,
    menu_tambah_itemnya,
    menu_lct_bone_active,
    rairig_panel,
    rairig_dinamis_snap_panel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()