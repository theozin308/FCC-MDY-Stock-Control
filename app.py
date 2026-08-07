from datetime import datetime
import io
import textwrap
import matplotlib.pyplot as plt
import pandas as pd
import pytz
import streamlit as st

st.set_page_config(
    page_title="Marketing Collaterals Stock System",
    page_icon="📦",
    layout="wide",
)

MM_TZ = pytz.timezone("Asia/Yangon")


def get_mmt_now():
    return datetime.now(MM_TZ)


# Custom CSS styling
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #F8F9FA;
            border-right: 1px solid #E9ECEF;
        }
        [data-testid="stSidebar"] .stRadio label {
            font-size: 0.95rem !important;
            font-weight: 500 !important;
            color: #333333 !important;
            padding: 8px 12px !important;
            border-radius: 6px !important;
        }
        [data-testid="stSidebar"] [data-checked="true"] label {
            background-color: #2C3E50 !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Initial dataset setup
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
    {
        "Items": "Pullup Banner",
        "Qty": 2,
        "Unit": "Pcs",
        "Remark": "Yangon Project (Used for MABA 10th year Anniversary Event)",
    },
    {"Items": "X Stand", "Qty": 3, "Unit": "Pcs", "Remark": "FCC MDY Logo"},
]

if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(INITIAL_DATA)

if "last_updated_dt" not in st.session_state:
    st.session_state.last_updated_dt = get_mmt_now()

if "transaction_logs" not in st.session_state:
    st.session_state.transaction_logs = pd.DataFrame(
        columns=[
            "Log_ID",
            "Date",
            "Issued By",
            "Description",
            "Items",
            "Qty",
            "Unit",
            "Balance",
            "Received By",
            "Sign",
            "Remark",
        ]
    )

st.title("📦 Marketing Collaterals Stock List - FCC MDY")
formatted_last_updated = st.session_state.last_updated_dt.strftime(
    "%d %b %Y, %I:%M %p"
)

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/box-settings.png", width=64)
    st.markdown("### **FCC MDY Stock Manager**")
    st.caption("Inventory & Movement System")
    st.divider()

    action = st.radio(
        "NAVIGATION",
        [
            "📦 View Inventory",
            "🔄 Log Movement (Take / Add)",
            "📋 View In/Out Logs",
            "➕ Add New Item",
            "📑 Reports & PNG Export",
        ],
    )

    st.divider()
    st.caption("🟢 **Status:** Operational")
    st.caption(f"🕒 **Updated (MMT):** {formatted_last_updated}")
    st.caption("🏢 **Location:** FCC Mandalay (UTC+6:30)")


# PNG Export Generator
def generate_report_png(df, title, is_log_report=False):
    report_df = df.copy()
    if "Log_ID" in report_df.columns:
        report_df = report_df.drop(columns=["Log_ID"])

    if "No" not in report_df.columns:
        report_df.insert(0, "No", range(1, len(report_df) + 1))

    if report_df.empty and is_log_report:
        blank_data = {col: [""] * 8 for col in report_df.columns}
        blank_data["No"] = list(range(1, 9))
        report_df = pd.DataFrame(blank_data)

    if is_log_report:
        col_widths = [
            0.05,
            0.09,
            0.10,
            0.12,
            0.15,
            0.06,
            0.05,
            0.07,
            0.10,
            0.06,
            0.15,
        ]
        wrap_limits = {
            "Items": 18,
            "Description": 15,
            "Remark": 18,
            "Issued By": 12,
            "Received By": 12,
        }
        fig_width = 16
    else:
        col_widths = [0.08, 0.42, 0.10, 0.10, 0.30]
        wrap_limits = {"Items": 35, "Remark": 30}
        fig_width = 11

    wrapped_data = []
    for _, row in report_df.iterrows():
        new_row = []
        for col_name, val in row.items():
            val_str = str(val) if pd.notna(val) else ""
            if col_name in wrap_limits and len(val_str) > wrap_limits[col_name]:
                val_str = textwrap.fill(val_str, width=wrap_limits[col_name])
            new_row.append(val_str)
        wrapped_data.append(new_row)

    total_lines = sum(
        max(cell.count("\n") + 1 for cell in row) for row in wrapped_data
    )
    fig_height = max(4.0, (total_lines + 2) * 0.38)

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
    table.set_fontsize(8 if is_log_report else 9.5)
    table.scale(1.0, 1.8)

    left_align_cols = {
        "Items",
        "Description",
        "Remark",
        "Issued By",
        "Received By",
    }
    for (row_idx, col_idx), cell in table.get_celld().items():
        col_name = report_df.columns[col_idx]
        cell.set_edgecolor("#D0D7DE")
        cell.set_linewidth(0.7)
        if row_idx == 0:
            cell.set_facecolor("#2C3E50")
            cell.set_text_props(weight="bold", color="#FFFFFF", ha="center", va="center")
        else:
            cell.set_facecolor("#F8F9FA" if row_idx % 2 == 0 else "#FFFFFF")
            align = "left" if col_name in left_align_cols else "center"
            cell.set_text_props(ha=align, va="center", color="#212529")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.4, dpi=300)
    buf.seek(0)
    plt.close(fig)
    return buf


