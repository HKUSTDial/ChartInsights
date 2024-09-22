import json
import os
import time
import base64
import pandas as pd
import requests

api_key ='Your API key'

with open('qa_pairs.json', 'r') as file:
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

def extract_csv_data(csv_file):
    x_axis = csv_file.iloc[:,0].values.flatten()
    data_str = ''
    x_axis_str = ''
    for each_xaxis in x_axis:
        x_axis_str += str(each_xaxis)
        x_axis_str += ', '
    return  x_axis_str.strip(', ')

def scatter_extract_csv_data(csv_file):
    categories = csv_file.iloc[:,-1].values.flatten()
    category_str = set()
    for each_category in categories:
        category_str.add(each_category)
    max_y_value = csv_file['y_data'].max()
    min_y_value = csv_file['y_data'].min()
    return category_str, min_y_value, max_y_value

def process_dataframe_generic(csv_file):
    df = pd.read_csv(csv_file,index_col=0)
    rows = df.index.tolist()
    columns = df.columns.tolist()

    result_string = ""
    if len(columns) >= 2:
        for row in rows:
            result_string += "- {}: ".format(row)
            for col in columns:
                value = df.loc[row, col]
                result_string += "{}: {}, ".format(col, value)
            result_string = result_string[:-2] 
            result_string += "\t"
    else:
        for row in rows:
            result_string += "- {}: ".format(row)
            for col in columns:
                value = df.loc[row, col]
                result_string += "{}, ".format(value)
            result_string = result_string[:-2] 
            result_string += "\t"
    return result_string 
root_image_path = 'charts/'
root_table_path = 'tables/'
prompt_pngs = []
for each_visual_qa_pair in visual_qa_pairs:
    image_index = each_visual_qa_pair['image_index']
    image_name = each_visual_qa_pair['image_url']
    image_type = each_visual_qa_pair['image_type']
    task_category = each_visual_qa_pair['type']
    question_level = each_visual_qa_pair['question_level']
    image_index_dict = {}
    image_index_dict['image_url'] = root_image_path + str(image_index) + '.png'
    image_index_dict['table_url'] = root_table_path + str(image_index) + '.csv'
    image_index_dict['task_category'] = task_category
    image_index_dict['QA_pairs'] = each_visual_qa_pair['QA_pairs']
    image_index_dict['id'] = image_index
    image_index_dict['image_type'] = image_type
    image_index_dict['question_level'] = question_level
    prompt_pngs.append(image_index_dict)

ChartCot = "Let's answer following questions one by one: 1.What type is this chart? 2.What are the labels of x-axis? 3.What are the data labels of each element? 4."
Scatter_ChartCot = "Let's answer following questions one by one: 1.What type is this chart? 2.What are the names of different categories? 3.What is the maximum and minimum value of this scatter plot? 4."
Roleplay = "You are an expert on chart understanding with specialized skills in numerical analysis. Your keen eye for detail allows you to accurately identify and extract numerical values from various chart elements, such as the x-axis/y-axis categories and the legend keys. Your role is to analyze charts, promptly determine the sum or average of specified elements, and communicate your findings in an accessible manner."
Tutorial = "Firstly, identify the chart's basic structure and type to understanding the visual elements used in the chart and how these elements represent data. Subsequently, observing the chart title, legend, and axes, which provide essential information about the data's theme and measurement units. Next, identify key data points, such as significant highs, lows, or trends. Further steps include comparing relationships between different data series and interpreting proportions of the data. Finally, summarize the information gathered."

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

    if image_type != 'scatter':
        #ChartCoT
        ChartCoT_fill_the_blank = ChartCot + fill_the_blank_question
        ChartCoT_multiple_choice = ChartCot + multiple_choice_question
        ChartCoT_judgement_question = ChartCot + Judgement_question_question
        ChartCoT_corrective_question = ChartCot + Corrective_question_question
    else:
        ChartCoT_fill_the_blank = Scatter_ChartCot + fill_the_blank_question
        ChartCoT_multiple_choice = Scatter_ChartCot + multiple_choice_question
        ChartCoT_judgement_question = Scatter_ChartCot + Judgement_question_question
        ChartCoT_corrective_question = Scatter_ChartCot + Corrective_question_question

