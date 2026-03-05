import pandas as pd

# Define the columns based on your specific mapping
columns = [
    "Date", "Party Name", "Location", "Vehicle No", "Revenue", 
    "Vehicle Charge (F)", "Green Scrap (G)", "White Scrap (H)", 
    "Party Rate (I)", "Mill Rate (J)", "Report Amount (K)", 
    "Total Revenue (L)", "Purchase Amount (M)", "Total GST (N)", "Total Saving (O)"
]

# Create a blank dataframe with one empty row for structure
df_template = pd.DataFrame(columns=columns)

# File path for the user
template_name = "SCRAP_Automated_Template.xlsx"
df_template.to_excel(template_name, index=False)

# Provide the download button in the UI
with open(template_name, "rb") as f:
    st.download_button(
        label="📥 Download Excel Template with Formulas",
        data=f,
        file_name=template_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
