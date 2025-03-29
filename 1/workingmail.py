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
            f.write('versioninfo\n{\n\t"editorversion" "400"\n\t"editorbuild" "8864"\n\t"mapversion" "1"\n')
            f.write('\t"formatversion" "100"\n\t"prefab" "0"\n}\n')
            f.write('visgroups\n{\n}\n')
            f.write('viewsettings\n{\n\t"bSnapToGrid" "1"\n\t"bShowGrid" "1"\n\t"bShowLogicalGrid" "0"\n')
            f.write('\t"nGridSpacing" "64"\n\t"bShow3DGrid" "0"\n}\n')
            f.write('world\n{\n\t"id" "1"\n\t"mapversion" "1"\n\t"classname" "worldspawn"\n')
            f.write('\t"skyname" "sky_day01_01"\n\t"sounds" "1"\n\t"MaxRange" "4096"\n')
            
            if self.optimization_level in ["high", "extreme"]:
                f.write('\t"detailmaterial" "detail/detailsprites"\n\t"detailvbsp" "detail.vbsp"\n')
                if self.optimization_level == "extreme":
                    f.write('\t"vrad_brush_cast_shadows" "1"\n\t"vrad_patch_shadows" "1"\n')
                    f.write('\t"vrad_patch_emitlight" "1"\n\t"vrad_force_non_rad" "1"\n')
                    f.write('\t"_light_env_maxdist" "2000"\n\t"_light_maxs" "1500"\n')
            
            for solid in self.solids:
                f.write('\tsolid\n\t{\n\t\t"id" "' + str(solid['id']) + '"\n')
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
            
            for entity in self.entities:
                if entity['id'] == 1:
                    continue
                f.write('entity\n{\n\t"id" "' + str(entity['id']) + '"\n')
                for key, value in entity.items():
                    if key != 'id':
                        f.write('\t"' + key + '" "' + str(value) + '"\n')
                f.write('}\n')
            
            f.write('cameras\n{\n\t"activecamera" "-1"\n}\n')
            f.write('cordon\n{\n\t"mins" "(-1024 -1024 -1024)"\n\t"maxs" "(1024 1024 1024)"\n\t"active" "0"\n}\n')
    
    def _get_next_id(self):
        """Get the next available ID and increment the counter."""
        id_val = self.next_id
        self.next_id += 1
        return id_val
    
    def _create_light_template(self, position, brightness=300, color=(255, 255, 255)):
        """Create a light entity template."""
        return {
            'id': self._get_next_id(),
            'classname': 'light',
            'origin': f"{position[0]} {position[1]} {position[2]}",
            '_light': f"{color[0]} {color[1]} {color[2]} {brightness}",
            'style': '0',
            'pattern': '',
            'falloff': '0'
        }
    
    def _create_player_start_template(self, position, angles=(0, 0, 0)):
        """Create a player start entity template."""
        return {
            'id': self._get_next_id(),
            'classname': 'info_player_start',
            'origin': f"{position[0]} {position[1]} {position[2]}",
            'angles': f"{angles[0]} {angles[1]} {angles[2]}"
        }
    
    def _create_npc_spawn_template(self, position, npc_type='npc_combine_s'):
        """Create an NPC spawn entity template."""
        return {
            'id': self._get_next_id(),
            'classname': npc_type,
            'origin': f"{position[0]} {position[1]} {position[2]}",
            'spawnflags': '0'
        }
    
    def _create_item_spawn_template(self, position, item_type='item_healthkit'):
        """Create an item spawn entity template."""
        return {
            'id': self._get_next_id(),
            'classname': item_type,
            'origin': f"{position[0]} {position[1]} {position[2]}",
            'spawnflags': '0'
        }
    
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
        return {
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
    
    def _create_health_template(self, position):
        """Create a health kit entity template."""
        return {
            'id': self._get_next_id(),
            'classname': 'item_healthkit',
            'origin': f"{position[0]} {position[1]} {position[2]}",
            'spawnflags': '0'
        }
    
    def _create_ammo_template(self, position):
        """Create an ammo box entity template."""
        return {
            'id': self._get_next_id(),
            'classname': 'item_ammo_pistol',
            'origin': f"{position[0]} {position[1]} {position[2]}",
            'spawnflags': '0'
        }
    
    def _create_vertex(self, x, y, z):
        """Create a vertex at the given coordinates."""
        return f"({x} {y} {z})"
    
    def _create_face(self, vertices, texture, u_axis, v_axis, rotation=0, u_scale=0.25, v_scale=0.25):
        """Create a face with the given vertices and texture."""
        return {
            'id': self._get_next_id(),
            'plane': ' '.join(vertices),
            'material': texture,
            'uaxis': f"[{u_axis[0]} {u_axis[1]} {u_axis[2]} 0] {u_scale}",
            'vaxis': f"[{v_axis[0]} {v_axis[1]} {v_axis[2]} 0] {v_scale}",
            'rotation': str(rotation),
            'lightmapscale': '16',
            'smoothing_groups': '0'
        }
    
    def _create_box(self, mins, maxs, textures):
        """Create a cube (brush) with the given dimensions and textures."""
        box_id = self._get_next_id()
        x1, y1, z1 = mins
        x2, y2, z2 = maxs
        
        v = [
            self._create_vertex(x1, y1, z1),
            self._create_vertex(x2, y1, z1),
            self._create_vertex(x2, y2, z1),
            self._create_vertex(x1, y2, z1),
            self._create_vertex(x1, y1, z2),
            self._create_vertex(x2, y1, z2),
            self._create_vertex(x2, y2, z2),
            self._create_vertex(x1, y2, z2)
        ]
        
        faces = [
            self._create_face([v[0], v[1], v[2], v[3]], textures.get('bottom', self.textures['floor']), 
                             [1, 0, 0], [0, -1, 0]),
            self._create_face([v[7], v[6], v[5], v[4]], textures.get('top', self.textures['ceiling']), 
                             [1, 0, 0], [0, -1, 0]),
            self._create_face([v[4], v[5], v[1], v[0]], textures.get('front', self.textures['wall']), 
                             [1, 0, 0], [0, 0, -1]),
            self._create_face([v[3], v[2], v[6], v[7]], textures.get('back', self.textures['wall']), 
                             [1, 0, 0], [0, 0, -1]),
            self._create_face([v[0], v[3], v[7], v[4]], textures.get('left', self.textures['wall']), 
                             [0, 1, 0], [0, 0, -1]),
            self._create_face([v[5], v[6], v[2], v[1]], textures.get('right', self.textures['wall']), 
                             [0, 1, 0], [0, 0, -1])
        ]
        
        return {'id': box_id, 'sides': faces}
    
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
        
        inner_mins = [x, y, z]
        inner_maxs = [x + width, y + length, z + height]
        
        thickness = 16
        walls = []
        
        if self.optimization_level in ["high", "extreme"]:
            floor_textures = {
                'top': textures['bottom'], 'bottom': self.textures['nodraw'],
                'front': self.textures['nodraw'], 'back': self.textures['nodraw'],
                'left': self.textures['nodraw'], 'right': self.textures['nodraw']
            }
            ceiling_textures = {
                'top': self.textures['nodraw'], 'bottom': textures['top'],
                'front': self.textures['nodraw'], 'back': self.textures['nodraw'],
                'left': self.textures['nodraw'], 'right': self.textures['nodraw']
            }
            front_wall_textures = {
                'top': self.textures['nodraw'], 'bottom': self.textures['nodraw'],
                'front': self.textures['nodraw'], 'back': textures['front'],
                'left': self.textures['nodraw'], 'right': self.textures['nodraw']
            }
            back_wall_textures = {
                'top': self.textures['nodraw'], 'bottom': self.textures['nodraw'],
                'front': textures['back'], 'back': self.textures['nodraw'],
                'left': self.textures['nodraw'], 'right': self.textures['nodraw']
            }
            left_wall_textures = {
                'top': self.textures['nodraw'], 'bottom': self.textures['nodraw'],
                'front': self.textures['nodraw'], 'back': self.textures['nodraw'],
                'left': self.textures['nodraw'], 'right': textures['left']
            }
            right_wall_textures = {
                'top': self.textures['nodraw'], 'bottom': self.textures['nodraw'],
                'front': self.textures['nodraw'], 'back': self.textures['nodraw'],
                'left': textures['right'], 'right': self.textures['nodraw']
            }
        else:
            floor_textures = {k: textures['bottom'] for k in ['top', 'bottom', 'front', 'back', 'left', 'right']}
            ceiling_textures = {k: textures['top'] for k in ['top', 'bottom', 'front', 'back', 'left', 'right']}
            front_wall_textures = {k: textures['front'] for k in ['top', 'bottom', 'front', 'back', 'left', 'right']}
            back_wall_textures = {k: textures['back'] for k in ['top', 'bottom', 'front', 'back', 'left', 'right']}
            left_wall_textures = {k: textures['left'] for k in ['top', 'bottom', 'front', 'back', 'left', 'right']}
            right_wall_textures = {k: textures['right'] for k in ['top', 'bottom', 'front', 'back', 'left', 'right']}

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
        
        front_wall = self._create_box(
            [inner_mins[0] - thickness, inner_mins[1] - thickness, inner_mins[2]],
            [inner_maxs[0] + thickness, inner_mins[1], inner_maxs[2]],
            front_wall_textures
        )
        walls.append(front_wall)
        
        back_wall = self._create_box(
            [inner_mins[0] - thickness, inner_maxs[1], inner_mins[2]],
            [inner_maxs[0] + thickness, inner_maxs[1] + thickness, inner_maxs[2]],
            back_wall_textures
        )
        walls.append(back_wall)
        
        left_wall = self._create_box(
            [inner_mins[0] - thickness, inner_mins[1], inner_mins[2]],
            [inner_mins[0], inner_maxs[1], inner_maxs[2]],
            left_wall_textures
        )
        walls.append(left_wall)
        
        right_wall = self._create_box(
            [inner_maxs[0], inner_mins[1], inner_mins[2]],
            [inner_maxs[0] + thickness, inner_maxs[1], inner_maxs[2]],
            right_wall_textures
        )
        walls.append(right_wall)
        
        if self.optimization_level == "extreme":
            hint_thickness = 1
            hint_h = self._create_box(
                [inner_mins[0], inner_mins[1] + length/2 - hint_thickness/2, inner_mins[2]],
                [inner_maxs[0], inner_mins[1] + length/2 + hint_thickness/2, inner_maxs[2]],
                {'front': self.textures['hint'], 'back': self.textures['hint']}
            )
            walls.append(hint_h)
            
            hint_v = self._create_box(
                [inner_mins[0] + width/2 - hint_thickness/2, inner_mins[1], inner_mins[2]],
                [inner_mins[0] + width/2 + hint_thickness/2, inner_maxs[1], inner_maxs[2]],
                {'front': self.textures['hint'], 'back': self.textures['hint']}
            )
            walls.append(hint_v)
        
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
        
        inner_mins = [x, y, z]
        inner_maxs = [x + width, y + length, z + height]
        
        thickness = 16
        door_width = 96
        door_height = 128
        
        walls = []
        
        if self.optimization_level in ["high", "extreme"]:
            floor_textures = {
                'top': textures['bottom'], 'bottom': self.textures['nodraw'],
                'front': self.textures['nodraw'], 'back': self.textures['nodraw'],
                'left': self.textures['nodraw'], 'right': self.textures['nodraw']
            }
            ceiling_textures = {
                'top': self.textures['nodraw'], 'bottom': textures['top'],
                'front': self.textures['nodraw'], 'back': self.textures['nodraw'],
                'left': self.textures['nodraw'], 'right': self.textures['nodraw']
            }
            wall_textures = {
                'top': self.textures['nodraw'], 'bottom': self.textures['nodraw'],
                'front': self.textures['nodraw'], 'back': self.textures['nodraw'],
                'left': self.textures['nodraw'], 'right': self.textures['nodraw']
            }
        else:
            floor_textures = {k: textures['bottom'] for k in ['top', 'bottom', 'front', 'back', 'left', 'right']}
            ceiling_textures = {k: textures['top'] for k in ['top', 'bottom', 'front', 'back', 'left', 'right']}
            wall_textures = {
                'top': textures.get('top', self.textures['ceiling']),
                'bottom': textures.get('bottom', self.textures['floor']),
                'front': textures.get('front', self.textures['wall']),
                'back': textures.get('back', self.textures['wall']),
                'left': textures.get('left', self.textures['wall']),
                'right': textures.get('right', self.textures['wall'])
            }

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
        
        if doorways.get('south', False):
            door_center_x = (inner_mins[0] + inner_maxs[0]) / 2
            door_start_x = door_center_x - door_width / 2
            door_end_x = door_center_x + door_width / 2
            
            if door_start_x > inner_mins[0]:
                left_wall = self._create_box(
                    [inner_mins[0] - thickness, inner_mins[1] - thickness, inner_mins[2]],
                    [door_start_x, inner_mins[1], inner_maxs[2]],
                    {**wall_textures, 'front': textures['front'], 'back': self.textures['nodraw']}
                )
                walls.append(left_wall)
            
            if door_end_x < inner_maxs[0]:
                right_wall = self._create_box(
                    [door_end_x, inner_mins[1] - thickness, inner_mins[2]],
                    [inner_maxs[0] + thickness, inner_mins[1], inner_maxs[2]],
                    {**wall_textures, 'front': textures['front'], 'back': self.textures['nodraw']}
                )
                walls.append(right_wall)
            
            if inner_mins[2] + door_height < inner_maxs[2]:
                top_wall = self._create_box(
                    [door_start_x, inner_mins[1] - thickness, inner_mins[2] + door_height],
                    [door_end_x, inner_mins[1], inner_maxs[2]],
                    {**wall_textures, 'front': textures['front'], 'back': self.textures['nodraw']}
                )
                walls.append(top_wall)
        else:
            front_wall = self._create_box(
                [inner_mins[0] - thickness, inner_mins[1] - thickness, inner_mins[2]],
                [inner_maxs[0] + thickness, inner_mins[1], inner_maxs[2]],
                {**wall_textures, 'front': textures['front'], 'back': self.textures['nodraw']}
            )
            walls.append(front_wall)
        
        if doorways.get('north', False):
            door_center_x = (inner_mins[0] + inner_maxs[0]) / 2
            door_start_x = door_center_x - door_width / 2
            door_end_x = door_center_x + door_width / 2
            
            if door_start_x > inner_mins[0]:
                left_wall = self._create_box(
                    [inner_mins[0] - thickness, inner_maxs[1], inner_mins[2]],
                    [door_start_x, inner_maxs[1] + thickness, inner_maxs[2]],
                    {**wall_textures, 'front': textures['back'], 'back': self.textures['nodraw']}
                )
                walls.append(left_wall)
            
            if door_end_x < inner_maxs[0]:
                right_wall = self._create_box(
                    [door_end_x, inner_maxs[1], inner_mins[2]],
                    [inner_maxs[0] + thickness, inner_maxs[1] + thickness, inner_maxs[2]],
                    {**wall_textures, 'front': textures['back'], 'back': self.textures['nodraw']}
                )
                walls.append(right_wall)
            
            if inner_mins[2] + door_height < inner_maxs[2]:
                top_wall = self._create_box(
                    [door_start_x, inner_maxs[1], inner_mins[2] + door_height],
                    [door_end_x, inner_maxs[1] + thickness, inner_maxs[2]],
                    {**wall_textures, 'front': textures['back'], 'back': self.textures['nodraw']}
                )
                walls.append(top_wall)
        else:
            back_wall = self._create_box(
                [inner_mins[0] - thickness, inner_maxs[1], inner_mins[2]],
                [inner_maxs[0] + thickness, inner_maxs[1] + thickness, inner_maxs[2]],
                {**wall_textures, 'front': textures['back'], 'back': self.textures['nodraw']}
            )
            walls.append(back_wall)
        
        if doorways.get('west', False):
            door_center_y = (inner_mins[1] + inner_maxs[1]) / 2
            door_start_y = door_center_y - door_width / 2
            door_end_y = door_center_y + door_width / 2
            
            if door_start_y > inner_mins[1]:
                front_wall = self._create_box(
                    [inner_mins[0] - thickness, inner_mins[1], inner_mins[2]],
                    [inner_mins[0], door_start_y, inner_maxs[2]],
                    {**wall_textures, 'right': textures['left'], 'left': self.textures['nodraw']}
                )
                walls.append(front_wall)
            
            if door_end_y < inner_maxs[1]:
                back_wall = self._create_box(
                    [inner_mins[0] - thickness, door_end_y, inner_mins[2]],
                    [inner_mins[0], inner_maxs[1], inner_maxs[2]],
                    {**wall_textures, 'right': textures['left'], 'left': self.textures['nodraw']}
                )
                walls.append(back_wall)
            
            if inner_mins[2] + door_height < inner_maxs[2]:
                top_wall = self._create_box(
                    [inner_mins[0] - thickness, door_start_y, inner_mins[2] + door_height],
                    [inner_mins[0], door_end_y, inner_maxs[2]],
                    {**wall_textures, 'right': textures['left'], 'left': self.textures['nodraw']}
                )
                walls.append(top_wall)
        else:
            left_wall = self._create_box(
                [inner_mins[0] - thickness, inner_mins[1], inner_mins[2]],
                [inner_mins[0], inner_maxs[1], inner_maxs[2]],
                {**wall_textures, 'right': textures['left'], 'left': self.textures['nodraw']}
            )
            walls.append(left_wall)
        
        if doorways.get('east', False):
            door_center_y = (inner_mins[1] + inner_maxs[1]) / 2
            door_start_y = door_center_y - door_width / 2
            door_end_y = door_center_y + door_width / 2
            
            if door_start_y > inner_mins[1]:
                front_wall = self._create_box(
                    [inner_maxs[0], inner_mins[1], inner_mins[2]],
                    [inner_maxs[0] + thickness, door_start_y, inner_maxs[2]],
                    {**wall_textures, 'left': textures['right'], 'right': self.textures['nodraw']}
                )
                walls.append(front_wall)
            
            if door_end_y < inner_maxs[1]:
                back_wall = self._create_box(
                    [inner_maxs[0], door_end_y, inner_mins[2]],
                    [inner_maxs[0] + thickness, inner_maxs[1], inner_maxs[2]],
                    {**wall_textures, 'left': textures['right'], 'right': self.textures['nodraw']}
                )
                walls.append(back_wall)
            
            if inner_mins[2] + door_height < inner_maxs[2]:
                top_wall = self._create_box(
                    [inner_maxs[0], door_start_y, inner_mins[2] + door_height],
                    [inner_maxs[0] + thickness, door_end_y, inner_maxs[2]],
                    {**wall_textures, 'left': textures['right'], 'right': self.textures['nodraw']}
                )
                walls.append(top_wall)
        else:
            right_wall = self._create_box(
                [inner_maxs[0], inner_mins[1], inner_mins[2]],
                [inner_maxs[0] + thickness, inner_maxs[1], inner_maxs[2]],
                {**wall_textures, 'left': textures['right'], 'right': self.textures['nodraw']}
            )
            walls.append(right_wall)
        
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
    
    def add_corridor(self, room1, room2, width=96, height=128, textures=None, add_doors=True):
        """Add a corridor connecting two rooms, stopping at the room walls."""
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
        
        corridor_mins = [0, 0, 0]
        corridor_maxs = [0, 0, 0]
        
        if dx > dy:  # X-axis corridor (east-west)
            if c1[0] < c2[0]:
                corridor_mins = [room1['maxs'][0], c1[1] - width / 2, min(room1['mins'][2], room2['mins'][2])]
                corridor_maxs = [room2['mins'][0], c1[1] + width / 2, min(room1['mins'][2], room2['mins'][2]) + height]
            else:
                corridor_mins = [room2['maxs'][0], c1[1] - width / 2, min(room1['mins'][2], room2['mins'][2])]
                corridor_maxs = [room1['mins'][0], c1[1] + width / 2, min(room1['mins'][2], room2['mins'][2]) + height]
        else:  # Y-axis corridor (north-south)
            if c1[1] < c2[1]:
                corridor_mins = [c1[0] - width / 2, room1['maxs'][1], min(room1['mins'][2], room2['mins'][2])]
                corridor_maxs = [c1[0] + width / 2, room2['mins'][1], min(room1['mins'][2], room2['mins'][2]) + height]
            else:
                corridor_mins = [c1[0] - width / 2, room2['maxs'][1], min(room1['mins'][2], room2['mins'][2])]
                corridor_maxs = [c1[0] + width / 2, room1['mins'][1], min(room1['mins'][2], room2['mins'][2]) + height]
        
        if corridor_mins[0] >= corridor_maxs[0] or corridor_mins[1] >= corridor_maxs[1]:
            return None
        
        corridor_walls = []
        
        floor = self._create_box(
            [corridor_mins[0], corridor_mins[1], corridor_mins[2] - thickness],
            [corridor_maxs[0], corridor_mins[1], corridor_mins[2]],
            {'top': textures['bottom'], 'bottom': textures['bottom']}
        )
        corridor_walls.append(floor)
        
        ceiling = self._create_box(
            [corridor_mins[0], corridor_mins[1], corridor_maxs[2]],
            [corridor_maxs[0], corridor_maxs[1], corridor_maxs[2] + thickness],
            {'top': textures['top'], 'bottom': textures['top']}
        )
        corridor_walls.append(ceiling)
        
        if dx > dy:
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
        else:
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
    
    def add_window(self, wall_face, position, size=(64, 64), texture=None):
        """Add a window to a wall."""
        if texture is None:
            texture = self.textures['glass']
        
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
        if self.optimization_level in ["high", "extreme"]:
            worldspawn['detailmaterial'] = 'detail/detailsprites'
            worldspawn['detailvbsp'] = 'detail.vbsp'
            if self.optimization_level == "extreme":
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
        spacing = max(base_room_size[0], base_room_size[1]) * 2
        
        grid_size = math.ceil(math.sqrt(room_count))
        
        room_info = []
        
        for i in range(min(room_count, grid_size * grid_size)):
            row = i // grid_size
            col = i % grid_size
            
            pos_x = int(base_position[0] + col * spacing)
            pos_y = int(base_position[1] + row * spacing)
            pos_z = base_position[2]
            
            size_factor = random.uniform(0.8, 1.2)
            room_size = [
                int(base_room_size[0] * size_factor),
                int(base_room_size[1] * size_factor),
                base_room_size[2]
            ]
            
            textures = {
                'bottom': random.choice([self.textures['floor'], self.textures['concrete'], self.textures['dirt']]),
                'top': random.choice([self.textures['ceiling'], self.textures['concrete']]),
                'front': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete'], self.textures['metal']]),
                'back': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete'], self.textures['metal']]),
                'left': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete'], self.textures['metal']]),
                'right': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete'], self.textures['metal']])
            }
            
            doorways = {'north': False, 'south': False, 'east': False, 'west': False}
            room = self.add_room_with_doorway([pos_x, pos_y, pos_z], room_size, textures, doorways)
            room_info.append({'room': room, 'index': i, 'row': row, 'col': col, 'doorways': doorways, 'textures': textures})
            rooms.append(room)
            
            self.add_light(
                [room['center'][0], room['center'][1], room['center'][2] + 100],
                brightness=300, color=(255, 255, 200)
            )
            
            if random.random() > 0.5:
                self.add_health(
                    [room['center'][0] + random.uniform(-100, 100),
                     room['center'][1] + random.uniform(-100, 100),
                     room['center'][2] + 16]
                )
            
            if random.random() > 0.5:
                self.add_ammo(
                    [room['center'][0] + random.uniform(-100, 100),
                     room['center'][1] + random.uniform(-100, 100),
                     room['center'][2] + 16]
                )
            
            if random.random() > 0.7:
                self.add_npc(
                    [room['center'][0] + random.uniform(-100, 100),
                     room['center'][1] + random.uniform(-100, 100),
                     room['center'][2] + 16]
                )
        
        if connect_all and len(rooms) > 1:
            for i in range(len(rooms)):
                row = room_info[i]['row']
                col = room_info[i]['col']
                
                if col < grid_size - 1 and i + 1 < len(rooms):
                    corridor_width = random.uniform(80, 120)
                    corridor_height = random.uniform(120, 160)
                    corridor_textures = {
                        'bottom': random.choice([self.textures['floor'], self.textures['concrete']]),
                        'top': random.choice([self.textures['ceiling'], self.textures['concrete']]),
                        'wall': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete']])
                    }
                    corridor = self.add_corridor(rooms[i], rooms[i + 1], width=corridor_width, height=corridor_height, textures=corridor_textures)
                    if corridor:
                        room_info[i]['doorways']['east'] = True
                        room_info[i + 1]['doorways']['west'] = True
                
                if row < grid_size - 1 and i + grid_size < len(rooms):
                    corridor_width = random.uniform(80, 120)
                    corridor_height = random.uniform(120, 160)
                    corridor_textures = {
                        'bottom': random.choice([self.textures['floor'], self.textures['concrete']]),
                        'top': random.choice([self.textures['ceiling'], self.textures['concrete']]),
                        'wall': random.choice([self.textures['wall'], self.textures['brick'], self.textures['concrete']])
                    }
                    corridor = self.add_corridor(rooms[i], rooms[i + grid_size], width=corridor_width, height=corridor_height, textures=corridor_textures)
                    if corridor:
                        room_info[i]['doorways']['south'] = True
                        room_info[i + grid_size]['doorways']['north'] = True
            
            self.solids = []
            for info in room_info:
                room = self.add_room_with_doorway(
                    [info['room']['mins'][0], info['room']['mins'][1], info['room']['mins'][2]],
                    [info['room']['maxs'][0] - info['room']['mins'][0], 
                     info['room']['maxs'][1] - info['room']['mins'][1], 
                     info['room']['maxs'][2] - info['room']['mins'][2]],
                    info['textures'],
                    info['doorways']
                )
                info['room'] = room
                rooms[info['index']] = room
        
        if rooms:
            self.add_player_start(
                [rooms[0]['center'][0], rooms[0]['center'][1], rooms[0]['mins'][2] + 32]
            )
        
        return rooms

    def create_arena_scenario(self, size=(2048, 2048, 512), npc_count=6):
        """Create a large arena for combat scenarios."""
        arena_textures = {
            'bottom': self.textures['concrete'],
            'top': self.textures['sky'],
            'front': self.textures['brick'],
            'back': self.textures['brick'],
            'left': self.textures['brick'],
            'right': self.textures['brick']
        }
        
        arena = self.add_room([0, 0, 64], size, arena_textures)
        
        cover_count = random.randint(5, 10)
        for i in range(cover_count):
            angle = (2 * math.pi * i) / cover_count
            distance = random.uniform(300, size[0] / 2 - 100)
            
            cover_x = arena['center'][0] + distance * math.cos(angle)
            cover_y = arena['center'][1] + distance * math.sin(angle)
            
            cover_size = [
                random.uniform(64, 128),
                random.uniform(64, 128),
                random.uniform(64, 128)
            ]
            
            cover = self._create_box(
                [cover_x - cover_size[0]/2, cover_y - cover_size[1]/2, arena['mins'][2]],
                [cover_x + cover_size[0]/2, cover_y + cover_size[1]/2, arena['mins'][2] + cover_size[2]],
                {'front': self.textures['concrete'], 'back': self.textures['concrete'], 
                 'left': self.textures['concrete'], 'right': self.textures['concrete'],
                 'top': self.textures['concrete'], 'bottom': self.textures['concrete']}
            )
            self.solids.append(cover)
        
        self.add_player_start(
            [arena['center'][0], arena['center'][1], arena['mins'][2] + 32]
        )
        
        light_count = 4
        for i in range(light_count):
            angle = (2 * math.pi * i) / light_count
            distance = size[0] / 3
            
            light_x = arena['center'][0] + distance * math.cos(angle)
            light_y = arena['center'][1] + distance * math.sin(angle)
            
            self.add_light(
                [light_x, light_y, arena['center'][2] + 200],
                brightness=500, color=(255, 255, 200)
            )
        
        for i in range(npc_count):
            angle = (2 * math.pi * i) / npc_count
            distance = random.uniform(100, 300)
            
            npc_x = arena['center'][0] + distance * math.cos(angle)
            npc_y = arena['center'][1] + distance * math.sin(angle)
            
            self.add_npc([npc_x, npc_y, arena['mins'][2] + 16])
        
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
        
        for i in range(maze_size):
            for j in range(maze_size):
                if random.random() > 0.7 and i < maze_size - 1:
                    wall = self._create_box(
                        [(i+1) * cell_size - wall_thickness/2, j * cell_size, wall_thickness],
                        [(i+1) * cell_size + wall_thickness/2, (j+1) * cell_size, wall_thickness + cell_size],
                        {'front': self.textures['wall'], 'back': self.textures['wall']}
                    )
                    self.solids.append(wall)
                
                if random.random() > 0.7 and j < maze_size - 1:
                    wall = self._create_box(
                        [i * cell_size, (j+1) * cell_size - wall_thickness/2, wall_thickness],
                        [(i+1) * cell_size, (j+1) * cell_size + wall_thickness/2, wall_thickness + cell_size],
                        {'front': self.textures['wall'], 'back': self.textures['wall']}
                    )
                    self.solids.append(wall)
        
        for i in range(maze_size):
            wall = self._create_box(
                [i * cell_size, 0, wall_thickness],
                [(i+1) * cell_size, wall_thickness, wall_thickness + cell_size],
                {'front': self.textures['wall'], 'back': self.textures['wall']}
            )
            self.solids.append(wall)
            
            wall = self._create_box(
                [i * cell_size, maze_size * cell_size - wall_thickness, wall_thickness],
                [(i+1) * cell_size, maze_size * cell_size, wall_thickness + cell_size],
                {'front': self.textures['wall'], 'back': self.textures['wall']}
            )
            self.solids.append(wall)
            
            wall = self._create_box(
                [0, i * cell_size, wall_thickness],
                [wall_thickness, (i+1) * cell_size, wall_thickness + cell_size],
                {'front': self.textures['wall'], 'back': self.textures['wall']}
            )
            self.solids.append(wall)
            
            wall = self._create_box(
                [maze_size * cell_size - wall_thickness, i * cell_size, wall_thickness],
                [maze_size * cell_size, (i+1) * cell_size, wall_thickness + cell_size],
                {'front': self.textures['wall'], 'back': self.textures['wall']}
            )
            self.solids.append(wall)
        
        self.add_player_start(
            [cell_size / 2, cell_size / 2, wall_thickness + 32]
        )
        
        for i in range(maze_size):
            for j in range(maze_size):
                if random.random() > 0.7:
                    self.add_light(
                        [(i + 0.5) * cell_size, (j + 0.5) * cell_size, wall_thickness + cell_size - 32],
                        brightness=200, color=(255, 255, 200)
                    )
        
        for i in range(5):
            item_x = random.randint(1, maze_size - 1) * cell_size + cell_size / 2
            item_y = random.randint(1, maze_size - 1) * cell_size + cell_size / 2
            
            if random.random() > 0.5:
                self.add_health([item_x, item_y, wall_thickness + 16])
            else:
                self.add_ammo([item_x, item_y, wall_thickness + 16])
        
        for i in range(3):
            door_x = random.randint(1, maze_size - 2) * cell_size + cell_size / 2
            door_y = random.randint(1, maze_size - 2) * cell_size + cell_size / 2
            door_angles = (0, 90, 0) if random.random() > 0.5 else (0, 0, 0)
            
            self.add_door(
                [door_x, door_y, wall_thickness + cell_size / 2],
                (64, 8, 96),
                door_angles
            )
        
        return {
            'mins': [0, 0, 0],
            'maxs': [maze_size * cell_size, maze_size * cell_size, wall_thickness + cell_size],
            'center': [maze_size * cell_size / 2, maze_size * cell_size / 2, (wall_thickness + cell_size) / 2]
        }

def main():
    parser = argparse.ArgumentParser(description='Generate a Source Engine map (.vmf) file.')
    parser.add_argument('--name', type=str, default='generated_map', help='Name of the output map file')
    parser.add_argument('--output', type=str, default=None, help='Output file path (if not specified, name.vmf will be used)')
    parser.add_argument('--optimization', type=str, choices=['standard', 'high', 'extreme'], default='standard', 
                        help='Optimization level for the map')
    parser.add_argument('--scenario', type=str, choices=['rooms', 'arena', 'maze'], default='rooms',
                        help='Type of map scenario to generate')
    parser.add_argument('--room-count', type=int, default=3, help='Number of rooms to generate (for rooms scenario)')
    parser.add_argument('--npc-count', type=int, default=6, help='Number of NPCs to spawn (for arena scenario)')
    parser.add_argument('--maze-size', type=int, default=5, help='Size of the maze (for maze scenario)')
    
    args = parser.parse_args()
    
    map_gen = SourceMapGenerator()
    map_gen.map_name = args.name
    map_gen.optimization_level = args.optimization
    
    map_gen.add_worldspawn()
    
    if args.scenario == 'rooms':
        map_gen.create_simple_room_scenario(room_count=args.room_count)
    elif args.scenario == 'arena':
        map_gen.create_arena_scenario(npc_count=args.npc_count)
    elif args.scenario == 'maze':
        map_gen.create_maze_scenario(maze_size=args.maze_size)
    
    output_path = args.output if args.output else f"{args.name}.vmf"
    map_gen.save_vmf(output_path)
    print(f"Map generation complete. Output saved to: {output_path}")

if __name__ == "__main__":
    main()