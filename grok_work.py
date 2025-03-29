import math
import random

class SourceMapGenerator:
    def __init__(self):
        self.solids = []
        self.entities = []
        self.textures = {
            'floor': 'DEV/DEV_MEASUREGENERIC01B',
            'ceiling': 'DEV/DEV_MEASUREGENERIC01',
            'wall': 'DEV/DEV_MEASUREWALL01A',
            'brick': 'BRICK/BRICKWALL034A',
            'concrete': 'CONCRETE/CONCRETEWALL046A',
            'metal': 'METAL/METALWALL045A',
            'dirt': 'NATURE/DIRTFLOOR005A'
        }

    def _create_vertex(self, x, y, z):
        return f"({x} {y} {z})"

    def _create_plane(self, v1, v2, v3, texture):
        return f"{v1} {v2} {v3} [{texture}] [0 0 0 0] [0 0 0 0] 0 1 1"

    def _create_side(self, vertices, texture):
        planes = []
        for i in range(4):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % 4]
            v3 = vertices[(i + 1) % 4 + 4]
            planes.append(self._create_plane(v1, v2, v3, texture))
        return planes

    def _create_box(self, mins, maxs, textures):
        # Define vertices for a box (unchanged)
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
        
        # Define faces with appropriate textures (unchanged)
        sides = [
            self._create_side([0, 1, 2, 3], textures.get('bottom', textures['wall'])),  # Bottom
            self._create_side([4, 5, 6, 7], textures.get('top', textures['wall'])),     # Top
            self._create_side([0, 1, 5, 4], textures.get('front', textures['wall'])),  # Front (Y-)
            self._create_side([2, 3, 7, 6], textures.get('back', textures['wall'])),   # Back (Y+)
            self._create_side([1, 2, 6, 5], textures.get('right', textures['wall'])),  # Right (X+)
            self._create_side([0, 3, 7, 4], textures.get('left', textures['wall']))    # Left (X-)
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

    def add_room(self, position, size, textures=None, doorways=None):
        """
        Adds a room with doorways on specified walls.
        
        Args:
            position (list): [x, y, z] coordinates of the room's origin
            size (list): [width, length, height] of the room
            textures (dict): Textures for each face (optional)
            doorways (dict): Dictionary specifying doorway ranges on each wall
                            e.g., {'left': [{'y_min': y1, 'y_max': y2}], 'right': [...], ...}
        """
        if textures is None:
            textures = {
                'bottom': self.textures['floor'],
                'top': self.textures['ceiling'],
                'front': self.textures['wall'],
                'back': self.textures['wall'],
                'left': self.textures['wall'],
                'right': self.textures['wall']
            }
        if doorways is None:
            doorways = {'left': [], 'right': [], 'front': [], 'back': []}

        x, y, z = position
        width, length, height = size
        inner_mins = [x, y, z]
        inner_maxs = [x + width, y + length, z + height]
        thickness = 16
        walls = []

        # Texture setup
        floor_textures = {'top': textures['bottom'], 'bottom': textures['bottom']}
        ceiling_textures = {'top': textures['top'], 'bottom': textures['top']}
        front_wall_textures = {'front': textures['front'], 'back': textures['front']}
        back_wall_textures = {'front': textures['back'], 'back': textures['back']}
        left_wall_textures = {'front': textures['left'], 'back': textures['left']}
        right_wall_textures = {'front': textures['right'], 'back': textures['right']}

        # Floor and Ceiling (unchanged)
        floor = self._create_box(
            [inner_mins[0] - thickness, inner_mins[1] - thickness, inner_mins[2] - thickness],
            [inner_maxs[0] + thickness, inner_maxs[1] + thickness, inner_mins[2]],
            floor_textures
        )
        walls.append(floor)
        ceiling = self._create_box(
            [inner_mins[0] - thickness, inner_mins[1] - thickness, inner_maxs[2]],
            [inner_maxs[0] + thickness, inner_maxs[1] + thickness, inner_maxs[2] + thickness],
            ceiling_textures
        )
        walls.append(ceiling)

        # Helper function to create wall segments around doorways
        def create_wall_with_doorways(wall_type, mins, maxs, textures, doorway_list):
            if not doorway_list:
                return [self._create_box(mins, maxs, textures)]
            segments = []
            if wall_type in ['left', 'right']:
                # Sort doorways by y_min
                doorway_list.sort(key=lambda d: d['y_min'])
                y_start = inner_mins[1]
                for doorway in doorway_list:
                    y_end = doorway['y_min']
                    if y_end > y_start:
                        segments.append(self._create_box(
                            [mins[0], y_start, mins[2]],
                            [maxs[0], y_end, maxs[2]],
                            textures
                        ))
                    y_start = doorway['y_max']
                if y_start < inner_maxs[1]:
                    segments.append(self._create_box(
                        [mins[0], y_start, mins[2]],
                        [maxs[0], inner_maxs[1], maxs[2]],
                        textures
                    ))
            elif wall_type in ['front', 'back']:
                # Sort doorways by x_min
                doorway_list.sort(key=lambda d: d['x_min'])
                x_start = inner_mins[0]
                for doorway in doorway_list:
                    x_end = doorway['x_min']
                    if x_end > x_start:
                        segments.append(self._create_box(
                            [x_start, mins[1], mins[2]],
                            [x_end, maxs[1], maxs[2]],
                            textures
                        ))
                    x_start = doorway['x_max']
                if x_start < inner_maxs[0]:
                    segments.append(self._create_box(
                        [x_start, mins[1], mins[2]],
                        [inner_maxs[0], maxs[1], maxs[2]],
                        textures
                    ))
            return segments

        # Create walls with doorways
        # Front wall (Y-)
        front_wall_segments = create_wall_with_doorways(
            'front',
            [inner_mins[0] - thickness, inner_mins[1] - thickness, inner_mins[2]],
            [inner_maxs[0] + thickness, inner_mins[1], inner_maxs[2]],
            front_wall_textures,
            doorways['front']
        )
        walls.extend(front_wall_segments)

        # Back wall (Y+)
        back_wall_segments = create_wall_with_doorways(
            'back',
            [inner_mins[0] - thickness, inner_maxs[1], inner_mins[2]],
            [inner_maxs[0] + thickness, inner_maxs[1] + thickness, inner_maxs[2]],
            back_wall_textures,
            doorways['back']
        )
        walls.extend(back_wall_segments)

        # Left wall (X-)
        left_wall_segments = create_wall_with_doorways(
            'left',
            [inner_mins[0] - thickness, inner_mins[1], inner_mins[2]],
            [inner_mins[0], inner_maxs[1], inner_maxs[2]],
            left_wall_textures,
            doorways['left']
        )
        walls.extend(left_wall_segments)

        # Right wall (X+)
        right_wall_segments = create_wall_with_doorways(
            'right',
            [inner_maxs[0], inner_mins[1], inner_mins[2]],
            [inner_maxs[0] + thickness, inner_maxs[1], inner_maxs[2]],
            right_wall_textures,
            doorways['right']
        )
        walls.extend(right_wall_segments)

        self.solids.extend(walls)
        return {
            'mins': inner_mins,
            'maxs': inner_maxs,
            'center': [
                (inner_mins[0] + inner_maxs[0]) / 2,
                (inner_mins[1] + inner_maxs[1]) / 2,
                (inner_mins[2] + inner_maxs[2]) / 2
            ]
        }

    def add_corridor(self, room1, room2, width=96, height=128, textures=None):
        """
        Adds a corridor connecting two rooms, aligned with their doorways.
        
        Args:
            room1 (dict): First room's data (mins, maxs, center)
            room2 (dict): Second room's data
            width (float): Width of the corridor
            height (float): Height of the corridor
            textures (dict): Textures for the corridor
        """
        if textures is None:
            textures = {
                'bottom': self.textures['floor'],
                'top': self.textures['ceiling'],
                'wall': self.textures['wall']
            }

        c1 = room1['center']
        c2 = room2['center']
        dx = abs(c2[0] - c1[0])
        dy = abs(c2[1] - c1[1])
        thickness = 16
        corridor_walls = []

        if dx > dy:  # X-axis corridor
            # Determine which room is on the left
            if c1[0] < c2[0]:
                left_room = room1
                right_room = room2
            else:
                left_room = room2
                right_room = room1

            # Calculate overlapping Y range
            y_min = max(left_room['mins'][1], right_room['mins'][1])
            y_max = min(left_room['maxs'][1], right_room['maxs'][1])
            if y_max - y_min < width:
                width = y_max - y_min  # Adjust width if overlap is too small
            corridor_y = (y_min + y_max) / 2

            corridor_mins = [
                left_room['maxs'][0],
                corridor_y - width / 2,
                min(room1['mins'][2], room2['mins'][2])
            ]
            corridor_maxs = [
                right_room['mins'][0],
                corridor_y + width / 2,
                min(room1['mins'][2], room2['mins'][2]) + height
            ]
        else:  # Y-axis corridor
            # Determine which room is on the bottom
            if c1[1] < c2[1]:
                bottom_room = room1
                top_room = room2
            else:
                bottom_room = room2
                top_room = room1

            # Calculate overlapping X range
            x_min = max(bottom_room['mins'][0], top_room['mins'][0])
            x_max = min(bottom_room['maxs'][0], top_room['maxs'][0])
            if x_max - x_min < width:
                width = x_max - x_min  # Adjust width if overlap is too small
            corridor_x = (x_min + x_max) / 2

            corridor_mins = [
                corridor_x - width / 2,
                bottom_room['maxs'][1],
                min(room1['mins'][2], room2['mins'][2])
            ]
            corridor_maxs = [
                corridor_x + width / 2,
                top_room['mins'][1],
                min(room1['mins'][2], room2['mins'][2]) + height
            ]

        # Create corridor brushes
        floor = self._create_box(
            [corridor_mins[0], corridor_mins[1], corridor_mins[2] - thickness],
            [corridor_maxs[0], corridor_maxs[1], corridor_mins[2]],
            {'top': textures['bottom'], 'bottom': textures['bottom']}
        )
        corridor_walls.append(floor)

        ceiling = self._create_box(
            [corridor_mins[0], corridor_mins[1], corridor_maxs[2]],
            [corridor_maxs[0], corridor_maxs[1], corridor_maxs[2] + thickness],
            {'top': textures['top'], 'bottom': textures['top']}
        )
        corridor_walls.append(ceiling)

        if dx > dy:  # X-axis corridor walls
            north_wall = self._create_box(
                [corridor_mins[0], corridor_maxs[1], corridor_mins[2]],
                [corridor_maxs[0], corridor_maxs[1] + thickness, corridor_maxs[2]],
                {'front': textures['wall'], 'back': textures['wall']}
            )
            corridor_walls.append(north_wall)

            south_wall = self._create_box(
                [corridor_mins[0], corridor_mins[1] - thickness, corridor_mins[2]],
                [corridor_maxs[0], corridor_mins[1], corridor_maxs[2]],
                {'front': textures['wall'], 'back': textures['wall']}
            )
            corridor_walls.append(south_wall)
        else:  # Y-axis corridor walls
            east_wall = self._create_box(
                [corridor_maxs[0], corridor_mins[1], corridor_mins[2]],
                [corridor_maxs[0] + thickness, corridor_maxs[1], corridor_maxs[2]],
                {'front': textures['wall'], 'back': textures['wall']}
            )
            corridor_walls.append(east_wall)

            west_wall = self._create_box(
                [corridor_mins[0] - thickness, corridor_mins[1], corridor_mins[2]],
                [corridor_mins[0], corridor_maxs[1], corridor_maxs[2]],
                {'front': textures['wall'], 'back': textures['wall']}
            )
            corridor_walls.append(west_wall)

        self.solids.extend(corridor_walls)
        return {
            'mins': corridor_mins,
            'maxs': corridor_maxs,
            'center': [
                (corridor_mins[0] + corridor_maxs[0]) / 2,
                (corridor_mins[1] + corridor_maxs[1]) / 2,
                (corridor_mins[2] + corridor_maxs[2]) / 2
            ]
        }

    def create_simple_room_scenario(self, room_count=3, connect_all=True):
        """
        Creates a scenario with rooms in a circular pattern, connected by corridors with doorways.
        
        Args:
            room_count (int): Number of rooms to generate
            connect_all (bool): Whether to connect all rooms in a loop
        """
        rooms = []
        base_room_size = [512, 512, 256]  # Can increase to ensure overlap if needed
        base_position = [0, 0, 64]

        # Step 1: Plan room positions and sizes
        planned_positions = []
        planned_sizes = []
        planned_mins = []
        planned_maxs = []
        planned_centers = []
        for i in range(room_count):
            angle = (2 * math.pi * i) / room_count
            distance = 1024
            pos_x = base_position[0] + distance * math.cos(angle)
            pos_y = base_position[1] + distance * math.sin(angle)
            size_factor = random.uniform(0.8, 1.2)
            room_size = [
                base_room_size[0] * size_factor,
                base_room_size[1] * size_factor,
                base_room_size[2]
            ]
            planned_positions.append([pos_x, pos_y, base_position[2]])
            planned_sizes.append(room_size)
            mins = [pos_x, pos_y, base_position[2]]
            maxs = [pos_x + room_size[0], pos_y + room_size[1], base_position[2] + room_size[2]]
            planned_mins.append(mins)
            planned_maxs.append(maxs)
            center = [(mins[0] + maxs[0])/2, (mins[1] + maxs[1])/2, (mins[2] + maxs[2])/2]
            planned_centers.append(center)

        # Step 2: Calculate doorways for each room based on corridor connections
        room_doorways = [{'left': [], 'right': [], 'front': [], 'back': []} for _ in range(room_count)]
        if connect_all and room_count > 1:
            for i in range(room_count):
                j = (i + 1) % room_count
                c1 = planned_centers[i]
                c2 = planned_centers[j]
                dx = abs(c2[0] - c1[0])
                dy = abs(c2[1] - c1[1])
                width = random.uniform(80, 120)
                height = random.uniform(120, 160)

                if dx > dy:  # X-axis corridor
                    y_overlap_min = max(planned_mins[i][1], planned_mins[j][1])
                    y_overlap_max = min(planned_maxs[i][1], planned_maxs[j][1])
                    if y_overlap_max <= y_overlap_min:
                        print(f"Warning: No Y overlap between rooms {i} and {j}; adjusting corridor placement")
                        corridor_y = (planned_centers[i][1] + planned_centers[j][1]) / 2
                    else:
                        corridor_y = (y_overlap_min + y_overlap_max) / 2
                        if y_overlap_max - y_overlap_min < width:
                            width = y_overlap_max - y_overlap_min
                    doorway_y_min = corridor_y - width / 2
                    doorway_y_max = corridor_y + width / 2
                    if c2[0] > c1[0]:
                        room_doorways[i]['right'].append({'y_min': doorway_y_min, 'y_max': doorway_y_max})
                        room_doorways[j]['left'].append({'y_min': doorway_y_min, 'y_max': doorway_y_max})
                    else:
                        room_doorways[i]['left'].append({'y_min': doorway_y_min, 'y_max': doorway_y_max})
                        room_doorways[j]['right'].append({'y_min': doorway_y_min, 'y_max': doorway_y_max})
                else:  # Y-axis corridor
                    x_overlap_min = max(planned_mins[i][0], planned_mins[j][0])
                    x_overlap_max = min(planned_maxs[i][0], planned_maxs[j][0])
                    if x_overlap_max <= x_overlap_min:
                        print(f"Warning: No X overlap between rooms {i} and {j}; adjusting corridor placement")
                        corridor_x = (planned_centers[i][0] + planned_centers[j][0]) / 2
                    else:
                        corridor_x = (x_overlap_min + x_overlap_max) / 2
                        if x_overlap_max - x_overlap_min < width:
                            width = x_overlap_max - x_overlap_min
                    doorway_x_min = corridor_x - width / 2
                    doorway_x_max = corridor_x + width / 2
                    if c2[1] > c1[1]:
                        room_doorways[i]['back'].append({'x_min': doorway_x_min, 'x_max': doorway_x_max})
                        room_doorways[j]['front'].append({'x_min': doorway_x_min, 'x_max': doorway_x_max})
                    else:
                        room_doorways[i]['front'].append({'x_min': doorway_x_min, 'x_max': doorway_x_max})
                        room_doorways[j]['back'].append({'x_min': doorway_x_min, 'x_max': doorway_x_max})

        # Step 3: Add rooms with their calculated doorways
        for i in range(room_count):
            textures = {
                'bottom': random.choice([self.textures['floor'], self.textures['concrete'], self.textures['dirt']]),
                'top': random.choice([self.textures['ceiling'], self.textures['concrete']]),
                'front': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete'], self.textures['metal']]),
                'back': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete'], self.textures['metal']]),
                'left': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete'], self.textures['metal']]),
                'right': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete'], self.textures['metal']])
            }
            room = self.add_room(planned_positions[i], planned_sizes[i], textures, doorways=room_doorways[i])
            rooms.append(room)

            # Add lights and items (unchanged)
            self.add_light([room['center'][0], room['center'][1], room['center'][2] + 100], brightness=300, color=(255, 255, 200))
            if random.random() > 0.5:
                self.add_health([room['center'][0] + random.uniform(-100, 100), room['center'][1] + random.uniform(-100, 100), room['center'][2] + 16])
            if random.random() > 0.5:
                self.add_ammo([room['center'][0] + random.uniform(-100, 100), room['center'][1] + random.uniform(-100, 100), room['center'][2] + 16])
            if random.random() > 0.7:
                self.add_npc([room['center'][0] + random.uniform(-100, 100), room['center'][1] + random.uniform(-100, 100), room['center'][2] + 16])

        # Step 4: Add corridors between rooms
        if connect_all and len(rooms) > 1:
            for i in range(len(rooms)):
                next_room = (i + 1) % len(rooms)
                corridor_width = random.uniform(80, 120)
                corridor_height = random.uniform(120, 160)
                corridor_textures = {
                    'bottom': random.choice([self.textures['floor'], self.textures['concrete']]),
                    'top': random.choice([self.textures['ceiling'], self.textures['concrete']]),
                    'wall': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete']])
                }
                self.add_corridor(rooms[i], rooms[next_room], width=corridor_width, height=corridor_height, textures=corridor_textures)

        # Step 5: Add player start
        if rooms:
            self.add_player_start([rooms[0]['center'][0], rooms[0]['center'][1], rooms[0]['mins'][2] + 32])

        return rooms

    def add_light(self, position, brightness=200, color=(255, 255, 255)):
        # Unchanged
        entity = "entity\n{\n"
        entity += "\"id\" \"{}\"\n".format(len(self.entities) + 1)
        entity += "\"classname\" \"light\"\n"
        entity += "\"origin\" \"{} {} {}\"\n".format(position[0], position[1], position[2])
        entity += "\"_light\" \"{} {} {} {}\"\n".format(color[0], color[1], color[2], brightness)
        entity += "}\n"
        self.entities.append(entity)

    def add_player_start(self, position):
        # Unchanged
        entity = "entity\n{\n"
        entity += "\"id\" \"{}\"\n".format(len(self.entities) + 1)
        entity += "\"classname\" \"info_player_start\"\n"
        entity += "\"origin\" \"{} {} {}\"\n".format(position[0], position[1], position[2])
        entity += "\"angles\" \"0 0 0\"\n"
        entity += "}\n"
        self.entities.append(entity)

    def add_health(self, position):
        # Unchanged
        entity = "entity\n{\n"
        entity += "\"id\" \"{}\"\n".format(len(self.entities) + 1)
        entity += "\"classname\" \"item_healthkit\"\n"
        entity += "\"origin\" \"{} {} {}\"\n".format(position[0], position[1], position[2])
        entity += "}\n"
        self.entities.append(entity)

    def add_ammo(self, position):
        # Unchanged
        entity = "entity\n{\n"
        entity += "\"id\" \"{}\"\n".format(len(self.entities) + 1)
        entity += "\"classname\" \"item_ammopack\"\n"
        entity += "\"origin\" \"{} {} {}\"\n".format(position[0], position[1], position[2])
        entity += "}\n"
        self.entities.append(entity)

    def add_npc(self, position):
        # Unchanged
        entity = "entity\n{\n"
        entity += "\"id\" \"{}\"\n".format(len(self.entities) + 1)
        entity += "\"classname\" \"npc_zombie\"\n"
        entity += "\"origin\" \"{} {} {}\"\n".format(position[0], position[1], position[2])
        entity += "\"angles\" \"0 {} 0\"\n".format(random.randint(0, 360))
        entity += "}\n"
        self.entities.append(entity)

    def generate_map(self, filename="output.map"):
        # Unchanged
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
            for solid in self.solids:
                f.write(solid)
            f.write("}\n")
            for entity in self.entities:
                f.write(entity)

# Example usage
if __name__ == "__main__":
    generator = SourceMapGenerator()
    generator.create_simple_room_scenario(room_count=3, connect_all=True)
    generator.generate_map("simple_map.map")
