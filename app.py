from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Marketing Collaterals Stock List", layout="wide")

# Initial inventory dataset from image data
INITIAL_DATA = [
    {"Items": "Rose Gold Vaccum Bottle Set", "Qty": 96, "Unit": "Pcs", "Remark": "Box Blue, Vaccum Bottle, Mobile bag & bag String and keychain"},
    {"Items": "Folding Umbrella", "Qty": 216, "Unit": "Pcs", "Remark": ""},
    {"Items": "UV Car Wind Sheild Umbrella", "Qty": 100, "Unit": "Pcs", "Remark": ""},
    {"Items": "Door Gift", "Qty": 50, "Unit": "Pcs", "Remark": "Recycle bag, notepad and keychain"},
    {"Items": "FCC Notebook Set", "Qty": 39, "Unit": "Pcs", "Remark": ""},
    {"Items": "FCC Paper bag", "Qty": 500, "Unit": "Pcs", "Remark": ""},
    {"Items": "Coffee Cup Gift Set", "Qty": 85, "Unit": "Pcs", "Remark": ""},
    {"Items": "Coffee Cup Gift Set's Bag", "Qty": 65, "Unit": "Pcs", "Remark": ""},
    {"Items": "Thadingyut Set", "Qty": 2, "Unit": "Set", "Remark": ""},
    {"Items": "White Mug", "Qty": 127, "Unit": "Pcs", "Remark": ""},
    {"Items": "Recycle Coffee Gift Set", "Qty": 10, "Unit": "Set", "Remark": ""},
    {"Items": "Mini Fan", "Qty": 53, "Unit": "Pcs", "Remark": ""},
    {"Items": "FCC Notepad", "Qty": 200, "Unit": "Pcs", "Remark": ""},
    {"Items": "FCC Keychain", "Qty": 200, "Unit": "Pcs", "Remark": ""},
    {"Items": "UV Car Wind Sheild", "Qty": 50, "Unit": "Pcs", "Remark": ""},
    {"Items": "Golf Umbrella", "Qty": 150, "Unit": "Pcs", "Remark": ""},
    {"Items": "Pullup Banner", "Qty": 6, "Unit": "Pcs", "Remark": ""},
    {"Items": "Pullup Banner", "Qty": 2, "Unit": "Pcs", "Remark": "Yangon Project (Used for MABA 10th year Anniversary Event)"},
    {"Items": "X Stand", "Qty": 3, "Unit": "Pcs", "Remark": "FCC MDY Logo"},
]

# Initialize Session States
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(INITIAL_DATA)

if "last_updated" not in st.session_state:
    st.session_state.last_updated = datetime.now().strftime("%d %B %Y, %I:%M %p")

if "transaction_logs" not in st.session_state:
    st.session_state.transaction_logs = pd.DataFrame(
        columns=["No", "Date", "Issued By", "Description", "Items", "Qty", "Unit", "Balance", "Received By", "Sign", "Remark"]
    )

# Header
st.title("📦 Marketing Collaterals Management System")
st.caption(f"Updated As Of: **{st.session_state.last_updated}**")

# Column configurations
inventory_column_config = {
    "No": st.column_config.NumberColumn("No", width="small"),
    "Items": st.column_config.TextColumn("Items", width="large"),
    "Qty": st.column_config.NumberColumn("Qty", width="small"),
    "Unit": st.column_config.TextColumn("Unit", width="small"),
    "Remark": st.column_config.TextColumn("Remark", width="large"),
}

log_column_config = {
    "No": st.column_config.NumberColumn("No", width="small"),
    "Date": st.column_config.TextColumn("Date", width="small"),
    "Issued By": st.column_config.TextColumn("Issued By", width="medium"),
    "Description": st.column_config.TextColumn("Description", width="large"),
    "Items": st.column_config.TextColumn("Items", width="medium"),
    "Qty": st.column_config.TextColumn("Qty", width="small"),
    "Unit": st.column_config.TextColumn("Unit", width="small"),
    "Balance": st.column_config.NumberColumn("Balance", width="small"),
    "Received By": st.column_config.TextColumn("Received By", width="medium"),
    "Sign": st.column_config.TextColumn("Sign", width="small"),
    "Remark": st.column_config.TextColumn("Remark", width="large"),
}

# Navigation Sidebar
action = st.sidebar.radio(
    "Select Action",
    ["View Inventory", "Log Stock Movement (Take / Add)", "Add New Item", "📊 Reports & Records"],
)

