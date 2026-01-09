import streamlit as st
import numpy as np
import pandas as pd
import time
import subprocess

# --- 1. BRANDING & UI ---
st.set_page_config(page_title="Ashvaka Smristi | Bio-Transport Lab", layout="wide")

st.markdown("""
    <style>
    .main-header { background-color: #1E1E1E; padding: 25px; border-radius: 15px; 
                  border-bottom: 5px solid #2ecc71; text-align: center; margin-bottom: 25px;}
    .title-text { color: white; font-size: 42px; font-weight: bold; margin: 0; letter-spacing: 3px;}
    .subtitle { color: #2ecc71; font-size: 16px; text-transform: uppercase; letter-spacing: 5px;}
    </style>
    <div class="main-header">
        <p class="title-text">ASHVAKA SMRISTI</p>
        <p class="subtitle">Clinical Cellular Transport Simulator</p>
    </div>
""", unsafe_allow_html=True)

# --- NEW: Species Physical Properties ---
SPECIES_DATA = {
    "Water": {"color": "#3498db", "size": 2, "mode": "Passive"},
    "Oxygen": {"color": "#f1c40f", "size": 2, "mode": "Passive"},
    "Glucose": {"color": "#2ecc71", "size": 5, "mode": "Facilitated"},
    "Sodium": {"color": "#e67e22", "size": 3, "mode": "Active"},
    "Potassium": {"color": "#9b59b6", "size": 3, "mode": "Active"},
    "Protein": {"color": "#e74c3c", "size": 8, "mode": "Blocked"}
}

# --- 2. SIDEBAR LOGO & CONTROL PANEL ---
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.divider()
st.sidebar.header("🕹️ Control Panel")

st.sidebar.header("🧪 Species Manager")
selected_species = st.sidebar.multiselect(
    "Select Components to Simulate",
    list(SPECIES_DATA.keys()),
    default=["Water", "Oxygen"]
)

# Initialize dictionary
species_levels = {}

# Dynamic concentration sliders
for s in selected_species:
    with st.sidebar.expander(f"{s} Levels"):
        ext = st.sidebar.slider(f"Extracellular {s}", 0, 300, 150, key=f"{s}_ext")
        intl = st.sidebar.slider(f"Intracellular {s}", 0, 300, 50, key=f"{s}_int")
        species_levels[s] = {"ext": ext, "int": intl}

scenario = st.sidebar.selectbox("🏥 Medical Scenario", 
    ["Manual Control", "Normal Cell (Homeostasis)", "Dehydration (High Osmotic)", "Hypoxia (Low O2 Flux)"],
    key="scen_select")

# Set global defaults
mode = "Passive (Diffusion)"
temp = 37
voltage = 0

# Mapping dictionary values back to global variables for metrics/physics
if selected_species:
    primary = selected_species[0]
    c_ext = species_levels[primary]["ext"]
    c_int = species_levels[primary]["int"]
else:
    c_ext, c_int = 150, 20

# Scenario Overrides
if scenario == "Normal Cell (Homeostasis)":
    temp, mode = 37, "Passive (Diffusion)"
elif scenario == "Dehydration (High Osmotic)":
    temp, mode = 39, "Passive (Diffusion)"
    st.sidebar.warning("Hypertonic state: High external pressure!")
elif scenario == "Hypoxia (Low O2 Flux)":
    temp, mode, voltage = 36, "Active (ATP Required)", -70
    st.sidebar.error("Low energy: System failing!")
else:
    # Manual Control logic
    mode = st.sidebar.selectbox("Select Transport Mechanism", ["Passive (Diffusion)", "Active (ATP Required)"], key="mode_manual")
    temp = st.sidebar.slider("System Temperature (°C)", 0, 100, 37)
    if mode == "Active (ATP Required)":
        voltage = st.sidebar.slider("Membrane Potential (mV)", -90, 50, -70)

st.sidebar.divider()

if st.sidebar.button("🚀 Launch Pygame Physics Engine"):
    subprocess.Popen([
        "python", "physics_engine.py", 
        str(temp), str(c_ext), str(c_int), mode, str(voltage)
    ])

# --- 3. MULTI-COMPONENT DASHBOARD METRICS ---
st.write("### 🧪 Live Component Analysis")

# Create a grid layout based on user selection
if selected_species:
    cols = st.columns(len(selected_species))

    for i, s in enumerate(selected_species):
        # Pull data from the dictionary created in the sidebar
        ext_val = species_levels[s]["ext"]
        int_val = species_levels[s]["int"]
        s_gradient = ext_val - int_val
        
        # Display individual metrics for each molecule
        with cols[i]:
            st.metric(
                label=f"{s} Level", 
                value=f"{s_gradient} Δ", 
                delta="Inward" if s_gradient > 0 else "Outward"
            )
            st.caption(f"Mode: {SPECIES_DATA[s]['mode']}")
