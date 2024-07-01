import random
import time
import requests
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

backendDomain = os.getenv("backendDomain")
maxQuestionCount = os.getenv("max_question_to_ask")


endConversationMessage = f"Thank you so much {st.session_state.candidate_name} for participating in this screening process. We will now be concluding this session."
limitReachedMessage = f"Thank you {st.session_state.candidate_name} for your responses. I seem to be having some difficulty with the evaluation. We will reach out to you with the next steps."


# Funtion to stream the AI's response
def get_AI_response(aiResponse):
    for word in aiResponse.split():
        yield word + " "
        time.sleep(0.05)


# Function to make API call
def fetch_question_to_ask(firstQuestion = False, candidateResponse="", evaluateCandidate = False):
    # Replace this URL with your actual API endpoint
    api_url = f"{backendDomain}/getQuestion"
    print(f"Calling Backend Server on {api_url}")
    
    print("st.session_state.messages: ",st.session_state.messages)

    body = {
        "isFirstQuestion": firstQuestion,
        "chatHistory": st.session_state.messages,
        "candidateName": st.session_state.candidate_name,
        "candidateResponse": candidateResponse,
        "jobTitle": st.session_state.job_title,
        "jobId": st.session_state.job_requisition_id,
        "candidateId": st.session_state.candidate_id,
        "evaluateCandidate": evaluateCandidate
    }

    print("Request body\n:", body)

    # Make a POST request to the API with the user's message
    response = requests.post(api_url, json=body)
    print("called /getQuestion: ", response.json())
    question = response.json()['response']
    

    st.session_state.questionToBeAsked = question
    # st.session_state.questionCounter += 1

    # returning but not catching it, using session_state to access question
    return question



st.set_page_config(
    page_title="TalentGENius - Mastek GenAI HR",
    page_icon="TalentGeniusHeadIcon.png",
)

st.image('TalentGeniusLogo.png', width=300)
st.markdown("___")
# st.subheader("TalentGENius - Mastek GenAI HR")

# Initialize chat history, meaning conversation is not started yet and first question needs to be asked by Assistant
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        role = "TalentGENius" if message["role"] == 'assistant' else "You"
        st.markdown(f"**{role}**")
        st.markdown(message["content"])


# Update question to be asked to the candidate
if "questionToBeAsked" not in st.session_state:
    with st.spinner(f'Please wait, while we connect you to our TalentGENius...'):
        fetch_question_to_ask(firstQuestion=True)
    # st.success("Let's get started!")
    with st.chat_message("assistant"):
        st.markdown("**TalentGENius**")
        response = st.write_stream(get_AI_response(st.session_state.questionToBeAsked))
    st.session_state.messages.append({"role": "assistant", "content": response})
else:
    print("else ma gayu, good!")

# with st.chat_message("assistant"):
#     response = st.write_stream(get_AI_response(st.session_state.questionToBeAsked))
#     # Add assistant question to chat history
#     st.session_state.messages.append({"role": "assistant", "content": response})


# Accept user input
if candidateSays := st.chat_input("Your response..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": candidateSays})
    # Display user message in chat
    with st.chat_message("user"):
        st.markdown("**You**")
        st.markdown(candidateSays)

    st.session_state.answerCount += 1

    if st.session_state.answerCount >= int(maxQuestionCount):
        print("\n\nmessage limit crossed - ending the session...\n")
        time.sleep(2.5)
        with st.chat_message("assistant"):
            response = st.write_stream(get_AI_response(limitReachedMessage))
        st.session_state.messages.append({"role": "assistant", "content": response})

        time.sleep(2.5)
        # move to end flow
        st.switch_page('./pages/2thankyou.py')
    else:
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
    
            with st.spinner(f'Thank you {st.session_state.candidate_name}. Please sit tight while I evaluate your response...'):
                fetch_question_to_ask(candidateResponse=candidateSays)
                

            
            st.markdown("**TalentGENius**")
            if 'None' in st.session_state.questionToBeAsked:
                time.sleep(2.5)
                response = st.write_stream(get_AI_response(endConversationMessage))
                st.session_state.messages.append({"role": "assistant", "content": response})

                # move to end flow
                time.sleep(2.5)
                st.switch_page('./pages/2thankyou.py')
            else:
                msg_container = st.empty()
                # msg_body = msg_container.container()
                with msg_container:
                    response = st.write_stream(get_AI_response(st.session_state.questionToBeAsked))
                    st.session_state.messages.append({"role": "assistant", "content": response})