# --- OPTION 1: View Inventory ---
if action == "View Inventory":
    st.subheader("Current Stock Table")
    display_df = st.session_state.inventory.copy()
    display_df.insert(0, "No", range(1, len(display_df) + 1))

    st.dataframe(
        display_df,
        column_config=inventory_column_config,
        use_container_width=True,
        hide_index=True,
    )

# --- OPTION 2: Log Stock Movement (Take / Add) ---
elif action == "Log Stock Movement (Take / Add)":
    st.subheader("Log Stock Movement")

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
            issued_by = st.text_input("Issued By")
            received_by = st.text_input("Received By")

        with col2:
            description = st.text_input("Description", value="Withdrawal" if movement_type == "Take (Withdraw)" else "Restock")
            sign = st.text_input("Sign", value="Signed")
            remark = st.text_input("Remark (Optional)")

        if st.button("Confirm Movement & Log"):
            log_no = len(st.session_state.transaction_logs) + 1

            if movement_type == "Take (Withdraw)":
                if current_qty >= qty_change:
                    new_balance = current_qty - qty_change
                    st.session_state.inventory.at[target_index, "Qty"] = new_balance

                    new_log = {
                        "No": log_no,
                        "Date": datetime.now().strftime("%Y-%m-%d"),
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
                        [st.session_state.transaction_logs, pd.DataFrame([new_log])], ignore_index=True
                    )
                    st.session_state.last_updated = datetime.now().strftime("%d %B %Y, %I:%M %p")
                    st.success(f"Removed {qty_change} units. Log created!")
                    st.rerun()
                else:
                    st.error(f"Cannot withdraw {qty_change} units. Only {current_qty} in stock!")
            else:
                new_balance = current_qty + qty_change
                st.session_state.inventory.at[target_index, "Qty"] = new_balance

                new_log = {
                    "No": log_no,
                    "Date": datetime.now().strftime("%Y-%m-%d"),
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
                    [st.session_state.transaction_logs, pd.DataFrame([new_log])], ignore_index=True
                )
                st.session_state.last_updated = datetime.now().strftime("%d %B %Y, %I:%M %p")
                st.success(f"Added {qty_change} units. Log created!")
                st.rerun()

# --- OPTION 3: Add New Item ---
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

                log_no = len(st.session_state.transaction_logs) + 1
                new_log = {
                    "No": log_no,
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Issued By": "System",
                    "Description": "New Item Creation",
                    "Items": item_name,
                    "Qty": f"+{quantity}",
                    "Unit": unit,
                    "Balance": quantity,
                    "Received By": "Store",
                    "Sign": "System",
                    "Remark": remark,
                }
                st.session_state.transaction_logs = pd.concat(
                    [st.session_state.transaction_logs, pd.DataFrame([new_log])], ignore_index=True
                )

                st.session_state.last_updated = datetime.now().strftime("%d %B %Y, %I:%M %p")
                st.success(f"Successfully added '{item_name}' to inventory.")
                st.rerun()

# --- OPTION 4: Reports Page ---
elif action == "📊 Reports & Records":
    st.header("📊 Stock & Transaction Reports")

    report_tab1, report_tab2 = st.tabs(["1. Total Items & Stock Report", "2. Store In/Out Log Record"])

    # TAB 1: Stock Report (Matching 1st Picture)
    with report_tab1:
        st.subheader("Marketing Collaterals Stock List of FCC MDY")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Unique Item Types", len(st.session_state.inventory))
        col2.metric("Total Stock Quantity", st.session_state.inventory["Qty"].sum())
        col3.metric("Low Stock Items (Qty ≤ 10)", len(st.session_state.inventory[st.session_state.inventory["Qty"] <= 10]))

        st.divider()

        stock_report_df = st.session_state.inventory.copy()
        stock_report_df.insert(0, "No", range(1, len(stock_report_df) + 1))

        st.dataframe(
            stock_report_df,
            column_config=inventory_column_config,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            label="📥 Export Stock Report to CSV",
            data=stock_report_df.to_csv(index=False),
            file_name=f"Stock_List_Report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    # TAB 2: In/Out Record (Matching 2nd Picture)
    with report_tab2:
        st.subheader("Marketing Collaterals In/Out Record")

        if st.session_state.transaction_logs.empty:
            st.info("No transaction records logged yet.")
        else:
            st.dataframe(
                st.session_state.transaction_logs,
                column_config=log_column_config,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                label="📥 Export In/Out Record to CSV",
                data=st.session_state.transaction_logs.to_csv(index=False),
                file_name=f"InOut_Log_Record_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
