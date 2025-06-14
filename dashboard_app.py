import streamlit as st
import pandas as pd
import altair as alt
import os
import numpy as np
from datetime import datetime, timedelta
import bcrypt # For password hashing

# --- DEBUGGING SECTION ---
# This section helps verify file paths on deployment.
# REMOVE THIS SECTION ONCE THE FILE NOT FOUND ERROR IS RESOLVED.
st.markdown("## Debugging File Paths")
try:
    current_dir = os.getcwd()
    st.write(f"Current working directory: `{current_dir}`")
    files_in_dir = os.listdir(current_dir)
    st.write("Files found in current directory:")
    for f in files_in_dir:
        st.write(f"- `{f}`")
    
    # Check specifically for WASAC file
    if 'WASAC_kpi_data.csv' in files_in_dir:
        st.success("✅ `WASAC_kpi_data.csv` found in the current directory!")
    else:
        st.error("❌ `WASAC_kpi_data.csv` NOT found in the current directory.")

    # List files in the directory containing the script if it's different
    script_dir = os.path.dirname(__file__)
    if script_dir and script_dir != current_dir:
        st.write(f"Script directory: `{script_dir}`")
        files_in_script_dir = os.listdir(script_dir)
        st.write("Files found in script directory:")
        for f in files_in_script_dir:
            st.write(f"- `{f}`")
        if 'WASAC_kpi_data.csv' in files_in_script_dir:
            st.success("✅ `WASAC_kpi_data.csv` found in the script directory!")
        else:
            st.error("❌ `WASAC_kpi_data.csv` NOT found in the script directory.")

except Exception as e:
    st.error(f"Error during file system debugging: {e}")
st.markdown("---")
# --- END DEBUGGING SECTION ---


# --- Configuration and Data Loading ---

# Define the companies and their corresponding CSV filenames
COMPANIES = {
    "EUCL": "EUCL_kpi_data.csv",
    "EDCL": "EDCL_kpi_data.csv",
    "WASAC": "WASAC_kpi_data.csv",
    "King Faisal Hospital": "King_Faisal_Hospital_kpi_data.csv",
    "Rwanda Medical Supply": "Rwanda_Medical_Supply_kpi_data.csv"
}

# Define Company Branding (Logo URLs and Primary Colors)
COMPANY_BRANDING = {
    "EUCL": {
        "logo_url": "https://placehold.co/100x100/008000/FFFFFF?text=EUCL",
        "primary_color": "#008000" # Dark Green, common in REG branding
    },
    "EDCL": {
        "logo_url": "https://placehold.co/100x100/004F9F/FFFFFF?text=EDCL",
        "primary_color": "#004F9F" # Strong Blue, common in REG branding
    },
    "WASAC": {
        "logo_url": "https://placehold.co/100x100/007BFF/FFFFFF?text=WASAC",
        "primary_color": "#007BFF" # Standard Blue for water
    },
    "King Faisal Hospital": {
        "logo_url": "https://placehold.co/100x100/1E90FF/FFFFFF?text=KFH",
        "primary_color": "#1E90FF" # Dodger Blue, common for healthcare
    },
    "Rwanda Medical Supply": {
        "logo_url": "https://placehold.co/100x100/28a745/FFFFFF?text=RMS",
        "primary_color": "#28a745" # Green, common in medical supply branding
    }
}

