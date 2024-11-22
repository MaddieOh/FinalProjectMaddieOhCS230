"""
Maddie Oh
CS230 - 6
Data Set: Volcanoes
URL:https://final-project-cs230-maddie-oh-3qzuyzbprthzzd62h9xrrc.streamlit.app/

Description:
This program analyzes the volcanoes data set looking at elevation as well as rock types.
I choose to incorporate a map that will display a radius around all volcanoes found within
the dataset, there is a zoom button, to scroll into the map. Additionally, I choose to analyze
the 10 ten countries with the most volcanoes and displayed it in a bar chart. Following I did a pie chart
that shows the rock types within the volcanoes that are present within that chosen region. Lastly,
there is a table that displays the volcano count in each region as well as volcanoes name and their elevation by ascending or descending order.
"""

import pandas as pd
import streamlit as st
import pydeck as pdk
import seaborn as sns
import matplotlib.pyplot as plt

# [PY3] Error checking with try/except
def load_data():
    try:
        df = pd.read_csv("volcanoes.csv", index_col="Volcano Number")
        return df
    except FileNotFoundError:
        st.error(f"File not found. Ensure the file is in the correct location.")
        return pd.DataFrame()

# [DA1] Clean the data
# [DA9] Perform calculations on DataFrame columns (convert 'Elevation (m)' to numeric)
def cleaning_data(df):
    # Use a lambda to convert 'Elevation (m)' to numeric, non-numeric errors will be coerced to missing values
    df['Elevation (m)'] = df['Elevation (m)'].apply(lambda x: pd.to_numeric(x, errors='coerce'))
    # Drop rows with missing data in columns
    df = df.dropna(subset=['Elevation (m)', 'Latitude', 'Longitude'])
    return df

# [ST1], [ST2], [ST3]
# [ST4] Sidebar customization
def sidebar(df):
    st.sidebar.header("Volcano Data Analysis")

    # [ST2] Dropdown widget: region selection
    region_options = ["All Regions"] + df['Volcanic Region'].unique().tolist()
    selected_region = st.sidebar.selectbox("Select a Region", region_options)

    # [ST1] button widget: elevation filter
    elevation_filter = st.sidebar.radio(
        "Show Volcanoes by Elevation",
        ("Highest", "Lowest")
    )
    return selected_region, elevation_filter

# [ST1] Text input widget: Search Bar
def search_bar(df):
    search_term = st.text_input("Search for a Country you want to see on the map:", "")
    if search_term:
        # [DA4] Filter data by one condition (case-insensitive search)
        search_term = search_term.strip().lower()
        # [PY4]List comprehension
        df['Country_lower'] = [x.strip().lower() for x in df['Country']]
        if search_term in df['Country_lower'].values:
            filtered_data = df[df['Country_lower'] == search_term]
            st.write(f"Showing data for country: {search_term.title()}:")
            return filtered_data
        else:
            st.warning(f"No country was found for '{search_term.title()}'.")
            return pd.DataFrame()
    else:
        return df

# [DA4]
def filter_data(df, selected_region):
    if selected_region != "All Regions":
        df = df[df['Volcanic Region'] == selected_region]
    return df

def elevation_filter_display(filtered_data, elevation_filter):
    if filtered_data.empty:  # Check for empty DF
        st.write("No data to display based on your filters.")
        return  # Exits function if no data

    if elevation_filter == "Highest":
        # [DA3] Find top largest/smallest values of a column
        highest_volcano = filtered_data.loc[filtered_data['Elevation (m)'].idxmax()]
    else:
        highest_volcano = filtered_data.loc[filtered_data['Elevation (m)'].idxmin()]

    st.write(f"The volcano with the {elevation_filter.lower()} elevation in this region is:")
    st.write(highest_volcano[['Volcano Name', 'Country', 'Elevation (m)']])

# [MAP] Detailed map include hover tooltips & two radius, one for exact location and other for visibility
def map(filtered_data):
    st.subheader("Map of Volcanoes Around the World: Zoom in or out & select regions in the sidebar")

    # Layer for larger radius for general location
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data = filtered_data,
        get_position = '[Longitude, Latitude]',
        get_radius = 7000,  # Larger radius for general view
        get_color = '[200, 30, 0, 160]',
        pickable = True,
        filled = True,                     #Fills to specified color
        stroked = False,                   #Provides outlines around circles
    )
    # Layer for  smaller radius for zoomed-in view for exact loco.
    exact_location_layer = pdk.Layer(
        "ScatterplotLayer",
        data = filtered_data,
        get_position = '[Longitude, Latitude]',
        get_radius = 1000,
        get_color = '[0, 0, 255, 160]',
        pickable = True,
        filled = True,
        stroked = False,
    )
    # Create a deck with both layers
    st.pydeck_chart(
        pdk.Deck(
            map_style = "mapbox://styles/mapbox/outdoors-v11", #Found from MapBox website
            initial_view_state = pdk.ViewState(
                latitude = filtered_data['Latitude'].mean(),
                longitude = filtered_data['Longitude'].mean(),
                zoom = 6,
                pitch = 30,
            ),
            layers = [scatter_layer, exact_location_layer],
            tooltip = {"text": "{Volcano Name}\nCountry: {Country}\nElevation: {Elevation (m)}m"}, # is used when you hover over the radius you will see the description
        )
    )

