# main.py

import bpy # type: ignore
import json
from bpy.types import Panel, Operator, PropertyGroup # type: ignore
from bpy.props import StringProperty, BoolProperty, PointerProperty, CollectionProperty, EnumProperty # type: ignore
import math
import re
import os

# ---------------------
# $1 UTILITY FUNCTIONS

# Function to set the context to the armature object and switch to Pose Mode
def set_pose_mode(armature_name):
    armature = bpy.data.objects.get(armature_name)
    if armature and armature.type == 'ARMATURE':
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
    return armature

# Function to select a specific bone
def select_bone(armature, bone_name):
    pose_bone = armature.pose.bones.get(bone_name)
    if pose_bone:
        bpy.context.object.data.bones.active = armature.data.bones[pose_bone.name]
    return pose_bone

# Function to parse string to list of floats
def parse_rotation_input(input_string):
    try:
        return [float(x) for x in input_string.strip('[]').split(',')]
    except ValueError:
        return None

# Convert degrees to radians
def degrees_to_radians(degrees):
    return [math.radians(deg) for deg in degrees]

# Convert radians to degrees
def radians_to_degrees(radians):
    return [math.degrees(rad) for rad in radians]

# Format a float to two decimal places, ensuring -0.00 is shown as 0.00
def format_float(value):
    formatted_value = format(round(value, 2), ".2f")
    if formatted_value == "-0.00":
        formatted_value = "0.00"
    return formatted_value

# Apply hand pose from blend file
def apply_hand_pose_from_blend(blend_path, hand_side):
    if not os.path.exists(blend_path):
        print(f"Pose file {blend_path} not found")
        return
    armature = bpy.data.objects.get("Armature")
    if not armature:
        print("Avatar armature not found")
        return
    hand_bones = RIGHT_HAND_BONES if hand_side == 'right' else LEFT_HAND_BONES
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    try:
        with bpy.data.libraries.load(blend_path) as (data_from, data_to):
            data_to.objects = data_from.objects

        for obj in data_to.objects:
            if obj and obj.type == 'ARMATURE':
                for bone_name in hand_bones:
                    if bone_name in obj.pose.bones:
                        bone_pose = obj.pose.bones[bone_name]
                        armature.pose.bones[bone_name].rotation_euler = bone_pose.rotation_euler
    except Exception as e:
        print(f"Failed to apply pose from {blend_path}: {e}")
        return
    bpy.ops.object.mode_set(mode='POSE')

# ----------------------
# $2 SCALE FUNCTIONS

def scale_values(bone_number, bone_side, rot_list):
    try:
        # Ensure the input rotation list contains floats
        rot_list = [float(x) for x in rot_list]
        
        # Check for index bounds before accessing the list
        if bone_side == "left" and bone_number < len(SCALE_LEFT):
            new_x = rot_list[0] / SCALE_LEFT[bone_number][0]
            new_y = rot_list[1] / SCALE_LEFT[bone_number][1]
            new_z = rot_list[2] / SCALE_LEFT[bone_number][2]
        elif bone_side == "right" and bone_number < len(SCALE_RIGHT):
            new_x = rot_list[0] / SCALE_RIGHT[bone_number][0]
            new_y = rot_list[1] / SCALE_RIGHT[bone_number][1]
            new_z = rot_list[2] / SCALE_RIGHT[bone_number][2]
        else:
            print("Scaling Error: Invalid bone number or bone side")
            return None
        return [new_x, new_y, new_z]
    except Exception as e:
        print("Scaling Error: ", e)
        return None

def unscale_values(bone_number, bone_side, rot_list):
    # print("Unscaling: ", bone_number, bone_side)
    # print("Input: ", rot_list)
    try:
        # Ensure the input rotation list contains floats
        rot_list = [float(x) for x in rot_list]
        
        # Check for index bounds before accessing the list
        if bone_side == "left" and bone_number < len(SCALE_LEFT):
            new_x = rot_list[0] * SCALE_LEFT[bone_number][0]
            new_y = rot_list[1] * SCALE_LEFT[bone_number][1]
            new_z = rot_list[2] * SCALE_LEFT[bone_number][2]
        elif bone_side == "right" and bone_number < len(SCALE_RIGHT):
            new_x = rot_list[0] * SCALE_RIGHT[bone_number][0]
            new_y = rot_list[1] * SCALE_RIGHT[bone_number][1]
            new_z = rot_list[2] * SCALE_RIGHT[bone_number][2]
        else:
            print("Scaling Error: Invalid bone number or bone side")
            return None
        return [new_x, new_y, new_z]
    except Exception as e:
        print("Scaling Error: ", e)
        return None

# ---------------------
# $3 LOAD CONSTANTS

# Global variables for constants
RIGHT_BONE_1, RIGHT_BONE_2, RIGHT_BONE_3 = "", "", ""
RIGHT_BONES = [RIGHT_BONE_1, RIGHT_BONE_2, RIGHT_BONE_3]
LEFT_BONE_1, LEFT_BONE_2, LEFT_BONE_3 = "", "", ""
LEFT_BONES = [LEFT_BONE_1, LEFT_BONE_2, LEFT_BONE_3]
ARMATURE_NAME = "Armature"
SCALE_RIGHT = []
SCALE_LEFT = []
RIGHT_HAND_BONES = []
LEFT_HAND_BONES = []
ANIMATIONS = []

