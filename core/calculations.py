import numpy as np

def calculate_rcr(length, width, h_rc):
    area = length * width
    if area == 0:
        return 0
    return (5 * h_rc * (length + width)) / area

def calculate_cu(rcr, reflectance_ceiling, reflectance_wall, reflectance_floor, fixture_type="Direct"):
    tables = {
        "Direct": [0.85, 0.78, 0.72, 0.66, 0.61, 0.56, 0.51, 0.47, 0.43, 0.39, 0.36],
        "Indirect": [0.60, 0.50, 0.42, 0.36, 0.30, 0.26, 0.22, 0.19, 0.16, 0.14, 0.12]
    }
    
    base_cu_arr = tables.get(fixture_type, tables["Direct"])
    base_cu = np.interp(rcr, np.arange(11), base_cu_arr)
    
    base_reflectance_ratio = (0.8*0.5*0.2)
    actual_reflectance_ratio = (reflectance_ceiling * reflectance_wall * reflectance_floor)
    
    adjustment = (actual_reflectance_ratio - base_reflectance_ratio) * 0.5
    cu = max(0.1, min(0.95, base_cu + adjustment))
    return cu

def lumen_method(target_lux, area, cu, llf, lumens_per_fixture):
    if cu == 0 or llf == 0 or lumens_per_fixture == 0:
        return 0, 0
    total_lumens_needed = (target_lux * area) / (cu * llf)
    num_fixtures = np.ceil(total_lumens_needed / lumens_per_fixture)
    return num_fixtures, total_lumens_needed

def generate_grid_layout(length, width, num_fixtures):
    if num_fixtures == 0:
        return 0, 0, []
        
    aspect_ratio = length / width
    rows = max(1, int(np.round(np.sqrt(num_fixtures / aspect_ratio))))
    cols = max(1, int(np.ceil(num_fixtures / rows)))
    
    spacing_x = length / rows
    spacing_y = width / cols
    
    fixtures_coords = []
    num_placed = 0
    # Center out distribution
    for r in range(rows):
        for c in range(cols):
            x = (r + 0.5) * spacing_x
            y = (c + 0.5) * spacing_y
            fixtures_coords.append((x, y))
            num_placed += 1
            if num_placed >= num_fixtures:
                break
        if num_placed >= num_fixtures:
            break
            
    return rows, cols, fixtures_coords

def pt_by_pt_illuminance(room_length, room_width, workplane_h, fixtures_coords, ies_parser, llf):
    resolution = max(0.2, min(room_length, room_width) / 20.0) 
    x_points = np.arange(0, room_length + resolution, resolution)
    y_points = np.arange(0, room_width + resolution, resolution)
    
    X, Y = np.meshgrid(x_points, y_points)
    lux_grid = np.zeros(X.shape)
    
    h = workplane_h
    if h <= 0: h = 0.001
    
    for fx, fy in fixtures_coords:
        dx = X - fx
        dy = Y - fy
        d2 = dx**2 + dy**2
        distance_squared = d2 + h**2
        distance = np.sqrt(distance_squared)
        
        cos_theta = h / distance
        theta_deg = np.degrees(np.arccos(cos_theta))
        
        phi_rad = np.arctan2(dy, dx)
        phi_deg = np.degrees(phi_rad) % 360
        
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                angle_v = theta_deg[i, j]
                angle_h = phi_deg[i, j]
                
                if ies_parser:
                    candela = ies_parser.get_candela(angle_h, angle_v)
                else:
                    I_max = 1200 
                    candela = I_max * np.cos(np.radians(angle_v))
                    
                illuminance = (candela / distance_squared[i, j]) * cos_theta[i, j]
                lux_grid[i, j] += illuminance * llf
                
    return x_points, y_points, lux_grid
