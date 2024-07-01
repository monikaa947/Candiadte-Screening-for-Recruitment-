import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

backendDomain = os.getenv("backendDomain")

st.set_page_config(
    page_title="TalentGENius - Mastek GenAI HR",
    page_icon="TalentGeniusHeadIcon.png",
)

# Function to make API call for evaluation
def evaluate_candidate():
    api_url = f"{backendDomain}/getQuestion"
    
    print("st.session_state.messages: ",st.session_state.messages)

    body = {
        "isFirstQuestion": False,
        "chatHistory": st.session_state.messages,
        "candidateName": st.session_state.candidate_name,
        "candidateResponse": "",
        "jobTitle": st.session_state.job_title,
        "jobId": st.session_state.job_requisition_id,
        "candidateId": st.session_state.candidate_id,
        "evaluateCandidate": True
    }

    # Make a POST request to the API with the user's message
    response = requests.post(api_url, json=body)
    print("response of eval_call: ", response.json())


st.image('TalentGeniusLogo.png', width=300)
st.markdown("___")
# st.subheader("TalentGENius - Mastek GenAI HR")
st.success(f"Thank you so much {st.session_state.candidate_name} for participating in this screening process! We truly appreciate the time and effort you've dedicated to this process. Your insights and perspectives were invaluable, and we're grateful for the opportunity to get to know you better.")

st.success("Feel free to exit the room at your convenience, and we'll be in touch soon with any further steps. Once again, thank you for your time, and we wish you a wonderful day ahead!")

# trigger candidate evaluation process in the backend
evaluate_candidate()