def load_constants_from_json(filepath):
    try:
        with open(bpy.path.abspath(filepath), 'r') as f:
            data = json.load(f)
        
        global RIGHT_BONE_1, RIGHT_BONE_2, RIGHT_BONE_3, RIGHT_BONES
        global LEFT_BONE_1, LEFT_BONE_2, LEFT_BONE_3, LEFT_BONES
        global ARMATURE_NAME
        global SCALE_RIGHT, SCALE_LEFT
        global RIGHT_HAND_BONES, LEFT_HAND_BONES
        
        RIGHT_BONE_1 = data.get("RIGHT_BONE_1", "Not found")
        RIGHT_BONE_2 = data.get("RIGHT_BONE_2", "Not found")
        RIGHT_BONE_3 = data.get("RIGHT_BONE_3", "Not found")
        RIGHT_BONES = [RIGHT_BONE_1, RIGHT_BONE_2, RIGHT_BONE_3]

        LEFT_BONE_1 = data.get("LEFT_BONE_1", "Not found")
        LEFT_BONE_2 = data.get("LEFT_BONE_2", "Not found")
        LEFT_BONE_3 = data.get("LEFT_BONE_3", "Not found")
        LEFT_BONES = [LEFT_BONE_1, LEFT_BONE_2, LEFT_BONE_3]

        ARMATURE_NAME = data.get("ARMATURE_NAME", "Armature")

        SCALE_RIGHT = data.get("SCALE_RIGHT", ["Right scale not found"])
        SCALE_LEFT = data.get("SCALE_LEFT", ["Left scale not found"])

        RIGHT_HAND_BONES = data.get("RIGHT_HAND_BONES", ["Right Hand bones not found"])
        LEFT_HAND_BONES = data.get("LEFT_HAND_BONES", ["Left Hand bones not found"])


        print("\n-----------------------------------")
        print("CONSTANTS:\n")
        print("ARMATURE NAME:       ", ARMATURE_NAME)
        print("RIGHT BONES:         ", RIGHT_BONES)
        print("LEFT BONES:          ", LEFT_BONES)
        print("RIGHT HAND BONES:    ", len(RIGHT_HAND_BONES))
        print("LEFT HAND BONES:     ", len(LEFT_HAND_BONES))
        print("SCALE RIGHT:         ", SCALE_RIGHT)
        print("SCALE LEFT:          ", SCALE_LEFT)
        print("-----------------------------------\n")
    
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from {filepath}.")
    except Exception as e:
        print(f"Failed to load constants from {filepath}: {e}")