# Define Company Profiles (Mandate, Vision, Strategic Plan Summary)
COMPANY_PROFILES = {
    "EUCL": {
        "mandate": "Providing energy utility services in Rwanda through operations and maintenance of existing generation plants, transmission and distribution networks, and retail of electricity to end-users.",
        "vision": "To be the leading regional provider of innovative and sustainable energy solutions for national development.",
        "strategic_plan": "Focuses on improving efficiency in utility operations, progressive system loss reduction, enhancing billing and collection efficiency, improving network reliability and quality of service, and optimizing generation capacity to meet growing demand."
    },
    "EDCL": {
        "mandate": "Increasing investment in and development of new energy generation projects in a timely and cost-efficient manner, developing appropriate transmission infrastructure, and planning/executing energy access projects to meet national targets.",
        "vision": "To be the leading regional provider of innovative and sustainable energy solutions for national development.",
        "strategic_plan": "Aims to expand energy supply capacity efficiently, develop least-cost energy development plans, direct the Electricity Access Roll-Out Program, and undertake economic/technical studies for infrastructure development."
    },
    "WASAC": {
        "mandate": "Responsible for developing water and sanitation projects, implementing government-led initiatives, and providing safe and reliable water and sanitation services across Rwanda.",
        "vision": "Providing safe and reliable water and sanitation services.",
        "strategic_plan": "Focuses on strengthening governance of water resources, preventing soil erosion, ensuring sufficient quality water availability, enhancing resilience to flooding, and strengthening organizational capacity and financial sustainability."
    },
    "King Faisal Hospital": {
        "mandate": "Provide specialized healthcare in East and Central Africa, focusing on clinical excellence, efficiency, and quality in health service delivery.",
        "vision": "A center of excellence in health service provision, clinical education and research.",
        "strategic_plan": "Aims to harness human capital, modern technology, and research capacity to improve patient outcomes, enhance corporate communication, and foster a patient-centered culture. Contributes to Rwanda's Health Sector Strategic Plan priorities."
    },
    "Rwanda Medical Supply": {
        "mandate": "Ensuring the availability and accessibility of quality essential medicines, medical devices, and health commodities throughout Rwanda.",
        "vision": "To be a world-class, self-sustaining medical supply chain organization, ensuring health security for all Rwandans.",
        "strategic_plan": "Prioritizes strengthening stakeholder engagement and customer satisfaction, improving order fulfillment rate, enhancing financial and operational efficiency, and adhering to quality standards and regulations."
    }
}

# Define KPIs to plot for each company within their respective tabs
# This structure helps organize which KPIs appear under which tab.
# Only lists KPIs that are expected to be plotted as line charts (trends).
COMPANY_TAB_KPIS = {
    "EUCL": {
        "Overview": ['Electricity Access Rate (%)', 'System Loss Rate (%)', 'Average Outage Duration (SAIDI)'],
        "Operational Efficiency": [
            'System Loss Rate (%)', 'Average Outage Duration (SAIDI)',
            'Customer Complaints Resolution Time (days)'
        ],
        "Financials & Projects": [
            'Revenue', 'Expenses', 'EBITDA',
            'Billing Efficiency (%)', 'Collection Efficiency (%)',
            'Number of New Connections (per quarter)', 'Operational Expenditure per kWh', 'Revenue per kWh Sold'
        ]
    },
    "EDCL": {
        "Overview": ['New Generation Capacity Developed (MW)', 'Projects Delivered On-Time (%)', '% of Funds Disbursed (Capex)'],
        "Project Performance": [
            'New Generation Capacity Developed (MW)', 'Projects Delivered On-Time (%)'
        ],
        "Financial & Compliance": [
            'Revenue', 'Expenses', 'EBITDA',
            'Cost per MW Installed', '% of Funds Disbursed (Capex)', 'Loan Absorption Rate (%)'
        ]
    },
    "WASAC": {
        "Overview": ['Water Coverage Rate (%)', 'Non-Revenue Water (NRW %)', 'Average Water Outage Duration'],
        "Water Supply & Quality": [
            'Non-Revenue Water (NRW %)', '% of Water Quality Tests Passed'
        ],
        "Sanitation & Assets": [
            'Sewerage Network Coverage (%)', 'Average Water Outage Duration'
        ]
    },
    "King Faisal Hospital": {
        "Overview": ['Bed Occupancy Rate (%)', 'Average Length of Stay (ALOS)', 'Outpatient Visits per Month'],
        "Patient Care Metrics": [
            'Bed Occupancy Rate (%)', 'Average Length of Stay (ALOS)', 'Mortality Rate', 'Patient Satisfaction Score'
        ],
        "Operational & Financial": [
            'Revenue', 'Expenses', 'EBITDA',
            'Outpatient Visits per Month', 'Insurance Claims Reimbursement Rate (%)'
        ]
    },
    "Rwanda Medical Supply": {
        "Overview": ['Stock Availability Rate (%)', 'Order Fulfillment Rate (%)', 'Inventory Turnover Ratio'],
        "Supply Chain Efficiency": [
            'Stock Availability Rate (%)', 'Order Fulfillment Rate (%)',
            '% of Expired Stock'
        ],
        "Financials & Quality": [
            'Revenue', 'Expenses', 'EBITDA',
            'Health Facility Satisfaction Score'
        ]
    }
}