# [VIZ1] Bar chart visualization
def bar_chart(df):
    st.subheader("Countries with Greatest Number of Volcanoes")
    top_countries = df['Country'].value_counts().head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_countries.values, y=top_countries.index, palette="crest", ax=ax) #Bar chart using Seaborn
    ax.set_title("Top 10 Countries by Number of Volcanoes")
    ax.set_xlabel("Number of Volcanoes")
    ax.set_ylabel("Country")
    st.pyplot(fig)


# [VIZ2] Pie chart visualization
# Pie chart for rock type distribution
def pie_chart(df):
    st.subheader("Volcano Rock Type Distribution")
    rock_types = df['Dominant Rock Type'].value_counts()

    if rock_types.empty:
        st.write("No data available for rock type distribution.")
        return
    fig2, ax2 = plt.subplots(figsize=(8, 8))  # Adjust figure size for clarity
    wedges, texts = ax2.pie(
        rock_types.values,
        startangle=90,
        colors=sns.color_palette("flare", len(rock_types)) #Used seaborn palette online
    )
    # Legend for rock types and percentage in the region
    ax2.legend(
        wedges,
        [f"{label} ({percent:.1f}%)" for label, percent in zip(rock_types.index, (rock_types.values / rock_types.sum()) * 100)],
        title="Rock Types",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
    )

    ax2.set_title("Distribution of Rock Types (By Regions)", fontsize=14)
    st.pyplot(fig2)

# [PY2] Function that returns multiple values
def elevation_stats(df):
    avg_elevation = df['Elevation (m)'].mean()
    min_elevation = df['Elevation (m)'].min()
    max_elevation = df['Elevation (m)'].max()
    return avg_elevation, min_elevation, max_elevation

def sorted_table(df):
    # Streamlit widgets to select sorting options
    sort_column = st.selectbox("Select column to sort by", ["Volcano Name", "Elevation (m)"])
    sort_order = st.radio("Select sort order", ["Ascending", "Descending"])

    # Sort the DF based on previous selections
    if sort_column == "Volcano Name":
        df_sorted = df.sort_values(by="Volcano Name", ascending=(sort_order == "Ascending"))
    else:
        df_sorted = df.sort_values(by="Elevation (m)", ascending=(sort_order == "Ascending"))

    # Display sorted table
    st.write("Sorted Volcano Data:")
    st.dataframe(df_sorted[['Volcano Name', 'Elevation (m)']])

def num_volcanoes_by_region(df):
    region_counts = df['Volcanic Region'].value_counts().reset_index()
    region_counts.columns = ['Region', 'Volcano Count']
    return region_counts

def display_region_counts(df):
    region_counts =num_volcanoes_by_region(df)
    st.subheader("Number of Volcanoes by Regions")
    st.write(region_counts)

# [PY1] Function with default parameter value
"""Help with ChatGPT see Section 1: """
def elevation_histogram(df, elevation_limit=1000, filter_above=True):
    # Filter the DF based on an elevation
    if filter_above:
        filtered_Volc = df[df['Elevation (m)'] > elevation_limit]
        title = f"Volcanoes with Elevation Above {elevation_limit}m"
    else:
        filtered_Volc = df[df['Elevation (m)'] <= elevation_limit]
        title = f"Volcanoes with Elevation Below {elevation_limit}m"

    # Plot histogram
    st.subheader(title)
    if filtered_Volc.empty:
        st.write("No volcanoes match this criteria.")
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(
        filtered_Volc['Elevation (m)'],
        bins=30,
        kde=True,
        color="coral",
        ax=ax
    )
    ax.set_title(title)
    ax.set_xlabel("Elevation (m)")
    ax.set_ylabel("Number of Volcanoes")
    st.pyplot(fig)

# Main function
def main():
    st.title("Maddie Oh CS230 Final Project: Volcanoes")
    df = load_data()                # Load and clean data
    df = cleaning_data(df)
    selected_region, elevation_filter = sidebar(df) # Sidebar for filtering options
    filtered_data = search_bar(df)                # Search Bar for country search
    # Filtered data based on sidebar selections
    if not filtered_data.empty:
        filtered_data = filter_data(filtered_data, selected_region)
        elevation_filter_display(filtered_data, elevation_filter)    #show highest/lowest elevation volcano
        map(filtered_data)              # Plot volcanoes map
        pie_chart(filtered_data)          #rock type distribution
        bar_chart(df)               # countries with most volcanoes

        display_region_counts(df)
        st.subheader("Table: Filtering Volcanoes & Elevation")
        st.write("(See all volcanoes and their elevation, adjust from ascending to descending order.)")
        sorted_table(df)

        # [PY1] Call the function twice, once with the default value, once without
        elevation_histogram(filtered_data) #Default value
        elevation_histogram(filtered_data, elevation_limit=1000, filter_above=False)

        # elevation stats in sidebar
        avg_elevation, min_elevation, max_elevation = elevation_stats(df)
        st.sidebar.write(f"Average Elevation: {avg_elevation:.2f} m")
        st.sidebar.write(f"Minimum Elevation: {min_elevation:.2f} m")
        st.sidebar.write(f"Maximum Elevation: {max_elevation:.2f} m")
    else:
        st.write("No data to display. Please check your country search input.")

if __name__ == "__main__":
    main()
