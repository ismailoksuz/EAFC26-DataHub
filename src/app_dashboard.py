import streamlit as st
import pandas as pd
import os
import json
from pathlib import Path

JSON_DIR = Path("output/json")
CSV_PATH = "data/players.csv"
CSS_PATH = Path("src/style.css") 
SELECTED_COLOR = "#07F468"

@st.cache_data
def load_data(file_path):
    """Loads a single JSON file or the full CSV into a pandas DataFrame."""
    try:
        if file_path.name.endswith('.json'):
            with open(file_path, 'r', encoding="utf-8") as f:
                data = json.load(f)
                df = pd.DataFrame(data)
        elif file_path.name.endswith('.csv'):
            df = pd.read_csv(file_path, low_memory=False)
        else:
            return pd.DataFrame()
        for col in df.columns:
            if df[col].dtype == 'object' and ('_eur' in col or 'version' in col):
                 df[col] = pd.to_numeric(df[col], errors='coerce')
            elif df[col].dtype in ['float64', 'int64'] and df[col].max() < 100:
                 df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
        return df
    except Exception:
        return pd.DataFrame()

def get_json_files():
    """Gets all JSON filenames from the output directory."""
    try:
        files = [f.name for f in JSON_DIR.glob("*.json")]
        files.sort()
        return files
    except Exception:
        return []

def load_and_inject_css():
    """Loads CSS from the external file and injects it."""
    try:
        with open(CSS_PATH) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Warning: {CSS_PATH} not found. Default styles will be used.")

def draw_sidebar_filters(df_base):
    """Draws custom filters on the sidebar dynamically based on columns."""
    st.sidebar.header("Custom Filters (ALL Search)")
    df_filtered = df_base.copy()
    rating_cols = ['overall', 'potential']
    basic_info_cols = ['age', 'player_positions', 'club_name', 'nationality_name']
    attribute_cols = [
        'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic', 
        'attacking_crossing', 'movement_reactions', 'power_shot_power'
    ]
    technical_cols = ['weak_foot', 'skill_moves', 'preferred_foot']
    st.sidebar.subheader("Ratings & Age")
    for col_name in rating_cols + ['age']:
        if col_name in df_filtered.columns:
            min_val = int(df_base[col_name].min())
            max_val = int(df_base[col_name].max())
            state_key = f"{col_name}_range"
            if state_key not in st.session_state:
                st.session_state[state_key] = (min_val, max_val)
            current_range = st.sidebar.slider(
                f"{col_name.replace('_', ' ').title()}:",
                min_value=min_val,
                max_value=max_val,
                value=st.session_state[state_key]
            )
            st.session_state[state_key] = current_range
            df_filtered = df_filtered[
                (df_filtered[col_name] >= current_range[0]) & 
                (df_filtered[col_name] <= current_range[1])
            ]
            
    st.sidebar.subheader("Key Attributes")
    for col_name in attribute_cols:
        if col_name in df_filtered.columns:
            min_val = int(df_base[col_name].min())
            max_val = int(df_base[col_name].max())
            state_key = f"{col_name}_range"
            if state_key not in st.session_state:
                st.session_state[state_key] = (min_val, max_val)
            current_range = st.sidebar.slider(
                f"{col_name.replace('_', ' ').title()}:",
                min_value=min_val,
                max_value=max_val,
                value=st.session_state[state_key]
            )
            st.session_state[state_key] = current_range
            df_filtered = df_filtered[
                (df_filtered[col_name] >= current_range[0]) & 
                (df_filtered[col_name] <= current_range[1])
            ]
    st.sidebar.subheader("Categorical & Technical")    
    for col_name in basic_info_cols + technical_cols:
        if col_name in df_filtered.columns:
            if col_name in ['skill_moves', 'weak_foot']:
                min_val = int(df_base[col_name].min())
                max_val = int(df_base[col_name].max())
                state_key = f"{col_name}_range"
                if state_key not in st.session_state:
                    st.session_state[state_key] = (min_val, max_val)
                current_range = st.sidebar.select_slider(
                    f"{col_name.replace('_', ' ').title()}:",
                    options=range(min_val, max_val + 1),
                    value=st.session_state[state_key]
                )
                st.session_state[state_key] = current_range
                df_filtered = df_filtered[
                    (df_filtered[col_name] >= current_range[0]) & 
                    (df_filtered[col_name] <= current_range[1])
                ]
            else:
                unique_values = df_base[col_name].dropna().unique()
                selected_options = st.sidebar.multiselect(
                    f"{col_name.replace('_', ' ').title()}:",
                    options=unique_values
                )
                if selected_options:
                    if col_name == 'player_positions':
                        df_filtered = df_filtered[
                            df_filtered['player_positions'].fillna('').apply(
                                lambda x: any(pos in x for pos in selected_options)
                            )
                        ]
                    else:
                        df_filtered = df_filtered[df_filtered[col_name].isin(selected_options)]
    return df_filtered
