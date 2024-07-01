import re
from orc_module.data_loader import load_JD_params


defualt_job_role = "Solution Architect"


def createFinalPrompt(candidate_name, job_role, job_requisition_id, candidate_response, chat_history):
   
   print("Here's what candidate says: ", candidate_response)
   
   # quick hack to avoid job titles like 'Demo Requisition'
   if ('Demo' in job_role) or ('TEST' in job_role):
      job_role = defualt_job_role
   elif '_AI-BOT' in job_role:
      # Use regex to remove " - AI-Bot"
      job_role = re.sub(r'_AI-BOT$', '', job_role)

   print("formatted job_role: ", job_role)
   
   # load the evaluation questions from fusion
   eval_params = load_JD_params(job_requisition_id)
   
# Simulate a screening interview scenario for the position of {job_role} with a candidate named "{candidate_name}". Follow these steps:

   SCREENING_INSTRUCTION_PROMPT = f"""
Your name is TalentGENius and you are to act as an interviewer who is conducting a screening interview for the position of {job_role} with a candidate named {candidate_name}. Follow these steps:

 
1. Start with a friendly greeting and welcome message. Ask "{candidate_name}" to introduce himself briefly.
 
2. After "{candidate_name}" introduces himself.
 
3. If "{candidate_name}" shares any initial thoughts or questions, acknowledge them and express appreciation. If not, proceed with the first question from EVALUATION QUESTIONS: {eval_params} only and do not disclose OPTIONS to the candidate.
 
4. After {candidate_name} provides answer for asked question, move to next question from EVALUATION QUESTIONS.
 
5. Repeat Step 4, Until the last question from EVALUATION QUESTIONS.
 
6. After {candidate_name} responds to the last question from EVALUATION QUESTIONS, conclude the interview by saying 'NO FURTHER QUESTIONS'.
   
Remember to maintain a natural and polite conversational tone throughout the interview. Address any final thoughts or questions from {candidate_name} in the closing statement.


Ensure that the your questions strictly avoids any mention, hint, or reference to the specific OPTIONS of EVALUATION QUESTIONS.
Do not ask more than 5 question.
Do not ask a question more than twice if candidate doesn't provide response to any particular question.
"""

   formatted_chat_history = format_chat_history_v2(chat_history)

   formatted_prompt = format_prompt(SCREENING_INSTRUCTION_PROMPT, candidate_response, formatted_chat_history)
   
   print("Final Formatted prompt: ", formatted_prompt)
   
   return formatted_prompt
   



def format_prompt(static_prompt, message, history):
   prompt = "<s>"
   # Add the static prompt as the first message
   prompt += f"[INST] {static_prompt} [/INST]"
   for user_prompt, bot_response in history:
      prompt += f"[INST] {user_prompt} [/INST]"
      prompt += f" {bot_response}</s> "
   prompt += f"[INST] {message} [/INST]"
      
   return prompt


def createInitQuestionPrompt(candidate_name, job_role):

   # quick hack to avoid job titles like 'Demo Requisition'
   if ('Demo' in job_role) or ('TEST' in job_role):
      job_role = defualt_job_role
   elif '_AI-BOT' in job_role:
      # Use regex to remove " - AI-Bot"
      job_role = re.sub(r'_AI-BOT$', '', job_role)

      print("formatted job_role: ", job_role)


   initQuestionPromp = f"""Generate a warm, personalized & breif opening question for candidate screening, inviting {candidate_name} to provide a brief overview of their background and experience for the role of {job_role}.
   Output:"""
   print("\nFormatted prompt: ", initQuestionPromp)

   # initQuestionPromp = json.dumps(initQuestionPromp)
   # print("String prompt: ", initQuestionPromp)
   return initQuestionPromp


def createClassificationPrompt(chat_history, job_requisition_id):

   eval_params = load_JD_params(job_requisition_id)

   convo_history = format_chat_history(chat_history)

   classificationPrompt = f"""<s>[INST]Your task is to refer to the given the CONVERSATION HISTORY between an Interviewer and a Candidate, and classify the given EVALUATION QUESTIONS as [Addressed] or [Unaddressed] by following the instruction for the classification.[/INST]

[INST]Classification Instructions:
1. Examine the CONVERSATION HISTORY to identify [Unaddressed] EVALUATION QUESTIONS asked by the interviewer and the responses provided by the candidate. The response can be either correct or incorrect for an EVALUATION QUESTION, and those responses should mark the EVALUATION QUESTION as [Addressed].
2. If the candidate has provided a response to a EVALUATION QUESTION, then mark it as [Addressed].
3. If an option(s) to an EVLUATION QUESTION is answered, then do not repeat those EVLUATION QUESTION. If the candidate has answered some options to an EVLUATION QUESTION in the CONVERSATION HISTORY, then mark that EVALUATION QUESTION as [Addressed].
4. Mark the EVALUATION QUESTION as [Unaddressed] only if it is not yet asked to the candidate in the CONVERSATION HISTORY.
5. Do not mark options or questions as [Unaddressed] if it is not part of the given EVALUATION QUESTIONS or it is not there in te CONVERSATION HISTORY.
6. Do not make up new questions or data of your own. Only refer to what is given in the context.[/INST]</s>
6. If the candidate's response says something on the line 'I am done' then mark everything as [Addressed].[/INST]</s>

CONVERSATION HISTORY:
{convo_history}


EVALUATION QUESTIONS:
{eval_params}

[INST]Strictly Adhere to the below given output format.[/INST]

OUTPUT FORMAT:
[Addressed]
- <name of the addressed parameter here>
- <name of the addressed Parameter here>
- <name of the addressed parameter here>
 
[Unaddressed]
- <name of the unaddressed parameter here>
- <name of the unaddressed parameter here>

Output:"""

   return classificationPrompt