# --- Helper Function for Visualization ---
def create_line_chart(df, x_col, y_col, title, y_format=',.2f', target_value=None, line_color=None, x_axis_type='T'):
    """Creates an interactive Altair line chart with optional target line and custom color."""
    base = alt.Chart(df).encode(
        x=alt.X(f'{x_col}:{x_axis_type}', title='Date' if x_axis_type == 'T' else x_col),
        y=alt.Y(f'{y_col}:Q', title=y_col),
        tooltip=[x_col, alt.Tooltip(f'{y_col}:Q', format=y_format)]
    ).properties(
        title=title
    )

    line_chart = base.mark_line(point=True, color=line_color if line_color else 'steelblue').interactive()

    if target_value is not None:
        target_line = alt.Chart(pd.DataFrame({y_col: [target_value]})).mark_rule(color='red', strokeDash=[5,5]).encode(
            y=alt.Y(f'{y_col}:Q')
        )
        return (line_chart + target_line).resolve_scale(y='independent')
    return line_chart

def format_currency_value(value):
    """Formats a currency value into K, M, B, or T (Thousands, Millions, Billions, Trillions)."""
    if pd.isna(value):
        return "N/A"
    
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        formatted_value = f"{value / 1_000_000_000_000:.1f} T"
    elif abs_value >= 1_000_000_000:
        formatted_value = f"{value / 1_000_000_000:.1f} B"
    elif abs_value >= 1_000_000:
        formatted_value = f"{value / 1_000_000:.1f} M"
    elif abs_value >= 1_000:
        formatted_value = f"{value / 1_000:.1f} K"
    else:
        formatted_value = f"{value:,.0f}" # Keep smaller numbers as-is

    return formatted_value


