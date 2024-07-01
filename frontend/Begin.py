import os
import time
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()
backendDomain = os.getenv("backendDomain")

# candidate_id = "85047"
# requisition_id = "7002"

# candidate_id = "1208"
# requisition_id = "7006"


def get_interview_details(job_requisition_id, candidate_id):

    api_url = f"{backendDomain}/startScreening"
    body = {
        "requisition_id": job_requisition_id,
        "candidate_id": candidate_id
    }
    # Make a POST request to the API with the user's message
    response = requests.post(api_url, json=body)
    # question = response.json()['response']
    print("called /startScreening: ", response.json())

    interview_data = response.json()
    return interview_data



st.set_page_config(
    page_title="TalentGENius - Mastek GenAI HR",
    page_icon="TalentGeniusHeadIcon.png",
)

job_requisition_id = st.query_params.get_all('j_id')
candidate_id = st.query_params.get_all('c_id')

if job_requisition_id or candidate_id:

    st.session_state.job_requisition_id = job_requisition_id[0]
    st.session_state.candidate_id = candidate_id[0]

    interview_data = get_interview_details(job_requisition_id[0], candidate_id[0])
    first_page_container = st.empty()
    first_page_body = first_page_container.container()


    with first_page_body:

        st.image('TalentGeniusLogo.png', width=300)
        # st.subheader("TalentGENius - Mastek GenAI HR")

        # st.session_state.candidate_name = "Prasanth"
        st.session_state.candidate_name = interview_data['candidate_name']
        st.session_state.job_title = interview_data['job_title']

        # st.markdown("___")
        st.markdown(f"##### Welcome {st.session_state.candidate_name}, please verify the below information and click 'Begin' to start the evaluation.")

        st.write("")
        st.markdown(f"> **Job Title:** {interview_data['job_title']} ({interview_data['requisition_id']})")
        st.markdown(f"> **Candidate Name:** {interview_data['candidate_full_name']}   |   **Candidate ID:** {interview_data['candidate_id']}") # keep full name here

        st.write("")
        st.write("")

        if st.button('Begin'):
            st.session_state.answerCount = 0
            first_page_container.empty()
            st.switch_page('./pages/1evaluation.py')
else:
    st.markdown("To get started, in the app URL, please add the query as follows: /?j_id=<jobID>&c_id=<candidateID>")