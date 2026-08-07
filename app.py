from datetime import datetime
import io
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Marketing Collaterals Stock List", layout="wide")

# Initial inventory dataset matching 1st image format
INITIAL_DATA = [
    {"Items": "Rose Gold Vaccum Bottle Set", "Qty": 96, "Unit": "", "Remark": "Box Blue, Vaccum Bottle, Mobile bag & bag String and keychain"},
    {"Items": "Folding Umbrella", "Qty": 216, "Unit": "", "Remark": ""},
    {"Items": "UV Car Wind Sheild Umbrella", "Qty": 100, "Unit": "", "Remark": ""},
    {"Items": "Door Gift", "Qty": 50, "Unit": "", "Remark": "Recycle bag, notepad and keychain"},
    {"Items": "FCC Notebook Set", "Qty": 39, "Unit": "", "Remark": ""},
    {"Items": "FCC Paper bag", "Qty": 500, "Unit": "", "Remark": ""},
    {"Items": "Coffee Cup Gift Set", "Qty": 85, "Unit": "", "Remark": ""},
    {"Items": "Coffee Cup Gift Set's Bag", "Qty": 65, "Unit": "", "Remark": ""},
    {"Items": "Thadingyut Set", "Qty": 2, "Unit": "", "Remark": ""},
    {"Items": "White Mug", "Qty": 127, "Unit": "", "Remark": ""},
    {"Items": "Recycle Coffee Gift Set", "Qty": 10, "Unit": "", "Remark": ""},
    {"Items": "Mini Fan", "Qty": 53, "Unit": "", "Remark": ""},
    {"Items": "FCC Notepad", "Qty": 200, "Unit": "", "Remark": ""},
    {"Items": "FCC Keychain", "Qty": 200, "Unit": "", "Remark": ""},
    {"Items": "UV Car Wind Sheild", "Qty": 50, "Unit": "", "Remark": ""},
    {"Items": "Golf Umbrella", "Qty": 150, "Unit": "", "Remark": ""},
    {"Items": "Pullup Banner", "Qty": 6, "Unit": "", "Remark": ""},
    {"Items": "Pullup Banner", "Qty": 2, "Unit": "", "Remark": "Yangon Project (Used for MABA 10th year Anniversary Event)"},
    {"Items": "X Stand", "Qty": 3, "Unit": "", "Remark": "FCC MDY Logo"},
]

# Initialize Session States
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(INITIAL_DATA)

if "last_updated" not in st.session_state:
    st.session_state.last_updated = datetime.now().strftime("%d %B %Y")

if "transaction_logs" not in st.session_state:
    st.session_state.transaction_logs = pd.DataFrame(
        columns=["Date", "Issued By", "Description", "Items", "Qty", "Unit", "Balance", "Received By", "Sign", "Remark"]
    )

# Header
st.title("📦 Marketing Collaterals Stock System - FCC MDY")

# Navigation Sidebar
action = st.sidebar.radio(
    "Select Action",
    ["View Inventory", "Log Stock Movement (Take / Add)", "Reports & PNG Export", "Add New Item"],
)

# Function to generate PNG image from DataFrame styled like official sheet
def dataframe_to_png(df, title):
    # Add sequential 'No' column for official report layout
    report_df = df.copy()
    report_df.insert(0, "No", range(1, len(report_df) + 1))
    
    fig, ax = plt.subplots(figsize=(14, max(4, len(report_df) * 0.45)))
    ax.axis('tight')
    ax.axis('off')
    
    # Title Banner
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Render Table
    table = ax.table(
        cellText=report_df.values,
        colLabels=report_df.columns,
        cellLoc='center',
        loc='center'
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)
    
    # Style header row (Blue background matching image 2)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor('#C6D9F1')
            cell.set_text_props(weight='bold')
        cell.set_linewidth(0.8)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=200)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- OPTION 1: View Inventory ---