def draw_main_content(df, title):
    """Draws the main table view."""
    st.header(title)
    if df.empty:
        st.info("No players found matching the criteria.")
        return
    st.subheader(f"Total Players: {len(df)}")
    columns_to_show = [
        'short_name', 'overall', 'potential', 'age', 'player_positions', 
        'club_name', 'nationality_name', 'value_eur', 'wage_eur'
    ]
    final_cols = [col for col in columns_to_show if col in df.columns]
    st.dataframe(df[final_cols].sort_values(by='overall', ascending=False), 
                 use_container_width=True)
def main_dashboard():
    st.set_page_config(layout="wide", page_title="FC26 DataHub")
    load_and_inject_css()    
    st.markdown("""
# FC26 DataHub Player Explorer
by [İsmail ÖKSÜZ](https://www.github.com/ismailoksuz)
""")
    available_files = get_json_files()
    if not available_files:
        st.warning(f"No JSON files found in the '{JSON_DIR}' directory. Please run generate.py first.")
        return
    if 'selected_list' not in st.session_state:
        st.session_state['selected_list'] = 'ALL'
    st.sidebar.header("Ready Player Lists")    
    filter_options = ['ALL'] + [f.replace('.json', '').replace('_', ' ').title() for f in available_files]
    for option_name in filter_options:
        key = f"click_{option_name.replace(' ', '_')}"
        is_selected = st.session_state['selected_list'] == option_name
        button_clicked = st.sidebar.button(
            option_name, 
            key=key, 
            use_container_width=True
        )
        if is_selected:
            st.markdown(
                f"""
                <style>
                div[data-testid="stSidebar"] div.stButton button[data-testid*="{key}-container"] {{
                    background-color: {SELECTED_COLOR} !important;
                    color: black !important;
                    font-weight: bold;
                }}
                </style>""", unsafe_allow_html=True
            )
        if button_clicked:
            st.session_state['selected_list'] = option_name
            st.rerun()
    st.sidebar.markdown("---")
    df_all = load_data(Path(CSV_PATH))
    df_filtered_all = draw_sidebar_filters(df_all)
    current_selection = st.session_state['selected_list']
    if current_selection == 'ALL':
        draw_main_content(df_filtered_all, "ALL Players (Filtered by Custom Controls)")
    else:
        original_filename = current_selection.lower().replace(' ', '_') + '.json'
        file_path = JSON_DIR / original_filename        
        df_ready_list = load_data(file_path)
        if 'overall' in df_ready_list.columns and 'overall_range' in st.session_state:
             df_ready_list = df_ready_list[
                (df_ready_list['overall'] >= st.session_state.overall_range[0]) & 
                (df_ready_list['overall'] <= st.session_state.overall_range[1])
             ]
        if 'age' in df_ready_list.columns and 'age_range' in st.session_state:
             df_ready_list = df_ready_list[
                (df_ready_list['age'] >= st.session_state.age_range[0]) & 
                (df_ready_list['age'] <= st.session_state.age_range[1])
             ]
        draw_main_content(df_ready_list, f"Ready List: {current_selection}")
if __name__ == "__main__":
    if not JSON_DIR.exists():
        JSON_DIR = Path(os.getcwd()) / JSON_DIR     
    main_dashboard()