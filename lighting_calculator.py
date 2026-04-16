import streamlit as st
import pandas as pd
import numpy as np

st.title("🪔 AI Lighting Design Calculator (MVP)")
st.write("Enter room details → Get lumens needed + fixture recommendations")

# Sidebar inputs
st.sidebar.header("Room Details")
length_m = st.sidebar.slider("Length (meters)", 1.0, 20.0, 3.05)  # 10 ft ≈ 3.05m
width_m = st.sidebar.slider("Width (meters)", 1.0, 20.0, 3.05)
height_m = st.sidebar.slider("Ceiling Height (meters)", 2.0, 5.0, 3.0)
room_type = st.sidebar.selectbox("Room Purpose", 
    ["Living Room / General", "Bedroom (Cozy)", "Kitchen / Office", "Reading / Task", "Warehouse / Industrial"])

# Reflectance (simple)
ceiling_ref = st.sidebar.slider("Ceiling Reflectance (0-1)", 0.5, 0.9, 0.8)
wall_ref = st.sidebar.slider("Wall Reflectance (0-1)", 0.2, 0.8, 0.5)
floor_ref = st.sidebar.slider("Floor Reflectance (0-1)", 0.1, 0.4, 0.2)

# Desired lux based on room type (approximate from IS 3646 guidelines)
lux_dict = {
    "Living Room / General": 300,
    "Bedroom (Cozy)": 200,
    "Kitchen / Office": 500,
    "Reading / Task": 750,
    "Warehouse / Industrial": 150
}
desired_lux = st.sidebar.slider("Desired Average Lux", 100, 1000, lux_dict[room_type])

# Calculations
area_m2 = length_m * width_m
maintenance_factor = 0.8

# Rough CU estimation (higher reflectance + lower height = better CU)
avg_reflectance = (ceiling_ref + wall_ref * 2 + floor_ref) / 4  # weighted
room_cavity_ratio = (5 * height_m * (length_m + width_m)) / (length_m * width_m)  # simplified
cu = max(0.4, min(0.75, 0.6 + (avg_reflectance - 0.5) * 0.5 - room_cavity_ratio * 0.05))

total_lumens_required = (area_m2 * desired_lux * maintenance_factor) / cu

st.subheader("📊 Results")
st.write(f"**Room Area**: {area_m2:.1f} m²")
st.write(f"**Coefficient of Utilization (CU)**: {cu:.2f}")
st.write(f"**Total Lumens Required**: **{total_lumens_required:.0f} lm** (after losses)")

# Fixture database (expand this later with real products)
fixtures = pd.DataFrame({
    "Type": ["Recessed Downlight", "LED Panel (2x2 ft)", "Surface Batten/Tube", "Pendant Light", "Wall Sconce"],
    "Lumens": [1200, 4000, 2000, 2500, 800],
    "Wattage": [12, 36, 20, 25, 10],
    "Approx Price (₹)": [450, 1200, 350, 850, 600],
    "Recommended Use": ["Even general", "Bright uniform", "Basic", "Decorative", "Accent"]
})

st.subheader("💡 Fixture Recommendations")
num_options = st.selectbox("How many fixture types to combine?", [1, 2, 3])

# Simple greedy suggestion: try to meet lumens with combinations
recommendations = []
remaining_lumens = total_lumens_required
for i in range(num_options):
    if remaining_lumens <= 0:
        break
    # Pick best fit (for demo, cycle through)
    fixture = fixtures.iloc[i % len(fixtures)]
    qty = max(1, int(np.ceil(remaining_lumens / fixture["Lumens"])))
    total_l = qty * fixture["Lumens"]
    total_w = qty * fixture["Wattage"]
    total_c = qty * fixture["Approx Price (₹)"]
    
    recommendations.append({
        "Fixture": fixture["Type"],
        "Quantity": qty,
        "Total Lumens": total_l,
        "Total Watts": total_w,
        "Est. Cost (₹)": total_c
    })
    remaining_lumens -= total_l

rec_df = pd.DataFrame(recommendations)
st.dataframe(rec_df, use_container_width=True)

total_cost = rec_df["Est. Cost (₹)"].sum()
total_watts = rec_df["Total Watts"].sum()
st.write(f"**Estimated Total Cost**: ₹{total_cost:.0f}")
st.write(f"**Total Power Consumption**: {total_watts} Watts")

# Placement advice
st.subheader("📍 Simple Placement Tips")
st.write("- Place fixtures evenly in a grid pattern.")
st.write(f"- For {length_m}x{width_m} room: Consider {int(np.ceil(length_m/1.5))} rows and columns.")
st.write("- Avoid placing directly above seating areas if using downlights (to reduce glare).")
st.write("- Mix direct + indirect for better brightness without harsh shadows.")

st.caption("Note: This is a simplified MVP. Real designs use Dialux/Relux for precision. Expand the fixture DB with real Havells/Philips catalogs.")