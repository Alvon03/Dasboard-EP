import streamlit as st
import pandas as pd
import plotly.express as px

# Load data from specified location
file_path = r'C:\Users\alvon.ws\Downloads\GT_merged.xlsx'
data = pd.read_excel(file_path)

# Convert 'Periode' to datetime
data['Periode'] = pd.to_datetime(data['Periode'])

# Extract month and year for filtering
data['Month'] = data['Periode'].dt.month
data['Year'] = data['Periode'].dt.year

# Title of the dashboard
st.title("Dashboard Pemakaian Mesin PLTGU PRIOK GT #3.1")

# Sidebar for filters
st.sidebar.header("Filters")
selected_suppliers = st.sidebar.multiselect(
    'Pilih Supplier',
    options=data['Supplier'].unique(),
    default=data['Supplier'].unique()
)

# Dropdown for month
selected_month = st.sidebar.selectbox(
    'Pilih Bulan',
    options=data['Month'].unique(),
    format_func=lambda x: f"Bulan {x}"
)

# Dropdown for year
selected_year = st.sidebar.selectbox(
    'Pilih Tahun',
    options=data['Year'].unique()
)

# Dropdown for machine names
selected_machines = st.sidebar.multiselect(
    'Pilih Nama Mesin',
    options=data['Nama Mesin'].unique(),
    default=data['Nama Mesin'].unique()
)

# Filter data based on selection
filtered_data = data[(data['Supplier'].isin(selected_suppliers)) & 
                     (data['Month'] == selected_month) & 
                     (data['Year'] == selected_year) & 
                     (data['Nama Mesin'].isin(selected_machines))]

# Display filtered data for debugging
st.write("Filtered Data")
st.dataframe(filtered_data)

# Function to convert filtered data to CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Create download button
if not filtered_data.empty:
    csv_data = convert_df_to_csv(filtered_data)
    st.download_button(
        label="Download data as CSV",
        data=csv_data,
        file_name='filtered_data.csv',
        mime='text/csv'
    )

if not filtered_data.empty:
    # Total Pemakaian Mesin Berdasarkan Tipe Transaksi
    total_pemakaian = filtered_data.groupby('Tipe Transaksi')['Jumlah'].sum().reset_index()
    fig_total_pemakaian = px.bar(total_pemakaian, x='Tipe Transaksi', y='Jumlah',
                                 title='Total Pemakaian Mesin Berdasarkan Tipe Transaksi',
                                 color_discrete_sequence=['#636EFA'])
    st.plotly_chart(fig_total_pemakaian)

    # Distribusi Energi Primer
    energi_primer = filtered_data['Energi Primer'].value_counts().reset_index()
    energi_primer.columns = ['Energi Primer', 'count']  # Rename columns
    fig_energi_primer = px.pie(energi_primer, values='count', names='Energi Primer',
                               title='Distribusi Energi Primer',
                               color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_energi_primer)

    # Biaya per Volume per Supplier
    biaya_per_volume = filtered_data.groupby('Supplier')['Biaya Rp/Volume'].mean().reset_index()
    fig_biaya_per_volume = px.bar(biaya_per_volume, x='Supplier', y='Biaya Rp/Volume',
                                  title='Biaya per Volume per Supplier',
                                  color_discrete_sequence=['#00CC96'])
    st.plotly_chart(fig_biaya_per_volume)

    # Jumlah Pemakaian Mesin Harian
    pemakaian_harian = filtered_data.groupby('Periode')['Jumlah'].sum().reset_index()
    fig_pemakaian_harian = px.line(pemakaian_harian, x='Periode', y='Jumlah',
                                   title='Jumlah Pemakaian Mesin Harian',
                                   color_discrete_sequence=['#EF553B'])
    st.plotly_chart(fig_pemakaian_harian)

    # Rincian Pemakaian per Supplier
    pemakaian_supplier = filtered_data.pivot_table(index='Periode', columns='Supplier', values='Jumlah', aggfunc='sum').reset_index()
    pemakaian_supplier = pemakaian_supplier.melt(id_vars='Periode', var_name='Supplier', value_name='Jumlah')
    fig_pemakaian_supplier = px.bar(pemakaian_supplier, x='Periode', y='Jumlah', color='Supplier',
                                    title='Rincian Pemakaian Mesin per Supplier', barmode='stack',
                                    color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pemakaian_supplier)
else:
    st.write("No data available for the selected filters.")