# --- Data Loading with Synthetic Regional Data Generation ---
@st.cache_data # Cache the data loading for better performance
def load_all_kpi_data():
    """
    Loads all generated KPI data from CSV files and adds synthetic governance data.
    Ensures numeric columns are correctly typed.
    """
    data_dict = {}
    regions = ['Kigali City', 'Eastern Province', 'Northern Province', 'Southern Province', 'Western Province']
    
    current_year = datetime.now().year
    
    for company_name, filename in COMPANIES.items():
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Explicitly convert known numeric columns to numeric, coercing errors
            # This list includes all KPIs that are expected to be numeric across all companies
            numeric_cols = [
                'Revenue', 'Expenses', 'EBITDA', 'Cost per MW Installed', 'Electricity Access Rate (%)',
                'System Loss Rate (%)', 'Average Outage Duration (SAIDI)', 'Customer Complaints Resolution Time (days)',
                'Billing Efficiency (%)', 'Collection Efficiency (%)', 'Number of New Connections (per quarter)',
                'Operational Expenditure per kWh', 'Revenue per kWh Sold', 'New Generation Capacity Developed (MW)',
                'Projects Delivered On-Time (%)', '% of Funds Disbursed (Capex)', 'Loan Absorption Rate (%)',
                'Water Coverage Rate (%)', 'Non-Revenue Water (NRW %)', 'Average Water Outage Duration',
                '% of Water Quality Tests Passed', 'Sewerage Network Coverage (%)', 'Asset Maintenance Compliance (%)',
                'Bed Occupancy Rate (%)', 'Average Length of Stay (ALOS)', 'Mortality Rate', 'Patient Satisfaction Score',
                'Outpatient Visits per Month', 'Insurance Claims Reimbursement Rate (%)', 'Stock Availability Rate (%)',
                'Order Fulfillment Rate (%)', 'Cold Chain Compliance Rate (%)', '% of Expired Stock',
                'Health Facility Satisfaction Score', 'Inventory Turnover Ratio'
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce') # Convert to numeric, turn errors into NaN
            
            # Add synthetic governance data
            if 'Date' in df.columns and not df.empty:
                years_in_data = df['Date'].dt.year.unique()
            else:
                years_in_data = range(2020, current_year + 1) # Default years if no data yet

            governance_data = []
            for year in years_in_data:
                board_completeness = np.clip(np.random.normal(95, 3), 80, 100)
                audit_opinion = np.random.choice([1, 0], p=[0.9, 0.1]) # 1 for Clean, 0 for Qualified
                internal_audit_score = np.clip(np.random.normal(80, 7), 60, 100)
                
                governance_data.append({
                    'Year': year,
                    'Board Completeness (%)': board_completeness,
                    'Audit Opinion': audit_opinion,
                    'Internal Audit Score (%)': internal_audit_score
                })
            
            governance_df = pd.DataFrame(governance_data)
            governance_df['Year'] = governance_df['Year'].astype(int)

            data_dict[company_name] = df
            data_dict[f"{company_name}_Governance"] = governance_df

            # --- Synthetic Regional Data Generation ---
            if company_name == "EUCL" and 'Region' not in df.columns:
                regional_eucl_data = []
                for date in df['Date'].unique():
                    for region in regions:
                        base_access = np.random.normal(70, 5) + (df[df['Date'] == date].index.values[0] / 60) * 20
                        if region == 'Kigali City':
                            access_rate = np.clip(base_access + np.random.normal(10, 2), 0, 100)
                        else:
                            access_rate = np.clip(base_access + np.random.normal(-5, 3), 0, 100)
                        regional_eucl_data.append({'Date': date, 'Region': region, 'Electricity Access Rate (%)': access_rate})
                data_dict[company_name + "_Regional_Access"] = pd.DataFrame(regional_eucl_data)

            if company_name == "WASAC" and 'Region' not in df.columns:
                regional_wasac_data = []
                for date in df['Date'].unique():
                    for region in regions:
                        base_coverage = np.random.normal(60, 5) + (df[df['Date'] == date].index.values[0] / 60) * 15
                        if region == 'Kigali City':
                            coverage_rate = np.clip(base_coverage + np.random.normal(15, 3), 0, 100)
                        else:
                            coverage_rate = np.clip(base_coverage + np.random.normal(-10, 4), 0, 100)
                        regional_wasac_data.append({'Date': date, 'Region': region, 'Water Coverage Rate (%)': coverage_rate})
                data_dict[company_name + "_Regional_Coverage"] = pd.DataFrame(regional_wasac_data)

        else:
            st.error(f"Error: Data file not found for {company_name} at {filename}. "
                     "Please ensure the generate_kpi_data.py script has been run "
                     "and the CSV files are in the same directory as this Streamlit app.")
            return None
    return data_dict

# Load the data
all_kpi_data = load_all_kpi_data()

# Exit if data loading failed
if all_kpi_data is None:
    st.stop()

# --- Streamlit Application Layout ---

st.set_page_config(
    page_title="National KPI Dashboard (MINECOFIN)",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 National KPI Dashboard")
st.markdown("### Strategic Oversight for Key Rwandan Entities")

# Initialize session state for authentication if not already present
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state: # Reverted to username
    st.session_state.username = None
if 'show_register_form' not in st.session_state:
    st.session_state.show_register_form = False

# In-memory user database (username: hashed_password) - FOR DEMO ONLY
# This data is NOT persistent across Streamlit app restarts.
if 'users_db' not in st.session_state:
    # Example user: username 'admin', password 'adminpass'
    st.session_state.users_db = {
        "admin": bcrypt.hashpw("adminpass".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    }

def login_user(username, password):
    if username in st.session_state.users_db:
        hashed_password = st.session_state.users_db[username]
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
            st.rerun() # Force rerun after successful login
        else:
            st.error("Invalid username or password.")
    else:
        st.error("Invalid username or password.")

def register_user(username, password, confirm_password):
    if username in st.session_state.users_db:
        st.error("Username already exists. Please choose a different one.")
    else:
        if password == confirm_password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            st.session_state.users_db[username] = hashed_password
            st.success("Registration successful! You can now log in.")
            st.session_state.show_register_form = False # Switch back to login form
            st.rerun() # Force rerun after successful registration
        else:
            st.error("Passwords do not match.")

def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.show_register_form = False
    st.success("You have been logged out.")
    st.rerun() # Force rerun after logout

# --- Authentication UI ---
if not st.session_state.authenticated:
    st.sidebar.empty() # Clear other sidebar content when not logged in
    st.markdown("## Access Required")
    st.info("Please log in or register to view the dashboard.")

    if st.session_state.show_register_form:
        st.markdown("### Register New Account")
        with st.form("register_form"):
            new_username = st.text_input("New Username", key="reg_username")
            new_password = st.text_input("Create Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
            register_button = st.form_submit_button("Register")

            if register_button:
                if new_username and new_password and confirm_password:
                    register_user(new_username, new_password, confirm_password)
                else:
                    st.error("Please fill in all fields.")
        
        # Using a button outside the form for navigation is fine with on_click
        st.button("Back to Login", on_click=lambda: st.session_state.update(show_register_form=False))
    else: # Login form
        st.markdown("### Login")
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username_input")
            password = st.text_input("Password", type="password", key="login_password_input")
            login_button = st.form_submit_button("Login")

            if login_button:
                if username and password:
                    login_user(username, password)
                else:
                    st.error("Please enter username and password.")
        
        # Button to switch to registration form
        st.button("Register New Account", on_click=lambda: st.session_state.update(show_register_form=True))

    st.markdown("---")
    st.warning("⚠️ **Security Notice:** This login system is for demonstration purposes only. User data is stored in memory and is NOT persistent across sessions or secure for production. For real applications, use Firebase Authentication or a dedicated secure authentication service.")

else: # --- Dashboard Content (Only visible if authenticated) ---
    st.sidebar.header(f"Welcome, {st.session_state.username}!")
    st.sidebar.button("Logout", on_click=logout)
    st.sidebar.markdown("---")


    # --- Sidebar Filters (consolidated for single page) ---
    st.sidebar.header("Company & Date Filters")
    selected_company = st.sidebar.selectbox(
        "Choose a company:",
        list(COMPANIES.keys())
    )

    # Get the full dataset for the selected company BEFORE any filtering for year/date range
    df_full_company_data = all_kpi_data[selected_company].copy()
    governance_df_full = all_kpi_data[f"{selected_company}_Governance"].copy()


    # Extract available years for the selected company, and add 'All Years' option
    available_years = sorted(df_full_company_data['Date'].dt.year.unique(), reverse=True)
    year_options = ['All Years'] + [str(year) for year in available_years] # Convert years to string for selectbox
    selected_year_str = st.sidebar.selectbox(
        "Select Year:",
        options=year_options,
        index=0 # Default to 'All Years'
    )

    # Filter by selected year for both main data and governance data
    if selected_year_str == 'All Years':
        df_filtered_by_year = df_full_company_data
        governance_df_filtered_by_year = governance_df_full
    else:
        selected_year = int(selected_year_str) # Convert back to int for filtering
        df_filtered_by_year = df_full_company_data[df_full_company_data['Date'].dt.year == selected_year]
        governance_df_filtered_by_year = governance_df_full[governance_df_full['Year'] == selected_year]


    # Date Range Filter - now based on the selected year's data
    if not df_filtered_by_year.empty:
        min_date_year = df_filtered_by_year['Date'].min().to_pydatetime()
        max_date_year = df_filtered_by_year['Date'].max().to_pydatetime()

        default_start_date = min_date_year
        default_end_date = max_date_year

        date_range = st.sidebar.slider(
            f"Refine Date Range (within {selected_year_str}):",
            min_value=min_date_year,
            max_value=max_date_year,
            value=(default_start_date, default_end_date),
            format="YYYY-MM"
        )
        df_selected = df_filtered_by_year[(df_filtered_by_year['Date'] >= date_range[0]) & (df_filtered_by_year['Date'] <= date_range[1])]
    else:
        st.sidebar.warning(f"No data for selected filters. Please adjust year or date range.")
        df_selected = pd.DataFrame() # Empty DataFrame if no data for year


    # Get branding info for selected company
    company_logo = COMPANY_BRANDING[selected_company]["logo_url"]
    company_color = COMPANY_BRANDING[selected_company]["primary_color"]

    # Display Logo and Company Header
    col_logo, col_header = st.columns([1, 4])
    with col_logo:
        st.image(company_logo, width=100)
    with col_header:
        st.markdown(f"<h1 style='color: {company_color};'>{selected_company} Performance Overview</h1>", unsafe_allow_html=True)


    # --- Company Profile Section ---
    company_profile = COMPANY_PROFILES[selected_company]
    st.markdown("---")
    st.markdown(f"<h3 style='color: {company_color};'>Company Profile</h3>", unsafe_allow_html=True)
    st.markdown(f"**Mandate:** {company_profile['mandate']}")
    st.markdown(f"**Vision:** {company_profile['vision']}")
    st.markdown(f"**Strategic Plan Summary:** {company_profile['strategic_plan']}")
    st.markdown("---")


    # --- Define Tabs based on selected company ---
    tabs_list = list(COMPANY_TAB_KPIS[selected_company].keys())
    selected_tab_title = st.tabs(tabs_list)


    # --- Content within Tabs ---
    for i, tab_title in enumerate(tabs_list):
        with selected_tab_title[i]:
            # --- Current Performance Snapshot (appears on first tab for now, can be moved) ---
            if i == 0: # Display on the "Overview" tab
                st.markdown(f"<h3 style='color: {company_color};'>Current Performance Snapshot</h3>", unsafe_allow_html=True)
                latest_data = df_selected.iloc[-1] if not df_selected.empty else pd.Series()

                if latest_data.empty:
                    st.warning("No data available for the selected date range and year.")
                else:
                    kpi_cols = [col for col in df_selected.columns if col not in ['Date']]
                    num_kpis = len(kpi_cols)
                    cols = st.columns(min(num_kpis, 4)) # Up to 4 metrics per row

                    col_index = 0
                    for kpi_name in kpi_cols:
                        if kpi_name in ['Environmental & Social Compliance', 'Accreditation/Standards Compliance']:
                            display_value = "Compliant ✅" if latest_data[kpi_name] == 1 else "Non-Compliant ❌"
                            cols[col_index % 4].metric(label=kpi_name, value=display_value)
                        elif kpi_name in ['Revenue', 'Expenses', 'EBITDA', 'Cost per MW Installed']: # Financials
                            current_value = latest_data[kpi_name]
                            previous_value = df_selected.iloc[-2][kpi_name] if len(df_selected) > 1 else None
                            delta = current_value - previous_value if previous_value is not None else None

                            # Custom display for financial metrics
                            cols[col_index % 4].markdown(f"**{kpi_name}**", unsafe_allow_html=True)
                            cols[col_index % 4].markdown(
                                f"<h4 style='color: {company_color}; margin-bottom: 0px;'><b>{format_currency_value(current_value)} Frw</b></h4>",
                                unsafe_allow_html=True
                            )
                            if delta is not None:
                                delta_str = format_currency_value(delta)
                                delta_color_style = ""
                                if (kpi_name in ['Revenue', 'EBITDA'] and delta >= 0) or \
                                   (kpi_name in ['Expenses', 'Cost per MW Installed'] and delta <= 0):
                                    delta_color_style = "color: green;"
                                elif (kpi_name in ['Revenue', 'EBITDA'] and delta < 0) or \
                                     (kpi_name in ['Expenses', 'Cost per MW Installed'] and delta > 0):
                                    delta_color_style = "color: red;"

                                cols[col_index % 4].markdown(
                                    f"<p style='font-size: 0.9em; {delta_color_style}; margin-top: 0px;'>Δ {delta_str} Frw</p>",
                                    unsafe_allow_html=True
                                )
                        else:
                            current_value = latest_data[kpi_name]
                            previous_value = df_selected.iloc[-2][kpi_name] if len(df_selected) > 1 else None
                            delta = current_value - previous_value if previous_value is not None else None

                            if '%' in kpi_name or 'Rate' in kpi_name or 'Efficiency' in kpi_name or 'Compliance' in kpi_name:
                                current_value_formatted = f"{current_value:.1f}%"
                                delta_formatted = f"{delta:.1f}%" if delta is not None else None
                                delta_color_option = "normal" if delta >= 0 else "inverse" if delta < 0 else "off"
                            elif 'System Loss Rate (%)' in kpi_name or 'Average Outage Duration (SAIDI)' in kpi_name or 'Non-Revenue Water (NRW %)' in kpi_name or '% of Expired Stock' in kpi_name or 'Average Length of Stay (ALOS)' in kpi_name or 'Mortality Rate' in kpi_name or 'Customer Complaints Resolution Time (days)' in kpi_name or 'Transportation Delivery Time (Avg. days)' in kpi_name or 'Procurement Lead Time (Avg. days)' in kpi_name:
                                current_value_formatted = f"{current_value:,.1f}" if 'Rate' not in kpi_name else f"{current_value:,.1f}%"
                                delta_formatted = f"{delta:,.1f}" if delta is not None else None
                                delta_color_option = "inverse" if delta > 0 else "normal" if delta < 0 else "off"
                            elif 'MW' in kpi_name or 'km' in kpi_name or 'Number' in kpi_name or 'Count' in kpi_name:
                                current_value_formatted = f"{current_value:,.0f}"
                                delta_formatted = f"{delta:,.0f}" if delta is not None else None
                                delta_color_option = "normal" if delta >= 0 else "inverse" if delta < 0 else "off"
                            else:
                                current_value_formatted = f"{current_value:,.1f}"
                                delta_formatted = f"{delta:,.1f}" if delta is not None else None
                                delta_color_option = "normal" if delta >= 0 else "inverse" if delta < 0 else "off"

                            cols[col_index % 4].metric(
                                label=kpi_name,
                                value=current_value_formatted,
                                delta=delta_formatted,
                                delta_color=delta_color_option
                            )
                        col_index += 1

            # --- Key Trends Over Time for the current tab ---
            st.markdown("---")
            st.markdown(f"<h3 style='color: {company_color};'>Key Trends Over Time ({tab_title})</h3>", unsafe_allow_html=True)

            kpis_to_plot_for_current_tab = COMPANY_TAB_KPIS[selected_company].get(tab_title, [])

            for kpi_name in kpis_to_plot_for_current_tab:
                # Determine which DataFrame to use for plotting trends
                # If "All Years" is selected, use df_full_company_data for trends.
                # Otherwise, use df_selected (which is filtered by date_range slider).
                data_for_trend_plot = df_full_company_data if selected_year_str == 'All Years' else df_selected

                # Special handling for regional data for EUCL Access Rate and WASAC Coverage Rate
                if selected_company == "EUCL" and kpi_name == "Electricity Access Rate (%)" and tab_title == "Operational Efficiency":
                    st.markdown("#### Electricity Access Rate (%) by Region")
                    regional_access_df = all_kpi_data.get("EUCL_Regional_Access", pd.DataFrame())
                    if not regional_access_df.empty:
                        # Filter regional data by selected year and then date range
                        if selected_year_str == 'All Years':
                            regional_access_df_filtered_year = regional_access_df
                        else:
                            regional_access_df_filtered_year = regional_access_df[regional_access_df['Date'].dt.year == int(selected_year_str)]

                        regional_access_df_filtered = regional_access_df_filtered_year[
                            (regional_access_df_filtered_year['Date'] >= date_range[0]) &
                            (regional_access_df_filtered_year['Date'] <= date_range[1])
                        ]
                        # Get latest month's regional data
                        latest_regional_access = regional_access_df_filtered[
                            regional_access_df_filtered['Date'] == regional_access_df_filtered['Date'].max()
                        ]
                        if not latest_regional_access.empty:
                            chart = alt.Chart(latest_regional_access).mark_bar(color=company_color).encode(
                                x=alt.X('Electricity Access Rate (%):Q', title='Access Rate (%)'),
                                y=alt.Y('Region:N', sort='-x', title='Region'),
                                tooltip=['Region', alt.Tooltip('Electricity Access Rate (%):Q', format=',.1f')]
                            ).properties(
                                title='Latest Electricity Access Rate by Region'
                            )
                            st.altair_chart(chart, use_container_width=True)
                        else:
                            st.info(f"📊 No regional access data for **{kpi_name}** in the selected period for {selected_company}. This may be due to filters or missing data.")
                    else:
                        st.info(f"⚠️ Regional access data simulation not available for {selected_company}.")
                elif selected_company == "WASAC" and kpi_name == "Water Coverage Rate (%)" and tab_title == "Water Supply & Quality":
                    st.markdown("#### Water Coverage Rate (%) by Region")
                    regional_coverage_df = all_kpi_data.get("WASAC_Regional_Coverage", pd.DataFrame())
                    if not regional_coverage_df.empty:
                        # Filter regional data by selected year and then date range
                        if selected_year_str == 'All Years':
                            regional_coverage_df_filtered_year = regional_coverage_df
                        else:
                            regional_coverage_df_filtered_year = regional_coverage_df[regional_coverage_df['Date'].dt.year == int(selected_year_str)]

                        regional_coverage_df_filtered = regional_coverage_df_filtered_year[
                            (regional_coverage_df_filtered_year['Date'] >= date_range[0]) &
                            (regional_coverage_df_filtered_year['Date'] <= date_range[1])
                        ]
                        # Get latest month's regional data
                        latest_regional_coverage = regional_coverage_df_filtered[
                            regional_coverage_df_filtered['Date'] == regional_coverage_df_filtered['Date'].max()
                        ]
                        if not latest_regional_coverage.empty:
                            chart = alt.Chart(latest_regional_coverage).mark_bar(color=company_color).encode(
                                x=alt.X('Water Coverage Rate (%):Q', title='Coverage Rate (%)'),
                                y=alt.Y('Region:N', sort='-x', title='Region'),
                                tooltip=['Region', alt.Tooltip('Water Coverage Rate (%):Q', format=',.1f')]
                            ).properties(
                                title='Latest Water Coverage Rate by Region'
                            )
                            st.altair_chart(chart, use_container_width=True)
                        else:
                            st.info(f"📊 No regional coverage data for **{kpi_name}** in the selected period for {selected_company}. This may be due to filters or missing data.")
                    else:
                        st.info(f"⚠️ Regional coverage data simulation not available for {selected_company}.")
                # For other KPIs that are not regional specific, plot them normally
                elif kpi_name in data_for_trend_plot.columns and data_for_trend_plot[kpi_name].dtype in ['float64', 'int64']:
                    # Ensure there's non-null data to plot
                    if not data_for_trend_plot[kpi_name].dropna().empty:
                        chart_title = f"{kpi_name} Trend"
                        y_format = ',.1f' if '%' in kpi_name or 'Rate' in kpi_name else (',.0f' if kpi_name in ['New Generation Capacity Developed (MW)'] else '$,.0f')
                        
                        st.altair_chart(create_line_chart(data_for_trend_plot, 'Date', kpi_name, chart_title, y_format, line_color=company_color), use_container_width=True)
                    else:
                        st.info(f"📊 No trend data available for **{kpi_name}** in the selected period for {selected_company}. This may be due to filters or missing data.")
                else: # If kpi_name is not even a column in data_for_trend_plot
                    st.info(f"⚠️ The KPI column **{kpi_name}** was not found in the dataset for {selected_company}.")


    # --- Governance Status Section (placed outside tabs, or can be in a dedicated tab) ---
    st.markdown("---")
    st.markdown(f"<h3 style='color: {company_color};'>Governance Status</h3>", unsafe_allow_html=True)
    if not governance_df_filtered_by_year.empty:
        latest_governance = governance_df_filtered_by_year.iloc[-1]
        
        gov_col1, gov_col2, gov_col3 = st.columns(3)
        with gov_col1:
            st.metric("Board Completeness", f"{latest_governance.get('Board Completeness (%)', 0):.1f}%")
        with gov_col2:
            audit_status = "Clean ✅" if latest_governance.get('Audit Opinion', 0) == 1 else "Qualified ❌"
            st.metric("Audit Opinion (Latest)", audit_status)
        with gov_col3:
            st.metric("Internal Audit Score", f"{latest_governance.get('Internal Audit Score (%)', 0):.1f}/100")

        st.markdown(f"<h4 style='color: {company_color};'>Governance Trend by Year</h4>", unsafe_allow_html=True)
        
        # Plotting governance trends (using full governance_df_full for historical yearly trends)
        # Ensure there's non-null data for plotting governance trends as well
        if 'Board Completeness (%)' in governance_df_full.columns and not governance_df_full['Board Completeness (%)'].dropna().empty:
            st.altair_chart(create_line_chart(governance_df_full, 'Year', 'Board Completeness (%)', 'Board Completeness Trend', y_format=',.1f', line_color=company_color, x_axis_type='O'), use_container_width=True) # Use 'O' for ordinal year
        else:
            st.info(f"📊 No trend data available for **Board Completeness (%)** in the selected period for {selected_company}. This may be due to filters or missing data.")
        
        if 'Internal Audit Score (%)' in governance_df_full.columns and not governance_df_full['Internal Audit Score (%)'].dropna().empty:
            st.altair_chart(create_line_chart(governance_df_full, 'Year', 'Internal Audit Score (%)', 'Internal Audit Score Trend', y_format=',.1f', line_color=company_color, x_axis_type='O'), use_container_width=True) # Use 'O' for ordinal year
        else:
            st.info(f"📊 No trend data available for **Internal Audit Score (%)** in the selected period for {selected_company}. This may be due to filters or missing data.")

    else:
        st.info("No governance data available for the selected company or year.")


    st.markdown("---")
    st.info("This dashboard uses **synthetic data** for demonstration purposes. "
            "Actual data would be integrated upon request and secure access.")
    st.markdown("### Further Enhancement Possibilities:")
    st.markdown("- **Direct Database Connectivity:** Implement secure connections to real data sources (e.g., SQL databases, APIs) for live data updates.")
    st.markdown("- **User Authentication:** Add login capabilities for secure access control.")
    st.markdown("- **Alerting and Notifications:** Set up alerts for KPIs falling below targets or exceeding thresholds.")
    st.markdown("- **Custom Theming:** Use `.streamlit/config.toml` to fully customize the dashboard's colors, fonts, and overall aesthetics to match MINECOFIN's branding.")
