import json
import os
import time
import base64
import pandas as pd
import requests

api_key ='Your API key'

with open('visual_qa_pairs.json', 'r') as file:
    visual_qa_pairs = json.load(file)

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

def get_gpt_4o_reply(image_url, final_question):
    base64_image = encode_image(image_url)
    payload = {
      "model": "gpt-4o",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": final_question
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/png;base64,{base64_image}",
              },
            }
          ]
        }
      ],
    "max_tokens": 1000,
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json())
    gpt_4o_reply = response.json()['choices'][0]['message']
    
    return gpt_4o_reply


root_image_path = 'charts/'

prompt_pngs = []
for each_visual_qa_pair in visual_qa_pairs:
    image_index = each_visual_qa_pair['image_index']
    image_name = each_visual_qa_pair['image_url']
    image_type = each_visual_qa_pair['image_type']
    task_category = each_visual_qa_pair['type']
    question_level = each_visual_qa_pair['question_level']
    image_index_dict = {}
    image_index_dict['image_url'] = root_image_path + str(image_index) + '.png'
    image_index_dict['task_category'] = task_category
    image_index_dict['QA_pairs'] = each_visual_qa_pair['QA_pairs']
    image_index_dict['id'] = image_index
    image_index_dict['image_type'] = image_type
    image_index_dict['question_level'] = question_level
    prompt_pngs.append(image_index_dict)


total_results = []
count = 0
is_test = True
for _, each_question in enumerate(prompt_pngs[count:]):
    begin = time.time()
    image_url = each_question['image_url']
    task_category = each_question['task_category']
    table_url = each_question['table_url']
    metadata = pd.read_csv(each_question['table_url'])
    qa_list = each_question['QA_pairs']
    image_type = each_question['image_type']
    image_id = each_question['id']
    each_answer_dict = {}
    each_answer_dict['image_url'] = image_url
    each_answer_dict['task_category'] = task_category
    each_answer_dict['image_type'] = image_type

    fill_the_blank_list = qa_list[0]['fill_the_blank']
    fill_the_blank_question = fill_the_blank_list[0]
    fill_the_blank_annotation = fill_the_blank_list[1]
    multiplt_choice_list = qa_list[1]['Multiple_choice']
    multiple_choice_question = multiplt_choice_list[0]
    multiple_choice_annotation = multiplt_choice_list[1]
    Judgement_question_list = qa_list[2]['Judgement_question']
    Judgement_question_question = Judgement_question_list[0]
    Judgement_question_annotation = Judgement_question_list[1]
    Corrective_question_list = qa_list[3]['Corrective_question']
    Corrective_question_question = Corrective_question_list[0]
    Corrective_question_annotation = Corrective_question_list[1]


 

    each_answer_dict['fill_the_blank_annotation'] = fill_the_blank_annotation
    each_answer_dict['fill_the_blank_question'] = fill_the_blank_question
    each_answer_dict['fill_the_blank_gpt-4o'] = get_gpt_4o_reply(image_url, fill_the_blank_question)


    each_answer_dict['multiple_choice_annotation'] = multiple_choice_annotation
    each_answer_dict['multiple_choice_question'] = multiple_choice_question
    each_answer_dict['multiple_choice_gpt-4o'] = get_gpt_4o_reply(image_url, multiple_choice_question)

    each_answer_dict['Judgement_question_annotation'] = Judgement_question_annotation
    each_answer_dict['Judgement_question_question'] = Judgement_question_question
    each_answer_dict['Judgement_question_gpt-4o'] = get_gpt_4o_reply(image_url, Judgement_question_question)


    each_answer_dict['Corrective_question_annotation'] = Corrective_question_annotation
    each_answer_dict['Corrective_question_question'] = Corrective_question_question
    each_answer_dict['Corrective_question_gpt-4o'] = get_gpt_4o_reply(image_url, Corrective_question_question)


    total_results.append(each_answer_dict)
    # with open(f'results/other_prompt/{image_id}_{task_category}_{count}.json','w') as file:
    #     json.dump(each_answer_dict, file, indent=4)
    # with open(f'results/other_prompt/total_results.json', 'w') as file:
    #     json.dump(total_results, file, indent=4)
    end = time.time()
    process = round(end - begin ,2)
    print(f"={image_id}_{task_category}，takes{process}s.{count+1}/{len(prompt_pngs)} has been finished")
    count += 1