else:
    st.info("Select components in the Sidebar to begin simulation.")

st.divider()

# --- GLOBAL STABILITY & HEALTH ---
# Calculate sum of all gradients to determine total osmotic pressure
total_osmotic_pressure = sum([abs(species_levels[s]["ext"] - species_levels[s]["int"]) for s in selected_species])

if 'history' not in st.session_state: 
    st.session_state.history = []

st.session_state.history.append(total_osmotic_pressure)
if len(st.session_state.history) > 20: 
    st.session_state.history.pop(0)

# Visualizing Global Stability
st.write("### Global Osmotic Stability Trend")
st.line_chart(st.session_state.history)

# Health Score: 100% is perfect homeostasis (0 pressure)
health_score = max(0, 100 - (total_osmotic_pressure // 5))
st.write(f"### Overall Cellular Health: {health_score}%")
st.progress(health_score / 100)

if health_score < 40:
    st.error("⚠️ CRITICAL: Extreme osmotic imbalance detected. Risk of Cell Death.")
elif health_score < 75:
    st.warning("⚠️ CAUTION: High osmotic stress. Homeostasis is struggling.")
else:
    st.success("✅ Homeostasis: The cellular environment is stable.")

# --- 4. THE LIVE VISUALIZER ---
chart_placeholder = st.empty()
def get_particles(ce, ci):
    y = np.concatenate([np.random.uniform(0.6, 1.0, int(ce)), np.random.uniform(0.0, 0.4, int(ci))])
    return pd.DataFrame({'x': np.random.uniform(0, 10, len(y)), 'y': y})

chart_placeholder.scatter_chart(get_particles(c_ext, c_int), x='x', y='y', color="#2ecc71")

if st.button("▶️ Run Equilibrium Time-Lapse"):
    curr_e, curr_i = float(c_ext), float(c_int)
    bar = st.progress(0)
    for t in range(10):
        flow = (curr_e - curr_i) * (0.05 + temp/200)
        curr_e -= flow; curr_i += flow
        chart_placeholder.scatter_chart(get_particles(curr_e, curr_i), x='x', y='y', color="#2ecc71")
        bar.progress((t + 1) * 10)
        time.sleep(0.5)
    st.toast('Homeostasis Achieved!', icon='✅')

# --- 5. ENHANCED LEARNING CENTER ---
# Removed the invalid syntax tags that caused the Script Execution Error
st.divider()
st.subheader("📖 Learning Center: Multi-Component Transport")
col1, col2 = st.columns(2)

with col1:
    with st.expander("🔬 Passive vs Active Transport"):
        st.write("""
        - **Water/Oxygen**: Small molecules using Simple Diffusion.
        - **Glucose**: Larger molecules using Facilitated Diffusion through channels.
        - **Sodium/Potassium**: Ions requiring the Na/K pump and ATP to move against gradients.
        """)
        # Cite: - Selective permeability logic

with col2:
    with st.expander("⚡ Membrane Potential & Proteins"):
        st.write("""
        - **Proteins**: Large, negatively charged molecules typically trapped inside.
        - **Potential**: Created by the unequal distribution of ions across the bilayer.
        """)
col_left, col_right = st.columns(2)

with col_left:
    with st.expander("🔬 Biological Logic & Membrane Structure"):
        st.write("**Q: How is Semi-Permeability modeled?**")
        st.write("In our Pygame engine, we define a 'lipid gap'. Molecules check coordinates against the protein channel.")
        
with col_right:
    with st.expander("💻 Software & Architecture"):
        st.write("**Q: Why use Pygame and Streamlit together?**")
        st.write("Streamlit handles Data State; Pygame handles Physics Rendering. This ensures the Dell Vostro maintains 60 FPS.")

with st.expander("🏥 Clinical Application"):
    st.write("By simulating **Dehydration**, we visualize how osmotic pressure affects cellular volume.")
    
with st.expander("⚡ The Physics of Membrane Potential"):
    st.write("In 'Active' mode, we simulate the **Electrochemical Gradient** necessary for Action Potentials.")
    
# --- 6. ABOUT THE DEVELOPERS ---
st.sidebar.divider()
with st.sidebar.expander("👥 About the Developers"):
    st.markdown("""
        ### **Team Ashvaka Smristi**
        **1. KRISH MITHRA N** (23MIS7003)  
        **2. SIDHANTH SAI K** (23BEC7185)  
        **3. SOHIL SUBRAMANYAM** (23BCE7429)
    """)
    if st.button("❤️ Support Our Research"):
        st.balloons()

st.sidebar.caption("Project Ashvaka Smristi v1.0")