def load_database_from_json(filepath):
    global ANIMATIONS
    try:
        with open(bpy.path.abspath(filepath), 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            print("\n-----------------------------------")
            print("ANIMATIONS:\n")
            count = 0
            for entry in data:
                if isinstance(entry, dict):
                    for animation_name, animation_content in entry.items():
                        ANIMATIONS.append(animation_content)
                        print(animation_name)
                        count += 1
                else:
                    print("Error: Each entry in the database should be a dictionary.")
            print("-----------------------------------\n")
            print(f"{count} animations loaded successfully.")
        else:
            print("Error: JSON root is not a list. Please check the structure of the JSON file.")
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from {filepath}.")
    except Exception as e:
        print(f"Failed to load database from {filepath}: {e}")

class GLOBAL_Load_JSON(Operator):
    bl_idname = "ivi_lsb.load_constants"
    bl_label = "Load JSON files"
    bl_description = "Load data from JSON files"
    
    def execute(self, context):
        json_filepath = context.scene.ivi_lsb_props.json_filepath
        db_filepath = context.scene.ivi_lsb_props.file_path
        try:
            c = 0
            if json_filepath:
                load_constants_from_json(json_filepath)
                c += 1
            if db_filepath:
                load_database_from_json(db_filepath)
                c += 1
            self.report({'INFO'}, f"{c} JSON files loaded successfully.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load constants or database: {str(e)}")
        return {'FINISHED'}

class GLOBAL_FileProperties(PropertyGroup):
    json_filepath: StringProperty( 
        name="Constants (JSON)",
        description="File path to the JSON file",
        maxlen=1024,
        subtype='FILE_PATH'
    ) # type: ignore
    file_path: StringProperty(
        name="Database (JSON)",
        description="Path to the JSON database",
        default="",
        subtype='FILE_PATH'
    ) # type: ignore

# ---------------------
# $4 USER INTERFACE FOR RIGHT ARM

class RIGHT_Panel(Panel):
    bl_label = "Pose Tools (RIGHT)"
    bl_idname = "VIEW3D_PT_ivi_lsb_right_arm_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "IVI LSB"

    def draw(self, context):
        layout = self.layout
        props = context.scene.ivi_lsb_props_right
        
        # Section 1: Rotations and sync with model in workspace
        layout.prop(props, "section_1", text="--- WORKSPACE SYNC ---", emboss=False)
        if props.section_1:
            armature = bpy.data.objects.get(ARMATURE_NAME)
            if armature and armature.type == 'ARMATURE':
                for i, bone_name in enumerate(RIGHT_BONES):
                    bone = armature.pose.bones.get(bone_name)
                    if bone:
                        row = layout.row()
                        row.label(text=f"R{i+1}:")
                        row.prop(bone, "rotation_euler", text="")

            layout.operator("ivi_lsb.reset_rotation_right", text="Reset rotations")
                
        # Section 2: Input and output vectors
        layout.prop(props, "section_2", text="--- INPUT VECTORS ---", emboss=False)
        if props.section_2:
            layout.operator("ivi_lsb.sync_rotation_right", text="Sync rotations")
            for i, prop_name in enumerate(['rot_display_bone_1', 'rot_display_bone_2', 'rot_display_bone_3']):
                layout.prop(props, prop_name, text=f"R{i+1} input")

            layout.operator("ivi_lsb.apply_rotation_input_right", text="Apply Rotations")

# ---------------------
# $5 USER INTERFACE FOR LEFT ARM

class LEFT_Panel(Panel):
    bl_label = "Pose Tools (LEFT)"
    bl_idname = "VIEW3D_PT_ivi_lsb_left_arm_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "IVI LSB"

    def draw(self, context):
        layout = self.layout
        props = context.scene.ivi_lsb_props_left
        
        # Section 1: Rotations and sync with model in workspace
        layout.prop(props, "section_1", text="--- WORKSPACE SYNC ---", emboss=False)
        if props.section_1:
            armature = bpy.data.objects.get(ARMATURE_NAME)
            if armature and armature.type == 'ARMATURE':
                for i, bone_name in enumerate(LEFT_BONES):
                    bone = armature.pose.bones.get(bone_name)
                    if bone:
                        row = layout.row()
                        row.label(text=f"L{i+1}:")
                        row.prop(bone, "rotation_euler", text="")

            layout.operator("ivi_lsb.reset_rotation_left", text="Reset rotations")
            
        # Section 2: Input and output vectors
        layout.prop(props, "section_2", text="--- INPUT VECTORS ---", emboss=False)
        if props.section_2:
            layout.operator("ivi_lsb.sync_rotation_left", text="Sync rotations")
            for i, prop_name in enumerate(['rot_display_bone_1', 'rot_display_bone_2', 'rot_display_bone_3']):
                layout.prop(props, prop_name, text=f"L{i+1} input")

            layout.operator("ivi_lsb.apply_rotation_input_left", text="Apply Rotations")

# ---------------------
# $6 COMPONENTS (LEFT and RIGHT)

# Property group to store rotation values and user input for right arm
class RIGHT_Properties(PropertyGroup):
    rot_display_bone_1: StringProperty(name="Rotation Display Bone 1", default="[0.00, 0.00, 0.00]") # type: ignore
    rot_display_bone_2: StringProperty(name="Rotation Display Bone 2", default="[0.00, 0.00, 0.00]") # type: ignore
    rot_display_bone_3: StringProperty(name="Rotation Display Bone 3", default="[0.00, 0.00, 0.00]") # type: ignore
    section_0: BoolProperty(name="Display Bone Names", default=True) # type: ignore
    section_1: BoolProperty(name="Rotations and Sync", default=True) # type: ignore
    section_2: BoolProperty(name="Input and Output Vectors", default=True) # type: ignore

# Property group to store rotation values and user input for left arm
class LEFT_Properties(PropertyGroup):
    rot_display_bone_1: StringProperty(name="Rotation Display Bone 1", default="[0.00, 0.00, 0.00]") # type: ignore
    rot_display_bone_2: StringProperty(name="Rotation Display Bone 2", default="[0.00, 0.00, 0.00]") # type: ignore
    rot_display_bone_3: StringProperty(name="Rotation Display Bone 3", default="[0.00, 0.00, 0.00]") # type: ignore
    section_0: BoolProperty(name="Display Bone Names", default=True) # type: ignore
    section_1: BoolProperty(name="Rotations and Sync", default=True) # type: ignore
    section_2: BoolProperty(name="Input and Output Vectors", default=True) # type: ignore

# Operator to reset the rotation of the bones for right arm
class RIGHT_Reset_Rotation(Operator):
    bl_label = "Reset Rotation"
    bl_idname = "ivi_lsb.reset_rotation_right"
    bl_description = "Reset bone rotations (R1, R2, R3) to [0.00, 0.00, 0.00]"

    def execute(self, context):
        props = context.scene.ivi_lsb_props_right

        armature = set_pose_mode(ARMATURE_NAME)
        if armature:
            for bone_name, prop_name in zip(RIGHT_BONES, ['rot_display_bone_1', 'rot_display_bone_2', 'rot_display_bone_3']):
                pose_bone = select_bone(armature, bone_name)
                if pose_bone:
                    pose_bone.rotation_mode = 'XYZ'
                    pose_bone.rotation_euler = (0.00, 0.00, 0.00)
                    setattr(props, prop_name, "[0.00, 0.00, 0.00]")
        
        print("Rotation reset to [0.00, 0.00, 0.00] for right arm bones")
        return {'FINISHED'}

# Operator to reset the rotation of the bones for left arm
class LEFT_Reset_Rotation(Operator):
    bl_label = "Reset Rotation"
    bl_idname = "ivi_lsb.reset_rotation_left"
    bl_description = "Reset bone rotations (L1, L2, L3) to [0.00, 0.00, 0.00]"

    def execute(self, context):
        props = context.scene.ivi_lsb_props_left

        armature = set_pose_mode(ARMATURE_NAME)
        if armature:
            for bone_name, prop_name in zip(LEFT_BONES, ['rot_display_bone_1', 'rot_display_bone_2', 'rot_display_bone_3']):
                pose_bone = select_bone(armature, bone_name)
                if pose_bone:
                    pose_bone.rotation_mode = 'XYZ'
                    pose_bone.rotation_euler = (0.00, 0.00, 0.00)
                    setattr(props, prop_name, "[0.00, 0.00, 0.00]")
        
        print("Rotation reset to [0.00, 0.00, 0.00] for left arm bones")
        return {'FINISHED'}

# Operator to sync the custom properties with the bones' rotation for right arm
class RIGHT_Sync_Rotation(Operator):
    bl_label = "Sync Rotation"
    bl_idname = "ivi_lsb.sync_rotation_right"
    bl_description = "Sync rotation properties with the right arm bones' rotation"

    def execute(self, context):
        props = context.scene.ivi_lsb_props_right

        armature = set_pose_mode(ARMATURE_NAME)
        if armature:
            print("\n-----------------------------------")
            print("Syncing rotation: RIGHT")
            for i, (bone_name, prop_name) in enumerate(zip(RIGHT_BONES, ['rot_display_bone_1', 'rot_display_bone_2', 'rot_display_bone_3'])):
                pose_bone = select_bone(armature, bone_name)
                if pose_bone:
                    try:
                        print("\nBONE: ", bone_name)
                        rotation = [pose_bone.rotation_euler.x, pose_bone.rotation_euler.y, pose_bone.rotation_euler.z]
                        print(f"BEFORE SCALE:      ", [format_float(rotation[k]) for k in range(3)])
                        rotation = radians_to_degrees(rotation)
                        print(f"AFTER TO DEGREES:  ", [format_float(rotation[k]) for k in range(3)])
                        scaled_rotation = scale_values(i, 'right', rotation)
                        if scaled_rotation:
                            print(f"AFTER SCALE:       ", [format_float(scaled_rotation[k]) for k in range(3)])
                            rotation_str = f"[{format_float(scaled_rotation[0])}, {format_float(scaled_rotation[1])}, {format_float(scaled_rotation[2])}]"
                            setattr(props, prop_name, rotation_str)
                        else:
                            raise ValueError("Scaling error")
                    except Exception as e:
                        print(f"Error in syncing rotation for {bone_name}: {str(e)}")
            print("-----------------------------------\n")
        
        return {'FINISHED'}

# Operator to sync the custom properties with the bones' rotation for left arm
class LEFT_Sync_Rotation(Operator):
    bl_label = "Sync Rotation"
    bl_idname = "ivi_lsb.sync_rotation_left"
    bl_description = "Sync rotation properties with the left arm bones' rotation"

    def execute(self, context):
        props = context.scene.ivi_lsb_props_left

        armature = set_pose_mode(ARMATURE_NAME)
        if armature:
            print("\n-----------------------------------")
            print("Syncing rotation: LEFT")
            for i, (bone_name, prop_name) in enumerate(zip(LEFT_BONES, ['rot_display_bone_1', 'rot_display_bone_2', 'rot_display_bone_3'])):
                pose_bone = select_bone(armature, bone_name)
                if pose_bone:
                    try:
                        print("\nBONE: ", bone_name)
                        rotation = [pose_bone.rotation_euler.x, pose_bone.rotation_euler.y, pose_bone.rotation_euler.z]
                        print(f"BEFORE SCALE:      ", [format_float(rotation[k]) for k in range(3)])
                        rotation = radians_to_degrees(rotation)
                        print(f"AFTER TO DEGREES:  ", [format_float(rotation[k]) for k in range(3)])
                        scaled_rotation = scale_values(i, 'left', rotation)
                        if scaled_rotation:
                            print(f"AFTER SCALE:       ", [format_float(scaled_rotation[k]) for k in range(3)])
                            rotation_str = f"[{format_float(scaled_rotation[0])}, {format_float(scaled_rotation[1])}, {format_float(scaled_rotation[2])}]"
                            setattr(props, prop_name, rotation_str)
                        else:
                            raise ValueError("Scaling error")
                    except Exception as e:
                        print(f"Error in syncing rotation for {bone_name}: {str(e)}")
            print("-----------------------------------\n")
        
        return {'FINISHED'}

# Operator to apply the rotation input provided by the user for right arm
class RIGHT_Apply_Input(Operator):
    bl_label = "Apply Rotation Input"
    bl_idname = "ivi_lsb.apply_rotation_input_right"
    bl_description = "Apply rotation input to the right arm bones"

    def execute(self, context):
        props = context.scene.ivi_lsb_props_right

        armature = set_pose_mode(ARMATURE_NAME)
        if armature:
            print("\n-----------------------------------")
            print("Applying rotation: RIGHT")
            for i, (bone_name, prop_name) in enumerate(zip(RIGHT_BONES, ['rot_display_bone_1', 'rot_display_bone_2', 'rot_display_bone_3'])):
                pose_bone = select_bone(armature, bone_name)
                prop = getattr(props, prop_name)
                if pose_bone:
                    try:
                        print("\nBONE: ", bone_name)
                        rotation_values = parse_rotation_input(prop)
                        if rotation_values is None:
                            raise ValueError("Invalid input format")
                        print("BEFORE UN-SCALE:   ", [format_float(rotation_values[k]) for k in range(3)])
                        unscaled_rotation = unscale_values(i, 'right', rotation_values)
                        if unscaled_rotation is None:
                            raise ValueError("Scaling error")
                        print("AFTER UN-SCALE:    ", [format_float(unscaled_rotation[k]) for k in range(3)])
                        unscaled_rotation = degrees_to_radians(unscaled_rotation)
                        print("AFTER TO RADIANS:  ", [format_float(unscaled_rotation[k]) for k in range(3)])
                        pose_bone.rotation_mode = 'XYZ'
                        pose_bone.rotation_euler = (
                            float(unscaled_rotation[0]), 
                            float(unscaled_rotation[1]), 
                            float(unscaled_rotation[2])
                        )
                    except Exception as e:
                        self.report({'ERROR'}, f"Invalid input for {bone_name}. Please enter a valid rotation vector like [1.00, 0.00, 0.00]. Error: {str(e)}")
            print("-----------------------------------\n")
        return {'FINISHED'}

# Operator to apply the rotation input provided by the user for left arm
class LEFT_Apply_Input(Operator):
    bl_label = "Apply Rotation Input"
    bl_idname = "ivi_lsb.apply_rotation_input_left"
    bl_description = "Apply rotation input to the left arm bones"

    def execute(self, context):
        props = context.scene.ivi_lsb_props_left

        armature = set_pose_mode(ARMATURE_NAME)
        if armature:
            print("\n-----------------------------------")
            print("Applying rotation: LEFT")
            for i, (bone_name, prop_name) in enumerate(zip(LEFT_BONES, ['rot_display_bone_1', 'rot_display_bone_2', 'rot_display_bone_3'])):
                pose_bone = select_bone(armature, bone_name)
                prop = getattr(props, prop_name)
                if pose_bone:
                    try:
                        print("\nBONE: ", bone_name)
                        rotation_values = parse_rotation_input(prop)
                        if rotation_values is None:
                            raise ValueError("Invalid input format")
                        print("BEFORE UN-SCALE:   ", [format_float(rotation_values[k]) for k in range(3)])
                        unscaled_rotation = unscale_values(i, 'left', rotation_values)
                        if unscaled_rotation is None:
                            raise ValueError("Scaling error")
                        print("AFTER UN-SCALE:    ", [format_float(unscaled_rotation[k]) for k in range(3)])
                        unscaled_rotation = degrees_to_radians(unscaled_rotation)
                        print("AFTER TO RADIANS:  ", [format_float(unscaled_rotation[k]) for k in range(3)])
                        pose_bone.rotation_mode = 'XYZ'
                        pose_bone.rotation_euler = (
                            float(unscaled_rotation[0]), 
                            float(unscaled_rotation[1]), 
                            float(unscaled_rotation[2])
                        )
                    except Exception as e:
                        self.report({'ERROR'}, f"Invalid input for {bone_name}. Please enter a valid rotation vector like [1.00, 0.00, 0.00]. Error: {str(e)}")
            print("-----------------------------------\n")
        return {'FINISHED'}

# Operator to Reset All transformations (rotation, location, and scale) for the avatar
class GLOBAL_Reset_All(Operator):
    bl_label = "Reset All"
    bl_idname = "ivi_lsb.reset_all"
    bl_description = "Reset all transformations (rotation, location, and scale) for the avatar and reset all input zones and hand poses"

    def execute(self, context):
        armature = set_pose_mode(ARMATURE_NAME)
        if armature:
            for bone in armature.pose.bones:
                armature.data.bones.active = armature.data.bones[bone.name]
                bpy.ops.pose.rot_clear()
                bpy.ops.pose.loc_clear()
                bpy.ops.pose.scale_clear()

        # Reset input zones for right arm
        right_props = context.scene.ivi_lsb_props_right
        for prop_name in ['rot_display_bone_1', 'rot_display_bone_2', 'rot_display_bone_3']:
            setattr(right_props, prop_name, "[0.00, 0.00, 0.00]")

        # Reset input zones for left arm
        left_props = context.scene.ivi_lsb_props_left
        for prop_name in ['rot_display_bone_1', 'rot_display_bone_2', 'rot_display_bone_3']:
            setattr(left_props, prop_name, "[0.00, 0.00, 0.00]")

        # Reset hand pose selectors
        hand_pose_props = context.scene.hand_pose_selector_props
        hand_pose_props.selected_pose_right = '---'
        hand_pose_props.selected_pose_left = '---'
        hand_pose_props.right_hand_pose_id = '---'
        hand_pose_props.left_hand_pose_id = '---'

        # Reset All Input
        global_props = context.scene.ivi_lsb_global_props
        global_props.pose_input_string = ""

        self.report({'INFO'}, "Global pose and input zones reset.")
        return {'FINISHED'}


# ---------------------
# $7 HAND POSE FUNCTIONS

def update_enum_items_with_prefix(context, prefix):
    items = [(pose.name, pose.name, "") for pose in context.scene.hand_pose_selector_props.pose_names if pose.name.startswith(prefix) or pose.name == "---"]
    return items

def update_enum_items_right(self, context):
    return update_enum_items_with_prefix(context, "R")

def update_enum_items_left(self, context):
    return update_enum_items_with_prefix(context, "L")

class HAND_PoseName(PropertyGroup):
    name: StringProperty() # type: ignore

class HAND_Properties(PropertyGroup):
    directory: StringProperty(
        name="Directory",
        description="Directory where hand poses are stored",
        default="",
        subtype='DIR_PATH'
    ) # type: ignore
    pose_names: CollectionProperty(type=HAND_PoseName) # type: ignore
    selected_pose_right: EnumProperty(
        name="Selected Right Hand Pose",
        items=update_enum_items_right
    ) # type: ignore
    selected_pose_left: EnumProperty(
        name="Selected Left Hand Pose",
        items=update_enum_items_left
    ) # type: ignore
    right_hand_pose_id: StringProperty(
        name="Right Hand Pose ID",
        description="ID of the selected right hand pose",
        default=""
    ) # type: ignore
    left_hand_pose_id: StringProperty(
        name="Left Hand Pose ID",
        description="ID of the selected left hand pose",
        default=""
    ) # type: ignore

class HAND_Import_Operator(Operator):
    bl_idname = "hand_pose.import"
    bl_label = "Load Hand Poses"

    def execute(self, context):
        directory = bpy.path.abspath(context.scene.hand_pose_selector_props.directory)
        if not directory:
            self.report({'ERROR'}, "Directory not set")
            return {'CANCELLED'}

        context.scene.hand_pose_selector_props.pose_names.clear()
        try:
            for file_name in os.listdir(directory):
                if file_name.endswith(".blend"):
                    pose_name = file_name[:-6]
                    new_pose = context.scene.hand_pose_selector_props.pose_names.add()
                    new_pose.name = pose_name
            print("\n-----------------------------------")
            print("HAND POSES:\n")
            ordered_list = sorted(context.scene.hand_pose_selector_props.pose_names, key=lambda x: x.name)
            c=0
            for pose in ordered_list:
                print(pose.name)
                c += 1
            print("-----------------------------------\n")
            self.report({'INFO'}, f"{c} hand poses loaded successfully.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load hand poses: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

# ---------------------
# $8 HAND POSE CLASSES

class HAND_RIGHT_Apply_Pose(Operator):
    bl_idname = "right_hand_pose.apply"
    bl_label = "Apply Pose"

    def execute(self, context):
        pose_name = context.scene.hand_pose_selector_props.selected_pose_right
        blend_path = os.path.join(bpy.path.abspath(context.scene.hand_pose_selector_props.directory), pose_name + ".blend")
        
        if not os.path.exists(blend_path):
            self.report({'ERROR'}, f"Pose file {blend_path} not found")
            print(f"Pose file {blend_path} not found")
            return {'CANCELLED'}

        armature = bpy.data.objects.get("Armature")
        if not armature:
            self.report({'ERROR'}, "Avatar armature not found")
            print("Avatar armature not found")
            return {'CANCELLED'}

        hand_bones = RIGHT_HAND_BONES

        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')

        try:
            with bpy.data.libraries.load(blend_path) as (data_from, data_to):
                data_to.objects = data_from.objects

            for obj in data_to.objects:
                if obj and obj.type == 'ARMATURE':
                    for bone_name in hand_bones:
                        if bone_name in obj.pose.bones:
                            bone_pose = obj.pose.bones[bone_name]
                            armature.pose.bones[bone_name].location = bone_pose.location
                            armature.pose.bones[bone_name].rotation_quaternion = bone_pose.rotation_quaternion
                            armature.pose.bones[bone_name].rotation_euler = bone_pose.rotation_euler
                            armature.pose.bones[bone_name].scale = bone_pose.scale

        except Exception as e:
            self.report({'ERROR'}, f"Failed to apply pose {pose_name}: {e}")
            print(f"Failed to apply pose {pose_name}: {e}")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='POSE')
        context.scene.hand_pose_selector_props.right_hand_pose_id = pose_name
    
        self.report({'INFO'}, f"Applied right hand pose {pose_name}")
        print(f"Applied right hand pose {pose_name}")
        return {'FINISHED'}

class HAND_LEFT_Apply_Pose(Operator):
    bl_idname = "left_hand_pose.apply"
    bl_label = "Apply Pose"

    def execute(self, context):
        pose_name = context.scene.hand_pose_selector_props.selected_pose_left
        blend_path = os.path.join(bpy.path.abspath(context.scene.hand_pose_selector_props.directory), pose_name + ".blend")
        
        if not os.path.exists(blend_path):
            self.report({'ERROR'}, f"Pose file {blend_path} not found")
            print(f"Pose file {blend_path} not found")
            return {'CANCELLED'}

        armature = bpy.data.objects.get("Armature")
        if not armature:
            self.report({'ERROR'}, "Avatar armature not found")
            print("Avatar armature not found")
            return {'CANCELLED'}

        hand_bones = LEFT_HAND_BONES

        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')

        try:
            with bpy.data.libraries.load(blend_path) as (data_from, data_to):
                data_to.objects = data_from.objects

            for obj in data_to.objects:
                if obj and obj.type == 'ARMATURE':
                    for bone_name in hand_bones:
                        if bone_name in obj.pose.bones:
                            bone_pose = obj.pose.bones[bone_name]
                            armature.pose.bones[bone_name].location = bone_pose.location
                            armature.pose.bones[bone_name].rotation_quaternion = bone_pose.rotation_quaternion
                            armature.pose.bones[bone_name].rotation_euler = bone_pose.rotation_euler
                            armature.pose.bones[bone_name].scale = bone_pose.scale

        except Exception as e:
            self.report({'ERROR'}, f"Failed to apply pose {pose_name}: {e}")
            print(f"Failed to apply pose {pose_name}: {e}")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='POSE')
        context.scene.hand_pose_selector_props.left_hand_pose_id = pose_name
        
        self.report({'INFO'}, f"Applied left hand pose {pose_name}")
        print(f"Applied left hand pose {pose_name}")
        return {'FINISHED'}

