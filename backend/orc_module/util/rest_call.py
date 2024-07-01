import urllib3
import regex as re
from dotenv import load_dotenv
import os
import json

load_dotenv()

domain = os.getenv("fusionDomain")
username = os.getenv("uname")
password = os.getenv("pass")

client = urllib3.PoolManager(headers=urllib3.make_headers(basic_auth=f'{username}:{password}'))

def get_job_description(requisition_id):
    req_id = int(requisition_id)
    response = client.request("GET", 
                   url=f"{domain}/hcmRestApi/resources/latest/recruitingJobRequisitions/{req_id}",
                   fields={"onlyData": "true"}
                   )
    print("Fusion API response: \n", response.data)
    print("get_job_description status: ", response.status)
    requisition =  response.json()
    print(requisition.keys())

    job_title = requisition['Title']
    job_description = requisition["ExternalRespStr"]
    job_qualification = requisition["InternalQualStr"]
    job_req_id = requisition['RequisitionId']
    job_req_no = requisition['RequisitionNumber']

    job_description = re.sub("[\r\n]+","",job_description)
    job_qualification = re.sub("[\r\n]+","",job_qualification)

    job_data = {
        'job_description' : job_qualification,
        'job_qualification': job_qualification,
        'job_title': job_title,
        'job_req_id': job_req_id
    }

    return job_data


def questions(requisition_id):
    questions = []
    jd_question_data = {
        '7003': '300000295560394', # HR Business Partner_AI-BOT
        '7004': '300000295560748', # Sales Associate_AI-BOT
        '7005': '300000295561129', # Business Analysis Associate_AI-BOT
        '7006': '300000295563007', # Solution Architect_AI-BOT
        '7007': '300000295558492', # Payroll Specialist_AI-BOT
    }

    folder_id = jd_question_data.get(requisition_id)

    print(f"ReqID: {requisition_id} --> QueFolderID: {folder_id}")


    response = client.request("GET", 
                   url=f"{domain}/hcmRestApi/resources/latest/questions",
                   fields={"onlyData": "true","q":f'FolderId={folder_id}','expand':'answers'},
                   )
    
    data =  response.json()

    for ques in data["items"]:
        # print(ques)
        question = {
                "question": {
                    "QuestionId": ques['QuestionId'],
                    # "QuestionCode": ques['QuestionCode'],
                    "QuestionText": ques['QuestionText'],
                    "MaximumPossibleScore": ques['MaximumPossibleScore']
                    },
                "answers": [
                    {
                        "QuestionAnswerId": answer['QuestionAnswerId'],
                        # "AnswerCode": answer['AnswerCode'],
                        "Score": answer['Score'],
                        "LongAnswerText": answer['LongAnswerText'],
                    }
                    for answer in ques['answers']
                ]
        }
        questions.append(question)
        
    return questions

def get_candidate_information(candidate_id):
    cand_id = str(candidate_id)
    candidate = {}
    response = client.request("GET", 
                url=f"{domain}/hcmRestApi/resources/latest/recruitingCandidates",
                fields={"onlyData": "true",
                        "finder":f'PrimaryKey;CandidateNumber={cand_id}',
                        "expand": "education,experience,licensesAndCertificates,skills"
                        },
                )
    data =  response.json()
    for ques in data["items"]:
        candidate = {
            "candidate_info":{
                "CandidateNumber": ques["CandidateNumber"],
                "LastName": ques["LastName"],
                "FirstName": ques["FirstName"],
                "FullName": ques["FullName"],
                "Email": ques["Email"],
                "PersonId": ques["PersonId"],

            }
        }
        if len(ques["education"]) > 0 :
            candidate.candidate_education = ques["education"]

        if len(ques["experience"]) > 0 :
            candidate.candidate_experience = ques["experience"]  
    
        if len(ques["licensesAndCertificates"]) > 0 :
            candidate.candidate_certificates = ques["licensesAndCertificates"]  
        
        if len(ques["skills"]) > 0 :
            candidate.candidate_skills = ques["skills"]

    return candidate


# def put_final_score(candidate_id, score):
#     cand_id = str(candidate_id)

#     response = client.request("GET", url=f"{domain}/hcmRestApi/resources/11.13.18.05/questions?limit=501&q=SubscriberName='Recruiting'")
#     data =  response.json()

#     print("Question data: ", data)


def get_candidate_extra_info(candidate_id):
    candidate_number = str(candidate_id)
    response = client.request("GET",
                              url=f"{domain}/hcmRestApi/resources/11.13.18.05/recruitingCandidateExtraInformation",
                              fields={"q": f"CandidateNumber='{candidate_number}'"}
                             )
    candidate_extra_info = response.json()
    return candidate_extra_info


def post_candidate_interview_score(candidate_id, score):
    response = get_candidate_extra_info(candidate_id)

    if response["items"] and len(response["items"]) > 0:
        extra_info = response["items"][0]

        person_id = extra_info["PersonId"] 
        category_code = extra_info["CategoryCode"]

        post_score_uri = ""
        for link in extra_info["links"]:
            if link["name"] == "jPersonExtraInformation":
                post_score_uri = link["href"]

       
        payload = json.dumps({
            "CategoryCode": category_code,
            "PersonId": person_id,
            "PersonExtraInformationContextScore_5FCandidateprivateVO": [
                {
                    "pleaseScoreTheCandidate": score,
                    "EffectiveStartDate": "2018-01-01"
                }
            ]
        })
        headers = urllib3.make_headers(basic_auth=f'{username}:{password}')
        headers["Upsert-Mode"] = "true"
        headers['REST-FRAMEWORK-VERSION'] = '3'
        headers['Content-Type'] = 'application/json'

        post_response = client.request("POST",
                                url=f"{post_score_uri}",
                                body=payload,
                                headers=headers
                            )
        
        print("SCORE POSTING:\n ", post_response)
        return post_response.status
    else:
        return None