# --- View Inventory ---
if action == "📦 View Inventory":
    st.subheader("Current Stock Table")
    st.caption(f"Updated As Of: **{formatted_last_updated} (MMT)**")
    st.dataframe(
        st.session_state.inventory, use_container_width=True, hide_index=True
    )

# --- Log Movement ---
elif action == "🔄 Log Movement (Take / Add)":
    st.subheader("Log Stock Movement & In/Out Record")
    items = st.session_state.inventory["Items"].unique().tolist()

    if not items:
        st.warning("Inventory is empty.")
    else:
        with st.form("movement_form", clear_on_submit=True):
            selected_item = st.selectbox("Select Item", items)
            matching_rows = st.session_state.inventory[
                st.session_state.inventory["Items"] == selected_item
            ]

            if len(matching_rows) > 1:
                row_options = [
                    f"Remark: {row['Remark'] or 'None'} (Qty: {row['Qty']})"
                    for _, row in matching_rows.iterrows()
                ]
                selected_row_idx = st.selectbox(
                    "Select Specific Entry",
                    range(len(row_options)),
                    format_func=lambda x: row_options[x],
                )
                target_index = matching_rows.index[selected_row_idx]
            else:
                target_index = matching_rows.index[0]

            unit_val = st.session_state.inventory.at[target_index, "Unit"]
            current_qty = st.session_state.inventory.at[target_index, "Qty"]

            st.write(f"**Current Stock:** `{current_qty} {unit_val}`")
            movement_type = st.radio(
                "Movement Type",
                ["Take (Withdraw)", "Add (Restock)"],
                horizontal=True,
            )

            col1, col2 = st.columns(2)
            with col1:
                qty_change = st.number_input(
                    "Quantity", min_value=1, value=1, step=1
                )
                issued_by = st.text_input("Issued By")
                received_by = st.text_input("Received By")

            with col2:
                description = st.text_input(
                    "Description",
                    value="Withdrawal"
                    if movement_type == "Take (Withdraw)"
                    else "Restock",
                )
                sign = st.text_input("Sign", value="Signed")
                remark = st.text_input("Remark")

            submitted = st.form_submit_button("⚡ Submit Movement")

            if submitted:
                now_mmt = get_mmt_now()
                log_id = f"LOG-{int(now_mmt.timestamp()*1000)}"

                if movement_type == "Take (Withdraw)":
                    if current_qty >= qty_change:
                        new_balance = current_qty - qty_change
                        st.session_state.inventory.at[
                            target_index, "Qty"
                        ] = new_balance

                        new_log = {
                            "Log_ID": log_id,
                            "Date": now_mmt.strftime("%Y-%m-%d"),
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
                            [
                                pd.DataFrame([new_log]),
                                st.session_state.transaction_logs,
                            ],
                            ignore_index=True,
                        )
                        st.session_state.last_updated_dt = now_mmt

                        st.toast(
                            f"✅ Withdrew {qty_change} x '{selected_item}'. New Balance: {new_balance}",
                            icon="📤",
                        )
                        st.rerun()
                    else:
                        st.error(
                            f"Insufficient stock! Available: {current_qty}, Requested: {qty_change}"
                        )
                else:
                    new_balance = current_qty + qty_change
                    st.session_state.inventory.at[
                        target_index, "Qty"
                    ] = new_balance

                    new_log = {
                        "Log_ID": log_id,
                        "Date": now_mmt.strftime("%Y-%m-%d"),
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
                        [
                            pd.DataFrame([new_log]),
                            st.session_state.transaction_logs,
                        ],
                        ignore_index=True,
                    )
                    st.session_state.last_updated_dt = now_mmt

                    st.toast(
                        f"✅ Added {qty_change} x '{selected_item}'. New Balance: {new_balance}",
                        icon="📥",
                    )
                    st.rerun()

