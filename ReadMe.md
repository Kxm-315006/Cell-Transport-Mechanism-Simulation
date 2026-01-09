# 🧬 Ashvaka Smristi: Clinical Cellular Transport Lab
**A Multi-Component Bio-Physics Simulator**

Ashvaka Smristi is an advanced simulation platform designed to visualize and analyze the complex dynamics of cellular transport. By integrating real-time medical scenarios with a high-fidelity physics kernel, the project models how various molecules—from simple water to complex proteins—interact with the semi-permeable cell membrane.

---

## 🚀 Key Features

### 1. Multi-Component Engine
Simulates six distinct biological species simultaneously, each with unique physical properties:
* **Water & Oxygen:** Small, non-polar molecules modeled using **Simple Diffusion**.
* **Glucose:** Large polar molecules requiring **Facilitated Diffusion** through protein channels.
* **Sodium & Potassium:** Ions requiring **Active Transport** (ATP) to move against electrochemical gradients.
* **Proteins:** Large macromolecules that remain "Blocked," simulating **Colloid Osmotic Pressure**.

### 2. Dual-Engine Architecture
* **Dashboard (Streamlit):** Handles medical scenarios (Dehydration, Hypoxia), real-time homeostasis tracking, and cellular health metrics.
* **Physics Kernel (Pygame):** A custom-built 2D physics engine that calculates collisions, kinetic energy (based on temperature), and selective permeability at 60 FPS.

### 3. Interactive Clinical Scenarios
* **Normal Homeostasis:** Balanced internal and external environments.
* **Dehydration:** High external osmotic pressure, demonstrating hypertonic effects.
* **Hypoxia:** Low oxygen flux and ATP failure, leading to the breakdown of active transport pumps.

---

## 🛠️ Technical Stack
* **Language:** Python 3.10+
* **Data Visualization:** Streamlit, Pandas, NumPy
* **Physics Rendering:** Pygame
* **Process Management:** Subprocess (Synchronizing the Dashboard with the Kernel)

---

## 📖 Installation & Usage

1. **Install Dependencies:**
   ```bash
   pip install streamlit pygame numpy pandas