import os
import argparse
import random
import math
from datetime import datetime

class SourceMapGenerator:
    def __init__(self):
        self.next_id = 1
        self.entities = []
        self.solids = []
        self.visgroups = []
        self.cameras = []
        self.cordon = {}
        self.active_visgroup = 0
        self.map_name = "generated_map"
        self.optimization_level = "standard"  # standard, high, extreme
        
        # Default textures
        self.textures = {
            'wall': 'DEV/DEV_MEASUREWALL01A',
            'floor': 'DEV/DEV_MEASUREFLOOR01A',
            'ceiling': 'DEV/DEV_MEASURECEILHT01A',
            'sky': 'TOOLS/TOOLSSKYBOX',
            'metal': 'METAL/METALWALL048A',
            'concrete': 'CONCRETE/CONCRETEWALL001A',
            'wood': 'WOOD/WOODWALL001A',
            'brick': 'BRICK/BRICKWALL001A',
            'glass': 'GLASS/GLASSWINDOW001A',
            'dirt': 'NATURE/DIRTFLOOR001A',
            'grass': 'NATURE/GRASSFLOOR001A',
            'water': 'NATURE/WATERFLOOR001A',
            'nodraw': 'TOOLS/TOOLSNODRAW',
            'hint': 'TOOLS/TOOLSHINT',
            'skip': 'TOOLS/TOOLSSKIP',
            'null': 'TOOLS/TOOLSNULL'
        }
        
        # Default entities
        self.entity_templates = {
            'light': self._create_light_template,
            'player_start': self._create_player_start_template,
            'npc_spawn': self._create_npc_spawn_template,
            'item_spawn': self._create_item_spawn_template,
            'trigger': self._create_trigger_template,
            'button': self._create_button_template,
            'door': self._create_door_template,
            'healthkit': self._create_health_template,
            'ammobox': self._create_ammo_template
        }
    
    def save_vmf(self, filename):
        """Save the map to a VMF file."""
        with open(filename, 'w') as f:
            # Write file header
            f.write('versioninfo\n{\n\t"editorversion" "400"\n\t"editorbuild" "8864"\n\t"mapversion" "1"\n')
            f.write('\t"formatversion" "100"\n\t"prefab" "0"\n}\n')
            
            # Write visgroups
            f.write('visgroups\n{\n}\n')
            
            # Write viewsettings
            f.write('viewsettings\n{\n\t"bSnapToGrid" "1"\n\t"bShowGrid" "1"\n\t"bShowLogicalGrid" "0"\n')
            f.write('\t"nGridSpacing" "64"\n\t"bShow3DGrid" "0"\n}\n')
            
            # Write world entity
            f.write('world\n{\n\t"id" "1"\n\t"mapversion" "1"\n\t"classname" "worldspawn"\n')
            f.write('\t"skyname" "sky_day01_01"\n\t"sounds" "1"\n\t"MaxRange" "4096"\n')
            
            # Add optimization entities if needed
            if self.optimization_level in ["high", "extreme"]:
                f.write('\t"detailmaterial" "detail/detailsprites"\n\t"detailvbsp" "detail.vbsp"\n')
                
                if self.optimization_level == "extreme":
                    f.write('\t"vrad_brush_cast_shadows" "1"\n\t"vrad_patch_shadows" "1"\n')
                    f.write('\t"vrad_patch_emitlight" "1"\n\t"vrad_force_non_rad" "1"\n')
                    f.write('\t"_light_env_maxdist" "2000"\n\t"_light_maxs" "1500"\n')
            
            # Write solids
            for solid in self.solids:
                f.write('\tsolid\n\t{\n\t\t"id" "' + str(solid['id']) + '"\n')
                
                # Write sides (faces)
                for side in solid['sides']:
                    f.write('\t\tside\n\t\t{\n\t\t\t"id" "' + str(side['id']) + '"\n')
                    f.write('\t\t\t"plane" "' + side['plane'] + '"\n')
                    f.write('\t\t\t"material" "' + side['material'] + '"\n')
                    f.write('\t\t\t"uaxis" "' + side['uaxis'] + '"\n')
                    f.write('\t\t\t"vaxis" "' + side['vaxis'] + '"\n')
                    f.write('\t\t\t"rotation" "' + side['rotation'] + '"\n')
                    f.write('\t\t\t"lightmapscale" "' + side['lightmapscale'] + '"\n')
                    f.write('\t\t\t"smoothing_groups" "' + side['smoothing_groups'] + '"\n')
                    f.write('\t\t}\n')
                
                f.write('\t}\n')
            
            f.write('}\n')
            
            # Write entities
            for entity in self.entities:
                if entity['id'] == 1:  # Skip worldspawn, already written
                    continue
                    
                f.write('entity\n{\n\t"id" "' + str(entity['id']) + '"\n')
                
                # Write entity properties
                for key, value in entity.items():
                    if key != 'id':  # Skip ID, already written
                        f.write('\t"' + key + '" "' + value + '"\n')
                
                f.write('}\n')
            
            # Write cameras
            for camera in self.cameras:
                f.write('cameras\n{\n\t"activecamera" "-1"\n}\n')
            
            # Write cordon
            f.write('cordon\n{\n\t"mins" "(-1024 -1024 -1024)"\n\t"maxs" "(1024 1024 1024)"\n')
            f.write('\t"active" "0"\n}\n')
        
    def _get_next_id(self):
        """Get the next available ID and increment the counter."""
        id_val = self.next_id
        self.next_id += 1
        return id_val
    
    def _create_light_template(self, position, brightness=300, color=(255, 255, 255)):
        """Create a light entity template."""
        light = {
            'id': self._get_next_id(),
            'classname': 'light',
            'origin': f"{position[0]} {position[1]} {position[2]}",
            '_light': f"{color[0]} {color[1]} {color[2]} {brightness}",
            'style': '0',
            'pattern': '',
            'falloff': '0'
        }
        return light
    
    def _create_player_start_template(self, position, angles=(0, 0, 0)):
        """Create a player start entity template."""
        start = {
            'id': self._get_next_id(),
            'classname': 'info_player_start',
            'origin': f"{position[0]} {position[1]} {position[2]}",
            'angles': f"{angles[0]} {angles[1]} {angles[2]}"
        }
        return start
    
    def _create_npc_spawn_template(self, position, npc_type='npc_combine_s'):
        """Create an NPC spawn entity template."""
        npc = {
            'id': self._get_next_id(),
            'classname': npc_type,
            'origin': f"{position[0]} {position[1]} {position[2]}",
            'spawnflags': '0'
        }
        return npc
    
    def _create_item_spawn_template(self, position, item_type='item_healthkit'):
        """Create an item spawn entity template."""
        item = {
            'id': self._get_next_id(),
            'classname': item_type,
            'origin': f"{position[0]} {position[1]} {position[2]}",
            'spawnflags': '0'
        }
        return item
    
    def _create_trigger_template(self, mins, maxs, output_target=None):
        """Create a trigger entity template."""
        trigger = {
            'id': self._get_next_id(),
            'classname': 'trigger_multiple',
            'mins': f"{mins[0]} {mins[1]} {mins[2]}",
            'maxs': f"{maxs[0]} {maxs[1]} {maxs[2]}",
            'spawnflags': '1',
            'wait': '1'
        }
        
        if output_target:
            trigger['OnTrigger'] = f"{output_target['targetname']},{output_target['input']},,"
        
        return trigger
    
    def _create_button_template(self, position, size=(16, 16, 8), output_target=None):
        """Create a button entity template."""
        button = {
            'id': self._get_next_id(),
            'classname': 'func_button',
            'origin': f"{position[0]} {position[1]} {position[2]}",
            'mins': f"{-size[0]/2} {-size[1]/2} {-size[2]/2}",
            'maxs': f"{size[0]/2} {size[1]/2} {size[2]/2}",
            'spawnflags': '1',
            'wait': '1',
            'speed': '5',
            'targetname': f"button_{self._get_next_id()}"
        }
        
        if output_target:
            button['OnPressed'] = f"{output_target['targetname']},{output_target['input']},,"
        
        return button
    
    def _create_door_template(self, position, size=(64, 4, 128), angles=(0, 0, 0)):
        """Create a door entity template."""
        door = {
            'id': self._get_next_id(),
            'classname': 'func_door',
            'origin': f"{position[0]} {position[1]} {position[2]}",
            'mins': f"{-size[0]/2} {-size[1]/2} {-size[2]/2}",
            'maxs': f"{size[0]/2} {size[1]/2} {size[2]/2}",
            'angles': f"{angles[0]} {angles[1]} {angles[2]}",
            'spawnflags': '0',
            'speed': '100',
            'wait': '4',
            'lip': '8',
            'targetname': f"door_{self._get_next_id()}"
        }
        return door
    
    def _create_health_template(self, position):
        """Create a health kit entity template."""
        health = {
            'id': self._get_next_id(),
            'classname': 'item_healthkit',
            'origin': f"{position[0]} {position[1]} {position[2]}",
            'spawnflags': '0'
        }
        return health
    
    def _create_ammo_template(self, position):
        """Create an ammo box entity template."""
        ammo = {
            'id': self._get_next_id(),
            'classname': 'item_ammo_pistol',
            'origin': f"{position[0]} {position[1]} {position[2]}",
            'spawnflags': '0'
        }
        return ammo
    
    def _create_vertex(self, x, y, z):
        """Create a vertex at the given coordinates."""
        return f"({x} {y} {z})"
    
    def _create_face(self, vertices, texture, u_axis, v_axis, rotation=0, u_scale=0.25, v_scale=0.25):
        """Create a face with the given vertices and texture."""
        face = {
            'id': self._get_next_id(),
            'plane': ' '.join(vertices),
            'material': texture,
            'uaxis': f"[{u_axis[0]} {u_axis[1]} {u_axis[2]} 0] {u_scale}",
            'vaxis': f"[{v_axis[0]} {v_axis[1]} {v_axis[2]} 0] {v_scale}",
            'rotation': str(rotation),
            'lightmapscale': '16',
            'smoothing_groups': '0'
        }
        return face
    
    def _create_box(self, mins, maxs, textures):
        """Create a cube (brush) with the given dimensions and textures."""
        box_id = self._get_next_id()
        
        # Extract coordinates
        x1, y1, z1 = mins
        x2, y2, z2 = maxs
        
        # Create 8 vertices for the cube
        v = [
            self._create_vertex(x1, y1, z1),  # bottom face
            self._create_vertex(x2, y1, z1),
            self._create_vertex(x2, y2, z1),
            self._create_vertex(x1, y2, z1),
            self._create_vertex(x1, y1, z2),  # top face
            self._create_vertex(x2, y1, z2),
            self._create_vertex(x2, y2, z2),
            self._create_vertex(x1, y2, z2)
        ]
        
        # Create 6 faces of the cube
        faces = [
            # Bottom face (floor)
            self._create_face([v[0], v[1], v[2], v[3]], textures.get('bottom', self.textures['floor']), 
                             [1, 0, 0], [0, -1, 0]),
            # Top face (ceiling)
            self._create_face([v[7], v[6], v[5], v[4]], textures.get('top', self.textures['ceiling']), 
                             [1, 0, 0], [0, -1, 0]),
            # Front face
            self._create_face([v[4], v[5], v[1], v[0]], textures.get('front', self.textures['wall']), 
                             [1, 0, 0], [0, 0, -1]),
            # Back face
            self._create_face([v[3], v[2], v[6], v[7]], textures.get('back', self.textures['wall']), 
                             [1, 0, 0], [0, 0, -1]),
            # Left face
            self._create_face([v[0], v[3], v[7], v[4]], textures.get('left', self.textures['wall']), 
                             [0, 1, 0], [0, 0, -1]),
            # Right face
            self._create_face([v[5], v[6], v[2], v[1]], textures.get('right', self.textures['wall']), 
                             [0, 1, 0], [0, 0, -1])
        ]
        
        # Create solid (brush)
        solid = {
            'id': box_id,
            'sides': faces
        }
        
        return solid
    
    def add_room(self, position, size, textures=None):
        """Add a room to the map."""
        if textures is None:
            textures = {
                'bottom': self.textures['floor'],
                'top': self.textures['ceiling'],
                'front': self.textures['wall'],
                'back': self.textures['wall'],
                'left': self.textures['wall'],
                'right': self.textures['wall']
            }
        
        x, y, z = position
        width, length, height = size
        
        # Calculate inner dimensions
        inner_mins = [x, y, z]
        inner_maxs = [x + width, y + length, z + height]
        
        # Wall thickness
        thickness = 16
        
        # Create outer walls (4 walls, floor and ceiling)
        walls = []
        
        # Apply optimization - use nodraw texture for faces that aren't visible
        if self.optimization_level in ["high", "extreme"]:
            # Floor - top face visible, bottom face invisible
            floor_textures = {
                'top': textures['bottom'],
                'bottom': self.textures['nodraw'],
                'front': self.textures['nodraw'],
                'back': self.textures['nodraw'],
                'left': self.textures['nodraw'],
                'right': self.textures['nodraw']
            }
            
            # Ceiling - bottom face visible, top face invisible
            ceiling_textures = {
                'top': self.textures['nodraw'],
                'bottom': textures['top'],
                'front': self.textures['nodraw'],
                'back': self.textures['nodraw'],
                'left': self.textures['nodraw'],
                'right': self.textures['nodraw']
            }
            
            # Wall textures - only inner faces visible
            front_wall_textures = {
                'top': self.textures['nodraw'],
                'bottom': self.textures['nodraw'],
                'front': self.textures['nodraw'],
                'back': textures['front'],
                'left': self.textures['nodraw'],
                'right': self.textures['nodraw']
            }
            
            back_wall_textures = {
                'top': self.textures['nodraw'],
                'bottom': self.textures['nodraw'],
                'front': textures['back'],
                'back': self.textures['nodraw'],
                'left': self.textures['nodraw'],
                'right': self.textures['nodraw']
            }
            
            left_wall_textures = {
                'top': self.textures['nodraw'],
                'bottom': self.textures['nodraw'],
                'front': self.textures['nodraw'],
                'back': self.textures['nodraw'],
                'left': self.textures['nodraw'],
                'right': textures['left']
            }
            
            right_wall_textures = {
                'top': self.textures['nodraw'],
                'bottom': self.textures['nodraw'],
                'front': self.textures['nodraw'],
                'back': self.textures['nodraw'],
                'left': textures['right'],
                'right': self.textures['nodraw']
            }
        else:
            # Standard optimization - use the same texture for all faces
            floor_textures = {'top': textures['bottom'], 'bottom': textures['bottom']}
            ceiling_textures = {'top': textures['top'], 'bottom': textures['top']}
            front_wall_textures = {'front': textures['front'], 'back': textures['front']}
            back_wall_textures = {'front': textures['back'], 'back': textures['back']}
            left_wall_textures = {'front': textures['left'], 'back': textures['left']}
            right_wall_textures = {'front': textures['right'], 'back': textures['right']}
        
        # Floor
        floor = self._create_box(
            [inner_mins[0] - thickness, inner_mins[1] - thickness, inner_mins[2] - thickness],
            [inner_maxs[0] + thickness, inner_maxs[1] + thickness, inner_mins[2]],
            floor_textures
        )
        walls.append(floor)
        
        # Ceiling
        ceiling = self._create_box(
            [inner_mins[0] - thickness, inner_mins[1] - thickness, inner_maxs[2]],
            [inner_maxs[0] + thickness, inner_maxs[1] + thickness, inner_maxs[2] + thickness],
            ceiling_textures
        )
        walls.append(ceiling)
        
        # Front wall (Y-)
        front_wall = self._create_box(
            [inner_mins[0] - thickness, inner_mins[1] - thickness, inner_mins[2]],
            [inner_maxs[0] + thickness, inner_mins[1], inner_maxs[2]],
            front_wall_textures
        )
        walls.append(front_wall)
        
        # Back wall (Y+)
        back_wall = self._create_box(
            [inner_mins[0] - thickness, inner_maxs[1], inner_mins[2]],
            [inner_maxs[0] + thickness, inner_maxs[1] + thickness, inner_maxs[2]],
            back_wall_textures
        )
        walls.append(back_wall)
        
        # Left wall (X-)
        left_wall = self._create_box(
            [inner_mins[0] - thickness, inner_mins[1], inner_mins[2]],
            [inner_mins[0], inner_maxs[1], inner_maxs[2]],
            left_wall_textures
        )
        walls.append(left_wall)
        
        # Right wall (X+)
        right_wall = self._create_box(
            [inner_maxs[0], inner_mins[1], inner_mins[2]],
            [inner_maxs[0] + thickness, inner_maxs[1], inner_maxs[2]],
            right_wall_textures
        )
        walls.append(right_wall)
        
        # Add hint brushes for visibility optimization
        if self.optimization_level == "extreme":
            # Add hint brushes at strategic locations
            hint_thickness = 1
            
            # Horizontal hint brush in the middle of the room
            hint_h = self._create_box(
                [inner_mins[0], inner_mins[1] + length/2 - hint_thickness/2, inner_mins[2]],
                [inner_maxs[0], inner_mins[1] + length/2 + hint_thickness/2, inner_maxs[2]],
                {'front': self.textures['hint'], 'back': self.textures['hint']}
            )
            walls.append(hint_h)
            
            # Vertical hint brush in the middle of the room
            hint_v = self._create_box(
                [inner_mins[0] + width/2 - hint_thickness/2, inner_mins[1], inner_mins[2]],
                [inner_mins[0] + width/2 + hint_thickness/2, inner_maxs[1], inner_maxs[2]],
                {'front': self.textures['hint'], 'back': self.textures['hint']}
            )
            walls.append(hint_v)
        
        # Add all walls to the solids list
        self.solids.extend(walls)
        
        # Return the inner dimensions of the room
        return {
            'mins': inner_mins,
            'maxs': inner_maxs,
            'center': [
                (inner_mins[0] + inner_maxs[0]) / 2,
                (inner_mins[1] + inner_maxs[1]) / 2,
                (inner_mins[2] + inner_maxs[2]) / 2
            ]
        }
    
    def add_window(self, wall_face, position, size=(64, 64), texture=None):
        """Add a window to a wall."""
        if texture is None:
            texture = self.textures['glass']
        
        # Create window brush
        window = self._create_box(
            [position[0] - size[0] / 2, position[1] - 4, position[2] - size[1] / 2],
            [position[0] + size[0] / 2, position[1] + 4, position[2] + size[1] / 2],
            {'front': texture, 'back': texture, 'top': texture, 'bottom': texture, 'left': texture, 'right': texture}
        )
        
        self.solids.append(window)
    
    def add_door(self, position, size=(64, 4, 128), angles=(0, 0, 0)):
        """Add a door entity to the map."""
        door = self.entity_templates['door'](position, size, angles)
        
        self.entities.append(door)
    
    def add_light(self, position, brightness=300, color=(255, 255, 255)):
        """Add a light entity to the map."""
        light = self.entity_templates['light'](position, brightness, color)
        
        self.entities.append(light)
    
    def add_player_start(self, position, angles=(0, 0, 0)):
        """Add a player start entity to the map."""
        player_start = self.entity_templates['player_start'](position, angles)
        
        self.entities.append(player_start)
    
    def add_npc(self, position, npc_type='npc_combine_s'):
        """Add an NPC entity to the map."""
        npc = self.entity_templates['npc_spawn'](position, npc_type)
        
        self.entities.append(npc)
    
    def add_health(self, position):
        """Add a health kit to the map."""
        health = self.entity_templates['healthkit'](position)
        
        self.entities.append(health)
    
    def add_ammo(self, position):
        """Add an ammo box to the map."""
        ammo = self.entity_templates['ammobox'](position)
        
        self.entities.append(ammo)
    
    def add_worldspawn(self):
        """Add the worldspawn entity to the map."""
        worldspawn = {
            'id': 1,
            'classname': 'worldspawn',
            'mapversion': '1',
            'sounds': '1',
            'MaxRange': '4096',
            'skyname': 'sky_day01_01'
        }
        
        # Add optimization entities for high and extreme optimization levels
        if self.optimization_level in ["high", "extreme"]:
            worldspawn['detailmaterial'] = 'detail/detailsprites'
            worldspawn['detailvbsp'] = 'detail.vbsp'
            
            # Settings for better visibility optimization
            if self.optimization_level == "extreme":
                # These settings help with visibility and compile times
                worldspawn['vrad_brush_cast_shadows'] = '1'
                worldspawn['vrad_patch_shadows'] = '1'
                worldspawn['vrad_patch_emitlight'] = '1'
                worldspawn['vrad_force_non_rad'] = '1'
                worldspawn['_light_env_maxdist'] = '2000'
                worldspawn['_light_maxs'] = '1500'
        
        self.entities.append(worldspawn)
    
    def create_simple_room_scenario(self, room_count=3, connect_all=True):
        """Create a simple scenario with multiple rooms connected by corridors in a grid pattern."""
        rooms = []
        base_room_size = [512, 512, 256]  # width, length, height
        base_position = [0, 0, 64]  # starting position
        spacing = max(base_room_size[0], base_room_size[1]) * 2  # Space between room centers
        
        # Calculate grid dimensions (roughly square)
        grid_size = math.ceil(math.sqrt(room_count))
        
        # Create rooms in a grid
        room_positions = []
        for i in range(min(room_count, grid_size * grid_size)):
            # Calculate row and column for this room
            row = i // grid_size
            col = i % grid_size
            
            # Calculate position for this room
            pos_x = int(base_position[0] + col * spacing)
            pos_y = int(base_position[1] + row * spacing)
            pos_z = base_position[2]
            
            # Store room position
            room_positions.append([pos_x, pos_y, pos_z])
            
            # Randomize room size slightly
            size_factor = random.uniform(0.8, 1.2)
            room_size = [
                int(base_room_size[0] * size_factor),
                int(base_room_size[1] * size_factor),
                base_room_size[2]
            ]
            
            # Randomize textures
            textures = {
                'bottom': random.choice([self.textures['floor'], self.textures['concrete'], self.textures['dirt']]),
                'top': random.choice([self.textures['ceiling'], self.textures['concrete']]),
                'front': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete'], self.textures['metal']]),
                'back': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete'], self.textures['metal']]),
                'left': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete'], self.textures['metal']]),
                'right': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete'], self.textures['metal']])
            }
            
            # Add room
            current_pos = room_positions[i]
            room = self.add_room([current_pos[0], current_pos[1], current_pos[2]], room_size, textures)
            rooms.append(room)
            
            # Add some lights
            self.add_light([
                room['center'][0],
                room['center'][1],
                room['center'][2] + 100
            ], brightness=300, color=(255, 255, 200))
            
            # Add some items
            if random.random() > 0.5:
                self.add_health([
                    room['center'][0] + random.uniform(-100, 100),
                    room['center'][1] + random.uniform(-100, 100),
                    room['center'][2] + 16
                ])
            
            if random.random() > 0.5:
                self.add_ammo([
                    room['center'][0] + random.uniform(-100, 100),
                    room['center'][1] + random.uniform(-100, 100),
                    room['center'][2] + 16
                ])
            
            # Add NPCs
            if random.random() > 0.7:
                self.add_npc([
                    room['center'][0] + random.uniform(-100, 100),
                    room['center'][1] + random.uniform(-100, 100),
                    room['center'][2] + 16
                ])
        
        # Connect rooms with corridors
        if connect_all and len(rooms) > 1:
            for i in range(len(rooms)):
                # Calculate row and column for this room
                row = i // grid_size
                col = i % grid_size
                
                # Connect to right neighbor (if it exists)
                if col < grid_size - 1 and i + 1 < len(rooms):
                    # Randomize corridor width slightly
                    corridor_width = random.uniform(80, 120)
                    corridor_height = random.uniform(120, 160)
                    
                    # Randomize textures
                    corridor_textures = {
                        'bottom': random.choice([self.textures['floor'], self.textures['concrete']]),
                        'top': random.choice([self.textures['ceiling'], self.textures['concrete']]),
                        'wall': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete']])
                    }
                    
                    self.add_corridor(rooms[i], rooms[i + 1], width=corridor_width, height=corridor_height, textures=corridor_textures)
                
                # Connect to bottom neighbor (if it exists)
                if row < grid_size - 1 and i + grid_size < len(rooms):
                    # Randomize corridor width slightly
                    corridor_width = random.uniform(80, 120)
                    corridor_height = random.uniform(120, 160)
                    
                    # Randomize textures
                    corridor_textures = {
                        'bottom': random.choice([self.textures['floor'], self.textures['concrete']]),
                        'top': random.choice([self.textures['ceiling'], self.textures['concrete']]),
                        'wall': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete']])
                    }
                    
                    self.add_corridor(rooms[i], rooms[i + grid_size], width=corridor_width, height=corridor_height, textures=corridor_textures)
        
        # Add player start to the first room
        if rooms:
            self.add_player_start([
                rooms[0]['center'][0],
                rooms[0]['center'][1],
                rooms[0]['mins'][2] + 32
            ])
        
        return rooms
    
    def create_arena_scenario(self, size=(2048, 2048, 512), npc_count=6):
        """Create a large arena for combat scenarios."""
        # Create a large open space
        arena_textures = {
            'bottom': self.textures['concrete'],
            'top': self.textures['sky'],
            'front': self.textures['brick'],
            'back': self.textures['brick'],
            'left': self.textures['brick'],
            'right': self.textures['brick']
        }
        
        arena = self.add_room([0, 0, 64], size, arena_textures)
        
        # Add some cover objects
        cover_count = random.randint(5, 10)
        for i in range(cover_count):
            angle = (2 * math.pi * i) / cover_count
            distance = random.uniform(300, size[0] / 2 - 100)
            
            cover_x = arena['center'][0] + distance * math.cos(angle)
            cover_y = arena['center'][1] + distance * math.sin(angle)
            
            # Randomize cover size
            cover_size = [
                random.uniform(64, 128),
                random.uniform(64, 128),
                random.uniform(64, 128)
            ]
            
            # Create a box for cover
            cover = self._create_box(
                [cover_x - cover_size[0]/2, cover_y - cover_size[1]/2, arena['mins'][2]],
                [cover_x + cover_size[0]/2, cover_y + cover_size[1]/2, arena['mins'][2] + cover_size[2]],
                {'front': self.textures['concrete'], 'back': self.textures['concrete'], 
                 'left': self.textures['concrete'], 'right': self.textures['concrete'],
                 'top': self.textures['concrete'], 'bottom': self.textures['concrete']}
            )
            
            self.solids.append(cover)
        
        # Add player start
        self.add_player_start([
            arena['center'][0],
            arena['center'][1],
            arena['mins'][2] + 32
        ])
        
        # Add lights
        light_count = 4
        for i in range(light_count):
            angle = (2 * math.pi * i) / light_count
            distance = size[0] / 3
            
            light_x = arena['center'][0] + distance * math.cos(angle)
            light_y = arena['center'][1] + distance * math.sin(angle)
            
            self.add_light([
                light_x,
                light_y,
                arena['center'][2] + 200
            ], brightness=500, color=(255, 255, 200))
        
        # Add NPCs in a circular pattern
        for i in range(npc_count):
            angle = (2 * math.pi * i) / npc_count
            distance = random.uniform(100, 300)
            
            npc_x = arena['center'][0] + distance * math.cos(angle)
            npc_y = arena['center'][1] + distance * math.sin(angle)
            
            self.add_npc([npc_x, npc_y, arena['mins'][2] + 16])
        
        # Add some health and ammo pickups
        pickup_count = random.randint(5, 10)
        for i in range(pickup_count):
            angle = (2 * math.pi * i) / pickup_count
            distance = random.uniform(100, size[0] / 2 - 200)
            
            pickup_x = arena['center'][0] + distance * math.cos(angle)
            pickup_y = arena['center'][1] + distance * math.sin(angle)
            
            if i % 2 == 0:
                self.add_health([pickup_x, pickup_y, arena['mins'][2] + 16])
            else:
                self.add_ammo([pickup_x, pickup_y, arena['mins'][2] + 16])
        
        return arena
    
    def create_maze_scenario(self, maze_size=5, cell_size=256):
        """Create a simple maze-like structure."""
        wall_thickness = 16
        
        # Create the base floor and ceiling
        floor = self._create_box(
            [0, 0, 0],
            [maze_size * cell_size, maze_size * cell_size, wall_thickness],
            {'top': self.textures['floor'], 'bottom': self.textures['floor']}
        )
        self.solids.append(floor)
        
        ceiling = self._create_box(
            [0, 0, wall_thickness + cell_size],
            [maze_size * cell_size, maze_size * cell_size, wall_thickness * 2 + cell_size],
            {'top': self.textures['ceiling'], 'bottom': self.textures['ceiling']}
        )
        self.solids.append(ceiling)
        
        # Create maze walls
        # This is a very simple maze generation - for a real maze, you would use
        # algorithms like Depth-First Search or Prim's algorithm
        for i in range(maze_size):
            for j in range(maze_size):
                # Add some random walls
                if random.random() > 0.7 and i < maze_size - 1:
                    # Vertical wall
                    wall = self._create_box(
                        [(i+1) * cell_size - wall_thickness/2, j * cell_size, wall_thickness],
                        [(i+1) * cell_size + wall_thickness/2, (j+1) * cell_size, wall_thickness + cell_size],
                        {'front': self.textures['wall'], 'back': self.textures['wall']}
                    )
                    self.solids.append(wall)
                
                if random.random() > 0.7 and j < maze_size - 1:
                    # Horizontal wall
                    wall = self._create_box(
                        [i * cell_size, (j+1) * cell_size - wall_thickness/2, wall_thickness],
                        [(i+1) * cell_size, (j+1) * cell_size + wall_thickness/2, wall_thickness + cell_size],
                        {'front': self.textures['wall'], 'back': self.textures['wall']}
                    )
                    self.solids.append(wall)
        
        # Add outer walls
        for i in range(maze_size):
            # North wall
            wall = self._create_box(
                [i * cell_size, 0, wall_thickness],
                [(i+1) * cell_size, wall_thickness, wall_thickness + cell_size],
                {'front': self.textures['wall'], 'back': self.textures['wall']}
            )
            self.solids.append(wall)
            
            # South wall
            wall = self._create_box(
                [i * cell_size, maze_size * cell_size - wall_thickness, wall_thickness],
                [(i+1) * cell_size, maze_size * cell
    
    def add_corridor(self, room1, room2, width=96, height=128, textures=None, add_doors=True):
        """Add a corridor connecting two rooms, stopping at the room walls."""
        if textures is None:
            textures = {
                'bottom': self.textures['floor'],
                'top': self.textures['ceiling'],
                'wall': self.textures['wall']
            }
        
        # Get room centers
        c1 = room1['center']
        c2 = room2['center']
        
        # Determine the primary direction of the corridor
        dx = abs(c2[0] - c1[0])
        dy = abs(c2[1] - c1[1])
        
        door_width = 96  # Make sure this matches the door width in the room creation
        thickness = 16   # Wall thickness
        
        # Calculate corridor endpoints that stop at the room walls
        corridor_mins = [0, 0, 0]
        corridor_maxs = [0, 0, 0]
        
        # Create corridor along the primary axis, stopping at room walls
        if dx > dy:  # X-axis corridor (east-west)
            if c1[0] < c2[0]:  # Room 1 is west, Room 2 is east
                corridor_mins = [
                    room1['maxs'][0],  # Start at right wall of room1
                    c1[1] - width / 2,
                    min(room1['mins'][2], room2['mins'][2])
                ]
                corridor_maxs = [
                    room2['mins'][0],  # End at left wall of room2
                    c1[1] + width / 2,
                    min(room1['mins'][2], room2['mins'][2]) + height
                ]
            else:  # Room 1 is east, Room 2 is west
                corridor_mins = [
                    room2['maxs'][0],  # Start at right wall of room2
                    c1[1] - width / 2,
                    min(room1['mins'][2], room2['mins'][2])
                ]
                corridor_maxs = [
                    room1['mins'][0],  # End at left wall of room1
                    c1[1] + width / 2,
                    min(room1['mins'][2], room2['mins'][2]) + height
                ]
        else:  # Y-axis corridor (north-south)
            if c1[1] < c2[1]:  # Room 1 is south, Room 2 is north
                corridor_mins = [
                    c1[0] - width / 2,
                    room1['maxs'][1],  # Start at north wall of room1
                    min(room1['mins'][2], room2['mins'][2])
                ]
                corridor_maxs = [
                    c1[0] + width / 2,
                    room2['mins'][1],  # End at south wall of room2
                    min(room1['mins'][2], room2['mins'][2]) + height
                ]
            else:  # Room 1 is north, Room 2 is south
                corridor_mins = [
                    c1[0] - width / 2,
                    room2['maxs'][1],  # Start at north wall of room2
                    min(room1['mins'][2], room2['mins'][2])
                ]
                corridor_maxs = [
                    c1[0] + width / 2,
                    room1['mins'][1],  # End at south wall of room1
                    min(room1['mins'][2], room2['mins'][2]) + height
                ]
        
        # Check if corridor has valid dimensions (rooms aren't too close)
        if corridor_mins[0] >= corridor_maxs[0] or corridor_mins[1] >= corridor_maxs[1]:
            # Rooms are too close, no need for a corridor
            return None
        
        # Create corridor walls, floor, and ceiling
        corridor_walls = []
        
        # Floor
        floor = self._create_box(
            [corridor_mins[0], corridor_mins[1], corridor_mins[2] - thickness],
            [corridor_maxs[0], corridor_maxs[1], corridor_mins[2]],
            {'top': textures['bottom'], 'bottom': textures['bottom']}
        )
        corridor_walls.append(floor)
        
        # Ceiling
        ceiling = self._create_box(
            [corridor_mins[0], corridor_mins[1], corridor_maxs[2]],
            [corridor_maxs[0], corridor_maxs[1], corridor_maxs[2] + thickness],
            {'top': textures['top'], 'bottom': textures['top']}
        )
        corridor_walls.append(ceiling)
        
        # Walls (depending on orientation)
        if dx > dy:  # X-axis corridor
            # North wall
            north_wall = self._create_box(
                [corridor_mins[0], corridor_maxs[1], corridor_mins[2]],
                [corridor_maxs[0], corridor_maxs[1] + thickness, corridor_maxs[2]],
                {'front': textures['wall'], 'back': textures['wall']}
            )
            corridor_walls.append(north_wall)
            
            # South wall
            south_wall = self._create_box(
                [corridor_mins[0], corridor_mins[1] - thickness, corridor_mins[2]],
                [corridor_maxs[0], corridor_mins[1], corridor_maxs[2]],
                {'front': textures['wall'], 'back': textures['wall']}
            )
            corridor_walls.append(south_wall)
        else:  # Y-axis corridor
            # East wall
            east_wall = self._create_box(
                [corridor_maxs[0], corridor_mins[1], corridor_mins[2]],
                [corridor_maxs[0] + thickness, corridor_maxs[1], corridor_maxs[2]],
                {'front': textures['wall'], 'back': textures['wall']}
            )
            corridor_walls.append(east_wall)
            
            # West wall
            west_wall = self._create_box(
                [corridor_mins[0] - thickness, corridor_mins[1], corridor_mins[2]],
                [corridor_mins[0], corridor_maxs[1], corridor_maxs[2]],
                {'front': textures['wall'], 'back': textures['wall']}
            )
            corridor_walls.append(west_wall)
        
        # Add all corridor walls to the solids list
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
    
    def add_room_with_doorway(self, position, size, textures=None, doorways=None):
        """Add a room with doorway cutouts in the walls."""
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
            doorways = {'north': False, 'south': False, 'east': False, 'west': False}
        
        x, y, z = position
        width, length, height = size
        
        # Calculate inner dimensions
        inner_mins = [x, y, z]
        inner_maxs = [x + width, y + length, z + height]
        
        # Wall thickness
        thickness = 16
        
        # Create walls
        walls = []
        
        # Apply optimization - use nodraw texture for faces that aren't visible
        if self.optimization_level in ["high", "extreme"]:
            # Floor - top face visible, bottom face invisible
            floor_textures = {
                'top': textures['bottom'],
                'bottom': self.textures['nodraw'],
                'front': self.textures['nodraw'],
                'back': self.textures['nodraw'],
                'left': self.textures['nodraw'],
                'right': self.textures['nodraw']
            }
            
            # Ceiling - bottom face visible, top face invisible
            ceiling_textures = {
                'top': self.textures['nodraw'],
                'bottom': textures['top'],
                'front': self.textures['nodraw'],
                'back': self.textures['nodraw'],
                'left': self.textures['nodraw'],
                'right': self.textures['nodraw']
            }
        else:
            # Standard optimization - use the same texture for all faces
            floor_textures = {'top': textures['bottom'], 'bottom': textures['bottom']}
            ceiling_textures = {'top': textures['top'], 'bottom': textures['top']}
        
        # Floor
        floor = self._create_box(
            [inner_mins[0] - thickness, inner_mins[1] - thickness, inner_mins[2] - thickness],
            [inner_maxs[0] + thickness, inner_maxs[1] + thickness, inner_mins[2]],
            floor_textures
        )
        walls.append(floor)
        
        # Ceiling
        ceiling = self._create_box(
            [inner_mins[0] - thickness, inner_mins[1] - thickness, inner_maxs[2]],
            [inner_maxs[0] + thickness, inner_maxs[1] + thickness, inner_maxs[2] + thickness],
            ceiling_textures
        )
        walls.append(ceiling)
        
        # Door dimensions
        door_width = 96
        door_height = 128
        
        # South wall (front, Y-)
        if doorways.get('south', False):
            # Calculate door position
            door_center_x = (inner_mins[0] + inner_maxs[0]) / 2
            door_start_x = door_center_x - door_width / 2
            door_end_x = door_center_x + door_width / 2
            
            # Create left section if needed
            if door_start_x > inner_mins[0] + thickness:
                left_wall = self._create_box(
                    [inner_mins[0] - thickness, inner_mins[1] - thickness, inner_mins[2]],
                    [door_start_x, inner_mins[1], inner_maxs[2]],
                    {'front': textures['front'], 'back': textures['front']}
                )
                walls.append(left_wall)
            
            # Create right section if needed
            if door_end_x < inner_maxs[0] - thickness:
                right_wall = self._create_box(
                    [door_end_x, inner_mins[1] - thickness, inner_mins[2]],
                    [inner_maxs[0] + thickness, inner_mins[1], inner_maxs[2]],
                    {'front': textures['front'], 'back': textures['front']}
                )
                walls.append(right_wall)
            
            # Create top of doorway if needed
            if inner_mins[2] + door_height < inner_maxs[2]:
                top_wall = self._create_box(
                    [door_start_x, inner_mins[1] - thickness, inner_mins[2] + door_height],
                    [door_end_x, inner_mins[1], inner_maxs[2]],
                    {'front': textures['front'], 'back': textures['front']}
                )
                walls.append(top_wall)
        else:
            # Create solid wall
            front_wall = self._create_box(
                [inner_mins[0] - thickness, inner_mins[1] - thickness, inner_mins[2]],
                [inner_maxs[0] + thickness, inner_mins[1], inner_maxs[2]],
                {'front': textures['front'], 'back': textures['front']}
            )
            walls.append(front_wall)
        
        # North wall (back, Y+)
        if doorways.get('north', False):
            # Calculate door position
            door_center_x = (inner_mins[0] + inner_maxs[0]) / 2
            door_start_x = door_center_x - door_width / 2
            door_end_x = door_center_x + door_width / 2
            
            # Create left section if needed
            if door_start_x > inner_mins[0] + thickness:
                left_wall = self._create_box(
                    [inner_mins[0] - thickness, inner_maxs[1], inner_mins[2]],
                    [door_start_x, inner_maxs[1] + thickness, inner_maxs[2]],
                    {'front': textures['back'], 'back': textures['back']}
                )
                walls.append(left_wall)
            
            # Create right section if needed
            if door_end_x < inner_maxs[0] - thickness:
                right_wall = self._create_box(
                    [door_end_x, inner_maxs[1], inner_mins[2]],
                    [inner_maxs[0] + thickness, inner_maxs[1] + thickness, inner_maxs[2]],
                    {'front': textures['back'], 'back': textures['back']}
                )
                walls.append(right_wall)
            
            # Create top of doorway if needed
            if inner_mins[2] + door_height < inner_maxs[2]:
                top_wall = self._create_box(
                    [door_start_x, inner_maxs[1], inner_mins[2] + door_height],
                    [door_end_x, inner_maxs[1] + thickness, inner_maxs[2]],
                    {'front': textures['back'], 'back': textures['back']}
                )
                walls.append(top_wall)
        else:
            # Create solid wall
            back_wall = self._create_box(
                [inner_mins[0] - thickness, inner_maxs[1], inner_mins[2]],
                [inner_maxs[0] + thickness, inner_maxs[1] + thickness, inner_maxs[2]],
                {'front': textures['back'], 'back': textures['back']}
            )
            walls.append(back_wall)
        
        # West wall (left, X-)
        if doorways.get('west', False):
            # Calculate door position
            door_center_y = (inner_mins[1] + inner_maxs[1]) / 2
            door_start_y = door_center_y - door_width / 2
            door_end_y = door_center_y + door_width / 2
            
            # Create front section if needed
            if door_start_y > inner_mins[1] + thickness:
                front_wall = self._create_box(
                    [inner_mins[0] - thickness, inner_mins[1], inner_mins[2]],
                    [inner_mins[0], door_start_y, inner_maxs[2]],
                    {'front': textures['left'], 'back': textures['left']}
                )
                walls.append(front_wall)
            
            # Create back section if needed
            if door_end_y < inner_maxs[1] - thickness:
                back_wall = self._create_box(
                    [inner_mins[0] - thickness, door_end_y, inner_mins[2]],
                    [inner_mins[0], inner_maxs[1], inner_maxs[2]],
                    {'front': textures['left'], 'back': textures['left']}
                )
                walls.append(back_wall)
            
            # Create top of doorway if needed
            if inner_mins[2] + door_height < inner_maxs[2]:
                top_wall = self._create_box(
                    [inner_mins[0] - thickness, door_start_y, inner_mins[2] + door_height],
                    [inner_mins[0], door_end_y, inner_maxs[2]],
                    {'front': textures['left'], 'back': textures['left']}
                )
                walls.append(top_wall)
        else:
            # Create solid wall
            left_wall = self._create_box(
                [inner_mins[0] - thickness, inner_mins[1], inner_mins[2]],
                [inner_mins[0], inner_maxs[1], inner_maxs[2]],
                {'front': textures['left'], 'back': textures['left']}
            )
            walls.append(left_wall)
        
        # East wall (right, X+)
        if doorways.get('east', False):
            # Calculate door position
            door_center_y = (inner_mins[1] + inner_maxs[1]) / 2
            door_start_y = door_center_y - door_width / 2
            door_end_y = door_center_y + door_width / 2
            
            # Create front section if needed
            if door_start_y > inner_mins[1] + thickness:
                front_wall = self._create_box(
                    [inner_maxs[0], inner_mins[1], inner_mins[2]],
                    [inner_maxs[0] + thickness, door_start_y, inner_maxs[2]],
                    {'front': textures['right'], 'back': textures['right']}
                )
                walls.append(front_wall)
            
            # Create back section if needed
            if door_end_y < inner_maxs[1] - thickness:
                back_wall = self._create_box(
                    [inner_maxs[0], door_end_y, inner_mins[2]],
                    [inner_maxs[0] + thickness, inner_maxs[1], inner_maxs[2]],
                    {'front': textures['right'], 'back': textures['right']}
                )
                walls.append(back_wall)
            
            # Create top of doorway if needed
            if inner_mins[2] + door_height < inner_maxs[2]:
                top_wall = self._create_box(
                    [inner_maxs[0], door_start_y, inner_mins[2] + door_height],
                    [inner_maxs[0] + thickness, door_end_y, inner_maxs[2]],
                    {'front': textures['right'], 'back': textures['right']}
                )
                walls.append(top_wall)
        else:
            # Create solid wall
            right_wall = self._create_box(
                [inner_maxs[0], inner_mins[1], inner_mins[2]],
                [inner_maxs[0] + thickness, inner_maxs[1], inner_maxs[2]],
                {'front': textures['right'], 'back': textures['right']}
            )
            walls.append(right_wall)
        
        # Add all walls to the solids list
        self.solids.extend(walls)
        
        # Return the inner dimensions of the room
        return {
            'mins': inner_mins,
            'maxs': inner_maxs,
            'center': [
                (inner_mins[0] + inner_maxs[0]) / 2,
                (inner_mins[1] + inner_maxs[1]) / 2,
                (inner_mins[2] + inner_maxs[2]) / 2
            ]
        }