class HAND_Panel(Panel):
    bl_label = "Pose Tools (HANDS)"
    bl_idname = "VIEW3D_PT_ivi_lsb_hand_pose_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "IVI LSB"

    def draw(self, context):
        layout = self.layout

        # Right Hand
        layout.label(text="RIGHT Hand")
        if context.scene.hand_pose_selector_props.pose_names:
            layout.prop(context.scene.hand_pose_selector_props, "selected_pose_right", text="")
            layout.operator("right_hand_pose.apply", text="Apply Pose")

        # Left Hand
        layout.label(text="LEFT Hand")
        if context.scene.hand_pose_selector_props.pose_names:
            layout.prop(context.scene.hand_pose_selector_props, "selected_pose_left", text="")
            layout.operator("left_hand_pose.apply", text="Apply Pose")

# ---------------------
# $9 GLOBAL PANEL

class GLOBAL_Panel(Panel):
    bl_label = "Pose Tools (GLOBAL)"
    bl_idname = "VIEW3D_PT_ivi_lsb_global_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "IVI LSB"

    def draw(self, context):
        layout = self.layout
        global_props = context.scene.ivi_lsb_global_props
        
        layout.prop(context.scene.ivi_lsb_props, "json_filepath", text="Constants (JSON)")
        layout.prop(context.scene.ivi_lsb_props, "file_path", text="Database (JSON)")
        layout.prop(context.scene.hand_pose_selector_props, "directory", text="Hand Poses (DIR)")
        layout.operator("ivi_lsb.load_constants", text="Load JSON files")
        layout.operator("hand_pose.import", text="Load Hand Poses")
        layout.prop(global_props, "pose_input_string", text="Global Input")
        layout.operator("ivi_lsb.apply_pose_from_input", text="Apply Global Pose")
        layout.operator("ivi_lsb.copy_to_clipboard_global", text="Copy Global Pose")
        layout.operator("ivi_lsb.reset_all", text="Reset All")
        
