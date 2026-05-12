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
from bpy.props import (
    FloatProperty,
    EnumProperty,
    IntProperty,
    BoolProperty,
    PointerProperty
)


#~~~~~~~~~~~~~~~~~~~~~~ update prop
def filter_snap_bone(self, context):
    if self.bone == self.target and not self.target == '':
        self.bone = ""
        
def filter_snap_target(self, context):
    if self.target == self.bone and not self.bone == '':
        self.target = ""
        
def filter_lct_bone(self, context):
    return
    #data = context.active_object.data
    #grup = data.rairig_grup[data.rairig_pilih_grup]
    #itemnya = grup.itemnya[grup.itemnya_pilih]
    #lct_bone = [a.name for a in itemnya.lct_bone]
    
    #if self.name in lct_bone:
        #self.name = ''
    #if not self.name == '':
        #self.name = ''
    
#~~~~~~~~~~~~~~~~~~~~~~ snap_bone
class rairig_snap_bone(bpy.types.PropertyGroup):
    bone: bpy.props.StringProperty(name='Bone', default='', update = filter_snap_bone)
    target: bpy.props.StringProperty(name='Bone', default='', update = filter_snap_target)
    pilih_bone: bpy.props.BoolProperty(name='Selection', default=True)
    loc: bpy.props.BoolProperty(name='L', default=True)
    rot: bpy.props.BoolProperty(name='R', default=True)
    scl: bpy.props.BoolProperty(name='S', default=True)
    
#~~~~~~~~~~~~~~~~~~~~~~ snap_bone
class rairig_lct_bone(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Bone', default='', update = filter_lct_bone)
    
#~~~~~~~~~~~~~~~~~~~~~~ itemnya
class rairig_itemnya(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name Property', default='')
    type: bpy.props.EnumProperty(name='Type', default='PROP',
                                      items=(
                                        ('LAB', "Label", "Type Label Text"),
                                        ('PROP', "Property", "Type Property"),
                                        ('SNP', "Snap Operator", "Type Snap Operator"),
                                        ('LCT', "Selection Operator", "Type Selection Operator")
                                        )
                                    )
                                    
    #Property
    data_path: bpy.props.StringProperty(name='Data Path', default='')
    owner: bpy.props.StringProperty(name='owner', default='')
    key: bpy.props.StringProperty(name='key', default='')
    i_key: bpy.props.IntProperty(name='Pilih', default=-1)
    sah_data_path: bpy.props.BoolProperty(name='Valid', default=True)
    
    #snap
    snap_bone: bpy.props.CollectionProperty(type=rairig_snap_bone)
    snap_lct_bone: bpy.props.BoolProperty(name='Selection Operator', default=True)
    snap_tambahan_lct_bone: bpy.props.BoolProperty(name='Additional Bones Selection', default=False)
    sah_snap_bone: bpy.props.BoolProperty(name='Valid', default=True)
    
    #pilihan operator
    lct_bone: bpy.props.CollectionProperty(type=rairig_lct_bone)
    lct_pilih: bpy.props.IntProperty(name='Pilih', default=0, min=0)
    lct_bone_active: bpy.props.StringProperty(name='Set Active', default='')

#~~~~~~~~~~~~~~~~~~~~~~ grup
class rairig_grup(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name Property', default='')
    
    itemnya: bpy.props.CollectionProperty(type=rairig_itemnya)
    itemnya_pilih: bpy.props.IntProperty(name='Pilih', default=0, min=0)


classes = [
    rairig_snap_bone,
    rairig_lct_bone,
    rairig_itemnya,
    rairig_grup
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Armature.rairig_header_name = bpy.props.StringProperty(name='Costume Header', default='')
    bpy.types.Armature.rairig_edit = bpy.props.BoolProperty(name='Edit', default=False)
    
    bpy.types.Armature.rairig_grup = bpy.props.CollectionProperty(type=rairig_grup)
    bpy.types.Armature.rairig_pilih_grup = bpy.props.IntProperty(name='Pilih', default=0, min=0)
    
    bpy.types.Armature.rairig_snap_iteration = bpy.props.IntProperty(name='Snap Max Step', default=100, min=2)
    bpy.types.Armature.rairig_snap_threshold = bpy.props.FloatProperty(name='Threshold', default=0.00001, min=0.00001, max=1.000, step=1, precision=5)
    
    bpy.types.Scene.rairig_snap_iteration = bpy.props.IntProperty(name='Snap Max Step', default=100, min=2)
    bpy.types.Scene.rairig_snap_threshold = bpy.props.FloatProperty(name='Threshold', default=0.0001, min=0.00001, max=1.000, step=1, precision=5)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Armature.rairig_header_name
    del bpy.types.Armature.rairig_edit
    
    del bpy.types.Armature.rairig_grup
    del bpy.types.Armature.rairig_pilih_grup
    
    del bpy.types.Armature.rairig_snap_iteration
    del bpy.types.Armature.rairig_snap_threshold

if __name__ == "__main__":
    register()