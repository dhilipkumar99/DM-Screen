import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# Set the page configuration
st.set_page_config(page_title="DM Screen", layout="wide")

# Title
st.markdown(
    "<h1 style='text-align: center; color: #4B0082;'>DM Screen</h1>",
    unsafe_allow_html=True
)

# Load the CSV file with updated caching
@st.cache_data
def load_d100s():
    try:
        df = pd.read_csv("d100s.csv")
        return df
    except FileNotFoundError:
        st.error("The file 'd100s.csv' was not found. Please ensure it's in the correct directory.")
        return pd.DataFrame()

d100s = load_d100s()

# Initialize session state for Initiative Tracker
if 'initiative_data' not in st.session_state:
    st.session_state.initiative_data = pd.DataFrame(columns=['Name', 'Initiative', 'AC'])

# Sidebar - Spell Search
st.sidebar.header("Spell Search")
spells_name = st.sidebar.text_input("Enter a Spell:")
goButton_spells = st.sidebar.button("Search Spell", key="search_spell_button")

# Tabs
tabs = st.tabs([
    "Spell Search",
    "Initiative Tracker",
    "Generated Environment Encounters",
    "Treasure Hoard",
    "Links"
])

# ---------------------- Spell Search Tab ----------------------
with tabs[0]:
    st.header("Spell Search")
    
    if goButton_spells:
        input_name = spells_name.strip()
        if input_name:
            formatted_name = input_name.replace(" ", "-")
            generated_link = f"https://www.aidedd.org/dnd/sorts.php?vo={formatted_name}"
            
            try:
                response = requests.get(generated_link)
                if response.status_code == 200:
                    content = response.text
                
                    # Remove all <script> tags and their contents
                    content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL)
                
                    # Remove specific JavaScript lines like 'window.dataLayer' or 'gtag'
                    content = re.sub(r'window\.dataLayer\s*=\s*\[\];', '', content)
                    content = re.sub(r'gtag\(.*?\);', '', content)
                
                    # Further clean the HTML by removing any other tags
                    cleaned_content = re.sub(r'<.*?>', '', content)
                    
                    # Find the position of the spell name
                    pattern = re.compile(re.escape(input_name), re.IGNORECASE)
                    match = pattern.search(cleaned_content)
                    if match:
                        spell_position = match.start()
                        cleaned_content = cleaned_content[spell_position:]
                    else:
                        st.warning("Spell name not found in the content.")
                    
                    st.text_area("Spell Details", cleaned_content, height=300)
                else:
                    st.error("Failed to fetch the webpage.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a spell name.")
    
    st.markdown("""
    ### Spells Resources:
    - [Spells Filter](https://www.aidedd.org/dnd-filters/spells-5e.php)
    """, unsafe_allow_html=True)

# ---------------------- Initiative Tracker Tab ----------------------
with tabs[1]:
    st.header("Initiative Tracker")
    
    col1, col2, col3, col4 = st.columns([3,1,1,1])
    
    with col1:
        name_init = st.text_input("Name", key="initiative_name_input")
    with col2:
        initiative = st.number_input("Initiative", value=0, step=1, key="initiative_number_input")
    with col3:
        ac = st.number_input("AC", value=0, step=1, key="ac_number_input")
    with col4:
        submit_init = st.button("Submit", key="submit_initiative_button")
    
    if submit_init:
        if name_init:
            new_row = pd.DataFrame({
                'Name': [name_init],
                'Initiative': [initiative],
                'AC': [ac]
            })
            st.session_state.initiative_data = pd.concat([st.session_state.initiative_data, new_row], ignore_index=True)
            # Sort the dataframe by Initiative descending
            st.session_state.initiative_data = st.session_state.initiative_data.sort_values(by='Initiative', ascending=False).reset_index(drop=True)
            st.success("Added to Initiative Tracker!")
        else:
            st.warning("Please enter a name.")
    
    # Display the table
    st.dataframe(st.session_state.initiative_data, height=300)
    
    reorder_button = st.button("Reorder in Descending Order", key="reorder_initiative_button")
    if reorder_button:
        st.session_state.initiative_data = st.session_state.initiative_data.sort_values(by='Initiative', ascending=False).reset_index(drop=True)
        st.success("Reordered the Initiative Tracker!")