def createQuestionGenerationPrompt(chat_history, classified_eval_params):
   # questions_already_asked = ""

   convo_history = format_chat_history(chat_history)

   # for msg in chat_history:
   #    if msg['role'] == 'assistant':
   #       questions_already_asked += f"Q: {msg['content']}\n"

   # print("questions_already_asked:\n",questions_already_asked)


   questionGeneratrionPrompt = f"""<s>[INST]Your task is to generate the question to be asked in the screening interview based on the Unaddressed parameters listed under EVALUATION PARAMETERS.[/INST]

[INST]Some instructions for question generation:
1. If there are multiple EVALUATION PARAMETERS, then generate a single concise question on any one [Unaddressed] parameter.
2. Do not generate any question on EVALUATION PARAMETERS which are already [Addressed] in CONVERSATION HISTORY.
3. Refer to CONVERSATION HISTORY below and do not generate repeated or similar question.
4. Ensure that the generated question strictly avoids any mention, hint, or reference to the specific EVALUATION PARAMETERS or the CONVERSATION HISTORY.
5. The output should not contain things like 'based on the given context...' or any guidelines of question generation.
6. If all EVALUATION PARAMETERS have been [Addressed], then simply state NO FURTHER QUESTIONS as the output.
7. If there are no [Unaddressed] EVALUATION PARAMETERS, then simply state NO FURTHER QUESTIONS as the output.[/INST]</s>

CONVERSATION HISTORY:
{convo_history}

EVALUATION PARAMETERS:
{classified_eval_params}


Output format: {{"question": "generated question over here"}}

Output:"""

   return questionGeneratrionPrompt


def createEvaluationPrompt(chat_history, job_requisition_id):
   
   eval_params = load_JD_params(job_requisition_id, True)

   convo_history = format_chat_history(chat_history)


#    evalPrompt_2 = f"""<s>[INST]Evaluate the candidate for the position, rating their suitability by calculating a final score using the given EVALUATION PARAMETERS, an example to calculate final score and the interivew conversation history.  EVALUATION PARAMETERS are dynamic and can vary. Ensure the output is clear and organized.
   
# SCORE CALCULATION INSTRUCTION:
# 1. First, get the calculated score for each parameter by identifying which options have been addressed by candidate from conversation history.
# 2. Do no try to assume stuff or make up stuff for evaluation, only consider whatever is there in the CONVERSATION HISTORY.
# 3. To calculate the score for each parameter, multiply each parameter's weight by its corresponding selected option's weight.
# 4. To calculate the final score for the candidate, just sum the calculated score for all parameters.


# ### START CONVERSATION HISTORY
# {convo_history}
# END CONVERSATION HISTORY ###

# >>> START EVALUATION PARAMETERS
# {eval_params}
# END EVALUATION PARAMETERS <<<
# [/INST]</s>

# [INST]Strictly adhere to the below given output format.
# {{"final_score": "<number>%", "paramter name here": "<number of parameter score>%", "parameter name here": "<number of parameter score>%", "parameter name here": "<number of parameter score>%"}}

# The parameter_1, parameter_2, parameter_3 shown in format are dynamic in nature, so use the proper paramter name as key value for the output JSON.

# Provide your final score:[/INST]"""


   evalPrompt_2 = f"""<s>[INST]Evaluate the candidate for the position, rating their suitability by calculating a final score using the given EVALUATION PARAMETERS and the interview CONVERSATION HISTORY. EVALUATION PARAMETERS are dynamic and can vary. Ensure the output is clear and organized.[/INST]
 
[INST]
SCORE CALCULATION INSTRUCTION:
1. First, get the calculated score for each parameter by identifying which options have been addressed by the candidate from the conversation history.
2. Do not try to assume or make up information for evaluation; only consider whatever is present in the CONVERSATION HISTORY.
3. To calculate the score for each parameter, multiply each parameter's weight by its corresponding selected option's weight.
4. To calculate the final score for the candidate, sum the calculated score for all parameters. [/INST]</s>

[INST] 
CONVERSATION HISTORY:
{convo_history}
[/INST]

[INST]
EVALUATION PARAMETERS:
{eval_params}
[/INST]

 
[INST]Strictly adhere to the below-given output format.
{{"final_score": "<number>%", "parameter name 1": "<number of parameter 1 score>%", "parameter name 2": "<number of parameter 2 score>%", "parameter name 3": "<number of parameter 3 score>%"}}[/INST]

[INST]The parameter names shown in the format are dynamic in nature, so use the proper parameter name as a key value for the output JSON.
Provide your final score:[/INST]"""

   print("\nFormatted prompt: ", evalPrompt_2)
   return evalPrompt_2



def format_chat_history(chat_history):

   convo_history = ""
   for msg in chat_history:
      if msg['role'] == 'assistant':
         convo_history += f"> Interviewer: {msg['content']}\n"
      if msg['role'] == 'user':
         convo_history += f"> Candidate: {msg['content']}\n\n"

   print("Conversation History:\n",convo_history)

   return convo_history


def format_chat_history_v2(chat_history):
    convo_history = []

    for msg in chat_history:
        if msg['role'] == 'user' and msg['content'] != '':
            user_message = f"{msg['content']}"
            # Append a new tuple for each user message
            convo_history.append((user_message, ""))
        elif msg['role'] == 'assistant' and msg['content'] != '':
            assistant_message = f"{msg['content']}"
            # If there's a previous user message, update the assistant message
            if convo_history:
                last_tuple = convo_history[-1]
                convo_history[-1] = (last_tuple[0], assistant_message)
            else:
                # If no previous user message, add an empty user message tuple
                convo_history.append(("", assistant_message))

    print("New conversation History:\n", convo_history)

    return convo_history