import pandas as pd
import streamlit as st

st.set_page_config(page_title="Stock Control App", layout="wide")

st.title("📦 Stock Control Management")

# Initialize inventory session state if it doesn't exist
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(
        [
            {"Item ID": "A101", "Item Name": "Laptop", "Category": "Electronics", "Quantity": 15, "Min Stock": 5},
            {"Item ID": "B202", "Item Name": "Desk Chair", "Category": "Furniture", "Quantity": 8, "Min Stock": 10},
            {"Item ID": "C303", "Item Name": "Notebook", "Category": "Stationery", "Quantity": 50, "Min Stock": 20},
        ]
    )

# Sidebar: Actions
st.sidebar.header("Actions")
action = st.sidebar.radio("Select Action", ["View / Edit Inventory", "Log Stock Movement (Take / Add)", "Add New Item"])

# --- OPTION 1: View / Edit Inventory ---
if action == "View / Edit Inventory":
    st.subheader("Current Inventory")
    st.caption("You can edit cells directly in the table below:")

    # Interactive table where users can edit quantities directly
    edited_df = st.data_editor(
        st.session_state.inventory,
        num_rows="dynamic",
        key="inventory_editor",
        use_container_width=True,
    )

    if st.button("Save Changes"):
        st.session_state.inventory = edited_df
        st.success("Inventory updated successfully!")

# --- OPTION 2: Log Stock Movement (Take / Add) ---
elif action == "Log Stock Movement (Take / Add)":
    st.subheader("Update Item Stock Level")

    item_list = st.session_state.inventory["Item Name"].tolist()
    if not item_list:
        st.warning("No items in inventory.")
    else:
        selected_item = st.selectbox("Select Item", item_list)
        movement_type = st.radio("Movement Type", ["Take (Withdraw)", "Add (Restock)"], horizontal=True)
        qty_change = st.number_input("Quantity", min_value=1, value=1, step=1)

        if st.button("Confirm Movement"):
            idx = st.session_state.inventory[st.session_state.inventory["Item Name"] == selected_item].index[0]
            current_qty = st.session_state.inventory.at[idx, "Quantity"]

            if movement_type == "Take (Withdraw)":
                if current_qty >= qty_change:
                    st.session_state.inventory.at[idx, "Quantity"] = current_qty - qty_change
                    st.success(f"Removed {qty_change} units of {selected_item}. New total: {current_qty - qty_change}")
                else:
                    st.error(f"Cannot withdraw {qty_change} units. Only {current_qty} in stock!")
            else:
                st.session_state.inventory.at[idx, "Quantity"] = current_qty + qty_change
                st.success(f"Added {qty_change} units to {selected_item}. New total: {current_qty + qty_change}")

# --- OPTION 3: Add New Item ---
elif action == "Add New Item":
    st.subheader("Add a New Product to Inventory")

    with st.form("add_item_form", clear_on_submit=True):
        item_id = st.text_input("Item ID (e.g. D404)")
        item_name = st.text_input("Item Name")
        category = st.text_input("Category")
        quantity = st.number_input("Initial Quantity", min_value=0, value=0)
        min_stock = st.number_input("Minimum Alert Threshold", min_value=0, value=5)

        submitted = st.form_submit_button("Add Item")

        if submitted:
            if not item_id or not item_name:
                st.error("Please fill in both Item ID and Item Name.")
            else:
                new_row = pd.DataFrame([
                    {"Item ID": item_id, "Item Name": item_name, "Category": category, "Quantity": quantity, "Min Stock": min_stock}
                ])
                st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
                st.success(f"Successfully added '{item_name}' to inventory.")

# --- Low Stock Alerts ---
st.divider()
st.subheader("⚠️ Low Stock Alerts")
low_stock_df = st.session_state.inventory[
    st.session_state.inventory["Quantity"] <= st.session_state.inventory["Min Stock"]
]

if not low_stock_df.empty:
    st.warning("The following items need restocked:")
    st.dataframe(low_stock_df[["Item ID", "Item Name", "Quantity", "Min Stock"]], use_container_width=True)
else:
    st.info("All items are above minimum stock levels.")