class GLOBAL_CopyToClipboard(Operator):
    bl_label = "Copy Global Pose"
    bl_idname = "ivi_lsb.copy_to_clipboard_global"
    bl_description = "Copy rotation inputs to clipboard for both arms"

    def execute(self, context):
        right_props = context.scene.ivi_lsb_props_right
        left_props = context.scene.ivi_lsb_props_left
        right_hand_pose_id = context.scene.hand_pose_selector_props.right_hand_pose_id
        left_hand_pose_id = context.scene.hand_pose_selector_props.left_hand_pose_id

        right_rotation_data = f"{{{right_hand_pose_id}, {right_props.rot_display_bone_1}, {right_props.rot_display_bone_2}, {right_props.rot_display_bone_3}}}"
        left_rotation_data = f"{{{left_hand_pose_id}, {left_props.rot_display_bone_1}, {left_props.rot_display_bone_2}, {left_props.rot_display_bone_3}}}"

        global_rotation_data = f"{right_rotation_data} - {left_rotation_data}"
        context.window_manager.clipboard = global_rotation_data

        print("\n-----------------------------------")
        print("COPIED POSE:")
        print(f"- H: {right_hand_pose_id}, {left_hand_pose_id}")
        print(f"- R: {right_rotation_data}")
        print(f"- L: {left_rotation_data}")
        print("-----------------------------------\n")

        self.report({'INFO'}, "Rotation data for both arms copied to clipboard.")
        return {'FINISHED'}