# --- View & Manage Logs (With Delete Log & Stock Reset) ---
elif action == "📋 View In/Out Logs":
    st.subheader("📋 Marketing Collaterals In/Out Record")

    if st.session_state.transaction_logs.empty:
        st.info("No movements recorded yet.")
    else:
        st.caption("Need to revert a mistake? Delete a log below to automatically restore stock quantities.")
        
        # Display each log entry with an Action/Delete button
        logs_df = st.session_state.transaction_logs.copy()
        
        # Iterate over logs row by row
        for idx, row in logs_df.iterrows():
            cols = st.columns([1, 1.2, 1.2, 2, 0.8, 0.6, 0.8, 1.2, 1, 1.5, 1])
            
            with cols[0]:
                st.write(f"**{row['Date']}**")
            with cols[1]:
                st.write(row["Issued By"])
            with cols[2]:
                st.write(row["Description"])
            with cols[3]:
                st.write(f"**{row['Items']}**")
            with cols[4]:
                st.write(f"`{row['Qty']}`")
            with cols[5]:
                st.write(row["Unit"])
            with cols[6]:
                st.write(f"**{row['Balance']}**")
            with cols[7]:
                st.write(row["Received By"])
            with cols[8]:
                st.write(row["Sign"])
            with cols[9]:
                st.write(row["Remark"] if row["Remark"] else "-")
            with cols[10]:
                if st.button("🗑️ Delete", key=f"del_{row['Log_ID']}_{idx}"):
                    item_name = row["Items"]
                    qty_str = str(row["Qty"])
                    
                    # Determine adjustment value (reversing the transaction)
                    if qty_str.startswith("+"):
                        val = int(qty_str.replace("+", ""))
                        adj = -val  # Reverse addition by subtracting
                    elif qty_str.startswith("-"):
                        val = int(qty_str.replace("-", ""))
                        adj = val   # Reverse withdrawal by adding back
                    else:
                        adj = 0

                    # Adjust stock in inventory
                    item_idx = st.session_state.inventory[st.session_state.inventory["Items"] == item_name].index
                    if not item_idx.empty:
                        target = item_idx[0]
                        st.session_state.inventory.at[target, "Qty"] += adj
                        new_qty = st.session_state.inventory.at[target, "Qty"]
                    else:
                        new_qty = "N/A"

                    # Remove the log row
                    st.session_state.transaction_logs = st.session_state.transaction_logs[
                        st.session_state.transaction_logs["Log_ID"] != row["Log_ID"]
                    ].reset_index(drop=True)

                    st.session_state.last_updated_dt = get_mmt_now()
                    st.toast(f"🗑️ Deleted log! Stock for '{item_name}' adjusted by {adj:+d} (Current: {new_qty})", icon="🔄")
                    st.rerun()

# --- Add New Item ---
elif action == "➕ Add New Item":
    st.subheader("Add a New Item to Stock")
    with st.form("add_item_form", clear_on_submit=True):
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Initial Quantity", min_value=0, value=0)
        unit = st.text_input("Unit", value="Pcs")
        remark = st.text_input("Remark")

        submitted = st.form_submit_button("⚡ Create New Item")

        if submitted:
            if not item_name.strip():
                st.error("Please enter an Item Name.")
            else:
                new_row = pd.DataFrame(
                    [
                        {
                            "Items": item_name.strip(),
                            "Qty": quantity,
                            "Unit": unit.strip(),
                            "Remark": remark.strip(),
                        }
                    ]
                )
                st.session_state.inventory = pd.concat(
                    [st.session_state.inventory, new_row], ignore_index=True
                )
                st.session_state.last_updated_dt = get_mmt_now()

                st.toast(
                    f"🎉 Successfully added new item: '{item_name}' ({quantity} {unit})",
                    icon="✨",
                )
                st.rerun()

# --- Reports & PNG Export ---
elif action == "📑 Reports & PNG Export":
    st.subheader("📑 Report Generation & PNG Export")
    report_type = st.radio(
        "Select Report Type",
        [
            "Stock List Summary Report (Pic 1 Style)",
            "In/Out Record Log Report (Pic 2 Style)",
        ],
        horizontal=True,
    )

    now_mmt = get_mmt_now()

    if report_type == "Stock List Summary Report (Pic 1 Style)":
        title_text = "Marketing Collaterals Stock List of FCC MDY"
        st.markdown(f"### {title_text}")
        st.dataframe(
            st.session_state.inventory, use_container_width=True, hide_index=True
        )

        png_bytes = generate_report_png(
            st.session_state.inventory, title_text, is_log_report=False
        )
        st.download_button(
            label="🖼️ Export Stock List Report as PNG",
            data=png_bytes,
            file_name=f"Stock_List_Report_{now_mmt.strftime('%Y%m%d')}.png",
            mime="image/png",
        )
    else:
        title_text = "Marketing Collaterals In/Out Record"
        st.markdown(f"### {title_text}")

        # Drop internal ID column before displaying/exporting
        display_logs = st.session_state.transaction_logs.drop(columns=["Log_ID"], errors="ignore")

        if display_logs.empty:
            st.info(
                "No transaction logs recorded yet. Displaying blank structure template in PNG export."
            )
            empty_df = pd.DataFrame(
                columns=[
                    "Date",
                    "Issued By",
                    "Description",
                    "Items",
                    "Qty",
                    "Unit",
                    "Balance",
                    "Received By",
                    "Sign",
                    "Remark",
                ]
            )
            png_bytes = generate_report_png(empty_df, title_text, is_log_report=True)
        else:
            st.dataframe(
                display_logs,
                use_container_width=True,
                hide_index=True,
            )
            png_bytes = generate_report_png(
                display_logs, title_text, is_log_report=True
            )

        st.download_button(
            label="🖼️ Export In/Out Log Report as PNG",
            data=png_bytes,
            file_name=f"InOut_Record_Report_{now_mmt.strftime('%Y%m%d')}.png",
            mime="image/png",
        )
