import io
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


# Helper function to generate table images using Matplotlib (Streamlit Cloud safe)
def generate_report_png(df, title, is_log_report=False):
    report_df = df.copy()

    # Add sequential No column
    if "No" not in report_df.columns:
        report_df.insert(0, "No", range(1, len(report_df) + 1))

    # Add empty rows if DataFrame is empty to show empty table template
    if report_df.empty and is_log_report:
        blank_data = {col: [""] * 10 for col in report_df.columns}
        blank_data["No"] = list(range(1, 11))
        report_df = pd.DataFrame(blank_data)

    # Set figure height dynamically based on row count
    row_count = max(len(report_df), 5)
    fig_height = max(3.5, row_count * 0.4)
    fig_width = 14 if is_log_report else 10

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis("tight")
    ax.axis("off")

    # Title Banner
    plt.title(title, fontsize=14, fontweight="bold", pad=15)

    # Render Table
    table = ax.table(
        cellText=report_df.values,
        colLabels=report_df.columns,
        cellLoc="center",
        loc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9 if is_log_report else 10)
    table.scale(1.1, 1.6)

    # Style header row (Blue background matching image style)
    header_color = "#B8CCE4" if is_log_report else "#DCE6F1"
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(weight="bold")
        cell.set_linewidth(0.8)

    # Export figure to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    buf.seek(0)
    plt.close(fig)
    return buf


# --- REPORTS & PNG EXPORT PAGE ---
if action == "Reports & PNG Export":
    st.subheader("📑 Report Generation & PNG Export")

    report_type = st.radio(
        "Select Report Type",
        [
            "Stock List Summary Report (Pic 1 Style)",
            "In/Out Record Log Report (Pic 2 Style)",
        ],
        horizontal=True,
    )

    if report_type == "Stock List Summary Report (Pic 1 Style)":
        title_text = f"Marketing Collaterals Stock List of FCC MDY"
        st.markdown(f"### {title_text}")

        # Display dataframe in UI
        st.dataframe(
            st.session_state.inventory, use_container_width=True, hide_index=True
        )

        # Generate PNG
        png_bytes = generate_report_png(
            st.session_state.inventory, title_text, is_log_report=False
        )

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
            png_bytes = generate_report_png(
                empty_df, title_text, is_log_report=True
            )
        else:
            st.dataframe(
                st.session_state.transaction_logs,
                use_container_width=True,
                hide_index=True,
            )
            png_bytes = generate_report_png(
                st.session_state.transaction_logs,
                title_text,
                is_log_report=True,
            )

        st.download_button(
            label="🖼️ Export In/Out Log Report as PNG",
            data=png_bytes,
            file_name=f"InOut_Record_Report_{datetime.now().strftime('%Y%m%d')}.png",
            mime="image/png",
        )
