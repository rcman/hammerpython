import re
import argparse

class VMFtoNODRAWConverter:
    def __init__(self):
        self.solids = []
        self.entities = []
        self.nodraw_texture = "TOOLS/TOOLSNODRAW"

    def parse_vmf(self, filename):
        """Parse a .vmf file and extract solids."""
        with open(filename, 'r') as f:
            content = f.read()

        # Regular expression to match solid blocks
        solid_pattern = r'solid\s*{\s*"id"\s*"(\d+)"(.*?)}\s*}'
        solids = re.findall(solid_pattern, content, re.DOTALL)

        for solid_id, solid_content in solids:
            # Extract sides within the solid
            side_pattern = r'side\s*{\s*"id"\s*"(\d+)"(.*?)}\s*}'
            sides = re.findall(side_pattern, solid_content, re.DOTALL)
            
            solid_sides = []
            for side_id, side_content in sides:
                # Extract plane and other properties
                plane_match = re.search(r'"plane"\s*"([^"]+)"', side_content)
                if plane_match:
                    plane = plane_match.group(1)
                    # Create a new side with NODRAW texture
                    side = {
                        'id': side_id,
                        'plane': plane,
                        'material': self.nodraw_texture,
                        'uaxis': '[1 0 0 0] 0.25',  # Default UV mapping
                        'vaxis': '[0 -1 0 0] 0.25',
                        'rotation': '0',
                        'lightmapscale': '16',
                        'smoothing_groups': '0'
                    }
                    solid_sides.append(side)
            
            if solid_sides:
                self.solids.append({
                    'id': solid_id,
                    'sides': solid_sides
                })

        # Optionally preserve entities (excluding worldspawn)
        entity_pattern = r'entity\s*{\s*"id"\s*"(\d+)"(.*?)}\s*}'
        entities = re.findall(entity_pattern, content, re.DOTALL)
        for entity_id, entity_content in entities:
            if '"classname" "worldspawn"' not in entity_content:
                self.entities.append({
                    'id': entity_id,
                    'content': entity_content.strip()
                })

    def write_vmf(self, filename):
        """Write a new .vmf file with all brushes textured as NODRAW."""
        with open(filename, 'w') as f:
            # Write header
            f.write('versioninfo\n{\n\t"editorversion" "400"\n\t"editorbuild" "8864"\n\t"mapversion" "1"\n')
            f.write('\t"formatversion" "100"\n\t"prefab" "0"\n}\n')
            f.write('visgroups\n{\n}\n')
            f.write('viewsettings\n{\n\t"bSnapToGrid" "1"\n\t"bShowGrid" "1"\n\t"bShowLogicalGrid" "0"\n')
            f.write('\t"nGridSpacing" "64"\n\t"bShow3DGrid" "0"\n}\n')

            # Write worldspawn with solids
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

            # Write preserved entities (if any)
            for entity in self.entities:
                f.write(f'entity\n{{\n\t"id" "{entity["id"]}"\n')
                f.write(f'{entity["content"]}\n')
                f.write('}\n')

            # Write footer
            f.write('cameras\n{\n\t"activecamera" "-1"\n}\n')
            f.write('cordon\n{\n\t"mins" "(-1024 -1024 -1024)"\n\t"maxs" "(1024 1024 1024)"\n\t"active" "0"\n}\n')

    def convert(self, input_file, output_file):
        """Convert the input VMF to a NODRAW-textured VMF."""
        self.parse_vmf(input_file)
        self.write_vmf(output_file)
        print(f"Converted map saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Convert a .vmf file to a NODRAW-textured version.')
    parser.add_argument('--input', type=str, required=True, help='Path to the input .vmf file')
    parser.add_argument('--output', type=str, default='nodraw_map.vmf', help='Path to the output .vmf file')

    args = parser.parse_args()

    converter = VMFtoNODRAWConverter()
    converter.convert(args.input, args.output)

if __name__ == "__main__":
    main()
