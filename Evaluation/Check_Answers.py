import re

def extract_numbers(s):

    return re.findall(r'\d+\.\d+|\d+', s)

def round_numbers(numbers, decimals=2):

    return [round(num, decimals) for num in numbers]

def numbers_match(annotation, content):

    annotation_numbers = extract_numbers(annotation)
    content_numbers = extract_numbers(content)


    annotation_numbers = [float(num) for num in annotation_numbers]
    content_numbers = [float(num) for num in content_numbers]
    if not annotation_numbers:
        return False

    content_numbers_rounded = round_numbers(content_numbers, 2)

    return all(num in content_numbers_rounded for num in annotation_numbers)

def normalize_answer(answer):

    return ''.join(answer.split()).replace(',', '').lower()

def number_to_words(number):

    num_map = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
               "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten"}
    return num_map.get(number, str(number))

def string_match(annotation, content):

    if isinstance(annotation, str):
        annotation = [annotation]


    return all(normalize_answer(string) in normalize_answer(content) for string in annotation)

def list_match(annotation, content):

    content_numbers = extract_numbers(content)


    for item in annotation:

        if isinstance(item, (int, float)):
            number_str = str(item)
            words = number_to_words(item)
            if not (number_str in content_numbers):
                return False

        elif isinstance(item, str) and normalize_answer(item) not in normalize_answer(content):
            return False

    return True

def validate_distribution(annotation,content):
    if isinstance(annotation, str):
        annotation_numbers = extract_numbers(annotaion)
        content_numbers = extract_numbers(content)


        annotation_numbers = [float(num) for num in annotation_numbers]
        content_numbers = [float(num) for num in content_numbers]
        min_num = min(annotation_numbers)
        max_num = max(annotation_numbers)
        min_con = min(content_numbers)
        max_con = max(content_numbers)
        if min_con<=min_num and max_con>=max_num:
            return True
        else:
            return False
    elif isinstance(annotation, list):
        content_numbers = extract_numbers(content)
        content_numbers = [float(num) for num in content_numbers]

        if isinstance(annotation[0],str):
            min_num  = float(extract_numbers(annotation[0])[0])
            max_num  =  float(extract_numbers(annotation[1])[0])
        else:
            min_num = min(annotation)
            max_num = max(annotation)
        min_con = min(content_numbers)
        max_con = max(content_numbers)
        if min_con<=min_num and max_con>=max_num:
            return True
        else:
            return False
    else:
        return False

def validate_order(annotation, content):

    pattern = re.compile(r'\b(' + '|'.join(re.escape(word) for word in annotation) + r')\b')
    matches = pattern.findall(content)

    return matches == annotation


def check_answers(data):
    result = {'answer': [0, 0, 0, 0], 'pair_index': data['pair_index'], 'image_type': data['image_type'],
              'task_category': data['task_category'],
              'url': data['image_url']}


    if numbers_match(str(data['fill_the_blank annotation']), data['fill_the_blank Reply']['content']):
        result['answer'][0] = 1

    if str(data['fill_the_blank annotation']).lower() in normalize_answer(data['fill_the_blank Reply']['content']):
        result['answer'][0] = 1

    if number_to_words(str(data['fill_the_blank annotation'])) in normalize_answer(
            data['fill_the_blank Reply']['content']):
        result['answer'][0] = 1

    if isinstance(data['fill_the_blank annotation'], list):
        if list_match(data['fill_the_blank annotation'], data['fill_the_blank Reply']['content']):
            result['answer'][0] = 1
    if data['task_category'] == 'distribution':
        if validate_distribution(data['fill_the_blank annotation'], data['fill_the_blank Reply']['content']):
            result['answer'][0] = 1
    if data['task_category'] == 'order' and isinstance(data['fill_the_blank annotation'], list):
        if validate_order(data['fill_the_blank annotation'], data['fill_the_blank Reply']['content']):
            result['answer'][0] = 1
        else:
            result['answer'][0] = 0


    if str(data['Multiple_choice annotation']) in normalize_answer(data['Multiple_choice Reply']['content']):
        result['answer'][1] = 1

    if numbers_match(str(data['Multiple_choice annotation']), data['Multiple_choice Reply']['content']):
        result['answer'][1] = 1

    if isinstance(data['Multiple_choice annotation'], list):
        if list_match(data['Multiple_choice annotation'], data['Multiple_choice Reply']['content']):
            result['answer'][1] = 1
    if data['task_category'] == 'order' and isinstance(data['Multiple_choice annotation'], list):
        if validate_order(data['Multiple_choice annotation'], data['Multiple_choice Reply']['content']):
            result['answer'][1] = 1
        else:
            result['answer'][1] = 0

 
    if str(data['Judgement_question annotation']).lower() in normalize_answer(
            data['Judgement_question Reply']['content']).lower():
        result['answer'][2] = 1


    if numbers_match(str(data['Corrective_question annotation']), data['Corrective_question Reply']['content']):
        result['answer'][3] = 1

    if str(data['Corrective_question annotation']).lower() in normalize_answer(
            data['Corrective_question Reply']['content']):
        result['answer'][3] = 1

    if number_to_words(str(data['Corrective_question annotation'])) in normalize_answer(
            data['Corrective_question Reply']['content']):
        result['answer'][3] = 1
    if isinstance(data['Corrective_question annotation'], list):
        if list_match(data['Corrective_question annotation'], data['Corrective_question Reply']['content']):
            result['answer'][3] = 1
    if data['task_category'] == 'distribution':
        if validate_distribution(data['Corrective_question annotation'],
                                 data['Corrective_question Reply']['content']):
            result['answer'][3] = 1
    if data['task_category'] == 'order' and isinstance(data['Corrective_question annotation'], list):
        if validate_order(data['Corrective_question annotation'], data['Corrective_question Reply']['content']):
            result['answer'][3] = 1
        else:
            result['answer'][3] = 0

    return result

