import streamlit as st
import pandas as pd
import numpy as np

from core.standards import ROOM_STANDARDS, MATERIALS_REFLECTANCE, calculate_llf
from core.ies_parser import IESParser
from core.calculations import calculate_rcr, calculate_cu, lumen_method, generate_grid_layout, pt_by_pt_illuminance
from ui.visuals import plot_isolux_contour, plot_3d_room

st.set_page_config(page_title="Pro Lighting Calculator", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    div[data-testid="stSidebar"] {
        background-color: #f7f9fc;
        padding: 20px;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
        border-top: 4px solid #1e3a8a;
    }
    .metric-value {
        font-size: 2.2em;
        font-weight: bold;
        color: #1e3a8a;
    }
    .metric-label {
        font-size: 0.9em;
        color: #64748b;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

st.title("🪔 Pro Lighting Calculator (Advanced)")

# --- SIDEBAR ---
st.sidebar.header("📏 Room Geometry")
length_m = st.sidebar.number_input("Length (m)", 1.0, 50.0, 10.0, step=0.5)
width_m = st.sidebar.number_input("Width (m)", 1.0, 50.0, 8.0, step=0.5)
ceiling_height_m = st.sidebar.number_input("Ceiling Height (m)", 2.0, 15.0, 3.0, step=0.1)
workplane_height_m = st.sidebar.number_input("Workplane Height (m)", 0.0, 2.0, 0.8, step=0.1)

st.sidebar.header("🏢 Standards & Purpose")
room_type = st.sidebar.selectbox("Room Type", list(ROOM_STANDARDS.keys()))
standard_data = ROOM_STANDARDS[room_type]
target_lux = st.sidebar.number_input("Target Lux ($E_m$)", 50, 2000, value=standard_data['lux'])

st.sidebar.header("🎨 Surface Materials")
ceil_mat = st.sidebar.selectbox("Ceiling Material", list(MATERIALS_REFLECTANCE["Ceiling"].keys()))
wall_mat = st.sidebar.selectbox("Wall Material", list(MATERIALS_REFLECTANCE["Walls"].keys()))
floor_mat = st.sidebar.selectbox("Floor Material", list(MATERIALS_REFLECTANCE["Floor"].keys()))

rho_c = MATERIALS_REFLECTANCE["Ceiling"][ceil_mat]
rho_w = MATERIALS_REFLECTANCE["Walls"][wall_mat]
rho_f = MATERIALS_REFLECTANCE["Floor"][floor_mat]

st.sidebar.header("🧹 Maintenance Factor")
environment = st.sidebar.selectbox("Environment Cleanliness", ["Very Clean", "Clean", "Normal", "Dirty"], index=2)
interval = st.sidebar.slider("Cleaning Interval (Years)", 1, 3, 1)
llf = calculate_llf(environment, interval, "LED")

# --- MAIN SCREEN ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("💡 Luminaire Specification")
    use_fixture_type = st.selectbox("Distribution Type", ["Direct", "Indirect"])
    
    ies_parser = None
    use_lumens = 3000
    
    uploaded_file = st.file_uploader("Upload Manufacturer .ies file (Optional for precision)", type=['ies'])
    
    if uploaded_file is not None:
        content = uploaded_file.read().decode("utf-8", errors="ignore")
        try:
            ies_parser = IESParser(content)
            parsed_lumens = ies_parser.get_total_lumens()
            if parsed_lumens > 0:
                use_lumens = parsed_lumens
                st.success(f"✅ IES file interpreted successfully. Calculated Lumens: **{int(use_lumens)} lm**")
            else:
                st.warning("⚠️ Parsed lumens computed as 0. Reverting to base generic values.")
        except Exception as e:
            st.error(f"Failed to parse IES file fully: {e}")
            ies_parser = None
    
    if not ies_parser:
        st.info("Using Generic Lambertian Distribution assumptions.")
        use_lumens = st.number_input("Fixture Total Lumens", 500, 50000, 3000)

with col2:
    st.subheader("🎯 Optimization Rules")
    st.write(f"**Target Illuminance:** {target_lux} lx")
    st.write(f"**Required Uniformity ($U_0$):** {standard_data['u0']}")
    st.write(f"**Target UGR Limit:** {standard_data['ugr']}")
    st.write(f"**Light Loss Factor Computed:** {llf:.2f}")

# --- CALCULATION PHASE 1: ZONAL CAVITY ---
area = length_m * width_m
h_rc = ceiling_height_m - workplane_height_m
rcr = calculate_rcr(length_m, width_m, h_rc)
cu = calculate_cu(rcr, rho_c, rho_w, rho_f, use_fixture_type)

num_fixtures, total_lumens_needed = lumen_method(target_lux, area, cu, llf, use_lumens)
rows, cols, fixtures_coords = generate_grid_layout(length_m, width_m, num_fixtures)

st.markdown("---")
st.markdown("### 📊 Zonal Cavity Method Estimates")
c1, c2, c3, c4 = st.columns(4)

c1.markdown(f'<div class="metric-card"><div class="metric-value">{area:.1f}</div><div class="metric-label">Area (m²)</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="metric-card"><div class="metric-value">{cu:.2f}</div><div class="metric-label">Calculated CU</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="metric-card"><div class="metric-value">{int(total_lumens_needed)}</div><div class="metric-label">Total Lumens Required</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="metric-card"><div class="metric-value">{int(num_fixtures)}</div><div class="metric-label">Fixtures to Install</div></div>', unsafe_allow_html=True)

if num_fixtures > 0:
    st.info(f"**Recommended Spatial Layout:** {rows} Rows × {cols} Columns (Centered)")

# --- CALCULATION PHASE 2: POINT-BY-POINT ---
st.markdown("---")
st.markdown("### 🗺️ Point-by-Point Grid Computations")
if st.button("🚀 Run Heavy Simulation (Inverse Square Law)"):
    if num_fixtures == 0:
        st.warning("No fixtures to calculate.")
    else:
        with st.spinner("Calculating light dispersion over grid matrix..."):
            x_pts, y_pts, lux_grid = pt_by_pt_illuminance(
                length_m, width_m, h_rc, fixtures_coords, ies_parser, llf
            )
            
            mean_lux = np.mean(lux_grid)
            min_lux = np.min(lux_grid)
            u0 = min_lux / mean_lux if mean_lux > 0 else 0
            
            # Display KPIs
            ucol1, ucol2 = st.columns(2)
            ucol1.metric("Simulated Average Workplane Illuminance", f"{int(mean_lux)} lx", delta=f"{int(mean_lux - target_lux)} lx from target baseline")
            
            safe_u0 = "✅ Passes Standards" if u0 >= standard_data['u0'] else "⚠️ Below Minimum Uniformity"
            delta_u0_color = "normal" if u0 >= standard_data['u0'] else "inverse"
            ucol2.metric("Calculated Uniformity ($U_0 \equiv E_{min}/E_{avg}$)", f"{u0:.2f}", delta=safe_u0, delta_color=delta_u0_color)
            
            # Visuals
            tab1, tab2 = st.tabs(["2D Isolux Contour Map", "3D Room Rendering"])
            
            with tab1:
                fig_2d = plot_isolux_contour(x_pts, y_pts, lux_grid, target_lux)
                st.plotly_chart(fig_2d, use_container_width=True)
                
            with tab2:
                fig_3d = plot_3d_room(length_m, width_m, ceiling_height_m, workplane_height_m, fixtures_coords)
                st.plotly_chart(fig_3d, use_container_width=True)
