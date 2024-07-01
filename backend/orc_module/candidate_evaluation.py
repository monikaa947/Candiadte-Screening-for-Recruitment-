import os
import re
import json
import urllib3
from dotenv import load_dotenv

from orc_module.screening_prompt import createEvaluationPrompt
from orc_module.util.rest_call import post_candidate_interview_score

load_dotenv()
llmDomain = os.getenv("llmDomain")
# llmDomain = "http://127.0.0.1:8000"

def generate_with_LLM(prompt):
    # Define the API endpoint
    api_url = f"{llmDomain}/generation"
    print(f"Calling LLM Server on {api_url}")

    # Prepare the request body
    request_body = {
        "query": prompt
    }

    encoded_body = json.dumps(request_body).encode('utf-8')

    # Create a connection pool with urllib3
    http = urllib3.PoolManager()
    response = http.request('POST', api_url, body=encoded_body, headers={'Content-Type': 'application/json'})
    print("Here's what LLM generated\n: ", response.json())

    return response



def doCandidateEvaluation(chat_history, job_requisition_id, candidate_id):

    print(f"\n**********chat history - evaluate_candidate:*********\n {chat_history}")

    evaluationPrompt = createEvaluationPrompt(chat_history, job_requisition_id)
    response = generate_with_LLM(evaluationPrompt)

    if response.status == 200:
        print("200 ma aivu")
        
        evalResp = response.json()['response']
        print("\n\nLLM evaluation response:\n", evalResp)

        pattern = r'\{[^}]*\}'
        match = re.search(pattern, evalResp)

        if match:
            extracted_json = match.group(0)
            print("json_eval_str: ",extracted_json)

            extracted_eval = json.loads(extracted_json)
            print("\n\n******Evaluation Score******\n\n", extracted_eval)
            
            final_score = extracted_eval['final_score']
            
            print(f"\n\n************Screening Result*****************\n\n")
            print(f"Candidate ID: {candidate_id}")
            print(f"Evaluation Score: {final_score}")
            print(f"\n\n*********************************************\n\n")
            
            formatted_score = int(final_score[:-1])
            scorePostingStatus = post_candidate_interview_score(candidate_id=candidate_id, score=formatted_score)
            
            if scorePostingStatus == 200:
                print('Score is posted to your HCM.')
                print('Evaluation completed!')
            else:
                print("Something went wrong while posting score to Fusion")
        else:
            print("No JSON found in the input string.")

    else:
        print("There has been some error", response.status)