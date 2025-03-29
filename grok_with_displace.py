# town_map_generator.py

# Global counters for unique IDs in the .vmf file
solid_id = 2  # Start from 2, as ID 1 is worldspawn
side_id = 1

def create_brush(min_x, min_y, min_z, max_x, max_y, max_z, texture="tools/toolsnodraw", displacement_face=None, displacement_distance=0):
    """
    Creates a rectangular brush in .vmf format with optional displacement on one face.
    
    Args:
        min_x, min_y, min_z: Minimum coordinates of the brush.
        max_x, max_y, max_z: Maximum coordinates of the brush.
        texture: Texture to apply (default: tools/toolsnodraw).
        displacement_face: Face to turn into a displacement ('top', etc.).
        displacement_distance: Distance to offset displacement vertices (e.g., for road).
    
    Returns:
        String representing the brush in .vmf format.
    """
    global solid_id, side_id
    # Define the six planes (counterclockwise from outside)
    planes = [
        f"({min_x} {min_y} {min_z}) ({min_x} {min_y} {max_z}) ({min_x} {max_y} {min_z})",  # min X
        f"({max_x} {max_y} {min_z}) ({max_x} {min_y} {min_z}) ({max_x} {min_y} {max_z})",  # max X
        f"({min_x} {min_y} {min_z}) ({max_x} {min_y} {min_z}) ({min_x} {min_y} {max_z})",  # min Y
        f"({max_x} {max_y} {max_z}) ({min_x} {max_y} {max_z}) ({min_x} {max_y} {min_z})",  # max Y
        f"({min_x} {min_y} {min_z}) ({min_x} {max_y} {min_z}) ({max_x} {min_y} {min_z})",  # min Z
        f"({max_x} {max_y} {max_z}) ({min_x} {max_y} {max_z}) ({min_x} {min_y} {max_z})"   # max Z
    ]
    # Texture alignment: U along primary axis, V along secondary
    uaxes = ["[0 1 0 0] 0.25", "[0 -1 0 0] 0.25", "[1 0 0 0] 0.25", "[-1 0 0 0] 0.25", "[1 0 0 0] 0.25", "[-1 0 0 0] 0.25"]
    vaxes = ["[0 0 -1 0] 0.25", "[0 0 -1 0] 0.25", "[0 0 -1 0] 0.25", "[0 0 -1 0] 0.25", "[0 -1 0 0] 0.25", "[0 -1 0 0] 0.25"]
    
    brush_str = f'solid\n{{\n\t"id" "{solid_id}"\n'
    for i in range(6):
        brush_str += f'\tside\n\t{{\n\t\t"id" "{side_id}"\n\t\t"plane" "{planes[i]}"\n\t\t"material" "{texture}"\n\t\t"uaxis" "{uaxes[i]}"\n\t\t"vaxis" "{vaxes[i]}"\n\t\t"rotation" "0"\n\t\t"lightmapscale" "16"\n\t\t"smoothing_groups" "0"\n'
        if displacement_face == 'top' and i == 5:
            # Add displacement info for top face (road)
            brush_str += f'\t\tdispinfo\n\t\t{{\n\t\t\t"power" "3"\n\t\t\t"startposition" "[{min_x} {min_y} {max_z}]"\n\t\t\t"flags" "0"\n\t\t\t"elevation" "0"\n\t\t\t"subdiv" "0"\n\t\t\tnormals\n\t\t\t{{\n'
            for row in range(9):
                brush_str += f'\t\t\t\t"row{row}" "0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1"\n'
            brush_str += '\t\t\t}\n\t\t\tdistances\n\t\t\t{\n'
            for row in range(9):
                brush_str += f'\t\t\t\t"row{row}" "{" ".join([str(displacement_distance)]*9)}"\n'
            brush_str += '\t\t\t}\n\t\t\talphas\n\t\t\t{\n'
            for row in range(9):
                brush_str += f'\t\t\t\t"row{row}" "0 0 0 0 0 0 0 0 0"\n'
            brush_str += '\t\t\t}\n\t\t\ttriangle_tags\n\t\t\t{\n'
            for row in range(8):
                brush_str += f'\t\t\t\t"row{row}" "9 9 9 9 9 9 9 9"\n'
            brush_str += '\t\t\t}\n\t\t\tallowed_verts\n\t\t\t{\n\t\t\t\t"10" "-1 -1 -1 -1 -1 -1 -1 -1 -1 -1"\n\t\t\t}\n\t\t}\n'
        brush_str += '\t}\n'
        side_id += 1
    brush_str += '}\n'
    solid_id += 1
    return brush_str

