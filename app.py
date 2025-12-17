import streamlit as st
import os
from openai import OpenAI

st.title("TEST STREAMLIT + OPENAI")

api_key = os.getenv("OPENAI_API_KEY")
st.write("API key tồn tại:", bool(api_key))

if not api_key:
    st.stop()

client = OpenAI(api_key=api_key)

if st.button("Test GPT"):
    res = client.responses.create(
        model="gpt-4o-mini",
        input="Nói OK"
    )
    st.write(res.output_text)