# ---------------------- Generated Environment Encounters Tab ----------------------
with tabs[2]:
    st.header("Generated Environment Encounters")
    
    encounter_output = st.empty()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("Dungeon Encounters", key="dungeon_encounters_button"):
            url = "https://randomencountersai.com/dungeon/"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    content = response.text
                    # Extract encounters using regex
                    match = re.search(r'D4 Random Dungeon Encounters(.*?)Generated by GPT-3 and lightly edited by a human', content, re.DOTALL)
                    if match:
                        clean_text = re.sub(r'<.*?>', '', match.group(1))
                        encounters = re.split(r'\.\s*', clean_text)
                        encounters = [enc.strip() for enc in encounters if enc.strip()]
                        encounter_output.text("\n".join(encounters))
                    else:
                        st.warning("Could not extract dungeon encounters.")
                else:
                    st.error("Failed to fetch the webpage.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    
    with col2:
        if st.button("City Encounters", key="city_encounters_button"):
            url = "https://randomencountersai.com/city/"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    content = response.text
                    match = re.search(r'D1 Random City Encounters(.*?)Generated by', content, re.DOTALL)
                    if match:
                        clean_text = re.sub(r'<.*?>', '', match.group(1))
                        encounters = re.split(r'\.\s*', clean_text)
                        encounters = [enc.strip() for enc in encounters if enc.strip()]
                        encounter_output.text("\n".join(encounters))
                    else:
                        st.warning("Could not extract city encounters.")
                else:
                    st.error("Failed to fetch the webpage.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    
    with col3:
        if st.button("Grassland Encounters", key="grassland_encounters_button"):
            url = "https://randomencountersai.com/grassland/"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    content = response.text
                    match = re.search(r'D1 Random Grassland Encounters(.*?)Generated by', content, re.DOTALL)
                    if match:
                        clean_text = re.sub(r'<.*?>', '', match.group(1))
                        encounters = re.split(r'\.\s*', clean_text)
                        encounters = [enc.strip() for enc in encounters if enc.strip()]
                        encounter_output.text("\n".join(encounters))
                    else:
                        st.warning("Could not extract grassland encounters.")
                else:
                    st.error("Failed to fetch the webpage.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    
    with col4:
        if st.button("Forest Encounters", key="forest_encounters_button"):
            url = "https://randomencountersai.com/forest/"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    content = response.text
                    match = re.search(r'D1 Random Forest Encounters(.*?)Generated by', content, re.DOTALL)
                    if match:
                        clean_text = re.sub(r'<.*?>', '', match.group(1))
                        encounters = re.split(r'\.\s*', clean_text)
                        encounters = [enc.strip() for enc in encounters if enc.strip()]
                        encounter_output.text("\n".join(encounters))
                    else:
                        st.warning("Could not extract forest encounters.")
                else:
                    st.error("Failed to fetch the webpage.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    
    with col5:
        if st.button("Townsfolk Backstories", key="backstory_button"):
            url = "https://backstorygenerator.com/"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    content = response.text
                    # Remove unwanted parts
                    cleaned_content = re.sub(r'.*Generated by GPT-3 and \(Lightly\) Edited by a Human for formatting', '', content, flags=re.DOTALL)
                    cleaned_content = re.sub(r'D&D Backstory Generator with GPT-3 AI.*', '', cleaned_content, flags=re.DOTALL)
                    # Remove HTML tags
                    clean_text = re.sub(r'<.*?>', '', cleaned_content)
                    sentences = re.split(r'\.\s*', clean_text)
                    sentences = [s.strip() for s in sentences if s.strip()]
                    encounter_output.text("\n".join(sentences))
                else:
                    st.error("Failed to fetch the webpage.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# ---------------------- Treasure Hoard Tab ----------------------
with tabs[3]:
    st.header("Treasure Hoard")
    
    row_number = st.number_input("Enter a number between 1 and 100:", min_value=1, max_value=100, value=1, step=1, key="treasure_row_input")
    submit_d100 = st.button("Submit", key="submit_treasure_button")
    
    if submit_d100:
        if not d100s.empty:
            if 1 <= row_number <= len(d100s):
                row = d100s.iloc[row_number - 1]
                st.subheader(f"Selected Row Number: {row_number}")
                for col in d100s.columns:
                    st.markdown(f"**{col}:** {row[col]}")
            else:
                st.error("Row number out of bounds.")
        else:
            st.error("The data frame is empty. Please check the CSV file.")

# ---------------------- Links Tab ----------------------
with tabs[4]:
    st.header("Links")
    
    # Conditions Search
    st.subheader("Conditions")
    
    condition_options = [
        "Ability Burn", "Ability Damaged", "Ability Drained", "Blinded", "Blown Away", "Checked",
        "Confused", "Cowering", "Dazed", "Dazzled", "Dead", "Deafened", "Disabled", "Dying",
        "Energy Drained", "Entangled", "Exhausted", "Fascinated", "Fatigued", "Flat-Footed",
        "Frightened", "Grappling", "Helpless", "Incorporeal", "Invisible", "Knocked Down",
        "Nauseated", "Panicked", "Paralyzed", "Petrified", "Pinned", "Prone", "Shaken",
        "Sickened", "Stable", "Staggered", "Stunned", "Turned", "Unconscious"
    ]
    
    condition_select = st.selectbox("Select a Condition:", options=condition_options, key="condition_select_box")
    goButton_conditions = st.button("Search Condition", key="search_condition_button")
    
    box_condition = st.empty()
    htmlContentOutputcondition = st.empty()
    
    if goButton_conditions:
        selected_condition = condition_select
        formatted_name = selected_condition.replace(" ", "_")
        generated_link = f"https://dungeons.fandom.com/wiki/SRD:{formatted_name}"
        
        try:
            response = requests.get(generated_link)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                paragraphs = soup.select(".mw-parser-output p")
                extracted_text = ' '.join([p.get_text() for p in paragraphs])
                htmlContentOutputcondition.text(extracted_text)
            else:
                htmlContentOutputcondition.error("Failed to fetch the webpage.")
        except Exception as e:
            htmlContentOutputcondition.error(f"An error occurred: {e}")
    
    # Dynamically update the box title based on the selected condition
    box_condition.markdown(f"### Condition: {condition_select}")
    
    st.markdown("---")
    
    # Useful Links for DMs
    st.subheader("Useful Links for DMs")
    links = {
        "Reference Sheet for Combat": "https://donjon.bin.sh/5e/quickref/",
        "Encounters with Stats": "https://www.chaosgen.com/dnd5e/encounter",
        "Quest Generator": "https://donjon.bin.sh/fantasy/random/",
        "Initiative Tracker": "https://donjon.bin.sh/5e/initiative/",
        "Monsters with Stats": "https://www.aidedd.org/dnd-filters/monsters.php",
        "Shops with Magic Items": "https://donjon.bin.sh/5e/magic/shop.html",
        "Spells": "https://www.aidedd.org/dnd-filters/spells-5e.php"
    }
    
    for name, link in links.items():
        st.markdown(f"- **{name}:** [Link]({link})")
