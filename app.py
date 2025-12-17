import os
import streamlit as st
import google.generativeai as genai

# 🔴 QUAN TRỌNG: ép dùng API key, không dùng ADC
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")
)

st.sidebar.header("🔐 Test Gemini API")

if st.sidebar.button("Test Gemini"):
    model = genai.GenerativeModel("gemini-2.5-flash")
    res = model.generate_content("Chỉ trả lời: OK")
    st.sidebar.success(res.text)