class GLOBAL_Properties(PropertyGroup):
    pose_input_string: StringProperty(name="Global Input", default="") # type: ignore

class GLOBAL_Apply_Pose(Operator):
    bl_label = "Apply Global Pose"
    bl_idname = "ivi_lsb.apply_pose_from_input"
    bl_description = "Apply pose to the avatar from input string"

    def execute(self, context):
        props = context.scene.ivi_lsb_global_props
        input_string = props.pose_input_string

        try:
            print("\n-----------------------------------")
            print("APPLYING GLOBAL POSE\n")
            
            # Use regular expressions to parse the input string
            pattern = re.compile(r'\{(.*?), (\[.*?\]), (\[.*?\]), (\[.*?\])\} - \{(.*?), (\[.*?\]), (\[.*?\]), (\[.*?\])\}')
            match = pattern.match(input_string.strip())
            if not match:
                raise ValueError("Input string format is incorrect")

            # Extract pose IDs and vectors
            right_pose_id, right_vector1, right_vector2, right_vector3, left_pose_id, left_vector1, left_vector2, left_vector3 = match.groups()
            right_vectors = [self.parse_vector(right_vector1), self.parse_vector(right_vector2), self.parse_vector(right_vector3)]
            left_vectors = [self.parse_vector(left_vector1), self.parse_vector(left_vector2), self.parse_vector(left_vector3)]

            # Apply hand poses
            right_pose_id = right_pose_id.strip()
            left_pose_id = left_pose_id.strip()
            context.scene.hand_pose_selector_props.right_hand_pose_id = right_pose_id
            context.scene.hand_pose_selector_props.left_hand_pose_id = left_pose_id

            armature = set_pose_mode(ARMATURE_NAME)
            if armature:
                # Apply arm rotations
                for i, (bone_name, vectors) in enumerate(zip(RIGHT_BONES, right_vectors)):
                    pose_bone = select_bone(armature, bone_name)
                    if pose_bone:
                        unscaled_rotation = unscale_values(i, 'right', vectors)
                        if unscaled_rotation:
                            radians_rotation = degrees_to_radians([float(val) for val in unscaled_rotation])
                            pose_bone.rotation_mode = 'XYZ'
                            pose_bone.rotation_euler = tuple(radians_rotation)

                for i, (bone_name, vectors) in enumerate(zip(LEFT_BONES, left_vectors)):
                    pose_bone = select_bone(armature, bone_name)
                    if pose_bone:
                        unscaled_rotation = unscale_values(i, 'left', vectors)
                        if unscaled_rotation:
                            radians_rotation = degrees_to_radians([float(val) for val in unscaled_rotation])
                            pose_bone.rotation_mode = 'XYZ'
                            pose_bone.rotation_euler = tuple(radians_rotation)

                # Apply the right hand pose
                right_blend_path = os.path.join(bpy.path.abspath(context.scene.hand_pose_selector_props.directory), f"{right_pose_id}.blend")
                if os.path.exists(right_blend_path):
                    print(f"Applying right hand pose from: {right_blend_path}")
                    self.apply_hand_pose_from_blend(right_blend_path, 'right')
                else:
                    print(f"Right hand pose file not found: {right_blend_path}")

                # Apply the left hand pose
                left_blend_path = os.path.join(bpy.path.abspath(context.scene.hand_pose_selector_props.directory), f"{left_pose_id}.blend")
                if os.path.exists(left_blend_path):
                    print(f"Applying left hand pose from: {left_blend_path}")
                    self.apply_hand_pose_from_blend(left_blend_path, 'left')
                else:
                    print(f"Left hand pose file not found: {left_blend_path}")

            print("\nGlobal pose applied successfully.")
            print("-----------------------------------\n")
            self.report({'INFO'}, "Pose applied successfully from input string.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to apply pose: {str(e)}")
            import traceback
            traceback.print_exc()
        return {'FINISHED'}

    def parse_vector(self, vector_str):
        try:
            return [float(x.strip()) for x in vector_str.strip('[]').split(',')]
        except ValueError:
            raise ValueError(f"Invalid vector format: {vector_str}")

    def apply_hand_pose_from_blend(self, blend_path, hand_side):
        try:
            with bpy.data.libraries.load(blend_path) as (data_from, data_to):
                data_to.objects = data_from.objects

            for obj in data_to.objects:
                if obj and obj.type == 'ARMATURE':
                    armature = bpy.data.objects.get(ARMATURE_NAME)
                    hand_bones = RIGHT_HAND_BONES if hand_side == 'right' else LEFT_HAND_BONES
                    for bone_name in hand_bones:
                        if bone_name in obj.pose.bones:
                            bone_pose = obj.pose.bones[bone_name]
                            target_bone = armature.pose.bones.get(bone_name)
                            if target_bone:
                                target_bone.location = bone_pose.location
                                target_bone.rotation_quaternion = bone_pose.rotation_quaternion
                                target_bone.rotation_euler = bone_pose.rotation_euler
                                target_bone.scale = bone_pose.scale
                                # print(f"Applied pose for {hand_side} hand bone {bone_name}")
                            else:
                                print(f"Bone {bone_name} not found in target armature")
        except Exception as e:
            print(f"Failed to apply hand pose from {blend_path}: {e}")


    def parse_vector(self, vector_str):
        try:
            return [float(x.strip()) for x in vector_str.strip('[]').split(',')]
        except ValueError:
            raise ValueError(f"Invalid vector format: {vector_str}")

    def parse_vector(self, vector_str):
        try:
            vector = [float(x.strip()) for x in vector_str.strip('[]').split(',')]
            print(f"Parsed vector: {vector}")
            return vector
        except ValueError as e:
            print(f"Error parsing vector {vector_str}: {str(e)}")
            raise ValueError(f"Invalid vector format: {vector_str}")

    def parse_pose_data(self, data):
        data = data.strip('{}').split(', ')
        pose_id = data[0].strip()
        vectors = [self.parse_vector(vec) for vec in data[1:]]
        return [pose_id] + vectors

