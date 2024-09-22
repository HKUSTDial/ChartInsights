import os
import json
from openai import OpenAI
import random
import base64
import requests
import time

api_key = 'YOUR API KEY'

## read relavant qa_pairs and annotations
with open("toalt_test_qa_pairs.json", 'r') as file:
    test_qa_pairs = json.load(file)
with open("test_annotations.json", 'r') as file:
    test_annotations = json.load(file)

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
      "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    gpt_4o_reply = response.json()['choices'][0]['message']
    return  gpt_4o_reply

## main function
start_length = 0
total_questions = 0
annotation_id = 0

for _, each_annotation in enumerate(test_annotations[annotation_id:]):
    total_charts = []
    begin = time.time()
    image_index = each_annotation['image']
    image_url = 'charts' + image_index
    image_type = each_annotation['type']
    index = each_annotation['id']

    for i, each_qa_pair in enumerate(test_qa_pairs[start_length:]):
        each_chart = {}
        each_chart['image_url'] = image_url
        each_chart['image_type'] = image_type
        task_category = each_qa_pair['type']
        each_chart['task_category'] = task_category
        print(each_qa_pair['QA_pairs'][0]['fill_the_blank'])
        if index == each_qa_pair['image_index']:
            start_length += 1
            total_questions += 4
            print(f"{index}, {task_category}")
            for each_question_format in each_qa_pair['QA_pairs']:
                each_key = list(each_question_format.keys())[0]
                final_question = each_question_format[each_key][0]
                annotation = each_question_format[each_key][1]
                gpt_4v_reply = get_gpt_4o_reply(image_url, final_question)
                each_chart[each_key + ' question'] = final_question
                each_chart[each_key + ' annotation'] = annotation
                each_chart[each_key + ' GPT-4v'] = gpt_4v_reply
            each_chart['start_length'] = start_length
            each_chart['annotation_id'] = annotation_id
            each_chart['pair_index'] = each_qa_pair['pair_index']
            total_charts.append(each_chart)
        else:
            break

    end = time.time()
    each_annotation_time = round(end - begin,2)
    annotation_id += 1
    print(f"{annotation_id}costs time{each_annotation_time}s")
    with open(f'gpt_4o{annotation_id}_{start_length} × 4_{total_questions}.json', 'w') as file:
        json.dump(total_charts, file, indent=4)
