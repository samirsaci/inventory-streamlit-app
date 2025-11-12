# [0] Import Libraries & Setup
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from inventory.inventory_models import InventoryParams
from inventory.inventory_analysis import InventorySimulation
seed = 1991
np.random.seed(seed)

st.set_page_config(page_title="Inventory Simulation – Streamlit", layout="wide")

# Set up the re-run mechanism
if "has_run" not in st.session_state:
    st.session_state.has_run = False

# [1] Minimalist sidebar 
with st.sidebar:

    st.markdown("**Inventory Parameters**")
    D = st.number_input("Annual demand D (units/year)", min_value=1, value=2000, step=50)
    T_total = st.number_input("Horizon T_total (days)", min_value=1, value=365, step=1)
    LD = st.number_input("Lead time LD (days)", min_value=0, value=0, step=1)
    T = st.number_input("Cycle time T (days)", min_value=1, value=10, step=1)
    Q = st.number_input("Order quantity Q (units)", min_value=0.0, value=55.0, step=10.0, format="%.2f")
    initial_ioh = st.number_input("Initial inventory on hand", min_value=0.0, value=55.0, step=1.0, format="%.2f")
    sigma = st.number_input("Daily demand std. dev. σ (units/day)", min_value=0.0, value=0.0, step=0.5, format="%.2f")
    method = st.radio(
        "Ordering method",
        options=["Simple Ordering", "Lead-time Ordering"],
        index=0
    )
    method_key = "order_leadtime" if method.startswith("Lead-time") else "order"
    
    run = st.button("Run simulation", type="primary")
    if run:
        st.session_state.has_run = True

# [2]---- Main: Header ----
st.title("Inventory Simulation Web Application")
# Selected Input Parameters
D_day = D / T_total
st.markdown("""
<style>
.quick-card{padding:.9rem 1rem;border:1px solid #eaeaea;border-radius:12px;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.03)}
.quick-card .label{font-size:.85rem;color:#5f6b7a;margin:0}
.quick-card .value{font-size:1.25rem;font-weight:700;margin:.15rem 0 0 0;color:#111}
.quick-card .unit{font-size:.8rem;color:#8a95a3;margin:0}
</style>
""", unsafe_allow_html=True)

def quick_card(label, value, unit=""):
    unit_html = f'<p class="unit">{unit}</p>' if unit else ""
    st.markdown(f'<div class="quick-card"><p class="label">{label}</p><p class="value">{value}</p>{unit_html}</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    quick_card("Average daily demand", f"{D_day:,.2f}", "units/day")
with c2:
    quick_card("Lead time", f"{LD}", "days")
with c3:
    quick_card("Cycle time", f"{T}", "days")
with c4:
    quick_card("Order quantity Q", f"{Q:,.0f}", "units")
with c5:
    quick_card("Initial IOH", f"{initial_ioh:,.0f}", "units")
with c6:
    quick_card("Demand σ", f"{sigma:.2f}", "units/day")

# [3] Run Calculation
if st.session_state.has_run:
    # Build params and call your engine
    params = InventoryParams(
        D=float(D),
        T_total=int(T_total),
        LD=int(LD),
        T=int(T),
        Q=float(Q),
        initial_ioh=float(initial_ioh),
        sigma=float(sigma)
    )

    sim_engine = InventorySimulation(params)

    if method_key == "order_leadtime":
        df = sim_engine.simulation_2(method="order_leadtime")
    elif method_key == "order":
        df = sim_engine.simulation_2(method="order")
    else:
        df = sim_engine.simulation_1()

    # Calculate key parameters that will be shown below the visual
    stockouts = (df["ioh"] < 0).sum()
    min_ioh = df["ioh"].min()
    avg_ioh = df["ioh"].mean()
    
    # Plot
    fig, axes = plt.subplots(3, 1, figsize=(9, 4), sharex=True)  # ↓ from (12, 8) to (9, 5)
    # Demand
    df.plot(x='time', y='demand', ax=axes[0], color='r', legend=False, grid=True)
    axes[0].set_ylabel("Demand", fontsize=8)
    # Orders
    df.plot.scatter(x='time', y='order', ax=axes[1], color='b')
    axes[1].set_ylabel("Orders", fontsize=8); axes[1].grid(True)
    # IOH
    df.plot(x='time', y='ioh', ax=axes[2], color='g', legend=False, grid=True)
    axes[2].set_ylabel("IOH", fontsize=8); axes[2].set_xlabel("Time (day)", fontsize=8)
    # Common x formatting
    axes[2].set_xlim(0, int(df["time"].max()))
    for ax in axes:
        ax.tick_params(axis='x', rotation=90, labelsize=6)
        ax.tick_params(axis='y', labelsize=6)
    plt.tight_layout()
    st.pyplot(fig, clear_figure=True, use_container_width=True)  # let width adapt
    
    # Key parameters presented below the visual
    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Stockout days", f"{stockouts}")
    kpi_cols[1].metric("Min IOH (units)", f"{min_ioh:,.0f}")
    kpi_cols[2].metric("Avg IOH (units)", f"{avg_ioh:,.0f}")

    # Message of information
    st.success("Simulation completed.")

else:
    st.info("Set your parameters on the left and click **Run simulation**.")
