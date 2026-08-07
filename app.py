import pandas as pd
import streamlit as st

st.set_page_config(page_title="Marketing Collaterals Stock List", layout="wide")

st.title("📦 Marketing Collaterals Stock List - FCC MDY")
st.caption("Updated As Of 31 July 2026")

# Initial data loaded from the image
INITIAL_DATA = [
    {"No": 1, "Items": "Rose Gold Vaccum Bottle", "Qty": 94, "Unit": "Pcs", "Remark": ""},
    {"No": 2, "Items": "Folding Umbrella", "Qty": 196, "Unit": "Pcs", "Remark": ""},
    {"No": 3, "Items": "UV Car Wind Shield Umbrella", "Qty": 100, "Unit": "Pcs", "Remark": ""},
    {"No": 4, "Items": "Recycle Bag", "Qty": 40, "Unit": "Pcs", "Remark": ""},
    {"No": 5, "Items": "FCC Notebook Set", "Qty": 64, "Unit": "Pcs", "Remark": ""},
    {"No": 6, "Items": "FCC Paper bag", "Qty": 283, "Unit": "Pcs", "Remark": ""},
    {"No": 7, "Items": "Coffee Cup Gift Set", "Qty": 85, "Unit": "Pcs", "Remark": ""},
    {"No": 8, "Items": "Coffee Cup Gift Set's Bag", "Qty": 97, "Unit": "Pcs", "Remark": ""},
    {"No": 9, "Items": "Thadingyut Set", "Qty": 2, "Unit": "Set", "Remark": ""},
    {"No": 10, "Items": "White Mug", "Qty": 243, "Unit": "Pcs", "Remark": ""},
    {"No": 11, "Items": "Recycle Coffee Gift Set", "Qty": 10, "Unit": "Set", "Remark": ""},
    {"No": 12, "Items": "Mini Fan", "Qty": 53, "Unit": "Pcs", "Remark": ""},
    {"No": 13, "Items": "FCC Notepad", "Qty": 183, "Unit": "Pcs", "Remark": ""},
    {"No": 14, "Items": "FCC Keychain", "Qty": 121, "Unit": "Pcs", "Remark": ""},
    {"No": 15, "Items": "UV Car UV Shield - Security", "Qty": 77, "Unit": "Pcs", "Remark": ""},
    {"No": 16, "Items": "Car UV Shield - Small", "Qty": 70, "Unit": "Pcs", "Remark": ""},
    {"No": 17, "Items": "Golf Umbrella", "Qty": 135, "Unit": "Pcs", "Remark": ""},
    {"No": 18, "Items": "Garden Umbrella", "Qty": 9, "Unit": "Pcs", "Remark": ""},
    {"No": 19, "Items": "Garden Umbrella Tripod", "Qty": 2, "Unit": "Pcs", "Remark": ""},
    {"No": 20, "Items": "Pullup Banner", "Qty": 6, "Unit": "Pcs", "Remark": ""},
    {"No": 21, "Items": "Pullup Banner", "Qty": 2, "Unit": "Pcs", "Remark": "Yangon Project (Used for MABA 10th year Anniversary Event)"},
    {"No": 22, "Items": "X Stand", "Qty": 3, "Unit": "Pcs", "Remark": "FCC MDY Logo"},
]

# Initialize inventory session state
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(INITIAL_DATA)

# Sidebar navigation
action = st.sidebar.radio("Select Action", ["View / Edit Inventory", "Log Stock Movement (Take / Add)", "Add New Item"])

# --- OPTION 1: View / Edit Inventory ---
if action == "View / Edit Inventory":
    st.subheader("Current Stock Table")
    st.caption("You can edit values directly in the table and click 'Save Changes' below.")

    edited_df = st.data_editor(
        st.session_state.inventory,
        num_rows="dynamic",
        use_container_width=True,
        key="inventory_editor",
    )

    if st.button("Save Changes"):
        st.session_state.inventory = edited_df
        st.success("Stock list saved successfully!")

# --- OPTION 2: Log Stock Movement (Take / Add) ---
elif action == "Log Stock Movement (Take / Add)":
    st.subheader("Update Item Quantity")

    items = st.session_state.inventory["Items"].unique().tolist()
    if not items:
        st.warning("Inventory is empty.")
    else:
        selected_item = st.selectbox("Select Item", items)
        
        # If there are multiple rows with the same name (e.g. Pullup Banner), allow choosing by No / Remark
        matching_rows = st.session_state.inventory[st.session_state.inventory["Items"] == selected_item]
        
        if len(matching_rows) > 1:
            row_options = [f"Item No. {row['No']} - Remark: ({row['Remark'] or 'None'})" for _, row in matching_rows.iterrows()]
            selected_row_idx = st.selectbox("Select Specific Entry", range(len(row_options)), format_func=lambda x: row_options[x])
            target_index = matching_rows.index[selected_row_idx]
        else:
            target_index = matching_rows.index[0]

        movement_type = st.radio("Movement Type", ["Take (Withdraw)", "Add (Restock)"], horizontal=True)
        qty_change = st.number_input("Quantity", min_value=1, value=1, step=1)

        if st.button("Confirm Movement"):
            current_qty = st.session_state.inventory.at[target_index, "Qty"]

            if movement_type == "Take (Withdraw)":
                if current_qty >= qty_change:
                    st.session_state.inventory.at[target_index, "Qty"] = current_qty - qty_change
                    st.success(f"Removed {qty_change} units of '{selected_item}'. New Qty: {current_qty - qty_change}")
                else:
                    st.error(f"Cannot withdraw {qty_change} units. Only {current_qty} in stock!")
            else:
                st.session_state.inventory.at[target_index, "Qty"] = current_qty + qty_change
                st.success(f"Added {qty_change} units to '{selected_item}'. New Qty: {current_qty + qty_change}")

# --- OPTION 3: Add New Item ---
elif action == "Add New Item":
    st.subheader("Add a New Item to Stock")

    with st.form("add_item_form", clear_on_submit=True):
        next_no = int(st.session_state.inventory["No"].max() + 1) if not st.session_state.inventory.empty else 1
        st.text_input("Item No.", value=str(next_no), disabled=True)
        
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Initial Quantity", min_value=0, value=0)
        unit = st.text_input("Unit", value="Pcs")
        remark = st.text_input("Remark")

        submitted = st.form_submit_button("Add Item")

        if submitted:
            if not item_name.strip():
                st.error("Please enter an Item Name.")
            else:
                new_row = pd.DataFrame([
                    {"No": next_no, "Items": item_name, "Qty": quantity, "Unit": unit, "Remark": remark}
                ])
                st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
                st.success(f"Successfully added '{item_name}' to inventory.")

# --- Low Stock Warning ---
st.divider()
st.subheader("⚠️ Low Stock Summary (Qty ≤ 10)")
low_stock_df = st.session_state.inventory[st.session_state.inventory["Qty"] <= 10]

if not low_stock_df.empty:
    st.dataframe(low_stock_df[["No", "Items", "Qty", "Unit", "Remark"]], use_container_width=True)
else:
    st.info("All items have healthy stock levels (> 10).")