# ---------------------
# $10 ANIMATION COMPONENTS

class ANIMATION_Properties(PropertyGroup):
    json_filepath: StringProperty(
        name="Constants (JSON)",
        description="File path to the JSON file",
        maxlen=1024,
        subtype='FILE_PATH'
    ) # type: ignore
    file_path: StringProperty(
        name="JSON Database",
        description="Path to the JSON database",
        default="",
        subtype='FILE_PATH'
    ) # type: ignore
    keyframe_spacing: StringProperty(
        name="Pose Duration",
        description="Spacing between keyframes",
        default="10"
    ) # type: ignore

class ANIMATION_Panel(Panel):
    bl_label = "Animation Tools"
    bl_idname = "VIEW3D_PT_ANIMATION_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "IVI LSB"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.ivi_lsb_props, "keyframe_spacing", text="Pose Duration")
        row = layout.row()
        row.operator("ivi_lsb.reset_all_animations", text="Reset All Transformations")
        row.operator("ivi_lsb.delete_all_keyframes", text="Clear All Keyframes")
        layout.operator("ivi_lsb.create_animation", text="Animate!")
    
# Operator to reset all transformations (rotation, location, and scale) for the entire armature
class ANIMATION_Reset_All(Operator):
    bl_label = "Reset All Transformations"
    bl_idname = "ivi_lsb.reset_all_animations"
    bl_description = "Reset all transformations (rot/loc/sca) for the entire armature"
    def execute(self, context):
        armature = set_pose_mode(ARMATURE_NAME)
        if armature:
            for bone in armature.pose.bones:
                armature.data.bones.active = armature.data.bones[bone.name]
                bpy.ops.pose.rot_clear()
                bpy.ops.pose.loc_clear()
                bpy.ops.pose.scale_clear()
        self.report({'INFO'}, "All transformations reset for the entire armature.")
        return {'FINISHED'}

# Operator to delete all keyframes for the entire armature and clear all actions
class ANIMATION_Reset_Keyframes(Operator):
    bl_label = "Delete All Keyframes"
    bl_idname = "ivi_lsb.delete_all_keyframes"
    bl_description = "Delete all keyframes for the entire armature and clear all actions"
    def execute(self, context):
        armature = set_pose_mode(ARMATURE_NAME)
        if armature:
            # Delete all keyframes
            for bone in armature.pose.bones:
                armature.data.bones.active = armature.data.bones[bone.name]
                bpy.ops.pose.select_all(action='SELECT')
                bpy.ops.anim.keyframe_clear_v3d()
            # Clear all actions
            if armature.animation_data:
                action = armature.animation_data.action
                if action:
                    armature.animation_data_clear()
                    bpy.data.actions.remove(action)
                # Permanently remove all unused actions
                for action in bpy.data.actions:
                    if not action.users:
                        action.use_fake_user = False
                        bpy.data.actions.remove(action)
        # Manually run Blender's internal garbage collector
        bpy.ops.outliner.orphans_purge()
        self.report({'INFO'}, "All keyframes and actions deleted for the entire armature.")
        return {'FINISHED'}

