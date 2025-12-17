import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

st.sidebar.header("🔐 Test Gemini API")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

if st.sidebar.button("Test Gemini"):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        res = model.generate_content("Chỉ trả lời: OK")
        st.sidebar.success("✅ GEMINI API HOẠT ĐỘNG")
        st.sidebar.code(res.text)
    except Exception as e:
        st.sidebar.error("❌ LỖI GEMINI API")
        st.sidebar.code(str(e))
