import argparse
import random
import math

class TownMapGenerator:
    def __init__(self):
        self.solids = []
        self.entities = []
        self.next_id = 1
        self.textures = {
            'road': 'CONCRETE/CONCRETEFLOOR027A',
            'building_wall': 'BRICK/BRICKWALL034A',
            'building_roof': 'CONCRETE/CONCRETEFLOOR039A',
            'alley': 'NATURE/DIRTFLOOR005A',
            'sidewalk': 'CONCRETE/CONCRETEFLOOR033A'
        }

    def get_next_id(self):
        """Get the next available ID and increment the counter."""
        current_id = self.next_id
        self.next_id += 1
        return current_id

    def _create_vertex(self, x, y, z):
        return f"{x} {y} {z}"

    def _create_box(self, mins, maxs, textures):
        """Create a brush box with the specified dimensions and textures."""
        # Create 8 vertices of the box
        v = [
            [mins[0], mins[1], mins[2]],  # 0: bottom left front
            [maxs[0], mins[1], mins[2]],  # 1: bottom right front
            [maxs[0], maxs[1], mins[2]],  # 2: bottom right back
            [mins[0], maxs[1], mins[2]],  # 3: bottom left back
            [mins[0], mins[1], maxs[2]],  # 4: top left front
            [maxs[0], mins[1], maxs[2]],  # 5: top right front
            [maxs[0], maxs[1], maxs[2]],  # 6: top right back
            [mins[0], maxs[1], maxs[2]]   # 7: top left back
        ]
        
        # Get the default texture
        default_texture = textures.get('default', self.textures['building_wall'])
        
        # Define the 6 planes (sides) of the box with correct vertex ordering for VMF
        sides = [
            # Bottom (floor)
            {
                "material": textures.get('bottom', default_texture),
                "plane": f"({v[0][0]} {v[0][1]} {v[0][2]}) ({v[1][0]} {v[1][1]} {v[1][2]}) ({v[2][0]} {v[2][1]} {v[2][2]})",
                "uaxis": "[1 0 0 0] 0.25",
                "vaxis": "[0 -1 0 0] 0.25",
            },
            # Top (ceiling/roof)
            {
                "material": textures.get('top', default_texture),
                "plane": f"({v[6][0]} {v[6][1]} {v[6][2]}) ({v[5][0]} {v[5][1]} {v[5][2]}) ({v[4][0]} {v[4][1]} {v[4][2]})",
                "uaxis": "[1 0 0 0] 0.25",
                "vaxis": "[0 -1 0 0] 0.25",
            },
            # Front (Y-)
            {
                "material": textures.get('front', default_texture),
                "plane": f"({v[0][0]} {v[0][1]} {v[0][2]}) ({v[4][0]} {v[4][1]} {v[4][2]}) ({v[5][0]} {v[5][1]} {v[5][2]})",
                "uaxis": "[1 0 0 0] 0.25",
                "vaxis": "[0 0 -1 0] 0.25",
            },
            # Back (Y+)
            {
                "material": textures.get('back', default_texture),
                "plane": f"({v[2][0]} {v[2][1]} {v[2][2]}) ({v[6][0]} {v[6][1]} {v[6][2]}) ({v[7][0]} {v[7][1]} {v[7][2]})",
                "uaxis": "[1 0 0 0] 0.25",
                "vaxis": "[0 0 -1 0] 0.25",
            },
            # Right (X+)
            {
                "material": textures.get('right', default_texture),
                "plane": f"({v[1][0]} {v[1][1]} {v[1][2]}) ({v[5][0]} {v[5][1]} {v[5][2]}) ({v[6][0]} {v[6][1]} {v[6][2]})",
                "uaxis": "[0 1 0 0] 0.25",
                "vaxis": "[0 0 -1 0] 0.25",
            },
            # Left (X-)
            {
                "material": textures.get('left', default_texture),
                "plane": f"({v[0][0]} {v[0][1]} {v[0][2]}) ({v[3][0]} {v[3][1]} {v[3][2]}) ({v[7][0]} {v[7][1]} {v[7][2]})",
                "uaxis": "[0 1 0 0] 0.25",
                "vaxis": "[0 0 -1 0] 0.25",
            }
        ]
        
        # Create a solid with unique ID
        solid_id = self.get_next_id()
        solid = {
            "id": solid_id,
            "sides": []
        }
        
        # Add each side with unique ID
        for side_data in sides:
            side = {
                "id": self.get_next_id(),
                "plane": side_data["plane"],
                "material": side_data["material"],
                "uaxis": side_data["uaxis"],
                "vaxis": side_data["vaxis"],
                "rotation": "0",
                "lightmapscale": "16",
                "smoothing_groups": "0"
            }
            solid["sides"].append(side)
        
        return solid

    def add_road(self, mins, maxs):
        """Add a flat road brush."""
        road_textures = {'top': self.textures['road'], 'bottom': self.textures['road']}
        road = self._create_box(
            [mins[0], mins[1], mins[2] - 16],  # Slightly below ground level
            [maxs[0], maxs[1], mins[2]],
            road_textures
        )
        self.solids.append(road)

    def add_building(self, mins, maxs):
        """Add a building with walls and roof."""
        building_textures = {
            'top': self.textures['building_roof'],
            'front': self.textures['building_wall'],
            'back': self.textures['building_wall'],
            'left': self.textures['building_wall'],
            'right': self.textures['building_wall'],
            'bottom': self.textures['building_wall']
        }
        building = self._create_box(mins, maxs, building_textures)
        self.solids.append(building)
        return {'mins': mins, 'maxs': maxs}

    def add_alley(self, mins, maxs):
        """Add a flat alley brush between buildings."""
        alley_textures = {'top': self.textures['alley'], 'bottom': self.textures['alley']}
        alley = self._create_box(
            [mins[0], mins[1], mins[2] - 16],
            [maxs[0], maxs[1], mins[2]],
            alley_textures
        )
        self.solids.append(alley)

    def add_sidewalk(self, mins, maxs):
        """Add a sidewalk brush."""
        sidewalk_textures = {'top': self.textures['sidewalk'], 'default': self.textures['sidewalk']}
        sidewalk = self._create_box(mins, maxs, sidewalk_textures)
        self.solids.append(sidewalk)

    def add_player_start(self, position):
        """Add a player start entity."""
        entity = {
            "id": self.get_next_id(),
            "classname": "info_player_start",
            "origin": f"{position[0]} {position[1]} {position[2]}",
            "angles": "0 0 0"
        }
        self.entities.append(entity)

    def create_town(self, streets_x=3, streets_y=3):
        """
        Generate a town with a grid of streets and buildings.
        
        Args:
            streets_x (int): Number of streets running east-west
            streets_y (int): Number of streets running north-south
        """
        road_width = 128  # Width of streets
        alley_width = 64  # Width of alleyways
        building_base_size = 256  # Base size for buildings
        building_height = 384  # Fixed height for simplicity
        sidewalk_width = 32  # Width of sidewalks along roads

        # Calculate total town dimensions
        total_width = (streets_x * (road_width + 2 * sidewalk_width)) + ((streets_x - 1) * (building_base_size + alley_width))
        total_length = (streets_y * (road_width + 2 * sidewalk_width)) + ((streets_y - 1) * (building_base_size + alley_width))
        origin = [0, 0, 0]  # Starting at origin

        buildings = []

        # Generate the grid
        for y in range(streets_y):
            for x in range(streets_x):
                # Calculate road position
                road_x = origin[0] + x * (road_width + 2 * sidewalk_width + building_base_size + alley_width)
                road_y = origin[1] + y * (road_width + 2 * sidewalk_width + building_base_size + alley_width)
                
                # Add horizontal road (east-west)
                self.add_road(
                    [road_x - (x * alley_width), road_y, origin[2]],
                    [road_x + road_width + (x * alley_width), road_y + road_width, origin[2]]
                )
                
                # Add vertical road (north-south)
                self.add_road(
                    [road_x, road_y - (y * alley_width), origin[2]],
                    [road_x + road_width, road_y + road_width + (y * alley_width), origin[2]]
                )

                # Add sidewalks around the intersection
                sidewalk_thickness = 8
                # North sidewalk
                self.add_sidewalk(
                    [road_x - sidewalk_width, road_y + road_width, origin[2]],
                    [road_x + road_width + sidewalk_width, road_y + road_width + sidewalk_width, origin[2] + sidewalk_thickness]
                )
                # South sidewalk
                self.add_sidewalk(
                    [road_x - sidewalk_width, road_y - sidewalk_width, origin[2]],
                    [road_x + road_width + sidewalk_width, road_y, origin[2] + sidewalk_thickness]
                )
                # East sidewalk
                self.add_sidewalk(
                    [road_x + road_width, road_y - sidewalk_width, origin[2]],
                    [road_x + road_width + sidewalk_width, road_y + road_width + sidewalk_width, origin[2] + sidewalk_thickness]
                )
                # West sidewalk
                self.add_sidewalk(
                    [road_x - sidewalk_width, road_y - sidewalk_width, origin[2]],
                    [road_x, road_y + road_width + sidewalk_width, origin[2] + sidewalk_thickness]
                )

                # Add buildings in the quadrants around the intersection
                # Top-right quadrant
                if x < streets_x - 1 and y < streets_y - 1:
                    building_width = building_base_size + random.uniform(-64, 64)
                    building_length = building_base_size + random.uniform(-64, 64)
                    building_mins = [
                        road_x + road_width + sidewalk_width,
                        road_y + road_width + sidewalk_width,
                        origin[2]
                    ]
                    building_maxs = [
                        building_mins[0] + building_width,
                        building_mins[1] + building_length,
                        origin[2] + building_height
                    ]
                    buildings.append(self.add_building(building_mins, building_maxs))

                    # Add alleyways
                    # Alley to the right
                    if x < streets_x - 2:
                        self.add_alley(
                            [building_maxs[0], building_mins[1], origin[2]],
                            [building_maxs[0] + alley_width, building_maxs[1], origin[2]]
                        )
                    # Alley to the top
                    if y < streets_y - 2:
                        self.add_alley(
                            [building_mins[0], building_maxs[1], origin[2]],
                            [building_maxs[0], building_maxs[1] + alley_width, origin[2]]
                        )

                # Top-left quadrant
                if x > 0 and y < streets_y - 1:
                    building_width = building_base_size + random.uniform(-64, 64)
                    building_length = building_base_size + random.uniform(-64, 64)
                    building_mins = [
                        road_x - building_width - sidewalk_width,
                        road_y + road_width + sidewalk_width,
                        origin[2]
                    ]
                    building_maxs = [
                        road_x - sidewalk_width,
                        building_mins[1] + building_length,
                        origin[2] + building_height
                    ]
                    buildings.append(self.add_building(building_mins, building_maxs))

                    # Alley to the left
                    if x > 1:
                        self.add_alley(
                            [building_mins[0] - alley_width, building_mins[1], origin[2]],
                            [building_mins[0], building_maxs[1], origin[2]]
                        )
                    # Alley to the top
                    if y < streets_y - 2:
                        self.add_alley(
                            [building_mins[0], building_maxs[1], origin[2]],
                            [building_maxs[0], building_maxs[1] + alley_width, origin[2]]
                        )

                # Bottom-right quadrant
                if x < streets_x - 1 and y > 0:
                    building_width = building_base_size + random.uniform(-64, 64)
                    building_length = building_base_size + random.uniform(-64, 64)
                    building_mins = [
                        road_x + road_width + sidewalk_width,
                        road_y - building_length - sidewalk_width,
                        origin[2]
                    ]
                    building_maxs = [
                        building_mins[0] + building_width,
                        road_y - sidewalk_width,
                        origin[2] + building_height
                    ]
                    buildings.append(self.add_building(building_mins, building_maxs))

                    # Alley to the right
                    if x < streets_x - 2:
                        self.add_alley(
                            [building_maxs[0], building_mins[1], origin[2]],
                            [building_maxs[0] + alley_width, building_maxs[1], origin[2]]
                        )
                    # Alley to the bottom
                    if y > 1:
                        self.add_alley(
                            [building_mins[0], building_mins[1] - alley_width, origin[2]],
                            [building_maxs[0], building_mins[1], origin[2]]
                        )

                # Bottom-left quadrant
                if x > 0 and y > 0:
                    building_width = building_base_size + random.uniform(-64, 64)
                    building_length = building_base_size + random.uniform(-64, 64)
                    building_mins = [
                        road_x - building_width - sidewalk_width,
                        road_y - building_length - sidewalk_width,
                        origin[2]
                    ]
                    building_maxs = [
                        road_x - sidewalk_width,
                        road_y - sidewalk_width,
                        origin[2] + building_height
                    ]
                    buildings.append(self.add_building(building_mins, building_maxs))

                    # Alley to the left
                    if x > 1:
                        self.add_alley(
                            [building_mins[0] - alley_width, building_mins[1], origin[2]],
                            [building_mins[0], building_maxs[1], origin[2]]
                        )
                    # Alley to the bottom
                    if y > 1:
                        self.add_alley(
                            [building_mins[0], building_mins[1] - alley_width, origin[2]],
                            [building_maxs[0], building_mins[1], origin[2]]
                        )

        # Add player start at the center of the town
        center_x = total_width / 2
        center_y = total_length / 2
        self.add_player_start([center_x, center_y, origin[2] + 32])

        return buildings

    def generate_vmf(self, filename="town.vmf"):
        """Save the town layout to a .vmf file (Valve Map Format)."""
        with open(filename, 'w') as f:
            # Write VMF header
            f.write("versioninfo\n{\n")
            f.write("\t\"editorversion\" \"400\"\n")
            f.write("\t\"editorbuild\" \"8864\"\n")
            f.write("\t\"mapversion\" \"1\"\n")
            f.write("\t\"formatversion\" \"100\"\n")
            f.write("\t\"prefab\" \"0\"\n")
            f.write("}\n")
            
            # Write visgroups
            f.write("visgroups\n{\n}\n")
            
            # Write viewsettings
            f.write("viewsettings\n{\n")
            f.write("\t\"bSnapToGrid\" \"1\"\n")
            f.write("\t\"bShowGrid\" \"1\"\n")
            f.write("\t\"bShowLogicalGrid\" \"0\"\n")
            f.write("\t\"nGridSpacing\" \"64\"\n")
            f.write("}\n")
            
            # Write world entity
            f.write("world\n{\n")
            f.write("\t\"id\" \"1\"\n")
            f.write("\t\"mapversion\" \"1\"\n")
            f.write("\t\"classname\" \"worldspawn\"\n")
            f.write("\t\"skyname\" \"sky_day01_01\"\n")
            f.write("\t\"maxpropscreenwidth\" \"-1\"\n")
            f.write("\t\"detailvbsp\" \"detail.vbsp\"\n")
            f.write("\t\"detailmaterial\" \"detail/detailsprites\"\n")
            
            # Write solid brushes for world
            for solid in self.solids:
                f.write("\tsolid\n\t{\n")
                f.write(f"\t\t\"id\" \"{solid['id']}\"\n")
                
                # Write sides
                for side in solid["sides"]:
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
            
            # Write entities
            for entity in self.entities:
                f.write("entity\n{\n")
                for key, value in entity.items():
                    if key != "id":  # id is handled separately
                        f.write(f"\t\"{key}\" \"{value}\"\n")
                f.write(f"\t\"id\" \"{entity['id']}\"\n")
                f.write("}\n")
            
            # Write cameras
            f.write("cameras\n{\n")
            f.write("\t\"activecamera\" \"-1\"\n")
            f.write("}\n")
            
            # Write cordon
            f.write("cordon\n{\n")
            f.write("\t\"mins\" \"(-1024 -1024 -1024)\"\n")
            f.write("\t\"maxs\" \"(1024 1024 1024)\"\n")
            f.write("\t\"active\" \"0\"\n")
            f.write("}\n")

def main():
    parser = argparse.ArgumentParser(description='Generate a Source Engine town VMF file.')
    parser.add_argument('--name', type=str, default='town', help='Name of the output map file')
    parser.add_argument('--output', type=str, default=None, help='Output file path (if not specified, name.vmf will be used)')
    parser.add_argument('--streets-x', type=int, default=3, help='Number of streets running east-west')
    parser.add_argument('--streets-y', type=int, default=3, help='Number of streets running north-south')

    args = parser.parse_args()

    # Create town generator
    town_gen = TownMapGenerator()
    
    # Generate the town
    town_gen.create_town(streets_x=args.streets_x, streets_y=args.streets_y)
    
    # Save the map as VMF
    output_path = args.output if args.output else f"{args.name}.vmf"
    town_gen.generate_vmf(output_path)
    print(f"Town map generation complete. Output saved to: {output_path}")

if __name__ == "__main__":
    main()