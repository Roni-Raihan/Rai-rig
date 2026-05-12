bl_info = {
    "name": "Rai-rig",
    "author": "Roni Raihan",
    "version": (1, 0),
    "blender": (5, 1, 0),
    "location": "Properties > Object Data Properties",
    "description": "Add UI for costume property and operator snap",
    "warning": "",
    "doc_url": "",
    "category": "Rigging",
}

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

from . import rg_property
from . import rg_operator
from . import rg_ui

def register():
    rg_property.register()
    rg_operator.register()
    rg_ui.register()

def unregister():
    rg_ui.unregister()
    rg_operator.unregister()
    rg_property.unregister()
    

if __name__ == "__main__":
    register()