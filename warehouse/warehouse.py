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
        "BRICK/BRICKFLOOR001A"
    )
    
    # Roof
    vmf_content += create_brush(
        [0, 0, height - wall_thickness],
        [width, length, height],
        "CONCRETE/CONCRETEFLOOR001A"
    )
    
    # North wall (excluding door area)
    vmf_content += create_brush(
        [0, length - wall_thickness, wall_thickness],
        [width/2 - door_width/2, length, height - wall_thickness],
        "BRICK/BRICKWALL001A"
    )
    
    vmf_content += create_brush(
        [width/2 + door_width/2, length - wall_thickness, wall_thickness],
        [width, length, height - wall_thickness],
        "BRICK/BRICKWALL001A"
    )
    
    # Above north door
    vmf_content += create_brush(
        [width/2 - door_width/2, length - wall_thickness, door_height],
        [width/2 + door_width/2, length, height - wall_thickness],
        "BRICK/BRICKWALL001A"
    )
    
    # South wall (excluding door area)
    vmf_content += create_brush(
        [0, 0, wall_thickness],
        [width/2 - door_width/2, wall_thickness, height - wall_thickness],
        "BRICK/BRICKWALL001A"
    )
    
    vmf_content += create_brush(
        [width/2 + door_width/2, 0, wall_thickness],
        [width, wall_thickness, height - wall_thickness],
        "BRICK/BRICKWALL001A"
    )
    
    # Above south door
    vmf_content += create_brush(
        [width/2 - door_width/2, 0, door_height],
        [width/2 + door_width/2, wall_thickness, height - wall_thickness],
        "BRICK/BRICKWALL001A"
    )
    
    # East wall (excluding door area)
    vmf_content += create_brush(
        [width - wall_thickness, wall_thickness, wall_thickness],
        [width, length/2 - door_width/2, height - wall_thickness],
        "BRICK/BRICKWALL001A"
    )
    
    vmf_content += create_brush(
        [width - wall_thickness, length/2 + door_width/2, wall_thickness],
        [width, length - wall_thickness, height - wall_thickness],
        "BRICK/BRICKWALL001A"
    )
    
    # Above east door
    vmf_content += create_brush(
        [width - wall_thickness, length/2 - door_width/2, door_height],
        [width, length/2 + door_width/2, height - wall_thickness],
        "BRICK/BRICKWALL001A"
    )
    
    # West wall (excluding door area)
    vmf_content += create_brush(
        [0, wall_thickness, wall_thickness],
        [wall_thickness, length/2 - door_width/2, height - wall_thickness],
        "BRICK/BRICKWALL001A"
    )
    
    vmf_content += create_brush(
        [0, length/2 + door_width/2, wall_thickness],
        [wall_thickness, length - wall_thickness, height - wall_thickness],
        "BRICK/BRICKWALL001A"
    )
    
    # Above west door
    vmf_content += create_brush(
        [0, length/2 - door_width/2, door_height],
        [wall_thickness, length/2 + door_width/2, height - wall_thickness],
        "BRICK/BRICKWALL001A"
    )
    
    # Create support posts
    num_posts_x = max(2, math.floor((width - 2*wall_thickness) / post_spacing))
    num_posts_y = max(2, math.floor((length - 2*wall_thickness) / post_spacing))
    
    post_x_spacing = (width - 2*wall_thickness) / num_posts_x
    post_y_spacing = (length - 2*wall_thickness) / num_posts_y
    
    for i in range(1, num_posts_x):
        for j in range(1, num_posts_y):
            post_x = wall_thickness + i * post_x_spacing
            post_y = wall_thickness + j * post_y_spacing
            
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
                    [post_x + post_size/2, post_y + post_size/2, height - wall_thickness],
                    "CONCRETE/CONCRETEWALL001A"
                )
    
    # Create roof trusses
    truss_height = 64
    truss_thickness = 16
    
    for j in range(num_posts_y + 1):
        truss_y = wall_thickness + j * post_y_spacing
        
        # Skip trusses that would conflict with doors
        if (truss_y > length/2 - door_width/2 - truss_thickness/2 and 
            truss_y < length/2 + door_width/2 + truss_thickness/2):
            continue
        
        # Main truss beam
        vmf_content += create_brush(
            [wall_thickness, truss_y - truss_thickness/2, height - truss_height],
            [width - wall_thickness, truss_y + truss_thickness/2, height - wall_thickness],
            "METAL/METALWALL001A"
        )
        
        # Add cross braces between trusses
        if j < num_posts_y:
            next_truss_y = wall_thickness + (j+1) * post_y_spacing
            
            # Skip cross braces if the next truss would conflict with doors
            if (next_truss_y > length/2 - door_width/2 - truss_thickness/2 and 
                next_truss_y < length/2 + door_width/2 + truss_thickness/2):
                continue
            
            for i in range(num_posts_x):
                post_x = wall_thickness + i * post_x_spacing
                next_post_x = wall_thickness + (i+1) * post_x_spacing
                
                # Add a simplified diagonal brace
                brace_thickness = 8
                
                # Skip braces that would conflict with doors
                door_conflict = False
                
                if (post_x < width/2 + door_width/2 + post_size/2 and 
                    next_post_x > width/2 - door_width/2 - post_size/2 and
                    (truss_y < wall_thickness + post_size*2 or 
                     next_truss_y > length - wall_thickness - post_size*2)):
                    door_conflict = True
                    
                if (truss_y < length/2 + door_width/2 + post_size/2 and 
                    next_truss_y > length/2 - door_width/2 - post_size/2 and
                    (post_x < wall_thickness + post_size*2 or 
                     next_post_x > width - wall_thickness - post_size*2)):
                    door_conflict = True
                
                if not door_conflict:
                    # Simplified diagonal brace (approximated as a rectangular brush)
                    vmf_content += create_brush(
                        [post_x, truss_y, height - truss_height + brace_thickness],
                        [next_post_x, next_truss_y, height - truss_height + brace_thickness*2],
                        "METAL/METALWALL001A"
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
        width=1024, 
        length=1024, 
        height=512,
        wall_thickness=16,
        post_size=32,
        post_spacing=256,
        door_width=128,
        door_height=196
    )