def create_building(x1, x2, y1, y2, h, front_y, door_height=96, door_width=48, window_height=64, window_width=48, wall_thickness=8):
    """
    Creates a hollow building with walls, floor, ceiling, and front wall openings.
    
    Args:
        x1, x2: X bounds of the building.
        y1, y2: Y bounds (y1 < y2).
        h: Height of the building.
        front_y: Y coordinate of the front wall (y1 or y2).
        door_height, door_width: Door dimensions.
        window_height, window_width: Window dimensions.
        wall_thickness: Thickness of walls.
    
    Returns:
        String of all brushes for the building.
    """
    # Determine wall direction based on front face
    if front_y == y1:  # North side
        wall_direction = wall_thickness
        back_y = y2
    elif front_y == y2:  # South side
        wall_direction = -wall_thickness
        back_y = y1
    else:
        raise ValueError("front_y must be y1 or y2")
    
    # Calculate door and window positions
    building_width = x2 - x1
    door_left = x1 + (building_width - door_width) / 2
    door_right = door_left + door_width
    window_spacing = 32
    window_left1 = door_left - window_width - window_spacing
    window_right1 = window_left1 + window_width
    window_left2 = door_right + window_spacing
    window_right2 = window_left2 + window_width
    window_bottom = 48
    window_top = window_bottom + window_height
    
    front_min_y = min(front_y, front_y + wall_direction)
    front_max_y = max(front_y, front_y + wall_direction)
    back_min_y = min(back_y, back_y - wall_thickness)
    back_max_y = max(back_y, back_y - wall_thickness)
    
    brushes = ""
    # Front wall with cutouts
    if x1 < window_left1:
        brushes += create_brush(x1, front_min_y, 32, window_left1, front_max_y, 32 + h)
    if window_right1 < door_left:
        brushes += create_brush(window_right1, front_min_y, 32, door_left, front_max_y, 32 + h)
    brushes += create_brush(window_left1, front_min_y, 32 + window_top, window_right1, front_max_y, 32 + h)
    brushes += create_brush(window_left1, front_min_y, 32, window_right1, front_max_y, 32 + window_bottom)
    brushes += create_brush(door_left, front_min_y, 32 + door_height, door_right, front_max_y, 32 + h)
    if door_right < window_left2:
        brushes += create_brush(door_right, front_min_y, 32, window_left2, front_max_y, 32 + h)
    brushes += create_brush(window_left2, front_min_y, 32 + window_top, window_right2, front_max_y, 32 + h)
    brushes += create_brush(window_left2, front_min_y, 32, window_right2, front_max_y, 32 + window_bottom)
    if window_right2 < x2:
        brushes += create_brush(window_right2, front_min_y, 32, x2, front_max_y, 32 + h)
    
    # Other walls
    brushes += create_brush(x1, y1, 32, x1 + wall_thickness, y2, 32 + h)  # Left
    brushes += create_brush(x2 - wall_thickness, y1, 32, x2, y2, 32 + h)  # Right
    brushes += create_brush(x1 + wall_thickness, back_min_y, 32, x2 - wall_thickness, back_max_y, 32 + h)  # Back
    
    # Floor and ceiling
    brushes += create_brush(x1 + wall_thickness, y1 + wall_thickness, 32, x2 - wall_thickness, y2 - wall_thickness, 48)
    brushes += create_brush(x1 + wall_thickness, y1 + wall_thickness, 32 + h - 16, x2 - wall_thickness, y2 - wall_thickness, 32 + h)
    
    return brushes

# .vmf header
vmf_content = '''versioninfo
{
	"editorversion" "400"
	"editorbuild" "8037"
	"mapversion" "1"
	"formatversion" "100"
	"prefab" "0"
}
visgroups
{
}
world
{
	"id" "1"
	"mapversion" "1"
	"classname" "worldspawn"
'''

# Main street (displacement lowered to Z=0)
vmf_content += create_brush(0, -64, 0, 2048, 64, 16, displacement_face='top', displacement_distance=-16)

# Sidewalks (curbs via height difference)
vmf_content += create_brush(0, -128, 16, 2048, -64, 32)  # South
vmf_content += create_brush(0, 64, 16, 2048, 128, 32)    # North

# Building definitions
buildings = [
    # South side (front at Y=-128)
    {"x1": 128, "x2": 384, "y1": -256, "y2": -128, "h": 128, "front_y": -128},  # 1 story
    {"x1": 448, "x2": 640, "y1": -320, "y2": -128, "h": 256, "front_y": -128},  # 2 stories
    {"x1": 704, "x2": 960, "y1": -384, "y2": -128, "h": 384, "front_y": -128},  # 3 stories
    # North side (front at Y=128)
    {"x1": 128, "x2": 384, "y1": 128, "y2": 256, "h": 128, "front_y": 128},     # 1 story
    {"x1": 448, "x2": 640, "y1": 128, "y2": 320, "h": 256, "front_y": 128},     # 2 stories
    {"x1": 704, "x2": 960, "y1": 128, "y2": 384, "h": 384, "front_y": 128},     # 3 stories
]

# Add buildings
for building in buildings:
    vmf_content += create_building(**building)

# Close worldspawn
vmf_content += '}\n'

# Write to file
with open("town_map.vmf", "w") as f:
    f.write(vmf_content)

print("town_map.vmf has been generated successfully.")
