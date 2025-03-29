def generate_simple_vmf(filename="simple_nodraw_building.vmf"):
    """Generate a very simple VMF file with a single square building using NODRAW texture."""
    
    with open(filename, "w") as f:
        # Write VMF header
        f.write('versioninfo\n{\n\t"editorversion" "400"\n\t"editorbuild" "8864"\n\t"mapversion" "1"\n\t"formatversion" "100"\n\t"prefab" "0"\n}\n')
        f.write('visgroups\n{\n}\n')
        f.write('viewsettings\n{\n\t"bSnapToGrid" "1"\n\t"bShowGrid" "1"\n\t"bShowLogicalGrid" "0"\n\t"nGridSpacing" "64"\n\t"bShow3DGrid" "0"\n}\n')
        
        # Write world entity
        f.write('world\n{\n')
        f.write('\t"id" "1"\n')
        f.write('\t"mapversion" "1"\n')
        f.write('\t"classname" "worldspawn"\n')
        f.write('\t"skyname" "sky_day01_01"\n')
        f.write('\t"maxpropscreenwidth" "-1"\n')
        f.write('\t"detailvbsp" "detail.vbsp"\n')
        f.write('\t"detailmaterial" "detail/detailsprites"\n')
        
        # Simple box with NODRAW texture
        f.write('\tsolid\n\t{\n')
        f.write('\t\t"id" "2"\n')
        
        # Bottom face
        f.write('\t\tside\n\t\t{\n')
        f.write('\t\t\t"id" "1"\n')
        f.write('\t\t\t"plane" "(-64 -64 0) (64 -64 0) (64 64 0)"\n')
        f.write('\t\t\t"material" "TOOLS/TOOLSNODRAW"\n')
        f.write('\t\t\t"uaxis" "[1 0 0 0] 0.25"\n')
        f.write('\t\t\t"vaxis" "[0 -1 0 0] 0.25"\n')
        f.write('\t\t\t"rotation" "0"\n')
        f.write('\t\t\t"lightmapscale" "16"\n')
        f.write('\t\t\t"smoothing_groups" "0"\n')
        f.write('\t\t}\n')
        
        # Top face
        f.write('\t\tside\n\t\t{\n')
        f.write('\t\t\t"id" "2"\n')
        f.write('\t\t\t"plane" "(-64 64 128) (64 64 128) (64 -64 128)"\n')
        f.write('\t\t\t"material" "TOOLS/TOOLSNODRAW"\n')
        f.write('\t\t\t"uaxis" "[1 0 0 0] 0.25"\n')
        f.write('\t\t\t"vaxis" "[0 -1 0 0] 0.25"\n')
        f.write('\t\t\t"rotation" "0"\n')
        f.write('\t\t\t"lightmapscale" "16"\n')
        f.write('\t\t\t"smoothing_groups" "0"\n')
        f.write('\t\t}\n')
        
        # North face
        f.write('\t\tside\n\t\t{\n')
        f.write('\t\t\t"id" "3"\n')
        f.write('\t\t\t"plane" "(-64 64 0) (64 64 0) (64 64 128)"\n')
        f.write('\t\t\t"material" "TOOLS/TOOLSNODRAW"\n')
        f.write('\t\t\t"uaxis" "[1 0 0 0] 0.25"\n')
        f.write('\t\t\t"vaxis" "[0 0 -1 0] 0.25"\n')
        f.write('\t\t\t"rotation" "0"\n')
        f.write('\t\t\t"lightmapscale" "16"\n')
        f.write('\t\t\t"smoothing_groups" "0"\n')
        f.write('\t\t}\n')
        
        # South face
        f.write('\t\tside\n\t\t{\n')
        f.write('\t\t\t"id" "4"\n')
        f.write('\t\t\t"plane" "(-64 -64 0) (-64 -64 128) (64 -64 128)"\n')
        f.write('\t\t\t"material" "TOOLS/TOOLSNODRAW"\n')
        f.write('\t\t\t"uaxis" "[1 0 0 0] 0.25"\n')
        f.write('\t\t\t"vaxis" "[0 0 -1 0] 0.25"\n')
        f.write('\t\t\t"rotation" "0"\n')
        f.write('\t\t\t"lightmapscale" "16"\n')
        f.write('\t\t\t"smoothing_groups" "0"\n')
        f.write('\t\t}\n')
        
        # East face
        f.write('\t\tside\n\t\t{\n')
        f.write('\t\t\t"id" "5"\n')
        f.write('\t\t\t"plane" "(64 -64 0) (64 -64 128) (64 64 128)"\n')
        f.write('\t\t\t"material" "TOOLS/TOOLSNODRAW"\n')
        f.write('\t\t\t"uaxis" "[0 1 0 0] 0.25"\n')
        f.write('\t\t\t"vaxis" "[0 0 -1 0] 0.25"\n')
        f.write('\t\t\t"rotation" "0"\n')
        f.write('\t\t\t"lightmapscale" "16"\n')
        f.write('\t\t\t"smoothing_groups" "0"\n')
        f.write('\t\t}\n')
        
        # West face
        f.write('\t\tside\n\t\t{\n')
        f.write('\t\t\t"id" "6"\n')
        f.write('\t\t\t"plane" "(-64 -64 0) (-64 64 0) (-64 64 128)"\n')
        f.write('\t\t\t"material" "TOOLS/TOOLSNODRAW"\n')
        f.write('\t\t\t"uaxis" "[0 1 0 0] 0.25"\n')
        f.write('\t\t\t"vaxis" "[0 0 -1 0] 0.25"\n')
        f.write('\t\t\t"rotation" "0"\n')
        f.write('\t\t\t"lightmapscale" "16"\n')
        f.write('\t\t\t"smoothing_groups" "0"\n')
        f.write('\t\t}\n')
        
        f.write('\t}\n')
        
        # Ground
        f.write('\tsolid\n\t{\n')
        f.write('\t\t"id" "3"\n')
        
        # Bottom face of ground
        f.write('\t\tside\n\t\t{\n')
        f.write('\t\t\t"id" "7"\n')
        f.write('\t\t\t"plane" "(-512 -512 -16) (512 -512 -16) (512 512 -16)"\n')
        f.write('\t\t\t"material" "TOOLS/TOOLSNODRAW"\n')
        f.write('\t\t\t"uaxis" "[1 0 0 0] 0.25"\n')
        f.write('\t\t\t"vaxis" "[0 -1 0 0] 0.25"\n')
        f.write('\t\t\t"rotation" "0"\n')
        f.write('\t\t\t"lightmapscale" "16"\n')
        f.write('\t\t\t"smoothing_groups" "0"\n')
        f.write('\t\t}\n')
        
        # Top face of ground
        f.write('\t\tside\n\t\t{\n')
        f.write('\t\t\t"id" "8"\n')
        f.write('\t\t\t"plane" "(-512 512 0) (512 512 0) (512 -512 0)"\n')
        f.write('\t\t\t"material" "TOOLS/TOOLSNODRAW"\n')
        f.write('\t\t\t"uaxis" "[1 0 0 0] 0.25"\n')
        f.write('\t\t\t"vaxis" "[0 -1 0 0] 0.25"\n')
        f.write('\t\t\t"rotation" "0"\n')
        f.write('\t\t\t"lightmapscale" "16"\n')
        f.write('\t\t\t"smoothing_groups" "0"\n')
        f.write('\t\t}\n')
        
        # North face of ground
        f.write('\t\tside\n\t\t{\n')
        f.write('\t\t\t"id" "9"\n')
        f.write('\t\t\t"plane" "(-512 512 -16) (512 512 -16) (512 512 0)"\n')
        f.write('\t\t\t"material" "TOOLS/TOOLSNODRAW"\n')
        f.write('\t\t\t"uaxis" "[1 0 0 0] 0.25"\n')
        f.write('\t\t\t"vaxis" "[0 0 -1 0] 0.25"\n')
        f.write('\t\t\t"rotation" "0"\n')
        f.write('\t\t\t"lightmapscale" "16"\n')
        f.write('\t\t\t"smoothing_groups" "0"\n')
        f.write('\t\t}\n')
        
        # South face of ground
        f.write('\t\tside\n\t\t{\n')
        f.write('\t\t\t"id" "10"\n')
        f.write('\t\t\t"plane" "(-512 -512 -16) (-512 -512 0) (512 -512 0)"\n')
        f.write('\t\t\t"material" "TOOLS/TOOLSNODRAW"\n')
        f.write('\t\t\t"uaxis" "[1 0 0 0] 0.25"\n')
        f.write('\t\t\t"vaxis" "[0 0 -1 0] 0.25"\n')
        f.write('\t\t\t"rotation" "0"\n')
        f.write('\t\t\t"lightmapscale" "16"\n')
        f.write('\t\t\t"smoothing_groups" "0"\n')
        f.write('\t\t}\n')
        
        # East face of ground
        f.write('\t\tside\n\t\t{\n')
        f.write('\t\t\t"id" "11"\n')
        f.write('\t\t\t"plane" "(512 -512 -16) (512 -512 0) (512 512 0)"\n')
        f.write('\t\t\t"material" "TOOLS/TOOLSNODRAW"\n')
        f.write('\t\t\t"uaxis" "[0 1 0 0] 0.25"\n')
        f.write('\t\t\t"vaxis" "[0 0 -1 0] 0.25"\n')
        f.write('\t\t\t"rotation" "0"\n')
        f.write('\t\t\t"lightmapscale" "16"\n')
        f.write('\t\t\t"smoothing_groups" "0"\n')
        f.write('\t\t}\n')
        
        # West face of ground
        f.write('\t\tside\n\t\t{\n')
        f.write('\t\t\t"id" "12"\n')
        f.write('\t\t\t"plane" "(-512 -512 -16) (-512 512 -16) (-512 512 0)"\n')
        f.write('\t\t\t"material" "TOOLS/TOOLSNODRAW"\n')
        f.write('\t\t\t"uaxis" "[0 1 0 0] 0.25"\n')
        f.write('\t\t\t"vaxis" "[0 0 -1 0] 0.25"\n')
        f.write('\t\t\t"rotation" "0"\n')
        f.write('\t\t\t"lightmapscale" "16"\n')
        f.write('\t\t\t"smoothing_groups" "0"\n')
        f.write('\t\t}\n')
        
        f.write('\t}\n')
        
        # Close the world entity
        f.write('}\n')
        
        # Add player start entity
        f.write('entity\n{\n')
        f.write('\t"id" "9"\n')
        f.write('\t"classname" "info_player_start"\n')
        f.write('\t"angles" "0 0 0"\n')
        f.write('\t"origin" "0 0 32"\n')
        f.write('}\n')
        
        # Add light entity
        f.write('entity\n{\n')
        f.write('\t"id" "10"\n')
        f.write('\t"classname" "light_environment"\n')
        f.write('\t"pitch" "-45"\n')
        f.write('\t"_light" "255 255 255 200"\n')
        f.write('\t"_ambient" "96 96 96 100"\n')
        f.write('\t"angles" "0 0 0"\n')
        f.write('\t"origin" "0 0 128"\n')
        f.write('}\n')
        
        # Add sky camera
        f.write('entity\n{\n')
        f.write('\t"id" "11"\n')
        f.write('\t"classname" "sky_camera"\n')
        f.write('\t"scale" "16"\n')
        f.write('\t"origin" "0 0 256"\n')
        f.write('}\n')
        
        # Add cameras section
        f.write('cameras\n{\n\t"activecamera" "-1"\n}\n')
        
        # Add cordon
        f.write('cordon\n{\n\t"mins" "(-1024 -1024 -1024)"\n\t"maxs" "(1024 1024 1024)"\n\t"active" "0"\n}\n')
    
    print(f"Successfully generated VMF file: {filename}")

if __name__ == "__main__":
    generate_simple_vmf()