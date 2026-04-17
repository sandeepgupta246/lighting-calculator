# core/standards.py

# CIBSE / IESNA General References
ROOM_STANDARDS = {
    "General Office": {"lux": 500, "ugr": 19, "u0": 0.60},
    "Open Plan Office": {"lux": 500, "ugr": 19, "u0": 0.60},
    "Computer Workstation": {"lux": 500, "ugr": 19, "u0": 0.60},
    "Meeting Room": {"lux": 500, "ugr": 19, "u0": 0.60},
    "Corridor": {"lux": 100, "ugr": 28, "u0": 0.40},
    "Stairs": {"lux": 150, "ugr": 25, "u0": 0.40},
    "Restroom / Toilet": {"lux": 200, "ugr": 22, "u0": 0.40},
    "Warehouse (Active)": {"lux": 200, "ugr": 25, "u0": 0.40},
    "Warehouse (Storage)": {"lux": 100, "ugr": 25, "u0": 0.40},
    "Retail Store": {"lux": 500, "ugr": 22, "u0": 0.60},
    "Classroom": {"lux": 300, "ugr": 19, "u0": 0.60},
    "Laboratory": {"lux": 500, "ugr": 19, "u0": 0.60},
    "Hospital Ward": {"lux": 100, "ugr": 19, "u0": 0.40},
    "Operating Theater": {"lux": 1000, "ugr": 19, "u0": 0.70},
    "Living Room": {"lux": 150, "ugr": 22, "u0": 0.40},
    "Kitchen": {"lux": 300, "ugr": 22, "u0": 0.40},
    "Bedroom": {"lux": 100, "ugr": 22, "u0": 0.40},
}

MATERIALS_REFLECTANCE = {
    "Ceiling": {
        "White Paint (Clean)": 0.85,
        "Off-white Paint": 0.75,
        "Acoustic Ceiling Tiles": 0.70,
        "Light Wood": 0.50,
        "Dark Wood / Exposed": 0.20
    },
    "Walls": {
        "White Paint": 0.80,
        "Light Color Paint": 0.60,
        "Medium Color Paint": 0.40,
        "Brick / Fair-faced Concrete": 0.30,
        "Dark Color Paint": 0.15,
        "Glass (windows)": 0.10
    },
    "Floor": {
        "Light Tiles / Marble": 0.40,
        "Light Wood / Carpet": 0.30,
        "Concrete (Clean)": 0.20,
        "Dark Carpet": 0.10
    }
}

def calculate_llf(environment="Clean", cleaning_interval_years=1, lamp_type="LED"):
    """
    Calculates Light Loss Factor (LLF) = LLD * LDD * RSDD * LSF
    """
    # Lamp Lumen Depreciation (LLD)
    lld_dict = {"LED": 0.90, "Fluorescent": 0.85, "Metal Halide": 0.75, "Incandescent": 0.95}
    lld = lld_dict.get(lamp_type, 0.85)

    # Luminaire Dirt Depreciation (LDD)
    ldd_matrix = {
        "Very Clean": {1: 0.95, 2: 0.92, 3: 0.90},
        "Clean": {1: 0.90, 2: 0.85, 3: 0.82},
        "Normal": {1: 0.85, 2: 0.80, 3: 0.75},
        "Dirty": {1: 0.80, 2: 0.72, 3: 0.65}
    }
    interval = max(1, min(3, int(cleaning_interval_years)))
    ldd = ldd_matrix.get(environment, ldd_matrix["Normal"]).get(interval, 0.80)

    # Room Surface Dirt Depreciation (RSDD)
    rsdd = 0.95  
    # Lamp Survival Factor (LSF)
    lsf = 1.0  
    
    return lld * ldd * rsdd * lsf