class ANIMATION_Create_Animation(Operator):
    bl_label = "Create Animation"
    bl_idname = "ivi_lsb.create_animation"
    bl_description = "Create animation from JSON database"

    def execute(self, context):
        armature = set_pose_mode(ARMATURE_NAME)
        if not armature:
            self.report({'ERROR'}, "Armature not found.")
            return {'CANCELLED'}
        
        keyframe_spacing_str = context.scene.ivi_lsb_props.keyframe_spacing
        try:
            keyframe_spacing = int(keyframe_spacing_str)
        except ValueError:
            self.report({'ERROR'}, "Invalid keyframe spacing value.")
            return {'CANCELLED'}

        global ANIMATIONS

        print("\n-----------------------------------")
        print("Starting animation creation process...")
        print(f"Total animations: {len(ANIMATIONS)}\n")
        
        for animation_content in ANIMATIONS:
            animation_name = animation_content.get("name")
            print(f"Creating animation: {animation_name}")
            action = bpy.data.actions.new(name=animation_name)
            armature.animation_data_create()
            armature.animation_data.action = action
            
            poses = animation_content.get("poses")
            if not poses:
                self.report({'ERROR'}, f"Poses data not found for {animation_name}.")
                continue

            # print(poses)

            # duplicate first and last pose
            pose_i = poses[0]
            pose_f = poses[-1]
            pose_i['speed'] = 2
            pose_f['speed'] = 2
            poses = [pose_i] + poses + [pose_f]
                        
            frame = 1
            for pose_index, pose in enumerate(poses):
                speed = pose.get('speed', 1)
                duration = keyframe_spacing / speed
                bpy.context.scene.frame_set(frame)
                
                # print(f"Applying pose {pose_index + 1}/{len(poses)} at frame {frame}")
                
                # Apply arm rotations
                for bone_name, rot in pose.items():
                    if bone_name in ['RH', 'LH', 'speed']:
                        continue
                    
                    bone_side = 'left' if 'L' in bone_name else 'right'
                    bone_index = int(bone_name[1]) - 1
                    rotation_values = parse_rotation_input(rot)
                    if not rotation_values:
                        print(f"Invalid rotation values for bone {bone_name}: {rot}")
                        continue
                    
                    unscaled_rotation = unscale_values(bone_index, bone_side, rotation_values)
                    if not unscaled_rotation:
                        print(f"Failed to unscale rotation for bone {bone_name}")
                        continue
                    
                    radians_rotation = degrees_to_radians(unscaled_rotation)
                    bone_full_name = LEFT_BONES[bone_index] if bone_side == 'left' else RIGHT_BONES[bone_index]
                    pose_bone = select_bone(armature, bone_full_name)
                    if pose_bone:
                        pose_bone.rotation_mode = 'XYZ'
                        pose_bone.rotation_euler = radians_rotation
                        pose_bone.keyframe_insert(data_path="rotation_euler", index=-1)
                        pose_bone.rotation_mode = 'QUATERNION'
                        pose_bone.rotation_quaternion = pose_bone.rotation_euler.to_quaternion()
                        pose_bone.keyframe_insert(data_path="rotation_quaternion", index=-1)
                        # print(f"Applied and keyframed rotation for bone {bone_full_name}")
                
                # Apply hand poses
                for hand_side in ['RH', 'LH']:
                    if hand_side in pose:
                        pose_file = pose[hand_side]
                        blend_path = os.path.join(bpy.path.abspath(context.scene.hand_pose_selector_props.directory), f"{pose_file}.blend")
                        # print(f"Applying hand pose from file: {blend_path}")

                        try:
                            with bpy.data.libraries.load(blend_path) as (data_from, data_to):
                                data_to.objects = data_from.objects

                            for obj in data_to.objects:
                                if obj and obj.type == 'ARMATURE':
                                    hand_bones = RIGHT_HAND_BONES if hand_side == 'RH' else LEFT_HAND_BONES
                                    for bone_name in hand_bones:
                                        if bone_name in obj.pose.bones:
                                            bone_pose = obj.pose.bones[bone_name]
                                            target_bone = armature.pose.bones.get(bone_name)
                                            if target_bone:
                                                target_bone.location = bone_pose.location
                                                target_bone.rotation_quaternion = bone_pose.rotation_quaternion
                                                target_bone.rotation_euler = bone_pose.rotation_euler
                                                target_bone.scale = bone_pose.scale
                                                target_bone.keyframe_insert(data_path="location", index=-1)
                                                target_bone.keyframe_insert(data_path="rotation_quaternion", index=-1)
                                                target_bone.keyframe_insert(data_path="scale", index=-1)
                                                # print(f"Applied and keyframed pose for hand bone {bone_name}")
                        except Exception as e:
                            self.report({'ERROR'}, f"Failed to apply hand pose {pose_file}: {e}")
                            print(f"Failed to apply hand pose {pose_file}: {e}")

                frame += int(duration)

            print(f"Animation created: {animation_name}")
            print(f"Length (frames): {frame}\n")

        print("-----------------------------------\n")
        self.report({'INFO'}, "Animations created successfully.")
        print("Animation creation process completed successfully.")
        return {'FINISHED'}

# ---------------------
# $X REGISTER COMPONENTS

classes = [
    RIGHT_Panel,
    RIGHT_Properties,
    RIGHT_Sync_Rotation,
    RIGHT_Reset_Rotation,
    RIGHT_Apply_Input,
    LEFT_Panel,
    LEFT_Properties,
    LEFT_Sync_Rotation,
    LEFT_Reset_Rotation,
    LEFT_Apply_Input,
    HAND_PoseName,
    HAND_Panel,
    HAND_Properties,
    HAND_Import_Operator,
    HAND_RIGHT_Apply_Pose,
    HAND_LEFT_Apply_Pose,
    GLOBAL_Panel,
    GLOBAL_Properties,
    GLOBAL_FileProperties,
    GLOBAL_Apply_Pose,
    GLOBAL_CopyToClipboard,
    GLOBAL_Reset_All,
    GLOBAL_Load_JSON,
    ANIMATION_Panel,
    ANIMATION_Properties,
    ANIMATION_Reset_All,            
    ANIMATION_Reset_Keyframes,
    ANIMATION_Create_Animation
]

def register():
    for cls in classes: 
        bpy.utils.register_class(cls)
    bpy.types.Scene.ivi_lsb_props_right         = PointerProperty(type=RIGHT_Properties)
    bpy.types.Scene.ivi_lsb_props_left          = PointerProperty(type=LEFT_Properties)
    bpy.types.Scene.hand_pose_selector_props    = PointerProperty(type=HAND_Properties)
    bpy.types.Scene.ivi_lsb_file_props          = PointerProperty(type=GLOBAL_FileProperties)
    bpy.types.Scene.ivi_lsb_global_props        = PointerProperty(type=GLOBAL_Properties)
    bpy.types.Scene.ivi_lsb_props               = PointerProperty(type=ANIMATION_Properties)

if __name__ == "__main__":
    register()
