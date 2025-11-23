import streamlit as st
import requests
import os
API_URL = os.environ.get('RECOMMEND_API', 'http://localhost:8000')

st.title('SHL Assessment Recommender')
q = st.text_area('Paste job description or write your query here', height=200)
k = st.slider('Number of results', 1, 10, 6)

if st.button('Get Recommendations'):
    if not q.strip():
        st.warning('Enter a query or job description')
    else:
        with st.spinner('Querying recommender...'):
            r = requests.post(f"{API_URL}/recommend", json={"query": q, "max_results": k}, timeout=30)
            if r.status_code == 200:
                data = r.json()
                rows = []
                for rec in data['recommendations']:
                    rows.append((rec['assessment_name'], rec['assessment_url']))
                st.table(rows)
            else:
                st.error(f"API error: {r.status_code} - {r.text}")
