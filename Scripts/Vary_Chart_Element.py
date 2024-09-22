import json
import os
import time
import base64
import pandas as pd
import requests 

api_key = "your api key"

with open('vary_element_qa_pairs.json', 'r') as file:
    vary_element_qa_pairs = json.load(file)
with open('vary_element_annotations.json', 'r') as file:
    vary_element_annotations = json.load(file)

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
#                 'detail':'high'
              },
            }
          ]
        }
      ],
      "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
#     gpt_4o_total_tokens = response.json()['usage']['total_tokens']
    print(response.json())
    gpt_4o_reply = response.json()['choices'][0]['message']

    return gpt_4o_reply
## main_function
start_length = 0
total_questions = 0
gap = False
annotation_id = 0

for _, each_annotation in enumerate(vary_element_annotations[annotation_id:]):
    total_charts = []
    if gap == True:
        break
    # print(each_annotation)
    begin = time.time()
    image_path = each_annotation['changed_image']
    vary_element = each_annotation['vary_element']
    vary_type = each_annotation['vary_type']
    # print(image_index)
    image_url = f'vary_element/{vary_element}/{vary_type}/'  + image_path
    image_type = each_annotation['type']
    index = each_annotation['id']
    for i, each_qa_pair in enumerate(vary_element_qa_pairs[start_length:]):
        each_chart = {}
        each_chart['image_url'] = image_url
        each_chart['image_type'] = image_type
        task_category = each_qa_pair['type']
        each_chart['task_category'] = task_category
        each_chart['vary_element'] = each_qa_pair['vary_element']
        each_chart['vary_type'] = each_qa_pair['vary_type']

        if index == each_qa_pair['image_index'] and vary_element == each_qa_pair['vary_element'] and vary_type == each_qa_pair['vary_type']:
            start_length += 1

            if task_category == 'reasoning' and ('variance' in each_qa_pair['QA_pairs'][0]['fill_the_blank'][0] or 'deviation' in each_qa_pair['QA_pairs'][0]['fill_the_blank'][0]):
                continue
            total_questions += 4

            print(f"{index}, {task_category}, {vary_type}")
            for each_question_format in each_qa_pair['QA_pairs']:
                each_key = list(each_question_format.keys())[0]

                final_question = each_question_format[each_key][0]
                annotation = each_question_format[each_key][1]

                qwen_reply = get_gpt_4o_reply(image_url, final_question)

                each_chart[each_key + ' question'] = final_question
                each_chart[each_key + ' annotation'] = annotation
                each_chart[each_key + ' gpt4o'] = qwen_reply
            each_chart['start_length'] = start_length
            each_chart['annotation_id'] = annotation_id
            each_chart['pair_index'] = each_qa_pair['pair_index']
            total_charts.append(each_chart)
        else:
            break

    annotation_id += 1
    # with open(f'results/gpt4o/gpt4o_element_{annotation_id}_{start_length}.json', 'w') as file:
    #     json.dump(total_charts, file, indent=4)
    print(f"{annotation_id}_{len(vary_element_annotations)}.{start_length}/{len(vary_element_qa_pairs)}has been saved")

