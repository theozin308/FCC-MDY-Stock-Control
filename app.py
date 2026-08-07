from datetime import datetime
import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Marketing Collaterals Stock System", layout="wide")

# Initial inventory dataset matching your live app items
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

if "transaction_logs" not in st.session_state:
    st.session_state.transaction_logs = pd.DataFrame(
        columns=["Date", "Issued By", "Description", "Items", "Qty", "Unit", "Balance", "Received By", "Sign", "Remark"]
    )

st.title("📦 Marketing Collaterals Stock List - FCC MDY")

# Sidebar
action = st.sidebar.radio(
    "Select Action",
    ["View Inventory", "Log Stock Movement (Take / Add)", "View In/Out Log Record", "Add New Item", "Reports & PNG Export"],
)

# Helper function to generate structured Plotly Table Figures
def create_report_figure(df, title, is_log_report=False):
    report_df = df.copy()
    
    # Add sequential No column
    report_df.insert(0, "No", range(1, len(report_df) + 1))
    
    # Column configuration and header styling
    headers = list(report_df.columns)
    header_color = "#B8CCE4" if is_log_report else "#DCE6F1"  # Light blue headers matching the image style
    
    # Define proportional column widths
    if is_log_report:
        column_widths = [5, 12, 12, 20, 15, 6, 6, 8, 12, 8, 20]
    else:
        column_widths = [6, 35, 10, 10, 39]

    fig = go.Figure(
        data=[
            go.Table(
                columnorder=list(range(1, len(headers) + 1)),
                columnwidth=column_widths,
                header=dict(
                    values=[f"<b>{h}</b>" for h in headers],
                    fill_color=header_color,
                    align="center",
                    font=dict(color="black", size=12),
                    line_color="black",
                    height=28
                ),
                cells=dict(
                    values=[report_df[col] for col in report_df.columns],
                    fill_color="white",
                    align=["center" if col in ["No", "Qty", "Unit", "Balance", "Sign", "Date"] else "left" for col in report_df.columns],
                    font=dict(color="black", size=11),
                    line_color="black",
                    height=24
                )
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            x=0.5,
            xanchor="center",
            font=dict(size=16)
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        width=1100 if is_log_report else 850,
        height=max(350, len(report_df) * 28 + 100)
    )
    
    return fig

# --- VIEW INVENTORY ---
if action == "View Inventory":
    st.subheader("Current Stock Table")
    st.caption(f"Updated As Of: **{st.session_state.last_updated}**")
    st.dataframe(st.session_state.inventory, use_container_width=True, hide_index=True)

# --- LOG MOVEMENT ---
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
                    st.session_state.transaction_logs = pd.concat([pd.DataFrame([new_log]), st.session_state.transaction_logs], ignore_index=True)
                    st.session_state.last_updated = datetime.now().strftime("%d %B %Y, %I:%M %p")
                    st.success("Movement logged successfully!")
                    st.rerun()
                else:
                    st.error(f"Cannot withdraw {qty_change} units. Only {current_qty} available.")
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
                st.session_state.transaction_logs = pd.concat([pd.DataFrame([new_log]), st.session_state.transaction_logs], ignore_index=True)
                st.session_state.last_updated = datetime.now().strftime("%d %B %Y, %I:%M %p")
                st.success("Restock logged successfully!")
                st.rerun()

# --- VIEW LOG RECORD ---
elif action == "View In/Out Log Record":
    st.subheader("📋 Marketing Collaterals In/Out Record")
    if st.session_state.transaction_logs.empty:
        st.info("No movements recorded yet.")
    else:
        st.dataframe(st.session_state.transaction_logs, use_container_width=True, hide_index=True)

# --- ADD NEW ITEM ---
elif action == "Add New Item":
    st.subheader("Add a New Item to Stock")
    with st.form("add_item_form", clear_on_submit=True):
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Initial Quantity", min_value=0, value=0)
        unit = st.text_input("Unit", value="Pcs")
        remark = st.text_input("Remark")

        if st.form_submit_button("Add Item"):
            if not item_name.strip():
                st.error("Please enter an Item Name.")
            else:
                new_row = pd.DataFrame([{"Items": item_name, "Qty": quantity, "Unit": unit, "Remark": remark}])
                st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
                st.session_state.last_updated = datetime.now().strftime("%d %B %Y, %I:%M %p")
                st.success(f"Added '{item_name}' to inventory.")
                st.rerun()

# --- REPORTS & PNG EXPORT PAGE ---
elif action == "Reports & PNG Export":
    st.subheader("📑 Report Generation & PNG Export")

    report_type = st.radio(
        "Select Report Type",
        ["Stock List Summary Report (Pic 1 Style)", "In/Out Record Log Report (Pic 2 Style)"],
        horizontal=True
    )

    if report_type == "Stock List Summary Report (Pic 1 Style)":
        title_text = "Marketing Collaterals Stock List of FCC MDY"
        fig = create_report_figure(st.session_state.inventory, title_text, is_log_report=False)
        
        st.plotly_chart(fig, use_container_width=True)

        img_bytes = fig.to_image(format="png", scale=2)
        st.download_button(
            label="🖼️ Export Stock List Report as PNG",
            data=img_bytes,
            file_name=f"Stock_List_Report_{datetime.now().strftime('%Y%m%d')}.png",
            mime="image/png"
        )

    else:
        title_text = "Marketing Collaterals In/Out Record"
        if st.session_state.transaction_logs.empty:
            st.info("No transaction logs recorded yet. Displaying blank structure template.")
            # Blank row structure matching Pic 2 layout
            empty_df = pd.DataFrame(columns=["Date", "Issued By", "Description", "Items", "Qty", "Unit", "Balance", "Received By", "Sign", "Remark"])
            fig = create_report_figure(empty_df, title_text, is_log_report=True)
        else:
            fig = create_report_figure(st.session_state.transaction_logs, title_text, is_log_report=True)
            
        st.plotly_chart(fig, use_container_width=True)

        img_bytes = fig.to_image(format="png", scale=2)
        st.download_button(
            label="🖼️ Export In/Out Log Report as PNG",
            data=img_bytes,
            file_name=f"InOut_Record_Report_{datetime.now().strftime('%Y%m%d')}.png",
            mime="image/png"
        )
