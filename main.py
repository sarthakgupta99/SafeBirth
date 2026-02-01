import streamlit as st
from streamlit_option_menu import option_menu
import pickle
import warnings
import pandas as pd
import plotly.express as px
from io import StringIO
import requests
import numpy as np
from sklearn.preprocessing import StandardScaler

# --- 1. CONFIGURATION (Must be the first Streamlit command) ---
st.set_page_config(
    page_title="SafeBirth AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import local modules (Ensure the codebase folder exists)
from codebase.dashboard_graphs import MaternalHealthDashboard

# --- 2. LOAD MODELS ---
# Note: Ensure both .sav files were trained on your current Python version
try:
    maternal_model = pickle.load(open("model/finalized_maternal_model.sav", 'rb'))
    fetal_model = pickle.load(open("model/fetal_health_classifier.sav", 'rb'))
    scaler_maternal = pickle.load(open('model/scaler_maternal_model.sav', 'rb'))
except FileNotFoundError:
    st.error("⚠️ Model files not found. Please check the 'model/' folder.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Error loading models: {e}. You may need to retrain them.")
    st.stop()

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("SafeBirth AI")
    st.caption("Advanced Maternal Health Analytics")
    
    selected = option_menu(
        menu_title=None,
        options=['About Project', 'Pregnancy Risk', 'Fetal Health', 'Live Dashboard'],
        icons=['info-circle', 'activity', 'heart-pulse', 'graph-up-arrow'],
        default_index=0,
    )
    
    st.markdown("---")
    
# --- 4. SECTIONS ---

# === ABOUT US ===
if selected == 'About Project':
    st.title("Welcome to SafeBirth AI 🏥")
    st.markdown("""
    **SafeBirth** leverages advanced predictive analytics to improve maternal and fetal healthcare outcomes. 
    Our system empowers proactive decisions by identifying potential risks early.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Pregnancy Risk Assessment")
        st.write("Analyzes critical maternal health markers—Age, Blood Pressure, and Glucose levels—to predict pregnancy risk categories (Low, Mid, High).")
        try:
            st.image("graphics/image1.png", use_column_width=True)
        except:
            st.warning("Image not found: graphics/image1.png")

    with col2:
        st.subheader("Fetal Health Screening")
        st.write("Utilizes Cardiotocogram (CTG) data to assess fetal well-being. This model helps identify pathological states requiring immediate intervention.")
        try:
            st.image("graphics/image2.png", use_column_width=True)
        except:
            st.warning("Image not found: graphics/image2.png")

# === PREGNANCY RISK PREDICTION ===
if selected == 'Pregnancy Risk':
    st.title('Maternal Pregnancy Risk Predictor')
    st.markdown("Enter the patient's physiological parameters below to assess risk levels.")
    st.divider()

    col1, col2, col3 = st.columns(3)
    
    # Using number_input is safer than text_input for models
    with col1:
        age = st.number_input('Age (Years)', min_value=10, max_value=70, value=25)
        bodyTemp = st.number_input('Body Temperature (°C)', min_value=30.0, max_value=45.0, value=37.0)

    with col2:
        diastolicBP = st.number_input('Diastolic BP (mmHg)', min_value=30, max_value=150, value=80)
        heartRate = st.number_input('Heart Rate (bpm)', min_value=40, max_value=200, value=70)

    with col3:
        BS = st.number_input('Blood Glucose (mmol/L)', min_value=0.0, max_value=20.0, value=7.0)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button('Analyze Risk Level', type="primary"):
        try:
            # Prepare input
            input_data = np.array([[age, diastolicBP, BS, bodyTemp, heartRate]])
            input_scaled = scaler_maternal.transform(input_data)
            
            # Predict
            predicted_risk = maternal_model.predict(input_scaled)
            
            st.divider()
            st.subheader("Prediction Result:")
            
            if predicted_risk[0] == 0:
                st.success("✅ Low Risk - Continue standard care.")
            elif predicted_risk[0] == 1:
                st.warning("⚠️ Medium Risk - Monitor closely.")
            else:
                st.error("🚨 High Risk - Immediate medical attention recommended.")
                
        except Exception as e:
            st.error(f"An error occurred during prediction: {e}")

# === FETAL HEALTH PREDICTION ===
if selected == 'Fetal Health':
    st.title('Fetal Health Screening (CTG Analysis)')
    st.markdown("Enter Cardiotocogram (CTG) derived data to classify fetal health status.")
    
    # TABS LAYOUT: This looks much cleaner than a long list
    tab1, tab2, tab3 = st.tabs(["📊 CTG Fundamentals", "📉 Variability Metrics", "📈 Histogram Data"])

    with tab1:
        col1, col2 = st.columns(2)
        BaselineValue = col1.number_input('Baseline FHR', value=120.0)
        Accelerations = col2.number_input('Accelerations', value=0.0)
        fetal_movement = col1.number_input('Fetal Movement', value=0.0)
        uterine_contractions = col2.number_input('Uterine Contractions', value=0.0)
        light_decelerations = col1.number_input('Light Decelerations', value=0.0)
        severe_decelerations = col2.number_input('Severe Decelerations', value=0.0)
        prolongued_decelerations = col1.number_input('Prolongued Decelerations', value=0.0)

    with tab2:
        col1, col2 = st.columns(2)
        abnormal_short_term_variability = col1.number_input('Abnormal Short Term Var.', value=0.0)
        mean_value_of_short_term_variability = col2.number_input('Mean Value Short Term Var.', value=0.0)
        percentage_of_time_with_abnormal_long_term_variability = col1.number_input('% Time Abn. Long Term Var.', value=0.0)
        mean_value_of_long_term_variability = col2.number_input('Mean Value Long Term Var.', value=0.0)

    with tab3:
        col1, col2, col3 = st.columns(3)
        histogram_width = col1.number_input('Hist Width', value=0.0)
        histogram_min = col2.number_input('Hist Min', value=0.0)
        histogram_max = col3.number_input('Hist Max', value=0.0)
        
        histogram_number_of_peaks = col1.number_input('Hist Peaks', value=0.0)
        histogram_number_of_zeroes = col2.number_input('Hist Zeroes', value=0.0)
        histogram_mode = col3.number_input('Hist Mode', value=0.0)
        
        histogram_mean = col1.number_input('Hist Mean', value=0.0)
        histogram_median = col2.number_input('Hist Median', value=0.0)
        histogram_variance = col3.number_input('Hist Variance', value=0.0)
        histogram_tendency = col1.number_input('Hist Tendency', value=0.0)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button('Analyze Fetal Health', type="primary"):
        try:
            features = [[BaselineValue, Accelerations, fetal_movement, uterine_contractions, 
                         light_decelerations, severe_decelerations, prolongued_decelerations, 
                         abnormal_short_term_variability, mean_value_of_short_term_variability,
                         percentage_of_time_with_abnormal_long_term_variability, 
                         mean_value_of_long_term_variability, histogram_width, histogram_min, 
                         histogram_max, histogram_number_of_peaks, histogram_number_of_zeroes, 
                         histogram_mode, histogram_mean, histogram_median, histogram_variance, 
                         histogram_tendency]]
            
            predicted_class = fetal_model.predict(features)
            
            st.divider()
            if predicted_class[0] == 1:
                st.success("🟢 Result: Normal")
            elif predicted_class[0] == 2:
                st.warning("🟠 Result: Suspect")
            else:
                st.error("🔴 Result: Pathological")
        except Exception as e:
            st.error(f"Prediction Error: {e}")

# === DASHBOARD ===
if selected == 'Live Dashboard':
    st.title("Maternal Health Analytics Dashboard")
    st.markdown("Real-time insights into institutional deliveries and healthcare performance.")
    
    # YOUR API KEY
    api_key = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
    api_endpoint = f"https://api.data.gov.in/resource/6d6a373a-4529-43e0-9cff-f39aa8aa5957?api-key={api_key}&format=csv"

    try:
        dashboard = MaternalHealthDashboard(api_endpoint)
        
        # FIX: Stack charts vertically instead of squeezing them into columns
        st.divider()
        st.subheader("1. Regional Performance (Bubble Chart)")
        st.caption("Comparison of performance vs. assessed needs across different regions.")
        dashboard.create_bubble_chart()
        
        st.divider()
        st.subheader("2. Delivery Statistics (Pie Chart)")
        st.caption("Distribution of institutional vs. home deliveries.")
        dashboard.create_pie_chart()
            
        with st.expander("View Raw Data Source"):
            st.code(dashboard.get_bubble_chart_data())
            
    except Exception as e:
        st.error("Could not load dashboard data. The API key may be invalid or the service is down.")