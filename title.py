import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

# MySQL connection details
def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Guvi@12345",
            database="tennis"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Predefined queries
queries = {
    "categories_table": "select * from categories_table;",
    "competitions_table": "select * from competitions_table;",
    "complexes_table": "select * from complexes_table;",
    "venues_table": " select * from venues_table;",
    "competitor_rankings_table": "select * from competitor_rankings_table;",
    "competitors_table": "select * from competitors_table;",
    "List all competitions along with their category name" : 
    """ SELECT c.name, cat.category_name 
    FROM competitions_table c 
    JOIN categories_table cat 
    ON c.category_id = cat.category_id;""",
    "Count the number of competitions in each category":
    """ SELECT cat.category_name,
    COUNT(c.id) AS competition_count
    FROM competitions_table c
    JOIN categories_table cat
    ON c.category_id = cat.category_id
    GROUP BY cat.category_name;""",
    "Find all competitions of type doubles":
    """ SELECT id,`name`,`type`
    FROM competitions_table
    WHERE `type` = 'doubles';""",
    "Get competitions that belong to a specific category (e.g., ITF Men)":
    """SELECT 
    c.id,
    c.`name`,
    c.category_id
FROM 
    competitions_table c
JOIN 
    categories_table cat
ON 
    c.category_id = cat.category_id
WHERE 
    cat.category_name = 'ITF Men';
""",
"Identify parent competitions and their sub-competitions":
"""SELECT p.`name` AS parent_competition, c.`name` AS sub_competition
FROM Competitions_table c
JOIN Competitions_table p ON c.id = p.id;
""",
"Analyze the distribution of competition types by category":
"""SELECT 
    cat.category_name,
    c.`type`,
    COUNT(c.id) AS count
FROM 
    competitions_table c
JOIN 
    categories_table cat
ON 
    c.category_id = cat.category_id
GROUP BY 
    cat.category_name, c.`type`
ORDER BY 
    cat.category_name, c.type;
""",
"List all competitions with no parent top-level competitions":
""" SELECT `name`   
FROM Competitions_table
WHERE id IS NULL;
""",
"List all venues along with their associated complex name":
"""
SELECT v.venue_name, c.name
FROM Venues_table v
JOIN Complexes_table c ON v.complex_id = c.complex_id;
""",
"Count the number of venues in each complex":
"""SELECT c.`name`, COUNT(v.venue_id) AS venue_count
FROM Venues_table v
JOIN Complexes_table c ON v.complex_id = c.complex_id
GROUP BY c.`name`;
""",
"Get details of venues in a specific country (e.g., Chile)":
"""
SELECT *
FROM Venues_table
WHERE country_name = 'Chile';""",
"Identify all venues and their timezones":
"""SELECT venue_name, timezone
FROM Venues_table;
""",
"Find complexes that have more than one venue":
"""SELECT c.`name`
FROM Venues_table v
JOIN Complexes_table c ON v.complex_id = c.complex_id
GROUP BY c.`name`
HAVING COUNT(v.venue_id) > 1;
""",
"List venues grouped by country":
"""SELECT country_name, GROUP_CONCAT(venue_name) AS venues
FROM Venues_table
GROUP BY country_name;
""",
"Find all venues for a specific complex (e.g., Nacional)":
"""
SELECT v.venue_name
FROM Venues_table v
JOIN Complexes_table c ON v.complex_id = c.complex_id
WHERE c.`name` = 'Nacional';
""",
"Get all competitors with their rank and points":
"""select rank_id, `rank`, points
from competitor_rankings_table
ORDER BY points ASC;
""",
"Find competitors ranked in the top 5":
"""select	c.competitor_id,com.`name`,`rank`
from competitor_rankings_table c
join competitors_table com
on c.competitor_id=com.competitor_id
where `rank` <=5 ;
""",
"Get the total points of competitors from a specific country (e.g., Croatia)":
"""
select c.points, cat.country, cat.`name`
from competitor_rankings_table c
join competitors_table cat
on c.competitor_id= cat.competitor_id
where country= 'Croatia';
""",
"Count the number of competitors per country":
"""
select country, country_code, count(competitor_id) AS number_of_competitor
from  Competitors_table
group by country, country_code;
""",
"Find competitors with the highest points in the current week":
"""
select c.points, cat.competitor_id, cat.`name`
from competitor_rankings_table c
join competitors_table cat
on c.competitor_id=cat.competitor_id
order by c.points ASC;
"""
}

# Load data from MySQL
def load_data(query, connection):
    try:
        return pd.read_sql(query, connection)
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()

# Main Streamlit app
def main():
    st.title("MySQL Table Viewer with Filters and Search")
    
    # Connect to MySQL
    connection = connect_to_mysql()
    if not connection:
        st.stop()
    
    # Sidebar for table selection
    selected_table = st.sidebar.selectbox("Select a table to view", list(queries.keys()))
    
    # Load the selected table data
    query = queries[selected_table]
    df = load_data(query, connection)
    
    if not df.empty:
        # Display the table
        st.header(f"Viewing {selected_table}")
        
        # Filters
        st.subheader("Filters")
        
        # Numeric column filters
        for column in df.select_dtypes(include=["int64", "float64"]).columns:
            min_val, max_val = int(df[column].min()), int(df[column].max())
            filter_range = st.slider(f"Filter by {column}", min_value=min_val, max_value=max_val, value=(min_val, max_val))
            df = df[(df[column] >= filter_range[0]) & (df[column] <= filter_range[1])]
        
        # Search filter
        st.subheader("Search")
        search_query = st.text_input("Search for a specific value:")
        if search_query:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
        
        # Display filtered and searched data
        st.dataframe(df)
    else:
        st.warning("No data available or error occurred.")
    
    # Close connection on app exit
    if connection.is_connected():
        connection.close()

if __name__ == "__main__":
    main()