#     Role-play
    Roleplay_fill_the_blank = Roleplay + fill_the_blank_question
    Roleplay_multiple_choice = Roleplay + multiple_choice_question
    Roleplay_judgement_question = Roleplay + Judgement_question_question
    Roleplay_corrective_question = Roleplay + Corrective_question_question

    #Turorial
    Tutorial_fill_the_blank = fill_the_blank_question +' ' + Tutorial
    Tutorial_multiple_choice = multiple_choice_question + ' '+Tutorial
    Tutorial_judgement_question = Judgement_question_question + ' ' + Tutorial
    Tutorial_corrective_question = Corrective_question_question + ' ' + Tutorial
    print(Tutorial_multiple_choice)

    #chart reasoning
    if image_type != 'scatter':
        chart_type = image_type.split(' ')[-1]

        x_axis_names = extract_csv_data(metadata)
        chart_data = process_dataframe_generic(table_url)
        Chart_reasoning_prompts = f"Learn from the previous three questions and answers one by one, and then answer the last question.1.Q:What type is this chart?A:{chart_type}. 2.Q:What are the labels of x-axis?A:{x_axis_names}. 3.Q:What are the data labels of each element? A:{chart_data}. 4.Q:"
        ChartQ_and_A_prompts = f"1.Q:What type is this chart?A:{chart_type}. 2.Q:What are the labels of x-axis?A:{x_axis_names}. 3.Q:What are the data labels of each element? A:{chart_data}. 4.Q:"
    elif image_type == 'scatter':
        chart_type = 'scatter'
        categories, min_value, max_value = scatter_extract_csv_data(metadata)
        Chart_reasoning_prompts = f"Learn from the previous three questions and answers one by one, and then answer the last question.1.Q:What type is this chart?A:{chart_type} chart. 2.Q:What are the names of different categories?A:{categories}. 3.Q:What is the maximum and minimum value of this scatter plot? A:{max_value, min_value}. 4.Q:"
        ChartQ_and_A_prompts = f"1.Q:What type is this chart?A:{chart_type} chart. 2.Q:What are the names of different categories?A:{categories}. 3.Q:What is the maximum and minimum value of this scatter plot? A:{max_value, min_value}. 4.Q:"
    Chart_reasoning_fill_the_blank = Chart_reasoning_prompts + fill_the_blank_question+'A:'
    Chart_reasoning_multiple_question = Chart_reasoning_prompts + multiple_choice_question+'A:'
    Chart_reasoning_judgement_question = Chart_reasoning_prompts + Judgement_question_question + 'A:'
    Chart_reasoning_corrective_question = Chart_reasoning_prompts + Corrective_question_question + 'A:'
    ChartQ_A_fill_the_blank = ChartQ_and_A_prompts + fill_the_blank_question + 'A:'
    ChartQ_A_multiple_choice_question = ChartQ_and_A_prompts + multiple_choice_question + 'A:'
    ChartQ_A_judgement_question = ChartQ_and_A_prompts + Judgement_question_question + 'A:'
    ChartQ_A_corrective_question = ChartQ_and_A_prompts + Corrective_question_question + 'A:'

    each_answer_dict['original_fill_the_blank_annotation'] = fill_the_blank_annotation
    each_answer_dict['chartcot_fill_the_blank'] = ChartCoT_fill_the_blank
    each_answer_dict['chartcot_fill_the_blank_gpt'] = get_gpt_4o_reply(image_url, ChartCoT_fill_the_blank)
    each_answer_dict['roleplay_fill_the_blank'] = Roleplay_fill_the_blank
    each_answer_dict['roleplay_fill_the_blank_gpt'] = get_gpt_4o_reply(image_url, Roleplay_fill_the_blank)
    each_answer_dict['tutorial_fill_the_blank'] = Tutorial_fill_the_blank
    each_answer_dict['tutorial_fill_the_blank_gpt'] = get_gpt_4o_reply(image_url, Tutorial_fill_the_blank)
    each_answer_dict['chartQA_fill_the_blank'] = ChartQ_A_fill_the_blank
    each_answer_dict['chartQA_fill_the_blank_gpt'] = get_gpt_4o_reply(image_url, ChartQ_A_fill_the_blank)
    each_answer_dict['chartrea_fill_the_blank'] = Chart_reasoning_fill_the_blank
    each_answer_dict['chartrea_fill_the_blank_gpt'] = get_gpt_4o_reply(image_url, Chart_reasoning_fill_the_blank)


    each_answer_dict['original_multiple_choice_annotation'] = multiple_choice_annotation
    each_answer_dict['chartcot_multiple_choice'] = ChartCoT_multiple_choice
    each_answer_dict['chartcot_multiple_choice_gpt'] = get_gpt_4o_reply(image_url, ChartCoT_multiple_choice)
    each_answer_dict['roleplay_multiple_choice'] = Roleplay_multiple_choice
    each_answer_dict['roleplay_multiple_choice_gpt'] = get_gpt_4o_reply(image_url, Roleplay_multiple_choice)
    each_answer_dict['tutorial_multiple_choice'] = Tutorial_multiple_choice
    each_answer_dict['tutorial_multiple_choice_gpt'] = get_gpt_4o_reply(image_url, Tutorial_multiple_choice)
    each_answer_dict['chartQA_multiple_choice'] = ChartQ_A_multiple_choice_question
    each_answer_dict['chartQA_multiple_choice_gpt'] = get_gpt_4o_reply(image_url, ChartQ_A_multiple_choice_question)
    each_answer_dict['chartrea_multiple_choice'] = Chart_reasoning_multiple_question
    each_answer_dict['chartrea_multiple_choice_gpt'] = get_gpt_4o_reply(image_url, Chart_reasoning_multiple_question)


    each_answer_dict['original_Judgement_question_annotation'] = Judgement_question_annotation
    each_answer_dict['chartcot_Judgement_question'] = ChartCoT_judgement_question
    each_answer_dict['chartcot_Judgement_question_gpt'] = get_gpt_4o_reply(image_url, ChartCoT_judgement_question)
    each_answer_dict['roleplay_Judgement_question'] = Roleplay_judgement_question
    each_answer_dict['roleplay_Judgement_question_gpt'] = get_gpt_4o_reply(image_url, Roleplay_judgement_question)
    each_answer_dict['tutorial_Judgement_question'] = Tutorial_judgement_question
    each_answer_dict['tutorial_Judgement_question_gpt'] = get_gpt_4o_reply(image_url, Tutorial_judgement_question)
    each_answer_dict['chartQA_Judgement_question'] = ChartQ_A_judgement_question
    each_answer_dict['chartQA_Judgement_question_gpt'] = get_gpt_4o_reply(image_url, ChartQ_A_judgement_question)
    each_answer_dict['chartrea_Judgement_question'] = Chart_reasoning_judgement_question
    each_answer_dict['chartrea_Judgement_question_gpt'] = get_gpt_4o_reply(image_url, Chart_reasoning_judgement_question)


    each_answer_dict['original_Corrective_question_annotation'] = Corrective_question_annotation
    each_answer_dict['chartcot_Corrective_question'] = ChartCoT_corrective_question
    each_answer_dict['chartcot_Corrective_question_gpt'] = get_gpt_4o_reply(image_url, ChartCoT_corrective_question)
    each_answer_dict['roleplay_Corrective_question'] = Roleplay_corrective_question
    each_answer_dict['roleplay_Corrective_question_gpt'] = get_gpt_4o_reply(image_url, Roleplay_corrective_question)
    
    
    each_answer_dict['tutorial_Corrective_question'] = Tutorial_corrective_question
    each_answer_dict['tutorial_Corrective_question_gpt'] = get_gpt_4o_reply(image_url, Tutorial_corrective_question)
    each_answer_dict['chartQA_Corrective_question'] = ChartQ_A_corrective_question
    each_answer_dict['chartQA_Corrective_question_gpt'] = get_gpt_4o_reply(image_url, ChartQ_A_corrective_question)
    each_answer_dict['chartrea_Corrective_question'] = Chart_reasoning_corrective_question
    each_answer_dict['chartrea_Corrective_question_gpt'] = get_gpt_4o_reply(image_url, Chart_reasoning_corrective_question)

    total_results.append(each_answer_dict)
    # with open(f'results/other_prompt/{image_id}_{task_category}_{count}.json','w') as file:
    #     json.dump(each_answer_dict, file, indent=4)
    # with open(f'results/other_prompt/total_results.json', 'w') as file:
    #     json.dump(total_results, file, indent=4)
    end = time.time()
    process = round(end - begin ,2)
    print(f"={image_id}_{task_category}，takes{process}s.{count+1}/{len(prompt_pngs)} has been finished")
    count += 1
