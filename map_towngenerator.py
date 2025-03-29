import argparse
import random
import math

class TownMapGenerator:
    def __init__(self):
        self.solids = []
        self.entities = []
        self.textures = {
            'road': 'CONCRETE/CONCRETEFLOOR027A',
            'building_wall': 'BRICK/BRICKWALL034A',
            'building_roof': 'CONCRETE/CONCRETEFLOOR039A',
            'alley': 'NATURE/DIRTFLOOR005A',
            'sidewalk': 'CONCRETE/CONCRETEFLOOR033A'
        }

    def _create_vertex(self, x, y, z):
        return f"({x} {y} {z})"

    def _create_plane(self, v1, v2, v3, texture):
        return f"{v1} {v2} {v3} [{texture}] [0 0 0 0] [0 0 0 0] 0 1 1"

    def _create_side(self, vertices, texture):
        # Define the 6 sides of a brush
        v = vertices
        sides = [
            # Bottom
            self._create_plane(v[0], v[1], v[2], texture),
            # Top
            self._create_plane(v[7], v[6], v[5], texture),
            # Front (Y-)
            self._create_plane(v[0], v[1], v[5], texture),
            # Back (Y+)
            self._create_plane(v[2], v[3], v[7], texture),
            # Right (X+)
            self._create_plane(v[1], v[2], v[6], texture),
            # Left (X-)
            self._create_plane(v[0], v[3], v[7], texture)
        ]
        return sides

    def _create_box(self, mins, maxs, textures):
        vertices = [
            self._create_vertex(mins[0], mins[1], mins[2]),
            self._create_vertex(maxs[0], mins[1], mins[2]),
            self._create_vertex(maxs[0], maxs[1], mins[2]),
            self._create_vertex(mins[0], maxs[1], mins[2]),
            self._create_vertex(mins[0], mins[1], maxs[2]),
            self._create_vertex(maxs[0], mins[1], maxs[2]),
            self._create_vertex(maxs[0], maxs[1], maxs[2]),
            self._create_vertex(mins[0], maxs[1], maxs[2])
        ]
        
        # Use specific texture for each face if provided, else default
        sides = [
            self._create_side([0, 1, 2, 3], textures.get('bottom', textures.get('default', self.textures['building_wall']))),
            self._create_side([4, 5, 6, 7], textures.get('top', textures.get('default', self.textures['building_wall']))),
            self._create_side([0, 1, 5, 4], textures.get('front', textures.get('default', self.textures['building_wall']))),
            self._create_side([2, 3, 7, 6], textures.get('back', textures.get('default', self.textures['building_wall']))),
            self._create_side([1, 2, 6, 5], textures.get('right', textures.get('default', self.textures['building_wall']))),
            self._create_side([0, 3, 7, 4], textures.get('left', textures.get('default', self.textures['building_wall'])))
        ]
        
        solid = "solid\n{\n"
        solid += f"\"id\" \"{len(self.solids) + 1}\"\n"
        for side in sides:
            solid += "side\n{\n"
            solid += f"\"id\" \"{len(self.solids) * 6 + sides.index(side) + 1}\"\n"
            solid += f"\"plane\" \"{side[0]}\"\n"
            solid += f"\"material\" \"{side[1]}\"\n"
            solid += f"\"uaxis\" \"{side[2]}\"\n"
            solid += f"\"vaxis\" \"{side[3]}\"\n"
            solid += f"\"rotation\" \"{side[4]}\"\n"
            solid += f"\"lightmapscale\" \"{side[5]}\"\n"
            solid += f"\"smoothing_groups\" \"{side[6]}\"\n"
            solid += "}\n"
        solid += "}\n"
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

    def add_player_start(self, position):
        """Add a player start entity."""
        entity = "entity\n{\n"
        entity += f"\"id\" \"{len(self.entities) + 1}\"\n"
        entity += "\"classname\" \"info_player_start\"\n"
        entity += f"\"origin\" \"{position[0]} {position[1]} {position[2]}\"\n"
        entity += "\"angles\" \"0 0 0\"\n"
        entity += "}\n"
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
                self._create_box(
                    [road_x - sidewalk_width, road_y + road_width, origin[2]],
                    [road_x + road_width + sidewalk_width, road_y + road_width + sidewalk_width, origin[2] + sidewalk_thickness],
                    {'top': self.textures['sidewalk']}
                )
                # South sidewalk
                self._create_box(
                    [road_x - sidewalk_width, road_y - sidewalk_width, origin[2]],
                    [road_x + road_width + sidewalk_width, road_y, origin[2] + sidewalk_thickness],
                    {'top': self.textures['sidewalk']}
                )
                # East sidewalk
                self._create_box(
                    [road_x + road_width, road_y - sidewalk_width, origin[2]],
                    [road_x + road_width + sidewalk_width, road_y + road_width + sidewalk_width, origin[2] + sidewalk_thickness],
                    {'top': self.textures['sidewalk']}
                )
                # West sidewalk
                self._create_box(
                    [road_x - sidewalk_width, road_y - sidewalk_width, origin[2]],
                    [road_x, road_y + road_width + sidewalk_width, origin[2] + sidewalk_thickness],
                    {'top': self.textures['sidewalk']}
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

    def generate_map(self, filename="town.map"):
        """Save the town layout to a .map file."""
        with open(filename, 'w') as f:
            f.write("versioninfo\n{\n")
            f.write("\"editorversion\" \"400\"\n")
            f.write("\"editorbuild\" \"6412\"\n")
            f.write("\"mapversion\" \"1\"\n")
            f.write("\"formatversion\" \"100\"\n")
            f.write("\"prefab\" \"0\"\n")
            f.write("}\n")
            f.write("world\n{\n")
            f.write("\"id\" \"1\"\n")
            f.write("\"classname\" \"worldspawn\"\n")
            f.write("\"skyname\" \"sky_day01_01\"\n")
            for solid in self.solids:
                f.write(solid)
            f.write("}\n")
            for entity in self.entities:
                f.write(entity)

def main():
    parser = argparse.ArgumentParser(description='Generate a Source Engine town map (.map) file.')
    parser.add_argument('--name', type=str, default='town', help='Name of the output map file')
    parser.add_argument('--output', type=str, default=None, help='Output file path (if not specified, name.map will be used)')
    parser.add_argument('--streets-x', type=int, default=3, help='Number of streets running east-west')
    parser.add_argument('--streets-y', type=int, default=3, help='Number of streets running north-south')

    args = parser.parse_args()

    # Create town generator
    town_gen = TownMapGenerator()
    
    # Generate the town
    town_gen.create_town(streets_x=args.streets_x, streets_y=args.streets_y)
    
    # Save the map
    output_path = args.output if args.output else f"{args.name}.map"
    town_gen.generate_map(output_path)
    print(f"Town map generation complete. Output saved to: {output_path}")

if __name__ == "__main__":
    main()
