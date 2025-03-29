# town_map_generator.py

# Global counters for unique IDs in the .vmf file
solid_id = 2  # Start from 2, as ID 1 is typically worldspawn
side_id = 1

def create_brush(min_x, min_y, min_z, max_x, max_y, max_z, texture="tools/toolsnodraw"):
    """
    Creates a rectangular brush in .vmf format with all faces textured with NODRAW.
    Args:
        min_x, min_y, min_z: Minimum coordinates of the brush.
        max_x, max_y, max_z: Maximum coordinates of the brush.
        texture: Texture to apply (default: tools/toolsnodraw).
    Returns:
        String representing the brush in .vmf format.
    """
    global solid_id, side_id
    # Define the six planes of the brush (three points each, counterclockwise from outside)
    planes = [
        f"({min_x} {min_y} {min_z}) ({min_x} {min_y} {max_z}) ({min_x} {max_y} {min_z})",  # min X
        f"({max_x} {max_y} {min_z}) ({max_x} {min_y} {min_z}) ({max_x} {min_y} {max_z})",  # max X
        f"({min_x} {min_y} {min_z}) ({max_x} {min_y} {min_z}) ({min_x} {min_y} {max_z})",  # min Y
        f"({max_x} {max_y} {max_z}) ({min_x} {max_y} {max_z}) ({min_x} {max_y} {min_z})",  # max Y
        f"({min_x} {min_y} {min_z}) ({min_x} {max_y} {min_z}) ({max_x} {min_y} {min_z})",  # min Z
        f"({max_x} {max_y} {max_z}) ({min_x} {max_y} {max_z}) ({min_x} {min_y} {max_z})"   # max Z
    ]
    # Texture alignment (U along primary axis, V along secondary, scale 0.25)
    uaxes = ["[0 1 0 0] 0.25", "[0 -1 0 0] 0.25", "[1 0 0 0] 0.25", "[-1 0 0 0] 0.25", "[1 0 0 0] 0.25", "[-1 0 0 0] 0.25"]
    vaxes = ["[0 0 -1 0] 0.25", "[0 0 -1 0] 0.25", "[0 0 -1 0] 0.25", "[0 0 -1 0] 0.25", "[0 -1 0 0] 0.25", "[0 -1 0 0] 0.25"]
    brush_str = f'solid\n{{\n\t"id" "{solid_id}"\n'
    for i in range(6):
        brush_str += f'\tside\n\t{{\n\t\t"id" "{side_id}"\n\t\t"plane" "{planes[i]}"\n\t\t"material" "{texture}"\n\t\t"uaxis" "{uaxes[i]}"\n\t\t"vaxis" "{vaxes[i]}"\n\t\t"rotation" "0"\n\t\t"lightmapscale" "16"\n\t\t"smoothing_groups" "0"\n\t}}\n'
        side_id += 1
    brush_str += '}\n'
    solid_id += 1
    return brush_str

