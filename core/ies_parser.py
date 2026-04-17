import numpy as np

class IESParser:
    def __init__(self, file_content):
        self.raw_content = file_content
        self.lumens_per_lamp = 0
        self.num_lamps = 0
        self.multiplier = 1.0
        self.num_vertical_angles = 0
        self.num_horizontal_angles = 0
        
        self.vertical_angles = []
        self.horizontal_angles = []
        self.candela_values = [] 
        
        self.parse()
        
    def parse(self):
        lines = [line.strip() for line in self.raw_content.splitlines() if line.strip()]
        data_lines = []
        
        tilt_found = False
        for line in lines:
            if line.upper().startswith("TILT="):
                tilt_found = True
                continue
            if tilt_found and not line.startswith("TILT"):
                data_lines.extend(line.split())
                
        if len(data_lines) < 13:
            raise ValueError("Invalid IES data format")
            
        self.num_lamps = float(data_lines[0])
        self.lumens_per_lamp = float(data_lines[1])
        self.multiplier = float(data_lines[2])
        self.num_vertical_angles = int(data_lines[3])
        self.num_horizontal_angles = int(data_lines[4])
        
        current_idx = 13
        
        # Vertical Angles
        self.vertical_angles = [float(x) for x in data_lines[current_idx:current_idx + self.num_vertical_angles]]
        current_idx += self.num_vertical_angles
        
        # Horizontal Angles
        self.horizontal_angles = [float(x) for x in data_lines[current_idx:current_idx + self.num_horizontal_angles]]
        current_idx += self.num_horizontal_angles
        
        # Candela values
        num_candelas = self.num_vertical_angles * self.num_horizontal_angles
        candela_flat = [float(x) for x in data_lines[current_idx:current_idx + num_candelas]]
        
        self.candela_values = []
        for i in range(self.num_horizontal_angles):
            start = i * self.num_vertical_angles
            end = start + self.num_vertical_angles
            self.candela_values.append(candela_flat[start:end])
            
    def get_total_lumens(self):
        if self.lumens_per_lamp > 1:
            return sum([self.num_lamps * self.lumens_per_lamp * self.multiplier])
        return self.calculate_lumens_from_candelas()
        
    def calculate_lumens_from_candelas(self):
        total_lumens = 0
        avg_candelas = np.mean(self.candela_values, axis=0)
        
        for i in range(len(self.vertical_angles) - 1):
            theta1 = np.radians(self.vertical_angles[i])
            theta2 = np.radians(self.vertical_angles[i+1])
            i1 = avg_candelas[i]
            i2 = avg_candelas[i+1]
            
            zonal_constant = 2 * np.pi * (np.cos(theta1) - np.cos(theta2))
            avg_intensity = (i1 + i2) / 2
            total_lumens += avg_intensity * zonal_constant
            
        return total_lumens * self.multiplier

    def get_candela(self, horizontal_angle, vertical_angle):
        h_idx = np.searchsorted(self.horizontal_angles, horizontal_angle)
        v_idx = np.searchsorted(self.vertical_angles, vertical_angle)
        
        h_idx = max(0, min(h_idx, len(self.horizontal_angles)-1))
        v_idx = max(0, min(v_idx, len(self.vertical_angles)-1))
        
        return self.candela_values[h_idx][v_idx] * self.multiplier
