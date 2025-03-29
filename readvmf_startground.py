import re
import argparse

class VMFtoNODRAWConverter:
    def __init__(self):
        self.solids = []
        self.entities = []
        self.nodraw_texture = "TOOLS/TOOLSNODRAW"
        self.map_bounds = {'min_x': float('inf'), 'min_y': float('inf'), 'min_z': float('inf'),
                          'max_x': float('-inf'), 'max_y': float('-inf'), 'max_z': float('-inf')}

    def parse_vmf(self, filename):
        """Parse a .vmf file, extract solids, and determine map bounds."""
        with open(filename, 'r') as f:
            content = f.read()

        solid_pattern = r'solid\s*{\s*"id"\s*"(\d+)"(.*?)}\s*}'
        solids = re.findall(solid_pattern, content, re.DOTALL)

        for solid_id, solid_content in solids:
            side_pattern = r'side\s*{\s*"id"\s*"(\d+)"(.*?)}\s*}'
            sides = re.findall(side_pattern, solid_content, re.DOTALL)
            solid_sides = []
            is_ground = True
            min_z = float('inf')

            for side_id, side_content in sides:
                plane_match = re.search(r'"plane"\s*"([^"]+)"', side_content)
                if plane_match:
                    plane = plane_match.group(1)
                    coords = re.findall(r'\(([^)]+)\)', plane)
                    vertices = [list(map(float, c.split())) for c in coords]
                    
                    # Update global map bounds
                    for x, y, z in vertices:
                        self.map_bounds['min_x'] = min(self.map_bounds['min_x'], x)
                        self.map_bounds['min_y'] = min(self.map_bounds['min_y'], y)
                        self.map_bounds['min_z'] = min(self.map_bounds['min_z'], z)
                        self.map_bounds['max_x'] = max(self.map_bounds['max_x'], x)
                        self.map_bounds['max_y'] = max(self.map_bounds['max_y'], y)
                        self.map_bounds['max_z'] = max(self.map_bounds['max_z'], z)
                        min_z = min(min_z, z)  # Track minimum Z for this solid
                    
                    z_values = [v[2] for v in vertices]
                    if max(z_values) - min(z_values) > 16:
                        is_ground = False
                    
                    solid_sides.append({
                        'id': side_id,
                        'plane': plane,
                        'material': self.nodraw_texture,
                        'uaxis': '[1 0 0 0] 0.25',
                        'vaxis': '[0 -1 0 0] 0.25',
                        'rotation': '0',
                        'lightmapscale': '16',
                        'smoothing_groups': '0',
                        'vertices': vertices  # Store vertices for adjustment
                    })
            
            if solid_sides and not is_ground:
                self.solids.append({
                    'id': solid_id,
                    'sides': solid_sides,
                    'min_z': min_z  # Store the lowest Z for this solid
                })

        entity_pattern = r'entity\s*{\s*"id"\s*"(\d+)"(.*?)}\s*}'
        entities = re.findall(entity_pattern, content, re.DOTALL)
        for entity_id, entity_content in entities:
            if '"classname" "worldspawn"' not in entity_content:
                self.entities.append({
                    'id': entity_id,
                    'content': entity_content.strip()
                })

    def add_generic_ground(self):
        """Add a generic ground plane based on map bounds."""
        ground_thickness = 16
        self.ground_level = self.map_bounds['min_z']  # Top of ground is at min_z
        ground_mins = [self.map_bounds['min_x'] - 128, self.map_bounds['min_y'] - 128, self.map_bounds['min_z'] - ground_thickness]
        ground_maxs = [self.map_bounds['max_x'] + 128, self.map_bounds['max_y'] + 128, self.map_bounds['min_z']]
        
        vertices = [
            f"({ground_mins[0]} {ground_mins[1]} {ground_mins[2]})",
            f"({ground_maxs[0]} {ground_mins[1]} {ground_mins[2]})",
            f"({ground_maxs[0]} {ground_maxs[1]} {ground_mins[2]})",
            f"({ground_mins[0]} {ground_maxs[1]} {ground_mins[2]})",
            f"({ground_mins[0]} {ground_mins[1]} {ground_maxs[2]})",
            f"({ground_maxs[0]} {ground_mins[1]} {ground_maxs[2]})",
            f"({ground_maxs[0]} {ground_maxs[1]} {ground_maxs[2]})",
            f"({ground_mins[0]} {ground_maxs[1]} {ground_maxs[2]})"
        ]
        
        sides = [
            {'plane': f"{vertices[0]} {vertices[1]} {vertices[2]}", 'id': "new1"},
            {'plane': f"{vertices[7]} {vertices[6]} {vertices[5]}", 'id': "new2"},
            {'plane': f"{vertices[0]} {vertices[1]} {vertices[5]}", 'id': "new3"},
            {'plane': f"{vertices[2]} {vertices[3]} {vertices[7]}", 'id': "new4"},
            {'plane': f"{vertices[1]} {vertices[2]} {vertices[6]}", 'id': "new5"},
            {'plane': f"{vertices[0]} {vertices[3]} {vertices[7]}", 'id': "new6"}
        ]
        
        for side in sides:
            side.update({
                'material': self.nodraw_texture,
                'uaxis': '[1 0 0 0] 0.25',
                'vaxis': '[0 -1 0 0] 0.25',
                'rotation': '0',
                'lightmapscale': '16',
                'smoothing_groups': '0'
            })
        
        self.solids.append({
            'id': "new_ground",
            'sides': sides
        })

    def adjust_buildings_to_ground(self):
        """Shift all buildings to start at the generic ground level."""
        for solid in self.solids:
            if solid['id'] != "new_ground":  # Skip the ground solid
                z_shift = self.ground_level - solid['min_z']
                for side in solid['sides']:
                    # Adjust each vertex in the plane
                    new_vertices = []
                    for x, y, z in side['vertices']:
                        new_z = z + z_shift
                        new_vertices.append(f"({x} {y} {new_z})")
                    side['plane'] = f"{new_vertices[0]} {new_vertices[1]} {new_vertices[2]}"
                    del side['vertices']  # Clean up temporary storage

    def write_vmf(self, filename):
        """Write a new .vmf file with NODRAW-textured buildings at ground level."""
        with open(filename, 'w') as f:
            f.write('versioninfo\n{\n\t"editorversion" "400"\n\t"editorbuild" "8864"\n\t"mapversion" "1"\n')
            f.write('\t"formatversion" "100"\n\t"prefab" "0"\n}\n')
            f.write('visgroups\n{\n}\n')
            f.write('viewsettings\n{\n\t"bSnapToGrid" "1"\n\t"bShowGrid" "1"\n\t"bShowLogicalGrid" "0"\n')
            f.write('\t"nGridSpacing" "64"\n\t"bShow3DGrid" "0"\n}\n')

            f.write('world\n{\n\t"id" "1"\n\t"mapversion" "1"\n\t"classname" "worldspawn"\n')
            f.write('\t"skyname" "sky_day01_01"\n\t"sounds" "1"\n\t"MaxRange" "4096"\n')

            for solid in self.solids:
                f.write(f'\tsolid\n\t{{\n\t\t"id" "{solid["id"]}"\n')
                for side in solid['sides']:
                    f.write(f'\t\tside\n\t\t{{\n\t\t\t"id" "{side["id"]}"\n')
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

            for entity in self.entities:
                f.write(f'entity\n{{\n\t"id" "{entity["id"]}"\n')
                f.write(f'{entity["content"]}\n')
                f.write('}\n')

            f.write('cameras\n{\n\t"activecamera" "-1"\n}\n')
            f.write('cordon\n{\n\t"mins" "(-1024 -1024 -1024)"\n\t"maxs" "(1024 1024 1024)"\n\t"active" "0"\n}\n')

    def convert(self, input_file, output_file):
        """Convert the input VMF to a NODRAW-textured VMF with buildings at ground level."""
        self.parse_vmf(input_file)
        self.add_generic_ground()
        self.adjust_buildings_to_ground()
        self.write_vmf(output_file)
        print(f"Converted map with buildings at ground level saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Convert a .vmf file to a NODRAW-textured version with buildings at ground level.')
    parser.add_argument('--input', type=str, required=True, help='Path to the input .vmf file')
    parser.add_argument('--output', type=str, default='nodraw_map.vmf', help='Path to the output .vmf file')

    args = parser.parse_args()

    converter = VMFtoNODRAWConverter()
    converter.convert(args.input, args.output)

if __name__ == "__main__":
    main()
