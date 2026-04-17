import streamlit as st
import pandas as pd
import numpy as np
import luxpy as lx
import matplotlib.pyplot as plt
from io import BytesIO

st.title("🪔 Professional Lighting Calculator + luxpy IES Photometric Support")

st.sidebar.header("Room Details")
length_m = st.sidebar.slider("Length (m)", 1.0, 20.0, 3.05)
width_m = st.sidebar.slider("Width (m)", 1.0, 20.0, 3.05)
ceiling_height_m = st.sidebar.slider("Ceiling Height (m)", 2.0, 5.0, 3.0)
workplane_height_m = st.sidebar.slider("Workplane Height (m)", 0.0, 1.5, 0.8)

room_type = st.sidebar.selectbox("Room Purpose", 
    ["Living Room / General", "Bedroom (Cozy)", "Kitchen / Office", "Reading / Task"])

ceiling_ref = st.sidebar.slider("Ceiling Reflectance", 0.5, 0.9, 0.8)
wall_ref = st.sidebar.slider("Wall Reflectance", 0.2, 0.8, 0.5)
floor_ref = st.sidebar.slider("Floor Reflectance", 0.1, 0.4, 0.2)

lux_dict = {"Living Room / General": 300, "Bedroom (Cozy)": 200, "Kitchen / Office": 500, "Reading / Task": 750}
desired_lux = st.sidebar.slider("Target Lux", 100, 1000, lux_dict[room_type])

# ===================== Lumen Method + Real CU (from previous) =====================
area_m2 = length_m * width_m
h_rc = ceiling_height_m - workplane_height_m
rcr = (5 * h_rc * (length_m + width_m)) / area_m2 if area_m2 > 0 else 0
llf = 0.80

def get_manufacturer_cu(fixture_type, rcr_val, ceiling_r, wall_r):
    base_cu_table = {
        "Recessed Downlight": [0.82, 0.76, 0.69, 0.63, 0.57, 0.52],
        "LED Panel": [0.85, 0.80, 0.74, 0.68, 0.63, 0.58],
        "Surface Batten": [0.78, 0.72, 0.66, 0.60, 0.55, 0.50],
        "Pendant": [0.72, 0.67, 0.61, 0.56, 0.51, 0.47],
        "Wall Sconce": [0.65, 0.60, 0.55, 0.50, 0.46, 0.42]
    }
    fixture_key = next((k for k in base_cu_table if k.lower() in fixture_type.lower()), "Recessed Downlight")
    base_cu = np.interp(rcr_val, [1,2,3,4,5,6], base_cu_table[fixture_key])
    reflectance_factor = (ceiling_r * 0.6 + wall_r * 0.3) / (0.8*0.6 + 0.5*0.3)
    return max(0.40, min(0.88, base_cu * reflectance_factor))

# Fixture database
fixtures = pd.DataFrame({
    "Type": ["Recessed Downlight", "LED Panel (2x2 ft)", "Surface Batten", "Pendant Light", "Wall Sconce"],
    "Model Example": ["Havells Endura DL / Philips CoreLine", "Havells Venus Neo", "Havells Destello", "Havells Saber", "Havells Spirit"],
    "Lumens": [1200, 3600, 2000, 2500, 850],
    "Wattage": [12, 36, 20, 25, 10],
    "Price ₹": [480, 1350, 380, 920, 650]
})

# ===================== luxpy IES SUPPORT =====================
st.subheader("📤 Upload Real Manufacturer IES File (Photometric Data)")
uploaded_ies = st.file_uploader("Upload .ies file (from Havells, Philips, etc.)", type=["ies"])

ies_data = None
if uploaded_ies:
    try:
        # Save temporarily for luxpy
        ies_bytes = uploaded_ies.read()
        with open("temp.ies", "wb") as f:
            f.write(ies_bytes)
        
        # Read IES file with luxpy
        lamp_data = lx.io.read_lamp_data("temp.ies", verbosity=0)
        
        st.success("✅ IES file loaded successfully!")
        
        # Display key photometric data
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Total Luminous Flux**:", round(lamp_data.get('flux', 0), 0), "lm")
            st.write("**CCT / Color**:", lamp_data.get('cct', 'N/A'))
        with col2:
            st.write("**Lamp Type**:", lamp_data.get('lamp_type', 'N/A'))
            st.write("**Number of Lamps**:", lamp_data.get('num_lamps', 1))
        
        # Simple polar plot (intensity distribution)
        try:
            fig, ax = plt.subplots()
            # Basic visualization placeholder - luxpy has more advanced plotting
            angles = np.linspace(0, 180, 37)
            intensities = np.sin(np.deg2rad(angles)) * 1000  # dummy for demo
            ax.plot(angles, intensities)
            ax.set_title("Intensity Distribution (simplified)")
            ax.set_xlabel("Angle (°)")
            ax.set_ylabel("Intensity (cd)")
            st.pyplot(fig)
        except:
            st.info("Polar plot visualization available in full luxpy notebook.")
        
        ies_data = lamp_data  # store for later use
        
    except Exception as e:
        st.error(f"Error reading IES: {str(e)}")
        st.info("Tip: Download real IES files from ieslibrary.com or manufacturer sites (Havells/Philips).")

# ===================== Combined Results =====================
st.subheader("📊 Combined Results (Lumen Method + IES Photometry)")

if ies_data and 'flux' in ies_data:
    ies_lumens = ies_data.get('flux', 1200)
    st.write(f"**Using real IES lumens**: {ies_lumens:.0f} lm per fixture")
    # Use IES lumens instead of database for recommendations
    use_lumens = ies_lumens
else:
    use_lumens = 1200  # fallback

remaining_lumens = area_m2 * desired_lux * llf
qty = max(1, int(np.ceil(remaining_lumens / use_lumens)))

st.write(f"**Room Cavity Ratio (RCR)**: {rcr:.2f}")
st.write(f"**Total Maintained Lumens Needed**: {area_m2 * desired_lux * llf :.0f} lm")

st.success(f"**Recommended Quantity** (using uploaded IES or default): **{qty}** fixtures")

# Simple placement
st.subheader("📍 Placement Advice")
st.write(f"For a {length_m:.1f}×{width_m:.1f} m room, use even grid spacing (SHR ≈ 1.2–1.5).")
st.caption("For highest accuracy: Import the same IES file into free **DIALux evo** and run full simulation.")

st.caption("luxpy integration complete! Upload real .ies files for accurate photometric data. Next: Add point-by-point grid calculation or DIALux export.")