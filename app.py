from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Marketing Collaterals Stock List", layout="wide")

# Initial inventory dataset
INITIAL_DATA = [
    {"Items": "Rose Gold Vaccum Bottle", "Qty": 94, "Unit": "Pcs", "Remark": ""},
    {"Items": "Folding Umbrella", "Qty": 196, "Unit": "Pcs", "Remark": ""},
    {"Items": "UV Car Wind Shield Umbrella", "Qty": 100, "Unit": "Pcs", "Remark": ""},
    {"Items": "Recycle Bag", "Qty": 40, "Unit": "Pcs", "Remark": ""},
    {"Items": "FCC Notebook Set", "Qty": 64, "Unit": "Pcs", "Remark": ""},
    {"Items": "FCC Paper bag", "Qty": 283, "Unit": "Pcs", "Remark": ""},
    {"Items": "Coffee Cup Gift Set", "Qty": 85, "Unit": "Pcs", "Remark": ""},
    {"Items": "Coffee Cup Gift Set's Bag", "Qty": 97, "Unit": "Pcs", "Remark": ""},
    {"Items": "Thadingyut Set", "Qty": 2, "Unit": "Set", "Remark": ""},
    {"Items": "White Mug", "Qty": 243, "Unit": "Pcs", "Remark": ""},
    {"Items": "Recycle Coffee Gift Set", "Qty": 10, "Unit": "Set", "Remark": ""},
    {"Items": "Mini Fan", "Qty": 53, "Unit": "Pcs", "Remark": ""},
    {"Items": "FCC Notepad", "Qty": 183, "Unit": "Pcs", "Remark": ""},
    {"Items": "FCC Keychain", "Qty": 121, "Unit": "Pcs", "Remark": ""},
    {"Items": "UV Car UV Shield - Security", "Qty": 77, "Unit": "Pcs", "Remark": ""},
    {"Items": "Car UV Shield - Small", "Qty": 70, "Unit": "Pcs", "Remark": ""},
    {"Items": "Golf Umbrella", "Qty": 135, "Unit": "Pcs", "Remark": ""},
    {"Items": "Garden Umbrella", "Qty": 9, "Unit": "Pcs", "Remark": ""},
    {"Items": "Garden Umbrella Tripod", "Qty": 2, "Unit": "Pcs", "Remark": ""},
    {"Items": "Pullup Banner", "Qty": 6, "Unit": "Pcs", "Remark": ""},
    {"Items": "Pullup Banner", "Qty": 2, "Unit": "Pcs", "Remark": "Yangon Project (Used for MABA 10th year Anniversary Event)"},
    {"Items": "X Stand", "Qty": 3, "Unit": "Pcs", "Remark": "FCC MDY Logo"},
]

# Initialize Session States
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(INITIAL_DATA)

if "last_updated" not in st.session_state:
    st.session_state.last_updated = datetime.now().strftime("%d %B %Y, %I:%M %p")

# Initialize Log Record state
if "transaction_logs" not in st.session_state:
    st.session_state.transaction_logs = pd.DataFrame(
        columns=["Date", "Issued By", "Description", "Items", "Qty", "Unit", "Balance", "Received By", "Sign", "Remark"]
    )

# Page Title
st.title("📦 Marketing Collaterals Stock List - FCC MDY")
st.caption(f"Updated As Of: **{st.session_state.last_updated}**")

# Column configurations
inventory_column_config = {
    "Items": st.column_config.TextColumn("Items", width="large"),
    "Qty": st.column_config.NumberColumn("Qty", width="small"),
    "Unit": st.column_config.TextColumn("Unit", width="small"),
    "Remark": st.column_config.TextColumn("Remark", width="large"),
}

log_column_config = {
    "Date": st.column_config.TextColumn("Date", width="small"),
    "Issued By": st.column_config.TextColumn("Issued By", width="medium"),
    "Description": st.column_config.TextColumn("Description", width="large"),
    "Items": st.column_config.TextColumn("Items", width="medium"),
    "Qty": st.column_config.NumberColumn("Qty", width="small"),
    "Unit": st.column_config.TextColumn("Unit", width="small"),
    "Balance": st.column_config.NumberColumn("Balance", width="small"),
    "Received By": st.column_config.TextColumn("Received By", width="medium"),
    "Sign": st.column_config.TextColumn("Sign", width="small"),
    "Remark": st.column_config.TextColumn("Remark", width="large"),
}

# Navigation Sidebar
action = st.sidebar.radio(
    "Select Action",
    ["View / Edit Inventory", "Log Stock Movement (Take / Add)", "View In/Out Log Record", "Add New Item"],
)

# --- OPTION 1: View / Edit Inventory ---
if action == "View / Edit Inventory":
    st.subheader("Current Stock Table")
    st.caption("You can edit values directly in the table and click 'Save Changes' below.")

    edited_df = st.data_editor(
        st.session_state.inventory,
        column_config=inventory_column_config,
        num_rows="dynamic",
        use_container_width=True,
        key="inventory_editor",
        hide_index=True,
    )

    if st.button("Save Changes"):
        st.session_state.inventory = edited_df
        st.session_state.last_updated = datetime.now().strftime("%d %B %Y, %I:%M %p")
        st.success("Stock list saved successfully!")
        st.rerun()

