"""
Warehouse VMF Generator
Creates a VMF file for a warehouse with:
- Doors on all four sides
- Interior support posts
- Roof trusses spanning the width

This script generates a complete VMF file that can be imported into Source Hammer editor.
"""

import math
import os

def generate_warehouse_vmf(filename="warehouse.vmf", width=1024, length=1024, height=512, 
                          wall_thickness=16, post_size=32, post_spacing=256, 
                          door_width=128, door_height=196):
    """
    Generate a warehouse VMF file with customizable dimensions
    
    Parameters:
    -----------
    filename: Output VMF filename
    width, length: Overall dimensions of the warehouse (x, y)
    height: Height of the warehouse
    wall_thickness: Thickness of exterior walls
    post_size: Width of support columns
    post_spacing: Distance between support columns
    door_width, door_height: Dimensions of the doors
    """
    
    # Initialize VMF file content
    vmf_content = """versioninfo
{
	"editorversion" "400"
	"editorbuild" "8864"
	"mapversion" "1"
	"formatversion" "100"
	"prefab" "0"
}
visgroups
{
}
viewsettings
{
	"bSnapToGrid" "1"
	"bShowGrid" "1"
	"bShowLogicalGrid" "0"
	"nGridSpacing" "16"
	"bShow3DGrid" "0"
}
world
{
	"id" "1"
	"mapversion" "1"
	"classname" "worldspawn"
	"skyname" "sky_day01_01"
	"maxpropscreenwidth" "-1"
	"detailvbsp" "detail.vbsp"
	"detailmaterial" "detail/detailsprites"
"""
    
    # Initialize counters
    solid_id = 1
    side_id = 1
    
    # Helper function to create a brush (solid)
    def create_brush(mins, maxs, material="BRICK/BRICKFLOOR001A"):
        nonlocal solid_id, side_id
        
        brush = f"""	solid
	{{
		"id" "{solid_id}"
"""
        solid_id += 1
        
        # Define the 6 sides of the brush (min x, max x, min y, max y, min z, max z)
        # Order: left, right, bottom, top, back, front
        
        # Left side (min x)
        brush += f"""		side
		{{
			"id" "{side_id}"
			"plane" "({mins[0]} {mins[1]} {mins[2]}) ({mins[0]} {maxs[1]} {mins[2]}) ({mins[0]} {maxs[1]} {maxs[2]})"
			"material" "{material}"
			"uaxis" "[0 1 0 0] 0.25"
			"vaxis" "[0 0 -1 0] 0.25"
			"rotation" "0"
			"lightmapscale" "16"
			"smoothing_groups" "0"
		}}
"""
        side_id += 1
        
        # Right side (max x)
        brush += f"""		side
		{{
			"id" "{side_id}"
			"plane" "({maxs[0]} {maxs[1]} {mins[2]}) ({maxs[0]} {mins[1]} {mins[2]}) ({maxs[0]} {mins[1]} {maxs[2]})"
			"material" "{material}"
			"uaxis" "[0 1 0 0] 0.25"
			"vaxis" "[0 0 -1 0] 0.25"
			"rotation" "0"
			"lightmapscale" "16"
			"smoothing_groups" "0"
		}}
"""
        side_id += 1
        
        # Bottom side (min z)
        brush += f"""		side
		{{
			"id" "{side_id}"
			"plane" "({maxs[0]} {mins[1]} {mins[2]}) ({maxs[0]} {maxs[1]} {mins[2]}) ({mins[0]} {maxs[1]} {mins[2]})"
			"material" "{material}"
			"uaxis" "[1 0 0 0] 0.25"
			"vaxis" "[0 -1 0 0] 0.25"
			"rotation" "0"
			"lightmapscale" "16"
			"smoothing_groups" "0"
		}}
"""
        side_id += 1
        
        # Top side (max z)
        brush += f"""		side
		{{
			"id" "{side_id}"
			"plane" "({mins[0]} {mins[1]} {maxs[2]}) ({mins[0]} {maxs[1]} {maxs[2]}) ({maxs[0]} {maxs[1]} {maxs[2]})"
			"material" "{material}"
			"uaxis" "[1 0 0 0] 0.25"
			"vaxis" "[0 -1 0 0] 0.25"
			"rotation" "0"
			"lightmapscale" "16"
			"smoothing_groups" "0"
		}}
"""
        side_id += 1
        
        # Back side (min y)
        brush += f"""		side
		{{
			"id" "{side_id}"
			"plane" "({maxs[0]} {mins[1]} {mins[2]}) ({mins[0]} {mins[1]} {mins[2]}) ({mins[0]} {mins[1]} {maxs[2]})"
			"material" "{material}"
			"uaxis" "[1 0 0 0] 0.25"
			"vaxis" "[0 0 -1 0] 0.25"
			"rotation" "0"
			"lightmapscale" "16"
			"smoothing_groups" "0"
		}}
"""
        side_id += 1
        
        # Front side (max y)
        brush += f"""		side
		{{
			"id" "{side_id}"
			"plane" "({mins[0]} {maxs[1]} {mins[2]}) ({maxs[0]} {maxs[1]} {mins[2]}) ({maxs[0]} {maxs[1]} {maxs[2]})"
			"material" "{material}"
			"uaxis" "[1 0 0 0] 0.25"
			"vaxis" "[0 0 -1 0] 0.25"
			"rotation" "0"
			"lightmapscale" "16"
			"smoothing_groups" "0"
		}}
"""
        side_id += 1
        
        brush += """	}
"""
        return brush
    
    # Create the main building shell (exterior walls)
    # Floor
    vmf_content += create_brush(
        [0, 0, 0],
        [width, length, wall_thickness],
        "TOOLS/TOOLSNODRAW"
    )
    
    # Single roof layer - defined only once
    roof_bottom = height - wall_thickness
    vmf_content += create_brush(
        [0, 0, roof_bottom],
        [width, length, height],
        "TOOLS/TOOLSNODRAW"
    )
    
    # North wall (excluding door area)
    vmf_content += create_brush(
        [0, length - wall_thickness, wall_thickness],
        [width/2 - door_width/2, length, height - wall_thickness],
        "TOOLS/TOOLSNODRAW"
    )
    
    vmf_content += create_brush(
        [width/2 + door_width/2, length - wall_thickness, wall_thickness],
        [width, length, height - wall_thickness],
        "TOOLS/TOOLSNODRAW"
    )
    
    # Above north door
    vmf_content += create_brush(
        [width/2 - door_width/2, length - wall_thickness, door_height],
        [width/2 + door_width/2, length, height - wall_thickness],
        "TOOLS/TOOLSNODRAW"
    )
    
    # South wall (excluding door area)
    vmf_content += create_brush(
        [0, 0, wall_thickness],
        [width/2 - door_width/2, wall_thickness, height - wall_thickness],
        "TOOLS/TOOLSNODRAW"
    )
    
    vmf_content += create_brush(
        [width/2 + door_width/2, 0, wall_thickness],
        [width, wall_thickness, height - wall_thickness],
        "TOOLS/TOOLSNODRAW"
    )
    
    # Above south door
    vmf_content += create_brush(
        [width/2 - door_width/2, 0, door_height],
        [width/2 + door_width/2, wall_thickness, height - wall_thickness],
        "TOOLS/TOOLSNODRAW"
    )
    
    # East wall (excluding door area)
    vmf_content += create_brush(
        [width - wall_thickness, wall_thickness, wall_thickness],
        [width, length/2 - door_width/2, height - wall_thickness],
        "TOOLS/TOOLSNODRAW"
    )
    
    vmf_content += create_brush(
        [width - wall_thickness, length/2 + door_width/2, wall_thickness],
        [width, length - wall_thickness, height - wall_thickness],
        "TOOLS/TOOLSNODRAW"
    )
    
    # Above east door
    vmf_content += create_brush(
        [width - wall_thickness, length/2 - door_width/2, door_height],
        [width, length/2 + door_width/2, height - wall_thickness],
        "TOOLS/TOOLSNODRAW"
    )
    
    # West wall (excluding door area)
    vmf_content += create_brush(
        [0, wall_thickness, wall_thickness],
        [wall_thickness, length/2 - door_width/2, height - wall_thickness],
        "TOOLS/TOOLSNODRAW"
    )
    
    vmf_content += create_brush(
        [0, length/2 + door_width/2, wall_thickness],
        [wall_thickness, length - wall_thickness, height - wall_thickness],
        "TOOLS/TOOLSNODRAW"
    )
    
    # Above west door
    vmf_content += create_brush(
        [0, length/2 - door_width/2, door_height],
        [wall_thickness, length/2 + door_width/2, height - wall_thickness],
        "TOOLS/TOOLSNODRAW"
    )
    
    # Create support posts - significantly fewer posts with larger spacing
    # Calculate a much larger post spacing
    post_spacing_x = width / 3  # Only 2 internal posts across width
    post_spacing_y = length / 4  # Only 3 internal posts across length
    
    # Calculate starting positions to center the posts
    start_x = wall_thickness + post_spacing_x / 2
    start_y = wall_thickness + post_spacing_y / 2
    
    # Create the reduced set of posts
    for i in range(2):  # Only 2 columns of posts
        for j in range(3):  # Only 3 rows of posts
            post_x = start_x + i * post_spacing_x
            post_y = start_y + j * post_spacing_y
            
            # Skip posts that would overlap with doors
            door_conflict = False
            
            # Check for north/south door conflicts
            if (post_x > width/2 - door_width/2 - post_size/2 and 
                post_x < width/2 + door_width/2 + post_size/2):
                if (post_y < wall_thickness + post_size/2 or 
                    post_y > length - wall_thickness - post_size/2):
                    door_conflict = True
            
            # Check for east/west door conflicts
            if (post_y > length/2 - door_width/2 - post_size/2 and 
                post_y < length/2 + door_width/2 + post_size/2):
                if (post_x < wall_thickness + post_size/2 or 
                    post_x > width - wall_thickness - post_size/2):
                    door_conflict = True
            
            if not door_conflict:
                vmf_content += create_brush(
                    [post_x - post_size/2, post_y - post_size/2, wall_thickness],
                    [post_x + post_size/2, post_y + post_size/2, roof_bottom - 1],  # Avoid overlapping with roof
                    "TOOLS/TOOLSNODRAW"
                )
    
    # Create roof trusses - ensure they don't overlap with the roof
    truss_height = 64
    truss_thickness = 16
    
    # Use fewer trusses with larger spacing
    num_trusses = 4  # Only 4 trusses total
    truss_spacing = length / (num_trusses + 1)
    
    for j in range(1, num_trusses + 1):
        truss_y = j * truss_spacing
        
        # Skip trusses that would conflict with doors
        if (truss_y > length/2 - door_width/2 - truss_thickness/2 and 
            truss_y < length/2 + door_width/2 + truss_thickness/2):
            continue
        
        # Main truss beam - note the roof_bottom - 2 to prevent overlap
        vmf_content += create_brush(
            [wall_thickness, truss_y - truss_thickness/2, roof_bottom - truss_height],
            [width - wall_thickness, truss_y + truss_thickness/2, roof_bottom - 2],  # -2 to ensure no overlap with roof
            "TOOLS/TOOLSNODRAW"
        )
        
        # Add cross braces between trusses - significantly reduced
        # Only add cross braces for adjacent trusses and at fewer positions
        if j < num_trusses:
            next_truss_y = (j + 1) * truss_spacing
            
            # Skip cross braces if the next truss would conflict with doors
            if (next_truss_y > length/2 - door_width/2 - truss_thickness/2 and 
                next_truss_y < length/2 + door_width/2 + truss_thickness/2):
                continue
            
            # Add only two cross braces per truss section
            brace_positions = [width/3, 2*width/3]
            
            for brace_x in brace_positions:
                brace_width = 8
                
                # Simplified diagonal brace (approximated as a rectangular brush)
                # Make sure it doesn't extend into the roof
                vmf_content += create_brush(
                    [brace_x - brace_width/2, truss_y, roof_bottom - truss_height + 10],
                    [brace_x + brace_width/2, next_truss_y, roof_bottom - truss_height + 20],
                    "TOOLS/TOOLSNODRAW"
                )
    
    # Close the world entity and add entity definitions if needed
    vmf_content += """}
entities
{
	entity
	{
		"id" "2"
		"classname" "light_environment"
		"_ambient" "255 255 255 20"
		"_ambientHDR" "-1 -1 -1 1"
		"_AmbientScaleHDR" "1"
		"_light" "255 255 255 200"
		"_lightHDR" "-1 -1 -1 1"
		"_lightscaleHDR" "1"
		"angles" "0 0 0"
		"pitch" "-90"
		"SunSpreadAngle" "0"
		"origin" "0 0 256"
	}
}
cameras
{
	"activecamera" "-1"
}
cordon
{
	"mins" "(-1024 -1024 -1024)"
	"maxs" "(1024 1024 1024)"
	"active" "0"
}
"""
    
    # Write the VMF file
    with open(filename, 'w') as f:
        f.write(vmf_content)
    
    return f"Warehouse VMF file created successfully as {filename}!"

# Example usage
if __name__ == "__main__":
    generate_warehouse_vmf(
        filename="warehouse.vmf", 
        width=2048,         # Doubled the width
        length=3072,        # Tripled the length
        height=768,         # Increased the height by 50%
        wall_thickness=32,  # Thicker walls for larger building
        post_size=48,       # Larger support posts
        post_spacing=384,   # Increased spacing between posts
        door_width=192,     # Wider doors
        door_height=256     # Taller doors
    )