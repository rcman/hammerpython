import random

class VMFGenerator:
    def __init__(self, filename="town_map.vmf"):
        self.filename = filename
        self.solids = []
        self.entities = []
        self.solid_id = 1
        self.side_id = 1
        self.entity_id = 1
        
    def create_brush(self, min_coords, max_coords, texture="DEV/DEV_MEASUREGENERIC01"):
        """Create a brush (solid) with the given coordinates and texture."""
        sides = []
        
        # Define the 6 sides of the brush
        # Bottom face
        sides.append(self.create_side(
            [(min_coords[0], min_coords[1], min_coords[2]), 
             (max_coords[0], min_coords[1], min_coords[2]), 
             (max_coords[0], max_coords[1], min_coords[2])],
            texture
        ))
        
        # Top face
        sides.append(self.create_side(
            [(min_coords[0], min_coords[1], max_coords[2]), 
             (max_coords[0], max_coords[1], max_coords[2]), 
             (max_coords[0], min_coords[1], max_coords[2])],
            texture
        ))
        
        # Front face
        sides.append(self.create_side(
            [(min_coords[0], max_coords[1], min_coords[2]), 
             (max_coords[0], max_coords[1], min_coords[2]), 
             (max_coords[0], max_coords[1], max_coords[2])],
            texture
        ))
        
        # Back face
        sides.append(self.create_side(
            [(min_coords[0], min_coords[1], min_coords[2]), 
             (max_coords[0], min_coords[1], max_coords[2]), 
             (max_coords[0], min_coords[1], min_coords[2])],
            texture
        ))
        
        # Left face
        sides.append(self.create_side(
            [(min_coords[0], min_coords[1], min_coords[2]), 
             (min_coords[0], max_coords[1], max_coords[2]), 
             (min_coords[0], max_coords[1], min_coords[2])],
            texture
        ))
        
        # Right face
        sides.append(self.create_side(
            [(max_coords[0], min_coords[1], min_coords[2]), 
             (max_coords[0], max_coords[1], min_coords[2]), 
             (max_coords[0], min_coords[1], max_coords[2])],
            texture
        ))
        
        solid = {
            "id": self.solid_id,
            "sides": sides
        }
        
        self.solid_id += 1
        self.solids.append(solid)
        return solid
    
    def create_side(self, points, texture):
        """Create a side of a brush with the given points and texture."""
        side = {
            "id": self.side_id,
            "plane": f"({points[0][0]} {points[0][1]} {points[0][2]}) ({points[1][0]} {points[1][1]} {points[1][2]}) ({points[2][0]} {points[2][1]} {points[2][2]})",
            "material": texture,
            "uaxis": "[1 0 0 0] 0.25",
            "vaxis": "[0 -1 0 0] 0.25",
            "rotation": "0",
            "lightmapscale": "16",
            "smoothing_groups": "0"
        }
        
        self.side_id += 1
        return side
    
    def create_entity(self, classname, origin, properties=None):
        """Create an entity with the given properties."""
        entity = {
            "id": self.entity_id,
            "classname": classname,
            "origin": f"{origin[0]} {origin[1]} {origin[2]}"
        }
        
        if properties:
            entity.update(properties)
            
        self.entity_id += 1
        self.entities.append(entity)
        return entity
    
    def create_prop_static(self, model, origin, angles=(0, 0, 0)):
        """Create a prop_static entity."""
        properties = {
            "model": model,
            "angles": f"{angles[0]} {angles[1]} {angles[2]}",
            "solid": "6",
            "skin": "0",
            "disableshadows": "0"
        }
        
        return self.create_entity("prop_static", origin, properties)
    
    def create_building(self, position, size, door_positions=None, window_positions=None, props=None):
        """Create a building with doors, windows, and props."""
        min_coords = position
        max_coords = [position[0] + size[0], position[1] + size[1], position[2] + size[2]]
        
        wall_thickness = 16  # Thickness of walls, floors, and ceilings (16 units)
        
        # Floor (16 units thick)
        self.create_brush(
            [min_coords[0], min_coords[1], min_coords[2]],
            [max_coords[0], max_coords[1], min_coords[2] + wall_thickness],
            "CONCRETE/CONCRETEFLOOR001A"  # Visible concrete texture
        )
        
        # Ceiling (16 units thick)
        self.create_brush(
            [min_coords[0], min_coords[1], max_coords[2] - wall_thickness],
            [max_coords[0], max_coords[1], max_coords[2]],
            "PLASTER/PLASTERWALL001A"  # Visible plaster texture
        )
        
        # Left wall (16 units thick)
        self.create_brush(
            [min_coords[0], min_coords[1], min_coords[2] + wall_thickness],  # Start above floor
            [min_coords[0] + wall_thickness, max_coords[1], max_coords[2] - wall_thickness],  # End below ceiling
            "BRICK/BRICKWALL001A"  # Visible brick texture
        )
        
        # Right wall (16 units thick)
        self.create_brush(
            [max_coords[0] - wall_thickness, min_coords[1], min_coords[2] + wall_thickness],  # Start above floor
            [max_coords[0], max_coords[1], max_coords[2] - wall_thickness],  # End below ceiling
            "BRICK/BRICKWALL001A"  # Visible brick texture
        )
        
        # Create front wall with door cutout if needed
        front_door = None
        if door_positions:
            front_door = next((dp for dp in door_positions if abs(dp[1] - min_coords[1]) < wall_thickness * 2), None)
        
        if front_door:
            # Left section of front wall
            self.create_brush(
                [min_coords[0] + wall_thickness, min_coords[1], min_coords[2] + wall_thickness],
                [front_door[0], min_coords[1] + wall_thickness, max_coords[2] - wall_thickness],
                "BRICK/BRICKWALL001A"
            )
            
            # Right section of front wall
            self.create_brush(
                [front_door[0] + 32, min_coords[1], min_coords[2] + wall_thickness],
                [max_coords[0] - wall_thickness, min_coords[1] + wall_thickness, max_coords[2] - wall_thickness],
                "BRICK/BRICKWALL001A"
            )
            
            # Top section of front wall above door
            self.create_brush(
                [front_door[0], min_coords[1], min_coords[2] + wall_thickness + 80],  # Door height = 80
                [front_door[0] + 32, min_coords[1] + wall_thickness, max_coords[2] - wall_thickness],
                "BRICK/BRICKWALL001A"
            )
        else:
            # Full front wall if no door
            self.create_brush(
                [min_coords[0] + wall_thickness, min_coords[1], min_coords[2] + wall_thickness],
                [max_coords[0] - wall_thickness, min_coords[1] + wall_thickness, max_coords[2] - wall_thickness],
                "BRICK/BRICKWALL001A"
            )
        
        # Create back wall with door cutout if needed
        back_door = None
        if door_positions:
            back_door = next((dp for dp in door_positions if abs(dp[1] - max_coords[1]) < wall_thickness * 2), None)
        
        if back_door:
            # Left section of back wall
            self.create_brush(
                [min_coords[0] + wall_thickness, max_coords[1] - wall_thickness, min_coords[2] + wall_thickness],
                [back_door[0], max_coords[1], max_coords[2] - wall_thickness],
                "BRICK/BRICKWALL001A"
            )
            
            # Right section of back wall
            self.create_brush(
                [back_door[0] + 32, max_coords[1] - wall_thickness, min_coords[2] + wall_thickness],
                [max_coords[0] - wall_thickness, max_coords[1], max_coords[2] - wall_thickness],
                "BRICK/BRICKWALL001A"
            )
            
            # Top section of back wall above door
            self.create_brush(
                [back_door[0], max_coords[1] - wall_thickness, min_coords[2] + wall_thickness + 80],  # Door height = 80
                [back_door[0] + 32, max_coords[1], max_coords[2] - wall_thickness],
                "BRICK/BRICKWALL001A"
            )
        else:
            # Full back wall if no door
            self.create_brush(
                [min_coords[0] + wall_thickness, max_coords[1] - wall_thickness, min_coords[2] + wall_thickness],
                [max_coords[0] - wall_thickness, max_coords[1], max_coords[2] - wall_thickness],
                "BRICK/BRICKWALL001A"
            )
            
        # Add windows if specified
        if window_positions:
            for window_pos in window_positions:
                # Create window frame with actual glass texture
                self.create_brush(
                    [window_pos[0], window_pos[1], window_pos[2]],
                    [window_pos[0] + 48, window_pos[1] + 4, window_pos[2] + 48],
                    "GLASS/GLASSWINDOW001A"  # Visible glass texture
                )
        
        # Add props
        if props:
            for prop in props:
                self.create_prop_static(prop["model"], prop["origin"], prop.get("angles", (0, 0, 0)))
    
    def create_street(self, start_position, width, length):
        """Create a street."""
        min_coords = start_position
        max_coords = [start_position[0] + length, start_position[1] + width, start_position[2] + 1]
        
        # Create the street brush with visible texture
        self.create_brush(min_coords, max_coords, "CONCRETE/CONCRETEFLOOR001A")
    
    def generate_town(self, size=3):
        """Generate a small town layout with buildings on both sides of a street."""
        # Create a ground plane with visible texture
        ground_size = size * 1024
        self.create_brush(
            [-ground_size/2, -ground_size/2, -16], 
            [ground_size/2, ground_size/2, 0], 
            "NATURE/GRASSFLOOR002A"  # Visible grass texture
        )
        
        # Create a main street
        street_width = 256
        self.create_street(
            [-ground_size/2, -street_width/2, 0],
            street_width,
            ground_size
        )
        
        # Create skybox
        self.create_entity("sky_camera", [0, 0, 128])
        
        # Create light environment
        self.create_entity("light_environment", [0, 0, 0], {
            "pitch": "-45",
            "_light": "255 255 255 200",
            "_ambient": "96 96 96 100",
            "angles": "0 0 0",
            "_ambientHDR": "96 96 96 100",
            "_lightHDR": "-1 -1 -1 1",
            "_lightscaleHDR": "1",
            "_quadratic_attn": "1"
        })
        
        # Create player start point
        self.create_entity("info_player_start", [0, 0, 16])
        
        # Create buildings on both sides of the street
        building_depth = 256
        building_width = 256
        building_height = 256
        
        # Common props for buildings
        furniture_models = [
            "models/props_interiors/furniture_chair01a.mdl",
            "models/props_interiors/furniture_couch01a.mdl",
            "models/props_interiors/furniture_desk01a.mdl",
            "models/props_interiors/furniture_shelf01a.mdl",
            "models/props_c17/furnituretable001a.mdl",
            "models/props_junk/wood_crate001a.mdl"
        ]
        
        # Create buildings on the left side of the street
        for i in range(-size+1, size):
            x_position = i * building_width
            y_position = -street_width/2 - building_depth
            
            # Determine door positions (front and back of building)
            front_door_pos = [
                x_position + building_width/2 - 16,  # Center door on building width
                y_position + building_depth - 4,     # Front side
                0                                    # Ground level
            ]
            
            back_door_pos = [
                x_position + building_width/2 - 16,  # Center door on building width
                y_position + 4,                      # Back side
                0                                    # Ground level
            ]
            
            # Determine window positions (sides of building)
            window_positions = [
                [x_position + 16, y_position + building_depth/2, 64],  # Front window
                [x_position + building_width - 64, y_position + building_depth/2, 64]  # Back window
            ]
            
            # Create some random props for the interior
            props = []
            for _ in range(3):
                props.append({
                    "model": random.choice(furniture_models),
                    "origin": [
                        x_position + random.randint(48, building_width-48),
                        y_position + random.randint(48, building_depth-48),
                        16
                    ],
                    "angles": (0, random.randint(0, 359), 0)
                })
            
            # Create the building with doors, windows, and props
            self.create_building(
                [x_position, y_position, 0],
                [building_width, building_depth, building_height],
                [front_door_pos, back_door_pos],
                window_positions,
                props
            )
        
        # Create buildings on the right side of the street
        for i in range(-size+1, size):
            x_position = i * building_width
            y_position = street_width/2
            
            # Determine door positions (front and back of building)
            front_door_pos = [
                x_position + building_width/2 - 16,  # Center door on building width
                y_position + 4,                      # Front side
                0                                    # Ground level
            ]
            
            back_door_pos = [
                x_position + building_width/2 - 16,  # Center door on building width
                y_position + building_depth - 4,     # Back side
                0                                    # Ground level
            ]
            
            # Determine window positions
            window_positions = [
                [x_position + 16, y_position + building_depth/2, 64],
                [x_position + building_width - 64, y_position + building_depth/2, 64]
            ]
            
            # Create some random props for the interior
            props = []
            for _ in range(3):
                props.append({
                    "model": random.choice(furniture_models),
                    "origin": [
                        x_position + random.randint(48, building_width-48),
                        y_position + random.randint(48, building_depth-48),
                        16
                    ],
                    "angles": (0, random.randint(0, 359), 0)
                })
            
            # Create the building with doors, windows, and props
            self.create_building(
                [x_position, y_position, 0],
                [building_width, building_depth, building_height],
                [front_door_pos, back_door_pos],
                window_positions,
                props
            )
    
    def write_vmf(self):
        """Write the VMF file."""
        with open(self.filename, "w") as f:
            # Write the VMF header
            f.write('versioninfo\n{\n\t"editorversion" "400"\n\t"editorbuild" "8864"\n\t"mapversion" "1"\n\t"formatversion" "100"\n\t"prefab" "0"\n}\n')
            f.write('visgroups\n{\n}\n')
            f.write('viewsettings\n{\n\t"bSnapToGrid" "1"\n\t"bShowGrid" "1"\n\t"bShowLogicalGrid" "0"\n\t"nGridSpacing" "64"\n\t"bShow3DGrid" "0"\n}\n')
            
            # Write the world entity
            f.write('world\n{\n')
            f.write('\t"id" "1"\n')
            f.write('\t"mapversion" "1"\n')
            f.write('\t"classname" "worldspawn"\n')
            f.write('\t"skyname" "sky_day01_01"\n')
            f.write('\t"maxpropscreenwidth" "-1"\n')
            f.write('\t"detailvbsp" "detail.vbsp"\n')
            f.write('\t"detailmaterial" "detail/detailsprites"\n')
            
            # Write all solids
            for solid in self.solids:
                f.write('\tsolid\n\t{\n')
                f.write(f'\t\t"id" "{solid["id"]}"\n')
                
                # Write all sides of the solid
                for side in solid["sides"]:
                    f.write('\t\tside\n\t\t{\n')
                    f.write(f'\t\t\t"id" "{side["id"]}"\n')
                    f.write(f'\t\t\t"plane" "{side["plane"]}"\n')
                    f.write(f'\t\t\t"material" "{side["material"]}"\n')
                    f.write(f'\t\t\t"uaxis" "{side["uaxis"]}"\n')
                    f.write(f'\t\t\t"vaxis" "{side["vaxis"]}"\n')
                    f.write(f'\t\t\t"rotation" "{side["rotation"]}"\n')
                    f.write(f'\t\t\t"lightmapscale" "{side["lightmapscale"]}"\n')
                    f.write(f'\t\t\t"smoothing_groups" "{side["smoothing_groups"]}"\n')
                    f.write('\t\t}\n')
                
                f.write('\t}\n')
            
            f.write('}\n')
            
            # Write all entities
            for entity in self.entities:
                f.write('entity\n{\n')
                
                for key, value in entity.items():
                    f.write(f'\t"{key}" "{value}"\n')
                
                f.write('}\n')
            
            # Write the cameras section
            f.write('cameras\n{\n\t"activecamera" "-1"\n}\n')
            f.write('cordon\n{\n\t"mins" "(-1024 -1024 -1024)"\n\t"maxs" "(1024 1024 1024)"\n\t"active" "0"\n}\n')

def main():
    # Create a new VMF Generator
    generator = VMFGenerator("town_map.vmf")
    
    # Generate the town
    generator.generate_town(size=3)
    
    # Write the VMF file
    generator.write_vmf()
    
    print(f"Successfully generated town map: {generator.filename}")

if __name__ == "__main__":
    main()