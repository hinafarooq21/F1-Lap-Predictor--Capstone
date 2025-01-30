import pandas as pd
import streamlit as st
import math
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
import joblib
import time as t


# SideBar
st.sidebar.title("🔧 How It Works")
st.sidebar.write("")
st.sidebar.write("""
🏎️ **Build your dream F1 track & predict lap times!**  

### 🔹 Step 1: Set Up Your Track  
Pick a **Street Circuit** or **Race Track**, then adjust the sliders to customise track length, corners, and straights.  

### 🔹 Step 2: Calculate Lap Time  
Hit **"Calculate Lap Time"**, and our model crunches the numbers! 

### 🔹 Step 3: Get Your Result  
See your estimated lap time in **minutes:seconds** format. 

Want a faster lap? 
**Tweak the track details** and try again!  

""")
st.sidebar.write("")
st.sidebar.write("📂 **Project Files & Docs:**")  
st.sidebar.write("Find all project files and documentation on **[GitHub](https://github.com/hinafarooq21/F1-Lap-Predictor--Capstone)**.")  


X_train = pd.read_csv('X_train.csv')
scaler = StandardScaler()
scaler.fit(X_train)
st.markdown('<h1 style="text-align: center;">Lap Time Predictions 🏎️</h1>', unsafe_allow_html=True)

circuit_type = st.radio("Please select one:", ["Street Circuit", "Race Track"])
Type_bool = 1 if circuit_type == "Race Track" else 0
length = st.slider("Choose your desired track length", 3500, 7000)
longest_straight = st.slider("Longest straight of your track", 300, 2000)
turns = st.slider("How many corners does your track have", 8, 40)
grand_prix_held = 1
year = 2024

direction = 1
DistTurn1 = 500
Elevation = 10
Width = 12

race_laps = math.ceil(305000 / length)
race_dist = length * race_laps

column_input = ['Direction', 'Length', 'Turns', 'Grands Prix held', 'Year', 'Race Laps', 'Race Dist', 'DistTurn1', 'Longst Straight', 'Elevation', 'Width', 'Type_bool']
df_input = pd.DataFrame([[direction, length, turns, grand_prix_held, year, race_laps, race_dist, DistTurn1, longest_straight, Elevation, Width, Type_bool]], columns=column_input)

# Scale the input using the previously fitted scaler
df_input_scaled = df_input.copy()
df_input_scaled[column_input] = scaler.transform(df_input_scaled[column_input])  # Transform only

# Add constant column for statsmodels
df_input_scaled = sm.add_constant(df_input_scaled)

df_input_scaled['racedl'] = df_input_scaled['Race Dist'] * df_input_scaled['Longst Straight'] * df_input_scaled['Length']
df_input_scaled['Length_turns'] = df_input_scaled['Length'] * df_input_scaled['Turns']
df_input_scaled['Dist_turns'] = df_input_scaled['Race Dist'] * df_input_scaled['Turns']
df_input_scaled['Length_squared'] = df_input_scaled['Length'] ** 2

coeffs = {
        "const": 88.069107,
        "Grands Prix held": -1.896392,
        "Year": -7.441924,
        "Race Laps": -13.112486,
        "Race Dist": 6.867117,
        "Type_bool": -2.101098,
        "racedl": -1.362798,
        "Length_Turns": 1.292200,
        "Dist_Turns": -5.452637,
        "Length_squared": 3.698070
    }

predicted_lap_time = (
        coeffs["const"] +
        coeffs["Grands Prix held"] * df_input_scaled['Grands Prix held'] +
        coeffs["Year"] * df_input_scaled['Year'] +
        coeffs["Race Laps"] * df_input_scaled["Race Laps"] +
        coeffs["Race Dist"] * df_input_scaled["Race Dist"] +
        coeffs["Type_bool"] * df_input_scaled['Type_bool'] +
        coeffs["racedl"] * df_input_scaled['racedl'] +
        coeffs["Length_Turns"] * df_input_scaled['Length_turns'] +
        coeffs["Dist_Turns"] * df_input_scaled['Dist_turns'] +
        coeffs["Length_squared"] * df_input_scaled['Length_squared']
    )

# If predicted_lap_time is a Series, extract the first value using .iloc[0]
if isinstance(predicted_lap_time, pd.Series):
        predicted_lap_time = predicted_lap_time.iloc[0]  # Convert Series to scalar

# Convert to minutes and seconds
minutes = int(predicted_lap_time // 60)  # Whole minutes
seconds = predicted_lap_time % 60  # Remaining seconds as a float

# Format correctly (ensure seconds is a float, not Series)
formatted_time = f"{minutes}:{seconds:.1f}"  # Display as M:SS.s

# if st.button ("Calculate Lap Time"):
#     with st.spinner("Loading"):
#         t.sleep(2)
# # Display the predicted lap time
#     st.write(f"**Number of Laps: {race_laps}**")
#     st.write(f"**Predicted Lap Time: {formatted_time}**")
#     st.write(f"**Total Distance: {race_dist} m**")

#     st.markdown("#### **Want a faster lap? Adjust the track details and try again! 🏎️💨**")


if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = False
def callback():
    st.session_state.button_clicked = True
if (
    st.button("Calculate Lap Time", on_click=callback)
    or st.session_state.button_clicked
):
    with st.spinner("Loading"):
        t.sleep(1)
# Display the predicted lap time
    st.subheader(f"**Predicted Lap Time: {formatted_time}**")
    st.write(f"**Number of Laps: {race_laps}**")
    st.write(f"**Total Distance: {race_dist} m**")

    st.markdown("#### **Want a faster lap? Adjust the track details and try again! 🏎️💨**")