if action == "View Inventory":
    st.subheader("Current Stock Table")
    st.caption(f"Updated As Of: **{st.session_state.last_updated}**")

    st.dataframe(
        st.session_state.inventory,
        use_container_width=True,
        hide_index=True,
    )

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
            issued_by = st.text_input("Issued By")
            received_by = st.text_input("Received By")

        with col2:
            description = st.text_input("Description", value="Withdrawal" if movement_type == "Take (Withdraw)" else "Restock")
            sign = st.text_input("Sign", value="Signed")
            remark = st.text_input("Remark")

        if st.button("Confirm Movement & Log"):
            if movement_type == "Take (Withdraw)":
                if current_qty >= qty_change:
                    new_balance = current_qty - qty_change
                    st.session_state.inventory.at[target_index, "Qty"] = new_balance

                    new_log = {
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
                        [pd.DataFrame([new_log]), st.session_state.transaction_logs], ignore_index=True
                    )
                    st.session_state.last_updated = datetime.now().strftime("%d %B %Y")
                    st.success("Movement recorded successfully!")
                    st.rerun()
                else:
                    st.error(f"Cannot withdraw {qty_change} units. Only {current_qty} in stock!")
            else:
                new_balance = current_qty + qty_change
                st.session_state.inventory.at[target_index, "Qty"] = new_balance

                new_log = {
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
                    [pd.DataFrame([new_log]), st.session_state.transaction_logs], ignore_index=True
                )
                st.session_state.last_updated = datetime.now().strftime("%d %B %Y")
                st.success("Stock added successfully!")
                st.rerun()

# --- OPTION 3: Reports & PNG Export ---
elif action == "Reports & PNG Export":
    st.subheader("📊 Report Generation & PNG Export")

    report_type = st.selectbox(
        "Select Report Type",
        ["1. Total Items & Stock Summary Report", "2. Store In/Out Log Record Report"]
    )

    if report_type == "1. Total Items & Stock Summary Report":
        st.markdown(f"### Marketing Collaterals Stock List of FCC MDY - Updated As Of {st.session_state.last_updated}")
        st.dataframe(st.session_state.inventory, use_container_width=True, hide_index=True)

        # PNG Export
        png_title = f"Marketing Collaterals Stock List of FCC MDY - Updated As Of {st.session_state.last_updated}"
        png_file = dataframe_to_png(st.session_state.inventory, png_title)

        st.download_button(
            label="🖼️ Download Report as PNG",
            data=png_file,
            file_name=f"Stock_Summary_Report_{datetime.now().strftime('%Y%m%d')}.png",
            mime="image/png"
        )

    else:
        st.markdown("### Marketing Collaterals In/Out Record")
        if st.session_state.transaction_logs.empty:
            st.info("No transaction logs recorded yet.")
        else:
            st.dataframe(st.session_state.transaction_logs, use_container_width=True, hide_index=True)

            # PNG Export
            png_title = "Marketing Collaterals In/Out Record"
            png_file = dataframe_to_png(st.session_state.transaction_logs, png_title)

            st.download_button(
                label="🖼️ Download In/Out Log Report as PNG",
                data=png_file,
                file_name=f"Store_InOut_Record_{datetime.now().strftime('%Y%m%d')}.png",
                mime="image/png"
            )

# --- OPTION 4: Add New Item ---
elif action == "Add New Item":
    st.subheader("Add a New Item to Stock")

    with st.form("add_item_form", clear_on_submit=True):
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Initial Quantity", min_value=0, value=0)
        unit = st.text_input("Unit", value="")
        remark = st.text_input("Remark")

        submitted = st.form_submit_button("Add Item")

        if submitted:
            if not item_name.strip():
                st.error("Please enter an Item Name.")
            else:
                new_row = pd.DataFrame([{"Items": item_name, "Qty": quantity, "Unit": unit, "Remark": remark}])
                st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
                st.session_state.last_updated = datetime.now().strftime("%d %B %Y")
                st.success(f"Successfully added '{item_name}' to inventory.")
                st.rerun()
