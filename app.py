import google.generativeai as genai

st.sidebar.header("🔐 Test Gemini API")

if st.sidebar.button("Test Gemini API"):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Chỉ trả lời: OK")
        st.sidebar.success("✅ GEMINI API HOẠT ĐỘNG")
        st.sidebar.code(response.text)
    except Exception as e:
        st.sidebar.error("❌ LỖI GEMINI API")
        st.sidebar.code(str(e))
