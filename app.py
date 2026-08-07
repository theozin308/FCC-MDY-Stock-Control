from datetime import datetime
import io
import textwrap
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Marketing Collaterals Stock System", layout="wide")

# ---------------------------------------------------------
# 1. INITIAL DATASET & SESSION STATE INITIALIZATION
# ---------------------------------------------------------
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

if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(INITIAL_DATA)

if "last_updated" not in st.session_state:
    st.session_state.last_updated = datetime.now().strftime("%d %B %Y, %I:%M %p")

if "transaction_logs" not in st.session_state:
    st.session_state.transaction_logs = pd.DataFrame(
        columns=["Date", "Issued By", "Description", "Items", "Qty", "Unit", "Balance", "Received By", "Sign", "Remark"]
    )

st.title("📦 Marketing Collaterals Stock List - FCC MDY")

# ---------------------------------------------------------
# 2. SIDEBAR NAVIGATION
# ---------------------------------------------------------
action = st.sidebar.radio(
    "Select Action",
    [
        "View Inventory",
        "Log Stock Movement (Take / Add)",
        "View In/Out Log Record",
        "Add New Item",
        "Reports & PNG Export",
    ],
)


# ---------------------------------------------------------
# 3. HELPER FUNCTION: GENERATE PNG TABLE REPORT
# ---------------------------------------------------------
def generate_report_png(df, title, is_log_report=False):
    report_df = df.copy()

    # Add sequential 'No' column if missing
    if "No" not in report_df.columns:
        report_df.insert(0, "No", range(1, len(report_df) + 1))

    # Add blank template rows if transaction log is empty
    if report_df.empty and is_log_report:
        blank_data = {col: [""] * 8 for col in report_df.columns}
        blank_data["No"] = list(range(1, 9))
        report_df = pd.DataFrame(blank_data)

    # 1. Column Widths & Wrap Constraints
    if is_log_report:
        col_widths = [0.05, 0.09, 0.10, 0.12, 0.15, 0.06, 0.05, 0.07, 0.10, 0.06, 0.15]
        wrap_limits = {"Items": 18, "Description": 15, "Remark": 18, "Issued By": 12, "Received By": 12}
        fig_width = 16
    else:
        col_widths = [0.08, 0.42, 0.10, 0.10, 0.30]
        wrap_limits = {"Items": 35, "Remark": 30}
        fig_width = 11

    # 2. Text Wrapping
    wrapped_data = []
    for _, row in report_df.iterrows():
        new_row = []
        for col_name, val in row.items():
            val_str = str(val) if pd.notna(val) else ""
            if col_name in wrap_limits and len(val_str) > wrap_limits[col_name]:
                val_str = textwrap.fill(val_str, width=wrap_limits[col_name])
            new_row.append(val_str)
        wrapped_data.append(new_row)

    # Calculate height based on line counts from text wrapping
    total_lines = sum(max(cell.count("\n") + 1 for cell in row) for row in wrapped_data)
    fig_height = max(4.0, (total_lines + 2) * 0.38)

    # 3. Figure Creation
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)
    ax.axis("off")

    plt.title(title, fontsize=15, fontweight="bold", pad=20, color="#1A2530")

    table = ax.table(
        cellText=wrapped_data,
        colLabels=report_df.columns,
        colWidths=col_widths,
        loc="center",
    )

    table.auto_set_font_size(False)
    font_size = 8 if is_log_report else 9.5
    table.set_fontsize(font_size)
    table.scale(1.0, 1.8)

    # 4. Styling & Alignment
    header_bg = "#2C3E50"  # Dark Slate Blue
    header_fg = "#FFFFFF"  # White Text
    row_even_bg = "#F8F9FA"  # Light Gray
    row_odd_bg = "#FFFFFF"  # Pure White

    left_align_cols = {"Items", "Description", "Remark", "Issued By", "Received By"}

    for (row_idx, col_idx), cell in table.get_celld().items():
        col_name = report_df.columns[col_idx]

        cell.set_edgecolor("#D0D7DE")
        cell.set_linewidth(0.7)

        if row_idx == 0:
            cell.set_facecolor(header_bg)
            cell.set_text_props(weight="bold", color=header_fg, ha="center", va="center")
        else:
            bg_color = row_even_bg if row_idx % 2 == 0 else row_odd_bg
            cell.set_facecolor(bg_color)

            align = "left" if col_name in left_align_cols else "center"
            cell.set_text_props(ha=align, va="center", color="#212529")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.4, dpi=300)
    buf.seek(0)
    plt.close(fig)
    return buf


# ---------------------------------------------------------
# 4. PAGE ROUTING & LOGIC
# ---------------------------------------------------------

# --- View Inventory ---
if action == "View Inventory":
    st.subheader("Current Stock Table")
    st.caption(f"Updated As Of: **{st.session_state.last_updated}**")
    st.dataframe(st.session_state.inventory, use_container_width=True, hide_index=True)

# --- Log Stock Movement ---
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

# --- View Log Record ---
elif action == "View In/Out Log Record":
    st.subheader("📋 Marketing Collaterals In/Out Record")
    if st.session_state.transaction_logs.empty:
        st.info("No movements recorded yet.")
    else:
        st.dataframe(st.session_state.transaction_logs, use_container_width=True, hide_index=True)

# --- Add New Item ---
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

# --- Reports & PNG Export ---
elif action == "Reports & PNG Export":
    st.subheader("📑 Report Generation & PNG Export")

    report_type = st.radio(
        "Select Report Type",
        ["Stock List Summary Report (Pic 1 Style)", "In/Out Record Log Report (Pic 2 Style)"],
        horizontal=True,
    )

    if report_type == "Stock List Summary Report (Pic 1 Style)":
        title_text = "Marketing Collaterals Stock List of FCC MDY"
        st.markdown(f"### {title_text}")

        st.dataframe(st.session_state.inventory, use_container_width=True, hide_index=True)

        png_bytes = generate_report_png(st.session_state.inventory, title_text, is_log_report=False)

        st.download_button(
            label="🖼️ Export Stock List Report as PNG",
            data=png_bytes,
            file_name=f"Stock_List_Report_{datetime.now().strftime('%Y%m%d')}.png",
            mime="image/png",
        )

    else:
        title_text = "Marketing Collaterals In/Out Record"
        st.markdown(f"### {title_text}")

        if st.session_state.transaction_logs.empty:
            st.info("No transaction logs recorded yet. Displaying blank structure template in PNG export.")
            empty_df = pd.DataFrame(
                columns=["Date", "Issued By", "Description", "Items", "Qty", "Unit", "Balance", "Received By", "Sign", "Remark"]
            )
            png_bytes = generate_report_png(empty_df, title_text, is_log_report=True)
        else:
            st.dataframe(st.session_state.transaction_logs, use_container_width=True, hide_index=True)
            png_bytes = generate_report_png(st.session_state.transaction_logs, title_text, is_log_report=True)

        st.download_button(
            label="🖼️ Export In/Out Log Report as PNG",
            data=png_bytes,
            file_name=f"InOut_Record_Report_{datetime.now().strftime('%Y%m%d')}.png",
            mime="image/png",
        )
