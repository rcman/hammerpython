import random

class VMFGenerator:
    def __init__(self, filename="street_scene.vmf"):
        self.filename = filename
        self.next_id = 1
        self.solids = []
        self.entities = []
        
    def get_next_id(self):
        """Get the next unique ID for VMF objects"""
        current_id = self.next_id
        self.next_id += 1
        return current_id
        
    def create_brush(self, coords, texture="TOOLS/TOOLSNODRAW"):
        """Create a brush with the given coordinates and texture"""
        brush_id = self.get_next_id()
        
        sides = []
        # Front face
        sides.append(self.create_side([coords[0], coords[1], coords[2]], 
                                     [coords[0], coords[1], coords[5]], 
                                     [coords[3], coords[1], coords[5]], 
                                     texture))
        # Back face
        sides.append(self.create_side([coords[3], coords[4], coords[2]], 
                                     [coords[0], coords[4], coords[2]], 
                                     [coords[0], coords[4], coords[5]], 
                                     texture))
        # Left face
        sides.append(self.create_side([coords[0], coords[4], coords[2]], 
                                     [coords[0], coords[1], coords[2]], 
                                     [coords[0], coords[1], coords[5]], 
                                     texture))
        # Right face
        sides.append(self.create_side([coords[3], coords[1], coords[2]], 
                                     [coords[3], coords[4], coords[2]], 
                                     [coords[3], coords[4], coords[5]], 
                                     texture))
        # Bottom face
        sides.append(self.create_side([coords[0], coords[4], coords[2]], 
                                     [coords[3], coords[4], coords[2]], 
                                     [coords[3], coords[1], coords[2]], 
                                     texture))
        # Top face
        sides.append(self.create_side([coords[0], coords[4], coords[5]], 
                                     [coords[3], coords[4], coords[5]], 
                                     [coords[3], coords[1], coords[5]], 
                                     texture))
        
        brush = {
            "id": brush_id,
            "sides": sides
        }
        
        self.solids.append(brush)
        return brush_id
        
    def create_side(self, p1, p2, p3, texture):
        """Create a brush side with the given points and texture"""
        side_id = self.get_next_id()
        
        side = {
            "id": side_id,
            "plane": f"({p1[0]} {p1[1]} {p1[2]}) ({p2[0]} {p2[1]} {p2[2]}) ({p3[0]} {p3[1]} {p3[2]})",
            "material": texture,
            "uaxis": "[1 0 0 0] 0.25",
            "vaxis": "[0 -1 0 0] 0.25",
            "rotation": "0",
            "lightmapscale": "16",
            "smoothing_groups": "0"
        }
        
        return side
        
    def create_entity(self, classname, properties=None, origin=None):
        """Create an entity with the given properties"""
        entity_id = self.get_next_id()
        
        entity = {
            "id": entity_id,
            "classname": classname
        }
        
        if origin:
            entity["origin"] = f"{origin[0]} {origin[1]} {origin[2]}"
            
        if properties:
            for key, value in properties.items():
                entity[key] = value
                
        self.entities.append(entity)
        return entity_id
    
    def create_street(self, length=1024, width=256, height=16):
        """Create a street with the given dimensions"""
        # Street is along x-axis
        return self.create_brush([
            -length/2, -width/2, -height,  # Min x, min y, min z
            length/2, width/2, 0           # Max x, max y, max z
        ])
        
    def create_building(self, x, y, width, depth, height, stories=1, doors=1):
        """Create a building with the given dimensions and number of doors"""
        # Main building structure
        building_id = self.create_brush([
            x, y, 0,
            x + width, y + depth, height * stories
        ])
        
        # Roof
        roof_id = self.create_brush([
            x, y, height * stories,
            x + width, y + depth, height * stories + 8
        ])
        
        # Windows
        window_offset = 64
        window_size = 32
        window_height = 48
        
        # Place windows on each story
        for story in range(stories):
            story_height = story * height
            # Make sure we don't place windows too close to edges
            if width > (window_offset * 2 + window_size):
                for wx in range(int(x + window_offset), int(x + width - window_offset - window_size), int(window_offset * 2)):
                    # Front windows
                    window_id = self.create_brush([
                        wx, y - 4, story_height + height // 2,
                        wx + window_size, y + 4, story_height + height // 2 + window_height
                    ])
                    
                    # Back windows
                    window_id = self.create_brush([
                        wx, y + depth - 4, story_height + height // 2,
                        wx + window_size, y + depth + 4, story_height + height // 2 + window_height
                    ])
        
        # Ensure at least one door
        doors = max(1, doors)
        
        # Place doors along the front of the building
        door_width = 48
        door_height = 80
        door_spacing = width / (doors + 1)
        
        for i in range(1, doors + 1):
            door_x = x + (door_spacing * i) - (door_width / 2)
            
            # Make sure door is within building bounds
            if door_x < x:
                door_x = x
            if door_x + door_width > x + width:
                door_x = x + width - door_width
                
            # Door frame
            frame_id = self.create_brush([
                door_x - 4, y - 4, 0,
                door_x + door_width + 4, y + 4, door_height + 4
            ])
            
            # Create hole for door (by carving out the wall where the door goes)
            # We do this by creating solid blocks to the left and right of the door
            if door_x > x:
                # Left side of door
                left_wall = self.create_brush([
                    x, y, 0,
                    door_x, y + 4, door_height
                ])
                
            if door_x + door_width < x + width:
                # Right side of door
                right_wall = self.create_brush([
                    door_x + door_width, y, 0,
                    x + width, y + 4, door_height
                ])
            
            # Door itself (as a brush)
            door_brush_id = self.create_brush([
                door_x, y - 8, 0,
                door_x + door_width, y, door_height
            ])
            
            # Create a func_door entity with solid brush reference
            door_entity_id = self.create_entity("func_door", {
                "speed": "100",
                "wait": "4",
                "lip": "0",
                "sounds": "3",
                "targetname": f"door_{door_brush_id}",
                "movedir": "0 90 0",  # Move direction (90 degrees = along Y axis)
                "disablereceiveshadows": "0",
                "disableshadows": "0",
                "spawnflags": "0"
            }, [door_x + door_width/2, y - 4, door_height/2])  # Origin at center of door
            
        return building_id
        
    def create_light(self, origin, brightness=300):
        """Create a point light"""
        return self.create_entity("light", {
            "_light": f"255 255 255 {brightness}",
            "_constant_attn": "0",
            "_linear_attn": "0",
            "_quadratic_attn": "1",
            "_lightHDR": "-1 -1 -1 1",
            "_lightscaleHDR": "1",
            "style": "0"
        }, origin)
        
    def create_streetlights(self, street_length, street_width, spacing=256):
        """Create streetlights along both sides of the street"""
        for x in range(int(-street_length/2 + spacing), int(street_length/2), spacing):
            # Left side
            pole_id = self.create_brush([
                x - 4, -street_width/2 - 16 - 4, 0,
                x + 4, -street_width/2 - 16 + 4, 128
            ])
            
            light_id = self.create_light([x, -street_width/2 - 16, 128], 500)
            
            # Right side
            pole_id = self.create_brush([
                x - 4, street_width/2 + 16 - 4, 0,
                x + 4, street_width/2 + 16 + 4, 128
            ])
            
            light_id = self.create_light([x, street_width/2 + 16, 128], 500)
            
    def create_skybox(self):
        """Create a skybox entity"""
        return self.create_entity("sky_camera", {
            "scale": "16"
        }, [0, 0, 512])
        
    def create_player_start(self):
        """Create a player start point"""
        return self.create_entity("info_player_start", {}, [0, 0, 64])
    
    def create_reference_cube(self):
        """Create a reference cube to help with visibility/orientation"""
        return self.create_brush([
            -32, -32, 0,
            32, 32, 64
        ], texture="DEV/DEV_MEASUREGENERIC01")
        
    def generate_map(self):
        """Generate a complete map with street and buildings"""
        street_length = 2048
        street_width = 256
        
        # Create the street
        self.create_street(street_length, street_width)
        
        # Create streetlights
        self.create_streetlights(street_length, street_width)
        
        # Create buildings on both sides of the street
        building_min_width = 128
        building_max_width = 384
        building_min_depth = 128
        building_max_depth = 256
        max_stories = 3
        
        # Left side buildings
        x = int(-street_length/2)
        while x < int(street_length/2):
            width = random.randint(building_min_width, building_max_width)
            depth = random.randint(building_min_depth, building_max_depth)
            stories = random.randint(1, max_stories)
            doors = random.randint(1, 3)
            
            self.create_building(x, -street_width/2 - depth, width, depth, 128, stories, doors)
            x += width + random.randint(16, 64)
            
        # Right side buildings
        x = int(-street_length/2)
        while x < int(street_length/2):
            width = random.randint(building_min_width, building_max_width)
            depth = random.randint(building_min_depth, building_max_depth)
            stories = random.randint(1, max_stories)
            doors = random.randint(1, 3)
            
            self.create_building(x, street_width/2, width, depth, 128, stories, doors)
            x += width + random.randint(16, 64)
        
        # Add a reference cube at the origin to help with visibility
        self.create_reference_cube()
        
        # Create skybox
        self.create_skybox()
        
        # Create player start
        self.create_player_start()
        
        # Create a light_environment entity for outdoor lighting
        self.create_entity("light_environment", {
            "_light": "255 255 255 200",
            "_ambient": "192 192 192 20",
            "angles": "0 0 0",
            "pitch": "-90",
            "_lightHDR": "-1 -1 -1 1",
            "_lightscaleHDR": "1",
            "sunspreadangle": "0"
        })
        
    def write_vmf(self):
        """Write the VMF file"""
        with open(self.filename, "w") as f:
            f.write("versioninfo\n{\n\t\"editorversion\" \"400\"\n\t\"editorbuild\" \"8864\"\n")
            f.write("\t\"mapversion\" \"1\"\n\t\"formatversion\" \"100\"\n\t\"prefab\" \"0\"\n}\n")
            
            f.write("visgroups\n{\n}\n")
            f.write("viewsettings\n{\n\t\"bSnapToGrid\" \"1\"\n\t\"bShowGrid\" \"1\"\n")
            f.write("\t\"bShowLogicalGrid\" \"0\"\n\t\"nGridSpacing\" \"16\"\n}\n")
            
            f.write("world\n{\n\t\"id\" \"1\"\n\t\"mapversion\" \"1\"\n")
            f.write("\t\"classname\" \"worldspawn\"\n\t\"skyname\" \"sky_day01_01\"\n")
            f.write("\t\"maxpropscreenwidth\" \"-1\"\n\t\"detailvbsp\" \"detail.vbsp\"\n")
            f.write("\t\"detailmaterial\" \"detail/detailsprites\"\n")
            
            # Write all brush solids for the world
            for solid in self.solids:
                f.write("\tsolid\n\t{\n")
                f.write(f"\t\t\"id\" \"{solid['id']}\"\n")
                
                for side in solid['sides']:
                    f.write("\t\tside\n\t\t{\n")
                    f.write(f"\t\t\t\"id\" \"{side['id']}\"\n")
                    f.write(f"\t\t\t\"plane\" \"{side['plane']}\"\n")
                    f.write(f"\t\t\t\"material\" \"{side['material']}\"\n")
                    f.write(f"\t\t\t\"uaxis\" \"{side['uaxis']}\"\n")
                    f.write(f"\t\t\t\"vaxis\" \"{side['vaxis']}\"\n")
                    f.write(f"\t\t\t\"rotation\" \"{side['rotation']}\"\n")
                    f.write(f"\t\t\t\"lightmapscale\" \"{side['lightmapscale']}\"\n")
                    f.write(f"\t\t\t\"smoothing_groups\" \"{side['smoothing_groups']}\"\n")
                    f.write("\t\t}\n")
                
                f.write("\t}\n")
            
            f.write("}\n")
            
            # Write all entities
            for entity in self.entities:
                f.write("entity\n{\n")
                for key, value in entity.items():
                    if key != "id":
                        f.write(f"\t\"{key}\" \"{value}\"\n")
                f.write(f"\t\"id\" \"{entity['id']}\"\n")
                f.write("}\n")
            
            # Write cameras section
            f.write("cameras\n{\n\t\"activecamera\" \"-1\"\n}\n")
            
            # Write cordon section
            f.write("cordon\n{\n\t\"mins\" \"(-1024 -1024 -1024)\"\n")
            f.write("\t\"maxs\" \"(1024 1024 1024)\"\n\t\"active\" \"0\"\n}\n")

if __name__ == "__main__":
    generator = VMFGenerator()
    generator.generate_map()
    generator.write_vmf()
    print(f"Map generated successfully: {generator.filename}")