import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Set page configuration
st.set_page_config(
    page_title="DHL Logistics Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_BASE_URL = "http://localhost:8000"

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #D40511;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: #505050;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #D40511;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #505050;
    }
    .status-delivered {
        color: #28a745;
        font-weight: bold;
    }
    .status-intransit {
        color: #ffc107;
        font-weight: bold;
    }
    .status-processing {
        color: #007bff;
        font-weight: bold;
    }
    .status-delayed {
        color: #dc3545;
        font-weight: bold;
    }
    .highlight {
        background-color: #FFECB3;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def format_status(status):
    status_lower = status.lower().replace(" ", "")
    if status_lower == "delivered":
        return f'<span class="status-delivered">{status}</span>'
    elif status_lower == "intransit" or status_lower == "in-transit":
        return f'<span class="status-intransit">{status}</span>'
    elif status_lower == "processing":
        return f'<span class="status-processing">{status}</span>'
    elif status_lower == "delayed":
        return f'<span class="status-delayed">{status}</span>'
    else:
        return status

def fetch_data(endpoint, params=None):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from {endpoint}: {str(e)}")
        return None

def update_data(endpoint, data):
    try:
        response = requests.put(f"{API_BASE_URL}/{endpoint}", json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating data at {endpoint}: {str(e)}")
        return None

def create_data(endpoint, data):
    try:
        response = requests.post(f"{API_BASE_URL}/{endpoint}", json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating data at {endpoint}: {str(e)}")
        return None

# Sidebar navigation
 
st.sidebar.markdown("<div class='main-header'>DHL Logistics</div>", unsafe_allow_html=True)
st.sidebar.image("https://logistics.dhl/content/dam/dhl/global/core/images/logos/dhl-logo.svg", width=100)

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Shipments", "Customers", "Parcels", "Analytics"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")


# Initialize session state
if 'customer_filter' not in st.session_state:
    st.session_state.customer_filter = None
if 'status_filter' not in st.session_state:
    st.session_state.status_filter = None

# Dashboard Page
if page == "Dashboard":
    st.markdown('<div class="main-header">DHL Logistics Dashboard</div>', unsafe_allow_html=True)

    # Get dashboard summary data
    dashboard_data = fetch_data("dashboard/summary")
    if dashboard_data:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f"""
                <div class="card">
                    <div class="metric-label">Total Customers</div>
                    <div class="metric-value">{dashboard_data.get('total_customers', 0)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"""
                <div class="card">
                    <div class="metric-label">Total Parcels</div>
                    <div class="metric-value">{dashboard_data.get('total_parcels', 0)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f"""
                <div class="card">
                    <div class="metric-label">Total Shipments</div>
                    <div class="metric-value">{dashboard_data.get('total_shipments', 0)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col4:
            st.markdown(
                f"""
                <div class="card">
                    <div class="metric-label">On-Time Delivery</div>
                    <div class="metric-value">{dashboard_data.get('on_time_percentage', 0):.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="sub-header">Shipment Status Breakdown</div>', unsafe_allow_html=True)
            
            status_data = dashboard_data.get('status_breakdown', {})
            if status_data:
                fig = px.pie(
                    names=list(status_data.keys()),
                    values=list(status_data.values()),
                    color_discrete_sequence=px.colors.sequential.RdBu,
                    hole=0.4
                )
                fig.update_layout(
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=300,
                    legend_title_text='Status'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No status data available")
        
        with col2:
            st.markdown('<div class="sub-header">Performance Metrics</div>', unsafe_allow_html=True)
            
            # Create a gauge chart for efficiency
            efficiency = dashboard_data.get('efficiency', 0)
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=efficiency,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Efficiency Score"},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1},
                    'bar': {'color': "red"},
                    'steps': [
                        {'range': [0, 33], 'color': "lightgray"},
                        {'range': [33, 66], 'color': "gray"},
                        {'range': [66, 100], 'color': "darkgray"}
                    ],
                    'threshold': {
                        'line': {'color': "green", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)

        # Recent shipments
        st.markdown('<div class="sub-header">Recent Shipments</div>', unsafe_allow_html=True)
        recent_shipments = dashboard_data.get('recent_shipments', [])
        
        if recent_shipments:
            df = pd.DataFrame(recent_shipments)
            for i, row in df.iterrows():
                status_html = format_status(row['Status'])
                
                st.markdown(
                    f"""
                    <div class="card">
                        <strong style="color:black;">Shipment:</strong><span style="color:navy; font-weight:bold;"> {row['ShipmentName']} (ID: {row['ShipmentID']}) <br>
                        <strong style="color:black;">Customer:</strong> {row['CustomerName']} <br>
                        <strong style="color:black;">Parcel:</strong> {row['ParcelName']} <br>
                        <strong style="color:black;">Status:</strong> {status_html} <br>
                        <strong style="color:black;">Location:</strong> {row['CurrentLocation']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No recent shipments to display")

# Customers Page
elif page == "Customers":
    st.markdown('<div class="main-header">Customer Management</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Customer List", "Add Customer"])
    
    with tab1:
        customers = fetch_data("customers", {"limit": 100})
        if customers:
            df = pd.DataFrame(customers)
            
            # Basic filtering
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                filter_name = st.text_input("Filter by Name")
            with filter_col2:
                customer_types = list(set(df['Type']))
                filter_type = st.selectbox("Filter by Type", ["All"] + customer_types)
            
            filtered_df = df.copy()
            if filter_name:
                filtered_df = filtered_df[filtered_df['Name'].str.contains(filter_name, case=False)]
            if filter_type != "All":
                filtered_df = filtered_df[filtered_df['Type'] == filter_type]
            
            if not filtered_df.empty:
                # Display as cards
                for i, row in filtered_df.iterrows():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(
                            f"""
                            <div class="card">
                                <strong>{row['Name']}</strong> <span style="color:navy; font-weight:bold;">(ID: {row['CustomerID']})
                                <br>Type: <span class="highlight">{row['Type']}</span>
                                <br>Email: {row['Email']}
                                <br>Phone: {row['Phone']}
                                <br>Address: {row['Address']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    with col2:
                        if st.button(f"View Details #{row['CustomerID']}", key=f"view_{row['CustomerID']}"):
                            customer_details = fetch_data(f"customers/{row['CustomerID']}")
                            if customer_details:
                                st.session_state.customer_filter = row['CustomerID']
                                st.rerun()
            else:
                st.info("No customers found with the selected filters")
        else:
            st.error("Failed to load customer data")
    
    with tab2:
        st.markdown('<div class="sub-header">Add New Customer</div>', unsafe_allow_html=True)
        
        with st.form("new_customer_form"):
            new_customer = {}
            
            col1, col2 = st.columns(2)
            with col1:
                new_customer['CustomerID'] = st.number_input("Customer ID", min_value=1, step=1)
                new_customer['Name'] = st.text_input("Name")
                new_customer['Email'] = st.text_input("Email")
            
            with col2:
                new_customer['Phone'] = st.text_input("Phone")
                new_customer['Address'] = st.text_input("Address")
                new_customer['Type'] = st.selectbox("Type", ["Individual", "Business", "Corporate", "Government"])
            
            submit_button = st.form_submit_button("Add Customer")
            
            if submit_button:
                if new_customer['Name'] and new_customer['Email']:
                    result = create_data("customers", new_customer)
                    if result:
                        st.success("Customer added successfully!")
                else:
                    st.warning("Please fill in all required fields")

# Parcels Page
elif page == "Parcels":
    st.markdown('<div class="main-header">Parcel Management</div>', unsafe_allow_html=True)
    
    # Get parcels data
    parcels = fetch_data("parcels", {"limit": 100})
    
    # Customer filter
    customers = fetch_data("customers", {"limit": 100})
    if customers:
        customer_options = ["All"] + [f"{c['Name']} (ID: {c['CustomerID']})" for c in customers]
        selected_customer = st.selectbox("Filter by Customer", customer_options)
        
        if selected_customer != "All":
            customer_id = int(selected_customer.split("ID: ")[1].strip(")"))
            parcels = fetch_data("parcels", {"customer_id": customer_id, "limit": 100})
    
    if parcels:
        df = pd.DataFrame(parcels)
        
        # Display parcels in a table
        st.markdown('<div class="sub-header">Parcels List</div>', unsafe_allow_html=True)
        st.dataframe(
            df[['ParcelID', 'ParcelName', 'CustomerID', 'Weight', 'Type', 'ShippingMethod']],
            use_container_width=True,
            column_config={
                "ParcelID": "ID",
                "ParcelName": "Name",
                "CustomerID": "Customer ID",
                "Weight": st.column_config.NumberColumn("Weight (kg)", format="%.2f"),
                "Type": "Type",
                "ShippingMethod": "Shipping Method"
            }
        )
        
        # Detailed view for selected parcel
        selected_parcel_id = st.selectbox(
            "Select Parcel for Details",
            ["None"] + df['ParcelID'].astype(str).tolist()
        )
        
        if selected_parcel_id != "None":
            parcel_detail = fetch_data(f"parcels/{selected_parcel_id}")
            if parcel_detail:
                with st.expander("Parcel Details", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Parcel Name:** {parcel_detail['ParcelName']}")
                        st.markdown(f"**Customer ID:** {parcel_detail['CustomerID']}")
                        st.markdown(f"**Type:** {parcel_detail['Type']}")
                    
                    with col2:
                        st.markdown(f"**Weight:** {parcel_detail['Weight']} kg")
                        st.markdown(f"**Shipping Method:** {parcel_detail['ShippingMethod']}")
                    
                    # Associated shipments
                    shipments = fetch_data("shipments", {"limit": 100})
                    if shipments:
                        parcel_shipments = [s for s in shipments if s['ParcelID'] == int(selected_parcel_id)]
                        
                        if parcel_shipments:
                            st.markdown("### Associated Shipments")
                            shipment_df = pd.DataFrame(parcel_shipments)
                            
                            for i, row in shipment_df.iterrows():
                                status_html = format_status(row['Status'])
                                
                                st.markdown(
                                    f"""
                                    <div class="card">
                                        <strong>Shipment:</strong> {row['ShipmentName']} (ID: {row['ShipmentID']}) <br>
                                        <strong>Status:</strong> {status_html} <br>
                                        <strong>Current Location:</strong> {row['CurrentLocation']} <br>
                                        <strong>Shipping Date:</strong> {row['ShipmentDate']} <br>
                                        <strong>Delivery Date:</strong> {row['DeliveryDate']}
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                        else:
                            st.info("No shipments found for this parcel")
    else:
        st.error("Failed to load parcel data")

# Shipments Page
elif page == "Shipments":
    st.markdown('<div class="main-header">Shipment Tracking</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        status_options = ["All", "Processing", "In Transit", "Delivered", "Delayed"]
        selected_status = st.selectbox("Filter by Status", status_options)
    
    with col2:
        # Customer filter
        customers = fetch_data("customers", {"limit": 100})
        if customers:
            customer_options = ["All"] + [f"{c['Name']} (ID: {c['CustomerID']})" for c in customers]
            selected_customer = st.selectbox("Filter by Customer", customer_options)
    
    # Fetch shipments with filters
    params = {"limit": 100}
    
    if selected_status != "All":
        params["status"] = selected_status
    
    if selected_customer != "All":
        customer_id = int(selected_customer.split("ID: ")[1].strip(")"))
        params["customer_id"] = customer_id
    
    shipments = fetch_data("shipments", params)
    
    if shipments:
        df = pd.DataFrame(shipments)
        
        # Map visualization for shipment locations
        st.markdown('<div class="sub-header">Shipment Locations</div>', unsafe_allow_html=True)
        
        # Mock location data (in a real application, you would get actual coordinates)
        locations = {
            "New York": [40.7128, -74.0060],
            "Los Angeles": [34.0522, -118.2437],
            "Chicago": [41.8781, -87.6298],
            "Houston": [29.7604, -95.3698],
            "Phoenix": [33.4484, -112.0740],
            "Philadelphia": [39.9526, -75.1652],
            "San Antonio": [29.4241, -98.4936],
            "San Diego": [32.7157, -117.1611],
            "Dallas": [32.7767, -96.7970],
            "San Jose": [37.3382, -121.8863],
            "Austin": [30.2672, -97.7431],
            "Jacksonville": [30.3322, -81.6557],
            "San Francisco": [37.7749, -122.4194],
            "Columbus": [39.9612, -82.9988],
            "Indianapolis": [39.7684, -86.1581],
            "Seattle": [47.6062, -122.3321],
            "Denver": [39.7392, -104.9903],
            "Washington": [38.9072, -77.0369],
            "Boston": [42.3601, -71.0589],
            "Nashville": [36.1627, -86.7816]
        }
        
        # If a location is not in our mock data, assign a random one
        import random
        map_data = []
        
        for i, row in df.iterrows():
            location = row['CurrentLocation']
            if location in locations:
                lat, lon = locations[location]
            else:
                # Pick a random location
                random_location = random.choice(list(locations.keys()))
                lat, lon = locations[random_location]
            
            map_data.append({
                'ShipmentID': row['ShipmentID'],
                'ShipmentName': row['ShipmentName'],
                'Status': row['Status'],
                'Location': location,
                'lat': lat,
                'lon': lon
            })
        
        map_df = pd.DataFrame(map_data)
        
        # Color mapping for status
        color_mapping = {
            'Processing': 'black',
            'In Transit': 'orange',
            'Delivered': 'green',
            'Delayed': 'red'
        }
        
        # Default color for status not in mapping
        map_df['color'] = map_df['Status'].apply(lambda x: color_mapping.get(x, 'gray'))
        
        fig = px.scatter_mapbox(
            map_df,
            lat="lat",
            lon="lon",
            hover_name="ShipmentName",
            hover_data=["ShipmentID", "Status", "Location"],
            color="Status",
            color_discrete_map=color_mapping,
            zoom=3,
            size=[15] * len(map_df),
            mapbox_style="carto-positron"
        )
        
        fig.update_layout(height=500, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        # Shipment list
        st.markdown('<div class="sub-header">Shipment List</div>', unsafe_allow_html=True)
        
        for i, row in df.iterrows():
            status_html = format_status(row['Status'])
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(
                    f"""
                    <div class="card">
                        <strong>Shipment:</strong> <span style="color:navy; font-weight:bold;">{row['ShipmentName']} (ID: {row['ShipmentID']}) <br>
                        <strong>Status:</strong> {status_html} <br>
                        <strong>Current Location:</strong> {row['CurrentLocation']} <br>
                        <strong>Shipping Date:</strong> {row['ShipmentDate']} <br>
                        <strong>Delivery Date:</strong> {row['DeliveryDate']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col2:
                # Status update form
                with st.form(key=f"update_form_{row['ShipmentID']}"):
                    new_status = st.selectbox(
                        "New Status",
                        ["Processing", "In Transit", "Delivered", "Delayed"],
                        key=f"status_{row['ShipmentID']}"
                    )
                    
                    if st.form_submit_button("Update Status"):
                        result = update_data(
                            f"shipments/{row['ShipmentID']}/status",
                            {"Status": new_status}
                        )
                        
                        if result:
                            st.success(f"Updated status to {new_status}")
                            st.rerun()
    else:
        st.error("Failed to load shipment data")

# Personnel Page
elif page == "Personnel":
    st.markdown('<div class="main-header">Personnel Management</div>', unsafe_allow_html=True)
    
    # Role filter
    role_filter = st.selectbox(
        "Filter by Role",
        ["All", "Driver", "Warehouse", "Customer Service", "Manager"]
    )
    
    # Fetch personnel data
    params = {"limit": 100}
    if role_filter != "All":
        params["role"] = role_filter
    
    personnel = fetch_data("personnel", params)
    
    if personnel:
        df = pd.DataFrame(personnel)
        
        # Display as a grid of cards
        st.markdown('<div class="sub-header">Personnel Directory</div>', unsafe_allow_html=True)
        
        # Create rows with 3 columns each
        for i in range(0, len(df), 3):
            cols = st.columns(3)
            
            for j in range(3):
                if i + j < len(df):
                    person = df.iloc[i + j]
                    
                    with cols[j]:
                        st.markdown(
                            f"""
                            <div class="card">
                                <strong>{person['Name']}</strong> <br>
                                <span class="highlight">{person['Role']}</span> <br>
                                ID: {person['PersonnelID']} <br>
                                Phone: {person['Phone']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
        
        # Personnel assignment to shipments
        st.markdown('<div class="sub-header">Assign Personnel to Shipment</div>', unsafe_allow_html=True)
        
        with st.form("personnel_assignment"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Get shipments for dropdown
                shipments = fetch_data("shipments", {"limit": 100})
                if shipments:
                    shipment_options = [f"{s['ShipmentName']} (ID: {s['ShipmentID']})" for s in shipments]
                    selected_shipment = st.selectbox("Select Shipment", shipment_options)
                    shipment_id = int(selected_shipment.split("ID: ")[1].strip(")"))
                else:
                    st.error("Could not load shipments")
                    shipment_id = None
            
            with col2:
                personnel_options = [f"{p['Name']} (ID: {p['PersonnelID']})" for p in personnel]
                selected_personnel = st.selectbox("Select Personnel", personnel_options)
                personnel_id = int(selected_personnel.split("ID: ")[1].strip(")"))
            
            submit = st.form_submit_button("Assign to Shipment")
            
            if submit and shipment_id:
                assignment_data = {
                    "ShipmentID": shipment_id,
                    "PersonnelID": personnel_id
                }
                
                # In a real app you would call the API to create the assignment
                st.success(f"Assigned {selected_personnel} to {selected_shipment}")
                
                # Mock display of currently assigned personnel
                st.markdown("### Current Assignments")
                st.info("This is a demo view. In a real application, this would show actual data from the API.")
                
                st.markdown(
                    f"""
                    <div class="card">
                        <strong>Shipment:</strong> {selected_shipment} <br>
                        <strong>Assigned Personnel:</strong> {selected_personnel}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.error("Failed to load personnel data")

# Analytics Page
elif page == "Analytics":
    st.markdown('<div class="main-header">Analytics & KPIs</div>', unsafe_allow_html=True)
    
    # Fetch analytics data
    kpi_data = fetch_data("analytics/kpi")
    analytics_data = fetch_data("analytics", {"limit": 100})
    customer_insights = fetch_data("dashboard/customer-insights")
    
    if kpi_data and analytics_data and customer_insights:
        # KPI Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                f"""
                <div class="card">
                    <div class="metric-label">Average Efficiency</div>
                    <div class="metric-value">{kpi_data.get('avg_efficiency', 0):.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div class="card">
                    <div class="metric-label">Customer Satisfaction</div>
                    <div class="metric-value">{kpi_data.get('avg_customer_rating', 0):.1f}/5</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f"""
                <div class="card">
                    <div class="metric-label">On-Time Delivery</div>
                    <div class="metric-value">{kpi_data.get('on_time_percentage', 0):.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # KPI Trends (mock data)
        st.markdown('<div class="sub-header">KPI Trends (Last 30 Days)</div>', unsafe_allow_html=True)
        
        # Create mock trend data
        import numpy as np
        
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
        
        # Efficiency trend (with some randomness)
        base_efficiency = kpi_data.get('avg_efficiency', 75)
        efficiency_data = [max(min(base_efficiency + np.random.normal(0, 5), 100), 50) for _ in range(30)]
        
        # Customer rating trend
        base_rating = kpi_data.get('avg_customer_rating', 4)
        rating_data = [max(min(base_rating + np.random.normal(0, 0.3), 5), 1) for _ in range(30)]
        
        # On-time trend
        base_ontime = kpi_data.get('on_time_percentage', 85)
        ontime_data = [max(min(base_ontime + np.random.normal(0, 3), 100), 70) for _ in range(30)]
        
        # Create trend dataframe
        trend_df = pd.DataFrame({
            'Date': dates,
            'Efficiency': efficiency_data,
            'Customer Rating': rating_data,
            'On-Time Percentage': ontime_data
        })
        
        # Plot trends
        tab1, tab2, tab3 = st.tabs(["Efficiency", "Customer Satisfaction", "On-Time Delivery"])
        
        with tab1:
            fig = px.line(
                trend_df, 
                x='Date', 
                y='Efficiency',
                title='Efficiency Score Trend',
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            fig = px.line(
                trend_df, 
                x='Date', 
                y='Customer Rating',
                title='Customer Satisfaction Trend',
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            fig = px.line(
                trend_df, 
                x='Date', 
                y='On-Time Percentage',
                title='On-Time Delivery Trend',
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Customer Insights
        st.markdown('<div class="sub-header">Customer Insights</div>', unsafe_allow_html=True)
        
        # Create customer distribution chart
        if 'customer_distribution' in customer_insights:
            customer_dist = customer_insights['customer_distribution']
            fig = px.bar(
                x=list(customer_dist.keys()),
                y=list(customer_dist.values()),
                title='Customer Type Distribution',
                labels={'x': 'Customer Type', 'y': 'Count'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Shipping volume by method
        if 'shipping_methods' in analytics_data:
            shipping_methods = analytics_data['shipping_methods']
            fig = px.pie(
                names=list(shipping_methods.keys()),
                values=list(shipping_methods.values()),
                title='Shipping Volume by Method',
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Failed to load analytics data")

# Network Visualization Page
elif page == "Network Visualization":
    st.markdown('<div class="main-header">Logistics Network</div>', unsafe_allow_html=True)
    
    # Fetch network data
    network_data = fetch_data("network")
    
    if network_data:
        # Display network information
        st.markdown('<div class="sub-header">Network Overview</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                f"""
                <div class="card">
                    <div class="metric-label">Total Hubs</div>
                    <div class="metric-value">{network_data.get('total_hubs', 0)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div class="card">
                    <div class="metric-label">Active Routes</div>
                    <div class="metric-value">{network_data.get('active_routes', 0)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f"""
                <div class="card">
                    <div class="metric-label">Fleet Size</div>
                    <div class="metric-value">{network_data.get('fleet_size', 0)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Network visualization
        st.markdown('<div class="sub-header">Network Map</div>', unsafe_allow_html=True)
        
        # Create a network graph (mock data)
        if 'hubs' in network_data and 'routes' in network_data:
            import networkx as nx
            
            # Create a graph
            G = nx.Graph()
            
            # Add nodes (hubs)
            for hub in network_data['hubs']:
                G.add_node(hub['name'], pos=(hub['lon'], hub['lat']), size=hub['size'])
            
            # Add edges (routes)
            for route in network_data['routes']:
                G.add_edge(route['origin'], route['destination'], weight=route['volume'])
            
            # Get positions
            pos = nx.get_node_attributes(G, 'pos')
            
            # Create a Plotly figure
            edge_x = []
            edge_y = []
            
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            node_x = []
            node_y = []
            node_text = []
            node_size = []
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)
                node_size.append(G.nodes[node]['size'] * 10)
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                hoverinfo='text',
                text=node_text,
                marker=dict(
                    showscale=True,
                    colorscale='YlOrRd',
                    size=node_size,
                    colorbar=dict(
                        thickness=15,
                        title='Hub Size',
                        xanchor='left',
                        titleside='right'
                    ),
                    line_width=2
                )
            )
            
            fig = go.Figure(data=[edge_trace, node_trace],
                            layout=go.Layout(
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=20, l=5, r=5, t=40),
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                            ))
            
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # List of hubs
            st.markdown('<div class="sub-header">Hub List</div>', unsafe_allow_html=True)
            
            hub_df = pd.DataFrame(network_data['hubs'])
            st.dataframe(
                hub_df,
                use_container_width=True,
                column_config={
                    "name": "Hub Name",
                    "type": "Hub Type",
                    "size": st.column_config.NumberColumn("Hub Size", format="%d"),
                    "capacity": st.column_config.NumberColumn("Capacity", format="%d"),
                    "utilization": st.column_config.ProgressColumn("Utilization", format="%d%%", min_value=0, max_value=100)
                }
            )
            
            # Fleet information
            if 'fleet' in network_data:
                st.markdown('<div class="sub-header">Fleet Information</div>', unsafe_allow_html=True)
                
                fleet_df = pd.DataFrame(network_data['fleet'])
                st.dataframe(
                    fleet_df,
                    use_container_width=True,
                    column_config={
                        "vehicle_id": "Vehicle ID",
                        "type": "Vehicle Type",
                        "capacity": st.column_config.NumberColumn("Capacity (kg)", format="%d"),
                        "status": "Status",
                        "location": "Current Location",
                    }
                )
        else:
            st.error("Incomplete network data")
    else:
        st.error("Failed to load network data")

# Run the app
if __name__ == "__main__":
    st.sidebar.info("This is a demo dashboard for DHL Logistics. Data is simulated.")