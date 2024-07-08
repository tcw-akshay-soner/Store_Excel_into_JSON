import streamlit as st
import pandas as pd
import json
import warnings
warnings.filterwarnings('ignore')

# Define functions outside the class
def extract_tables(df):
    tables = []
    current_table = []
    for i, row in df.iterrows():
        if row.isnull().all():
            if current_table:
                tables.append(pd.DataFrame(current_table).reset_index(drop=True))
                current_table = []
        else:
            current_table.append(row)
    if current_table:
        tables.append(pd.DataFrame(current_table).reset_index(drop=True))
    return tables

def separate_tables(table):
    blank_col_index = table.columns[table.isnull().all()].tolist()
    print(blank_col_index)

    if blank_col_index:
        blank_col_index = table.columns.get_loc(blank_col_index[2])
        tname = table.iloc[:, 2:blank_col_index]
        values_df = table.iloc[:, 2:blank_col_index]
        percentages_df = table.iloc[1:, blank_col_index+2:]
    else:
        values_df = table
        percentages_df = pd.DataFrame()

    if not values_df.empty:
        values_df.columns = values_df.iloc[1]
        values_df = values_df[2:]
        values_df.set_index(values_df.columns[0], inplace=True)

    if not percentages_df.empty:
        percentages_df.columns = percentages_df.iloc[0]
        percentages_df = percentages_df[1:]
        percentages_df.set_index(percentages_df.columns[0], inplace=True)

    return values_df, percentages_df, tname

st.title("Store the Excel data into Json")

uploaded_file = st.file_uploader("Upload an Excel file", type="xlsx")

if uploaded_file:
    file = pd.ExcelFile(uploaded_file)
    sheets = file.sheet_names[1:]

    selected_sheet = st.selectbox("Select a sheet", sheets, key="sheet_selectbox")

    if selected_sheet:
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        tables = extract_tables(df)
        clean_tables = [separate_tables(table) for table in tables]

        data = {}

        for i, (values_df, percentages_df, tname) in enumerate(clean_tables):
            table_name = f"Table {i + 1}: {tname.iloc[0, 0]}"
            sheet_name = selected_sheet

            values_df = pd.DataFrame(values_df)
            percentages_df = pd.DataFrame(percentages_df)

            if sheet_name not in data:
                data[sheet_name] = {}

            data[sheet_name][table_name] = (values_df, percentages_df)
            # print(data)
            st.write(data)
            # json_data = data.to_json('temp1.json', orient='records',lines=True)
            df1 = pd.DataFrame(data)

            json_df = df1.to_json()
            csv_df = df1.to_csv("temp1.csv")
            with open('temp1.json','w') as f:
                json.dump(json_df,f)


else:
    st.write("Please upload an Excel file.")


