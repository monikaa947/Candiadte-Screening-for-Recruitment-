import os
import json
import urllib3
import logging
from typing import Union, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException, status
from pydantic import BaseModel
from dotenv import load_dotenv

from orc_module.data_loader import load_interview_data, clean_and_process_string
from orc_module.screening_prompt import createFinalPrompt
from orc_module.candidate_evaluation import doCandidateEvaluation


load_dotenv()
llmDomain = os.getenv("llmDomain")
# llmDomain = "http://127.0.0.1:8000"

app = FastAPI()

logger = logging.getLogger("HR_Screening_App")

# Class for the input data
class StartScreening(BaseModel):
    requisition_id: str
    candidate_id: str

# Class for input data for general prompt to model
class EvaluationInput(BaseModel):
    question: str
    candidateResponse: str

# Class for input data for general prompt to model
class GetQuestion(BaseModel):
    # prevAnswer: str
    isFirstQuestion: bool
    evaluateCandidate: bool
    chatHistory: list[dict]
    candidateName: Optional[str]
    candidateResponse: str
    jobTitle: Optional[str]
    jobId: str
    candidateId: str

# Class for the output data
class OutputData(BaseModel):
    response: str


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


@app.get("/")
async def start():
    return "Please go to /docs to try the API endpoints"



"""
Initiates the interview screening
"""
@app.post("/startScreening", response_model=OutputData)
async def start_screening(request: Request, input_data: StartScreening, q: Union[str, None] = None) -> JSONResponse:
    """
    Start the screening process based on the requisition_id and candidate_id.
    """
    try:
        requisition_id = input_data.requisition_id
        candidate_id = input_data.candidate_id

        if requisition_id and candidate_id:
            interview_data = load_interview_data(requisition_id, candidate_id)
            print("interview_data", interview_data)
            return JSONResponse(content=interview_data)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="requisition_id and candidate_id cannot be empty")
    except Exception as error:
        # Log the exception
        logger.error(f"Error in start_screening: {error}")
        # Return a 500 Internal Server Error response
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


"""
Get the question to be asked to the candidate
"""
@app.post("/getQuestion/", response_model=OutputData)
async def get_question(request: Request, input_data: GetQuestion, q: bool = False):
    response = None
    questionGenerationPrompt = None
    # newGeneratedQuestion = None

    try:
        isFirst_question = input_data.isFirstQuestion
        evaluate_candidate = input_data.evaluateCandidate
        chat_history = input_data.chatHistory
        candidate_id = input_data.candidateId
        candidate_name = input_data.candidateName
        candidate_response = input_data.candidateResponse
        job_title = input_data.jobTitle
        job_requisition_id = input_data.jobId


        if evaluate_candidate:
            print("got trigger for candidate eval, goto evaluation flow")
            doCandidateEvaluation(chat_history, job_requisition_id, candidate_id)

        else:
            ask_llm_prompt = createFinalPrompt(
                candidate_name=candidate_name,
                job_role=job_title,
                job_requisition_id=job_requisition_id,
                candidate_response=candidate_response,
                chat_history=chat_history
                )

            questionGenerationPrompt = ask_llm_prompt

        print("\n\nquestionGenerationPrompt: ", questionGenerationPrompt)

        if questionGenerationPrompt:
            # Calling the LLM with newly generated prompt
            response = generate_with_LLM(questionGenerationPrompt)
            if response.status == 200:
                print("200 ma aivu")
                
                data = response.json()['response']
                print("\n\nLLM response:\n", data)

                if any(item.lower() in data.lower() for item in ['NO FURTHER QUESTIONS', 'Thank you for participating']):
                    newGeneratedQuestion = 'None'
                else:
                    newGeneratedQuestion = clean_and_process_string(data)


                print(">>>> here newGeneratedQuestion: ", newGeneratedQuestion)
                return OutputData(response=newGeneratedQuestion)
            else:
                print("error ma gayu")
                raise HTTPException(status_code=response.status, detail="API request failed")
        else:
            return OutputData(response="Candidate screening has been completed!")
    except Exception as error:
        print(error)
        raise HTTPException(status_code=500, detail=f"Internal Server Error:\n{error}")