# --- OPTION 2: Log Stock Movement (Take / Add) ---
elif action == "Log Stock Movement (Take / Add)":
    st.subheader("Log Stock Movement & In/Out Record")

    items = st.session_state.inventory["Items"].unique().tolist()
    if not items:
        st.warning("Inventory is empty.")
    else:
        selected_item = st.selectbox("Select Item", items)
        matching_rows = st.session_state.inventory[st.session_state.inventory["Items"] == selected_item]

        if len(matching_rows) > 1:
            row_options = [f"Remark: {row['Remark'] or 'None'} (Current Qty: {row['Qty']})" for _, row in matching_rows.iterrows()]
            selected_row_idx = st.selectbox("Select Specific Entry", range(len(row_options)), format_func=lambda x: row_options[x])
            target_index = matching_rows.index[selected_row_idx]
        else:
            target_index = matching_rows.index[0]

        unit_val = st.session_state.inventory.at[target_index, "Unit"]
        current_qty = st.session_state.inventory.at[target_index, "Qty"]

        movement_type = st.radio("Movement Type", ["Take (Withdraw)", "Add (Restock)"], horizontal=True)

        col1, col2 = st.columns(2)
        with col1:
            qty_change = st.number_input("Quantity", min_value=1, value=1, step=1)
            
            # Dynamic labels according to operation type
            issued_by_label = "Issued By (Staff/Issuer)" if movement_type == "Take (Withdraw)" else "Issued By (Supplier/Vendor)"
            received_by_label = "Received By (Recipient/Dept)" if movement_type == "Take (Withdraw)" else "Received By (Warehouse/Receiver)"

            issued_by = st.text_input(issued_by_label)
            received_by = st.text_input(received_by_label)

        with col2:
            default_desc = "Withdrawal for Event" if movement_type == "Take (Withdraw)" else "Restock Delivery"
            description = st.text_input("Description", value=default_desc)
            sign = st.text_input("Sign (Initials/Signature Code)", value="Signed")
            remark = st.text_input("Remark (Optional)")

        if st.button("Confirm Movement & Log"):
            if movement_type == "Take (Withdraw)":
                if current_qty >= qty_change:
                    new_balance = current_qty - qty_change
                    st.session_state.inventory.at[target_index, "Qty"] = new_balance

                    # Add row to logs
                    new_log = {
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Issued By": issued_by,
                        "Description": description,
                        "Items": selected_item,
                        "Qty": f"-{qty_change}",
                        "Unit": unit_val,
                        "Balance": new_balance,
                        "Received By": received_by,
                        "Sign": sign,
                        "Remark": remark,
                    }
                    st.session_state.transaction_logs = pd.concat(
                        [pd.DataFrame([new_log]), st.session_state.transaction_logs], ignore_index=True
                    )
                    st.session_state.last_updated = datetime.now().strftime("%d %B %Y, %I:%M %p")
                    st.success(f"Removed {qty_change} units of '{selected_item}'. Log recorded!")
                    st.rerun()
                else:
                    st.error(f"Cannot withdraw {qty_change} units. Only {current_qty} in stock!")
            else:
                new_balance = current_qty + qty_change
                st.session_state.inventory.at[target_index, "Qty"] = new_balance

                # Add row to logs
                new_log = {
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Issued By": issued_by,
                    "Description": description,
                    "Items": selected_item,
                    "Qty": f"+{qty_change}",
                    "Unit": unit_val,
                    "Balance": new_balance,
                    "Received By": received_by,
                    "Sign": sign,
                    "Remark": remark,
                }
                st.session_state.transaction_logs = pd.concat(
                    [pd.DataFrame([new_log]), st.session_state.transaction_logs], ignore_index=True
                )
                st.session_state.last_updated = datetime.now().strftime("%d %B %Y, %I:%M %p")
                st.success(f"Added {qty_change} units to '{selected_item}'. Log recorded!")
                st.rerun()

# --- OPTION 3: View In/Out Log Record ---
elif action == "View In/Out Log Record":
    st.subheader("📋 Marketing Collaterals In/Out Record")

    if st.session_state.transaction_logs.empty:
        st.info("No movements recorded yet.")
    else:
        st.dataframe(
            st.session_state.transaction_logs,
            column_config=log_column_config,
            use_container_width=True,
            hide_index=True,
        )

        # Export log to CSV
        csv_data = st.session_state.transaction_logs.to_csv(index=False)
        st.download_button(
            label="📥 Export Log Record to CSV",
            data=csv_data,
            file_name=f"Marketing_Collaterals_Log_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

# --- OPTION 4: Add New Item ---
elif action == "Add New Item":
    st.subheader("Add a New Item to Stock")

    with st.form("add_item_form", clear_on_submit=True):
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Initial Quantity", min_value=0, value=0)
        unit = st.text_input("Unit", value="Pcs")
        remark = st.text_input("Remark")

        submitted = st.form_submit_button("Add Item")

        if submitted:
            if not item_name.strip():
                st.error("Please enter an Item Name.")
            else:
                new_row = pd.DataFrame([{"Items": item_name, "Qty": quantity, "Unit": unit, "Remark": remark}])
                st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)

                # Log creation transaction
                new_log = {
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Issued By": "System Admin",
                    "Description": "New Item Initial Registration",
                    "Items": item_name,
                    "Qty": f"+{quantity}",
                    "Unit": unit,
                    "Balance": quantity,
                    "Received By": "Warehouse",
                    "Sign": "System",
                    "Remark": remark,
                }
                st.session_state.transaction_logs = pd.concat(
                    [pd.DataFrame([new_log]), st.session_state.transaction_logs], ignore_index=True
                )

                st.session_state.last_updated = datetime.now().strftime("%d %B %Y, %I:%M %p")
                st.success(f"Successfully added '{item_name}' to inventory.")
                st.rerun()

# --- Low Stock Warning ---
st.divider()
st.subheader("⚠️ Low Stock Summary (Qty ≤ 10)")
low_stock_df = st.session_state.inventory[st.session_state.inventory["Qty"] <= 10]

if not low_stock_df.empty:
    st.dataframe(
        low_stock_df[["Items", "Qty", "Unit", "Remark"]],
        column_config=inventory_column_config,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("All items have healthy stock levels (> 10).")
