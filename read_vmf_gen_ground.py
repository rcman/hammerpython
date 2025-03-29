import re
import argparse
import sys

class VMFtoNODRAWConverter:
    def __init__(self):
        self.solids = []
        self.entities = []
        self.nodraw_texture = "TOOLS/TOOLSNODRAW"
        self.map_bounds = {'min_x': float('inf'), 'min_y': float('inf'), 'min_z': float('inf'),
                          'max_x': float('-inf'), 'max_y': float('-inf'), 'max_z': float('-inf')}

    def parse_vmf(self, filename):
        """Parse a .vmf file, extract solids, and determine map bounds."""
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading input file: {e}")
            sys.exit(1)

        # Parse solids
        solid_pattern = r'solid\s*{\s*"id"\s*"(\d+)"(.*?)}\s*}'
        solids = re.findall(solid_pattern, content, re.DOTALL)
        
        if not solids:
            print("Warning: No solids found in the VMF file. Check file format.")

        for solid_id, solid_content in solids:
            side_pattern = r'side\s*{\s*"id"\s*"(\d+)"(.*?)}\s*}'
            sides = re.findall(side_pattern, solid_content, re.DOTALL)
            solid_sides = []
            is_ground = True  # Assume ground until proven otherwise

            for side_id, side_content in sides:
                plane_match = re.search(r'"plane"\s*"([^"]+)"', side_content)
                if plane_match:
                    plane = plane_match.group(1)
                    # Extract vertices from plane (e.g., "(x1 y1 z1) (x2 y2 z2) (x3 y3 z3)")
                    coords = re.findall(r'\(([^)]+)\)', plane)
                    
                    # Validate coordinate format
                    try:
                        vertices = [list(map(float, c.split())) for c in coords]
                        if len(vertices) != 3 or any(len(v) != 3 for v in vertices):
                            print(f"Warning: Invalid vertices in plane definition for side {side_id}. Skipping.")
                            continue
                    except ValueError:
                        print(f"Warning: Could not parse coordinates in plane for side {side_id}. Skipping.")
                        continue
                    
                    # Update map bounds
                    for x, y, z in vertices:
                        self.map_bounds['min_x'] = min(self.map_bounds['min_x'], x)
                        self.map_bounds['min_y'] = min(self.map_bounds['min_y'], y)
                        self.map_bounds['min_z'] = min(self.map_bounds['min_z'], z)
                        self.map_bounds['max_x'] = max(self.map_bounds['max_x'], x)
                        self.map_bounds['max_y'] = max(self.map_bounds['max_y'], y)
                        self.map_bounds['max_z'] = max(self.map_bounds['max_z'], z)
                    
                    # Check if this solid is flat (potential ground)
                    z_values = [v[2] for v in vertices]
                    if max(z_values) - min(z_values) > 16:  # If height > 16, not ground
                        is_ground = False
                    
                    # Extract original material, uaxis, vaxis from the side content
                    material_match = re.search(r'"material"\s*"([^"]+)"', side_content)
                    material = material_match.group(1) if material_match else self.nodraw_texture
                    
                    uaxis_match = re.search(r'"uaxis"\s*"([^"]+)"', side_content)
                    uaxis = uaxis_match.group(1) if uaxis_match else '[1 0 0 0] 0.25'
                    
                    vaxis_match = re.search(r'"vaxis"\s*"([^"]+)"', side_content)
                    vaxis = vaxis_match.group(1) if vaxis_match else '[0 -1 0 0] 0.25'
                    
                    rotation_match = re.search(r'"rotation"\s*"([^"]+)"', side_content)
                    rotation = rotation_match.group(1) if rotation_match else '0'
                    
                    lightmapscale_match = re.search(r'"lightmapscale"\s*"([^"]+)"', side_content)
                    lightmapscale = lightmapscale_match.group(1) if lightmapscale_match else '16'
                    
                    smoothing_groups_match = re.search(r'"smoothing_groups"\s*"([^"]+)"', side_content)
                    smoothing_groups = smoothing_groups_match.group(1) if smoothing_groups_match else '0'
                    
                    side = {
                        'id': side_id,
                        'plane': plane,
                        'material': self.nodraw_texture,
                        'uaxis': uaxis,
                        'vaxis': vaxis,
                        'rotation': rotation,
                        'lightmapscale': lightmapscale,
                        'smoothing_groups': smoothing_groups
                    }
                    solid_sides.append(side)
            
            if solid_sides and not is_ground:  # Only keep non-ground solids (buildings)
                self.solids.append({
                    'id': solid_id,
                    'sides': solid_sides
                })

        # Parse entities (excluding worldspawn)
        entity_pattern = r'entity\s*{\s*"id"\s*"(\d+)"(.*?)}\s*}'
        entities = re.findall(entity_pattern, content, re.DOTALL)
        for entity_id, entity_content in entities:
            if '"classname" "worldspawn"' not in entity_content:
                self.entities.append({
                    'id': entity_id,
                    'content': entity_content.strip()
                })

        print(f"Parsed {len(self.solids)} building solids and {len(self.entities)} entities")

    def add_generic_ground(self):
        """Add a generic ground plane based on map bounds."""
        # Make sure we have valid bounds
        if (self.map_bounds['min_x'] == float('inf') or 
            self.map_bounds['max_x'] == float('-inf')):
            print("Warning: Invalid map bounds. Skipping ground creation.")
            return
            
        # Round bounds to nearest 64 units for cleaner geometry
        ground_thickness = 32  # Increased thickness for stability
        padding = 256  # Extra padding around map

        min_x = int(self.map_bounds['min_x'] - padding) // 64 * 64
        min_y = int(self.map_bounds['min_y'] - padding) // 64 * 64
        min_z = int(self.map_bounds['min_z'] - ground_thickness) // 64 * 64
        
        max_x = int(self.map_bounds['max_x'] + padding) // 64 * 64 + 64
        max_y = int(self.map_bounds['max_y'] + padding) // 64 * 64 + 64
        max_z = int(self.map_bounds['min_z']) // 64 * 64  # Ground top at map minimum z
        
        # Create a proper ground brush using Hammer-compatible geometry
        # Top face
        top_face = {
            'id': 'g1',
            'plane': f"({min_x} {min_y} {max_z}) ({max_x} {min_y} {max_z}) ({max_x} {max_y} {max_z})",
            'material': self.nodraw_texture,
            'uaxis': '[1 0 0 0] 0.25',
            'vaxis': '[0 -1 0 0] 0.25',
            'rotation': '0',
            'lightmapscale': '16',
            'smoothing_groups': '0'
        }
        
        # Bottom face
        bottom_face = {
            'id': 'g2',
            'plane': f"({min_x} {max_y} {min_z}) ({max_x} {max_y} {min_z}) ({max_x} {min_y} {min_z})",
            'material': self.nodraw_texture,
            'uaxis': '[1 0 0 0] 0.25',
            'vaxis': '[0 -1 0 0] 0.25',
            'rotation': '0',
            'lightmapscale': '16',
            'smoothing_groups': '0'
        }
        
        # North face
        north_face = {
            'id': 'g3',
            'plane': f"({max_x} {max_y} {max_z}) ({max_x} {max_y} {min_z}) ({min_x} {max_y} {min_z})",
            'material': self.nodraw_texture,
            'uaxis': '[1 0 0 0] 0.25',
            'vaxis': '[0 0 -1 0] 0.25',
            'rotation': '0',
            'lightmapscale': '16',
            'smoothing_groups': '0'
        }
        
        # South face
        south_face = {
            'id': 'g4',
            'plane': f"({max_x} {min_y} {min_z}) ({max_x} {min_y} {max_z}) ({min_x} {min_y} {max_z})",
            'material': self.nodraw_texture,
            'uaxis': '[1 0 0 0] 0.25',
            'vaxis': '[0 0 -1 0] 0.25',
            'rotation': '0',
            'lightmapscale': '16',
            'smoothing_groups': '0'
        }
        
        # East face
        east_face = {
            'id': 'g5',
            'plane': f"({max_x} {min_y} {min_z}) ({max_x} {max_y} {min_z}) ({max_x} {max_y} {max_z})",
            'material': self.nodraw_texture,
            'uaxis': '[0 1 0 0] 0.25',
            'vaxis': '[0 0 -1 0] 0.25',
            'rotation': '0',
            'lightmapscale': '16',
            'smoothing_groups': '0'
        }
        
        # West face
        west_face = {
            'id': 'g6',
            'plane': f"({min_x} {min_y} {max_z}) ({min_x} {max_y} {max_z}) ({min_x} {max_y} {min_z})",
            'material': self.nodraw_texture,
            'uaxis': '[0 1 0 0] 0.25',
            'vaxis': '[0 0 -1 0] 0.25',
            'rotation': '0',
            'lightmapscale': '16',
            'smoothing_groups': '0'
        }
        
        # Add the ground solid
        self.solids.append({
            'id': 'ground',
            'sides': [top_face, bottom_face, north_face, south_face, east_face, west_face]
        })
        
        print(f"Created ground brush: {min_x},{min_y},{min_z} to {max_x},{max_y},{max_z}")

    def write_vmf(self, filename):
        """Write a new .vmf file with NODRAW-textured buildings and a generic ground."""
        try:
            with open(filename, 'w') as f:
                # Write VMF header
                f.write('versioninfo\n{\n\t"editorversion" "400"\n\t"editorbuild" "8864"\n\t"mapversion" "1"\n')
                f.write('\t"formatversion" "100"\n\t"prefab" "0"\n}\n')
                f.write('visgroups\n{\n}\n')
                f.write('viewsettings\n{\n\t"bSnapToGrid" "1"\n\t"bShowGrid" "1"\n\t"bShowLogicalGrid" "0"\n')
                f.write('\t"nGridSpacing" "64"\n\t"bShow3DGrid" "0"\n}\n')

                # Write world block start
                f.write('world\n{\n\t"id" "1"\n\t"mapversion" "1"\n\t"classname" "worldspawn"\n')
                f.write('\t"skyname" "sky_day01_01"\n\t"sounds" "1"\n\t"MaxRange" "4096"\n')

                # Write solids
                for solid in self.solids:
                    f.write(f'\tsolid\n\t{{\n\t\t"id" "{solid["id"]}"\n')
                    
                    # Check if solid has sides
                    if not solid.get('sides'):
                        print(f"Warning: Solid {solid['id']} has no sides. Adding dummy side.")
                        f.write('\t\tside\n\t\t{\n\t\t\t"id" "dummy"\n')
                        f.write('\t\t\t"plane" "(0 0 0) (64 0 0) (64 64 0)"\n')
                        f.write('\t\t\t"material" "TOOLS/TOOLSNODRAW"\n')
                        f.write('\t\t\t"uaxis" "[1 0 0 0] 0.25"\n')
                        f.write('\t\t\t"vaxis" "[0 -1 0 0] 0.25"\n')
                        f.write('\t\t\t"rotation" "0"\n')
                        f.write('\t\t\t"lightmapscale" "16"\n')
                        f.write('\t\t\t"smoothing_groups" "0"\n')
                        f.write('\t\t}\n')
                    else:
                        # Write each side
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
                    
                    # Close solid block
                    f.write('\t}\n')
                
                # Close world block
                f.write('}\n')

                # Write entities
                for entity in self.entities:
                    f.write(f'entity\n{{\n\t"id" "{entity["id"]}"\n')
                    f.write(f'{entity["content"]}\n')
                    f.write('}\n')

                # Write cameras and cordon sections
                f.write('cameras\n{\n\t"activecamera" "-1"\n}\n')
                f.write('cordon\n{\n\t"mins" "(-1024 -1024 -1024)"\n\t"maxs" "(1024 1024 1024)"\n\t"active" "0"\n}\n')
        
        except Exception as e:
            print(f"Error writing output file: {e}")
            sys.exit(1)

    def convert(self, input_file, output_file):
        """Convert the input VMF to a NODRAW-textured VMF with a generic ground."""
        print(f"Starting conversion: {input_file} -> {output_file}")
        self.parse_vmf(input_file)
        self.add_generic_ground()
        self.write_vmf(output_file)
        print(f"Conversion complete: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Convert a .vmf file to a NODRAW-textured version with a generic ground.')
    parser.add_argument('--input', type=str, required=True, help='Path to the input .vmf file')
    parser.add_argument('--output', type=str, default='nodraw_map.vmf', help='Path to the output .vmf file')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    try:
        converter = VMFtoNODRAWConverter()
        converter.convert(args.input, args.output)
        print(f"Successfully converted VMF file.")
    except Exception as e:
        print(f"Error during conversion: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()