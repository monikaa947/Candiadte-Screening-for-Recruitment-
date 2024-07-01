
import re
import json

from orc_module.util import rest_call




def load_interview_data(requisition_id, candidate_id):
   #Passing static folder if. In future a method will be used to obtain folder ID from mapping.
   requisition = rest_call.get_job_description(requisition_id)
   # questions = rest_call.questions(requisition_id)
   
   candidate_info = rest_call.get_candidate_information(candidate_id)

   print(f"requisition data:\n{requisition}\n\n")
   # print(f"questions data:\n{questions}\n\n")
   print(f"candidate_info data:\n{candidate_info}\n\n")


   interview_data = {
      'requisition_id': requisition_id,
      'job_title': requisition['job_title'],
      'candidate_id': candidate_info['candidate_info']['CandidateNumber'],
      'candidate_name': candidate_info['candidate_info']['FirstName'],
      'candidate_full_name': candidate_info['candidate_info']['FullName'],
   }

   return interview_data



def clean_and_process_string(input_string: str) -> str:
    
   print("String to clean:", input_string)

   pattern = r'\{[^}]*\}'
   match = re.search(pattern, input_string)

   if match:
      extracted_json = match.group(0)
      print("json_question_str: ",extracted_json)

      extracted_question_str = json.loads(extracted_json)
      print("extracted_question_str: ", extracted_question_str)

      input_string = extracted_question_str['question']
   else:
      print("No JSON found in the input string.")

   # Remove leading and trailing whitespaces
   processed_string = input_string.strip()

   # Remove double and single inverted commas
   processed_string = processed_string.replace('"', '')

   # Remove newline characters
   processed_string = processed_string.replace('\n', '')

   # Remove angle brackets
   processed_string = processed_string.replace('<', '').replace('>', '')

   # Remove certain special characters
   special_chars = '#()'
   processed_string = ''.join(char for char in processed_string if char not in special_chars)

   # Remove extra whitespaces
   processed_string = ' '.join(processed_string.split())

   # Preserve the question mark at the end of the string
   # if processed_string.endswith('?'):
   #     processed_string = processed_string[:-1]  # Remove the trailing question mark for processing

   return processed_string


def format_evaluation_params(questions, includeWeights):
    param_string = ""
    rc = 0

    if includeWeights:
        for record in questions:
            rc += 1
            param_string += f"\n{rc}. {record['question']['QuestionText']} (Parameter weight: {record['question']['MaximumPossibleScore']}%)\n---OPTIONS---\n"
            for ans in record['answers']:
                param_string += f"- {ans['LongAnswerText']}: {ans['Score']}%\n"
                print(param_string)

    else:
        for record in questions:
            rc += 1
            param_string += f"\n{rc}. {record['question']['QuestionText']}\n---OPTIONS---\n"
            for ans in record['answers']:
                param_string += f"- {ans['LongAnswerText']}\n"
                print(param_string)

    return param_string


def load_JD_params(job_requisition_id, withWeights=False):
   questions = rest_call.questions(job_requisition_id)
   print(f"questions data:\n{questions}\n\n")

   # only taking 3 questions for screening round.
   if len(questions) > 3:
      questions = questions[:3]

   jd_params = format_evaluation_params(questions, withWeights)

   return jd_params

