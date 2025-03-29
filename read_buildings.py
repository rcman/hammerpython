#!/usr/bin/env python3
"""
VMF Building NODRAW Converter

This script reads a Source Engine Hammer Editor VMF file, identifies all building structures,
and creates a new VMF file with all building surfaces textured with NODRAW.
"""

import re
import os
import sys
from collections import defaultdict

def parse_vmf(vmf_path):
    """Parse a VMF file into a hierarchical structure."""
    with open(vmf_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Parse the VMF file structure
    blocks = []
    stack = [blocks]
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for opening braces (new block)
        if line.endswith('{'):
            block_name = line[:-1].strip()
            new_block = {'__type__': block_name, '__contents__': []}
            stack[-1].append(new_block)
            stack.append(new_block['__contents__'])
        
        # Check for closing braces (end block)
        elif line == '}':
            stack.pop()
        
        # Otherwise it's a property
        else:
            key_value = line.split('" "', 1)
            if len(key_value) == 2:
                key = key_value[0].strip('"')
                value = key_value[1].strip('"')
                stack[-1].append({'__type__': 'property', 'key': key, 'value': value})
    
    return blocks

def find_buildings(vmf_blocks):
    """
    Identify all solids that are likely to be buildings.
    In a typical VMF file, buildings are represented as brush entities or world brushes.
    """
    building_solids = []
    
    # Helper function to process blocks recursively
    def process_blocks(blocks, is_building_entity=False):
        for block in blocks:
            if isinstance(block, dict):
                if block['__type__'] == 'solid':
                    # If within a building entity or in world, consider it a building
                    if is_building_entity:
                        building_solids.append(block)
                    else:
                        # Check if this solid has building-like textures (not NODRAW, not tools, etc.)
                        has_building_texture = False
                        for content in block['__contents__']:
                            if content['__type__'] == 'side' and any(
                                prop['__type__'] == 'property' and 
                                prop['key'] == 'material' and 
                                not (prop['value'].startswith('TOOLS/') or 'NODRAW' in prop['value'])
                                for prop in content['__contents__']
                            ):
                                has_building_texture = True
                                break
                        
                        if has_building_texture:
                            building_solids.append(block)
                
                # Recursively check entities that might contain buildings
                elif block['__type__'] == 'entity':
                    # Check if this entity is a building (func_detail, prop_static, etc.)
                    entity_class = next((
                        prop['value'] for prop in block['__contents__'] 
                        if isinstance(prop, dict) and 
                        prop['__type__'] == 'property' and 
                        prop['key'] == 'classname'
                    ), None)
                    
                    is_building = entity_class in [
                        'func_detail', 'prop_static', 'func_brush', 'func_wall', 
                        'func_illusionary', 'func_breakable'
                    ]
                    
                    process_blocks(block['__contents__'], is_building)
                else:
                    # Process other block types
                    process_blocks(block['__contents__'], is_building_entity)
    
    # Start processing from the top level
    process_blocks(vmf_blocks)
    
    return building_solids

def apply_nodraw_texture(solids):
    """Apply NODRAW texture to all sides of the provided solids."""
    for solid in solids:
        for content in solid['__contents__']:
            if content['__type__'] == 'side':
                for prop in content['__contents__']:
                    if isinstance(prop, dict) and prop['__type__'] == 'property' and prop['key'] == 'material':
                        prop['value'] = 'TOOLS/TOOLSNODRAW'
    
    return solids

def generate_new_vmf(original_blocks, modified_solids):
    """Generate a new VMF structure using the original blocks but with modified solids."""
    # Create a mapping of original solids to modified solids
    solid_map = {id(original): modified for original, modified in zip(
        [s for s in find_buildings(original_blocks)],
        modified_solids
    )}
    
    # Deep copy blocks with replacements
    def deep_copy_with_replacements(blocks):
        result = []
        for block in blocks:
            if isinstance(block, dict):
                if block['__type__'] == 'solid' and id(block) in solid_map:
                    # Replace with the modified solid
                    result.append(solid_map[id(block)])
                else:
                    # Copy the block and recursively process contents
                    new_block = {
                        '__type__': block['__type__'],
                        '__contents__': deep_copy_with_replacements(block['__contents__']) if '__contents__' in block else []
                    }
                    
                    # Copy any other properties
                    for key, value in block.items():
                        if key != '__type__' and key != '__contents__':
                            new_block[key] = value
                            
                    result.append(new_block)
            else:
                # Direct copy for non-dict items
                result.append(block)
        
        return result
    
    return deep_copy_with_replacements(original_blocks)

def serialize_vmf(blocks, indent=0):
    """Serialize the hierarchical structure back to VMF format."""
    result = []
    
    for block in blocks:
        if isinstance(block, dict):
            if block['__type__'] == 'property':
                # Format: "key" "value"
                result.append(f"{' ' * indent}\"{block['key']}\" \"{block['value']}\"")
            else:
                # Block with opening brace
                result.append(f"{' ' * indent}{block['__type__']}")
                result.append(f"{' ' * indent}{{")
                
                # Recursively serialize contents
                result.extend(serialize_vmf(block['__contents__'], indent + 4))
                
                # Closing brace
                result.append(f"{' ' * indent}}}")
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python vmf_nodraw_converter.py <input_vmf_file> [output_vmf_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(input_file)[0] + "_nodraw.vmf"
    
    print(f"Reading VMF file: {input_file}")
    vmf_blocks = parse_vmf(input_file)
    
    print("Identifying building structures...")
    building_solids = find_buildings(vmf_blocks)
    print(f"Found {len(building_solids)} building structures")
    
    print("Applying NODRAW texture to all building surfaces...")
    modified_solids = apply_nodraw_texture(building_solids)
    
    print("Generating new VMF structure...")
    new_vmf_blocks = generate_new_vmf(vmf_blocks, modified_solids)
    
    print(f"Writing new VMF file: {output_file}")
    new_vmf_content = "\n".join(serialize_vmf(new_vmf_blocks))
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(new_vmf_content)
    
    print("Conversion complete!")

if __name__ == "__main__":
    main()