def create_building(x1, x2, y1, y2, h, front_y, door_height=96, door_width=48, window_height=64, window_width=48, wall_thickness=8):
    """
    Creates a building with walls, floor, ceiling, and front wall with door and window openings.
    Args:
        x1, x2: X bounds of the building.
        y1, y2: Y bounds of the building (y1 < y2).
        h: Height of the building.
        front_y: Y coordinate of the front wall (either y1 or y2).
        door_height, door_width: Dimensions of the door.
        window_height, window_width: Dimensions of the windows.
        wall_thickness: Thickness of the walls.
    Returns:
        String of all brushes for the building in .vmf format.
    """
    # Determine front and back wall positions
    if front_y == y1:  # North side (front at smaller Y)
        wall_direction = wall_thickness
        back_y = y2
    elif front_y == y2:  # South side (front at larger Y)
        wall_direction = -wall_thickness
        back_y = y1
    else:
        raise ValueError("front_y must be y1 or y2")
    
    # Calculate door and window positions (centered on front wall)
    building_width = x2 - x1
    door_left = x1 + (building_width - door_width) / 2
    door_right = door_left + door_width
    window_spacing = 32  # Space between door and windows
    window_left1 = door_left - window_width - window_spacing
    window_right1 = window_left1 + window_width
    window_left2 = door_right + window_spacing
    window_right2 = window_left2 + window_width
    window_bottom = 48  # Window bottom height
    window_top = window_bottom + window_height
    
    front_min_y = min(front_y, front_y + wall_direction)
    front_max_y = max(front_y, front_y + wall_direction)
    back_min_y = min(back_y, back_y - wall_direction)
    back_max_y = max(back_y, back_y - wall_direction)
    
    # Front wall brushes (split for door and windows)
    brushes = ""
    # Left of first window
    if x1 < window_left1:
        brushes += create_brush(x1, front_min_y, 0, window_left1, front_max_y, h)
    # Between first window and door
    if window_right1 < door_left:
        brushes += create_brush(window_right1, front_min_y, 0, door_left, front_max_y, h)
    # Above first window
    brushes += create_brush(window_left1, front_min_y, window_top, window_right1, front_max_y, h)
    # Below first window
    brushes += create_brush(window_left1, front_min_y, 0, window_right1, front_max_y, window_bottom)
    # Above door
    brushes += create_brush(door_left, front_min_y, door_height, door_right, front_max_y, h)
    # Between door and second window
    if door_right < window_left2:
        brushes += create_brush(door_right, front_min_y, 0, window_left2, front_max_y, h)
    # Above second window
    brushes += create_brush(window_left2, front_min_y, window_top, window_right2, front_max_y, h)
    # Below second window
    brushes += create_brush(window_left2, front_min_y, 0, window_right2, front_max_y, window_bottom)
    # Right of second window
    if window_right2 < x2:
        brushes += create_brush(window_right2, front_min_y, 0, x2, front_max_y, h)
    
    # Side walls
    brushes += create_brush(x1, y1, 0, x1 + wall_thickness, y2, h)  # Left wall
    brushes += create_brush(x2 - wall_thickness, y1, 0, x2, y2, h)  # Right wall
    
    # Back wall
    brushes += create_brush(x1 + wall_thickness, back_min_y, 0, x2 - wall_thickness, back_max_y, h)
    
    # Floor and ceiling
    brushes += create_brush(x1 + wall_thickness, y1 + wall_thickness, 0, x2 - wall_thickness, y2 - wall_thickness, 16)
    brushes += create_brush(x1 + wall_thickness, y1 + wall_thickness, h - 16, x2 - wall_thickness, y2 - wall_thickness, h)
    
    return brushes

# Initialize .vmf file content
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

# Add main street
vmf_content += create_brush(0, -256, 0, 2048, 256, 16)

# Define buildings (x1, x2, y1, y2, height, front_y)
buildings = [
    # South side (front at Y=-256)
    {"x1": 128, "x2": 384, "y1": -384, "y2": -256, "h": 144, "front_y": -256},  # 1 story
    {"x1": 448, "x2": 640, "y1": -448, "y2": -256, "h": 288, "front_y": -256},  # 2 stories
    {"x1": 704, "x2": 960, "y1": -512, "y2": -256, "h": 432, "front_y": -256},  # 3 stories
    # North side (front at Y=256)
    {"x1": 128, "x2": 384, "y1": 256, "y2": 384, "h": 144, "front_y": 256},     # 1 story
    {"x1": 448, "x2": 640, "y1": 256, "y2": 448, "h": 288, "front_y": 256},     # 2 stories
    {"x1": 704, "x2": 960, "y1": 256, "y2": 512, "h": 288, "front_y": 256},     # 2 stories
]

# Add buildings to the map
for building in buildings:
    vmf_content += create_building(**building)

# Close worldspawn
vmf_content += '}\n'

# Write to file
with open("town_map.vmf", "w") as f:
    f.write(vmf_content)

print("town_map.vmf has been generated successfully.")
