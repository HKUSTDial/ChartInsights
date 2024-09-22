
from Check_Answers import check_answers
import json
import os
import pandas as pd

def analysis():

    file_path = 'results.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        total_data = json.load(file)

    results = []
    for item in total_data:
        results.append(check_answers(item))

    chart_types = ['grouped bar', 'stacked bar', 'grouped line', 'bar', 'line', 'scatterplot', 'pie']
    question_types = ['fill_the_blank', 'single_choice', 'judgement_question', 'corrective_question']
    task_categories = ['data retrieval', 'extreme', 'cluster', 'filter', 'determine range', 'order', 'distribution',
                       'anomaly', 'correlation', 'reasoning']
    element_types = ['original', 'no label', 'larger label', 'smaller label', 'larger x labels', 'smaller x labels',
                     'no x labels', 'larger y labels', 'smaller y labels', 'no y labels', 'larger scale',
                     'smaller scale', 'different', 'similar', "add shape", "no color"]
    element_combined_types = ['original', 'data label', 'x-axis', 'y-axis', 'different scale', 'color', "legend"]

    counters_element = {}
    counters_question = {}
    counters_chart = {}
    chart_rate = {}
    element_rate = {}
    question_rate = {}
    charts_rate = {}
    questions_rate = {}
    chart2question_rate = {}
    task_rate = {}
    counters_chart2question = {}
    counters_chart = {}
    counters_question_answer = {}
    counters_chart_answer = {}
    counters_chart2question_answer = {}


    for q_type in question_types:
        for task_cat in task_categories:
            counters_question[f"{q_type}_{task_cat}"] = 0


    for item in total_data:
        task_category = item['task_category']

        for q_type in question_types:
            counters_question[f"{q_type}_{task_category}"] += 1



    for c_type in chart_types:
        for q_type in question_types:
            counters_chart2question[f"{c_type}_{q_type}"] = 0


    for item in total_data:

        c_type = item['image_type']

        for q_type in question_types:
            counters_chart2question[f"{c_type}_{q_type}"] += 1

    for v_type in element_types:
        for task_cat in task_categories:
            counters_element[f"{v_type}_{task_cat}"] = 0

    # 遍历数据统计每种组合
    for item in total_data:
        task_category = item['task_category']
        v_type = item['vary_type']
        counters_element[f"{v_type}_{task_category}"] += 1

    # 打印结果
    for key, value in counters_element.items():
        print(f"{key}: {value}")

    for c_type in chart_types:
        for task_cat in task_categories:
            counters_chart[f"{c_type}_{task_cat}"] = 0


    for item in total_data:
        task_category = item['task_category']

        c_type = item['image_type']

        counters_chart[f"{c_type}_{task_category}"] += 1

    for c_type in chart_types:
        for task_cat in task_categories:
            counters_chart_answer[f"{c_type}_{task_cat}"] = 0

    for q_type in question_types:
        for task_cat in task_categories:
            counters_question_answer[f"{q_type}_{task_cat}"] = 0

    for c_type in chart_types:
        for q_type in question_types:
            counters_chart2question_answer[f"{c_type}_{q_type}"] = 0

    counters_element2question = {}

    # 初始化所有可能的组合为0
    for element_type in element_types:
        for q_type in question_types:
            counters_element2question[f"{element_type}_{q_type}"] = 0

    counters_element2chart = {}

    # 初始化所有可能的组合为0
    for element_type in element_types:
        for c_type in chart_types:
            counters_element2chart[f"{element_type}_{c_type}"] = 0

    # 遍历数据统计每种组合
    for item in total_data:
        element_type = item['vary_type']
        # 检查每种元素
        c_type = item['image_type']
        counters_element2chart[f"{element_type}_{c_type}"] += 1

    # 打印结果
    for key, value in counters_element2chart.items():
        print(f"{key}: {value}")
    # 遍历数据统计每种组合
    for item in total_data:
        element_type = item['vary_type']
        # 检查每种元素
        for q_type in question_types:
            counters_element2question[f"{element_type}_{q_type}"] += 1

    # 打印结果
    for key, value in counters_element2question.items():
        print(f"{key}: {value}")

    for item in results:
        chart_type = item['image_type']
        task_category = item['task_category']
        counter = 0
        if item['answer'][0] == 1:
            counters_question_answer[f"fill_the_blank_{task_category}"] += 1
            counters_chart2question_answer[f"{chart_type}_fill_the_blank"] += 1
            counter += 1

        if item['answer'][1] == 1:
            counters_question_answer[f"single_choice_{task_category}"] += 1
            counters_chart2question_answer[f"{chart_type}_single_choice"] += 1
            counter += 1

        if item['answer'][2] == 1:
            counters_question_answer[f"judgement_question_{task_category}"] += 1
            counters_chart2question_answer[f"{chart_type}_judgement_question"] += 1
            counter += 1

        if item['answer'][3] == 1:
            counters_question_answer[f"corrective_question_{task_category}"] += 1
            counters_chart2question_answer[f"{chart_type}_corrective_question"] += 1
            counter += 1

        counters_chart_answer[f"{chart_type}_{task_category}"] += counter


    for key, correct_count in counters_chart_answer.items():
        total_count = counters_chart[key]*4

        if total_count > 0:
            charts_rate[key] = correct_count / total_count
        else:
            charts_rate[key] = 0 


    for key, correct_count in counters_question_answer.items():
        total_count = counters_question[key]

        if total_count > 0:
            questions_rate[key] = correct_count / total_count
        else:
            questions_rate[key] = 0


    for key, correct_count in counters_chart2question_answer.items():
        total_count = counters_chart2question[key]

        if total_count > 0:
            chart2question_rate[key] = correct_count / total_count
        else:
            chart2question_rate[key] = 0

            # 计算题型任务类别的正确率
    for key, correct_count in counters_element_answer.items():
        total_count = counters_element[key] * 4
        # 避免除以零
        if total_count > 0:
            element_rate[key] = correct_count / total_count
        else:
            element_rate[key] = 0  # 如果没有这种类型的题目，正确率设置为0

    for chart_type in chart_types:
        total_count = 0
        correct_count = 0
        for task_category in task_categories:
            key = f"{chart_type}_{task_category}"
            total_count += counters_chart.get(key, 0)*4
            correct_count += counters_chart_answer.get(key, 0)

        chart_rate[chart_type] = correct_count / total_count if total_count > 0 else 0

    question_rate = {}


    for q_type in question_types:
        total_count = 0
        correct_count = 0
        for task_category in task_categories:
            key = f"{q_type}_{task_category}"
            total_count += counters_question.get(key, 0)
            correct_count += counters_question_answer.get(key, 0)

        question_rate[q_type] = correct_count / total_count if total_count > 0 else 0

    task_rate = {}


    for task_category in task_categories:
        total_count = 0
        correct_count = 0
        for q_type in question_types:
            key = f"{q_type}_{task_category}"
            total_count += counters_question.get(key, 0)
            correct_count += counters_question_answer.get(key, 0)

        task_rate[task_category] = correct_count / total_count if total_count > 0 else 0

    import pandas as pd

    df = pd.DataFrame([chart_rate], index=["overall"])
    df = df*100
    df = df.round(2)
    df.to_csv('Accuracy Table/Overall_chart_accuracy.csv')

    df = pd.DataFrame([task_rate], index=["overall"])
    df = df*100
    df = df.round(2)
    df.to_csv('Accuracy Table/Overall_task_accuracy.csv')

    df = pd.DataFrame([question_rate], index=["overall"])
    df = df*100
    df = df.round(2)
    df.to_csv('Accuracy Table/Overall_question_accuracy.csv')


    charts_df = pd.DataFrame(index=chart_types, columns=[task.capitalize() if task not in ['data retrieval', 'determine range'] else task.split()[1].capitalize() for task in task_categories])


    for chart in chart_types:
        for task in task_categories:
            key = f"{chart}_{task}"
            charts_df.at[chart, task.capitalize() if task not in ['data retrieval', 'determine range'] else task.split()[1].capitalize()] = charts_rate.get(key, 0)


    question_df = pd.DataFrame(index=question_types, columns=[task.capitalize() if task not in ['data retrieval', 'determine range'] else task.split()[1].capitalize() for task in task_categories])


    for question in question_types:
        for task in task_categories:
            key = f"{question}_{task}"
            question_df.at[question, task.capitalize() if task not in ['data retrieval', 'determine range'] else task.split()[1].capitalize()] = questions_rate.get(key, 0)

    charts2question_df = pd.DataFrame(index=chart_types, columns=question_types)


    for chart in chart_types:
        for question in question_types:
            key = f"{chart}_{question}"
            charts2question_df.at[chart, question] = chart2question_rate.get(key, 0)

    df_percent = charts_df * 100  # Convert to percentage
    df_rounded = df_percent.applymap(lambda x: f'{x:.2f}')  # Apply formatting
    df_rounded.replace("0.00", "-", inplace=True)
    df_rounded.to_csv("Accuracy Table/Chart2Task_accuracy.csv")


    df_percent = question_df * 100  # Convert to percentage
    df_rounded = df_percent.applymap(lambda x: f'{x:.2f}')  # Apply formatting
    df_rounded.to_csv("Accuracy Table/Question2Task_accuracy.csv")


    df_percent = charts2question_df * 100  # Convert to percentage
    df_rounded = df_percent.applymap(lambda x: f'{x:.2f}')  # Apply formatting
    df_rounded.to_csv("Accuracy Table/Chart2Question_accuracy.csv")

    # element_types = ['original', 'no label','larger label', 'smaller label','larger x labels','smaller x labels','no x labels', 'larger y labels','smaller y labels','no y labels', 'larger scale','smaller scale','different','similar']
    # 计算每个prompt_type的总体正确率
    total_correct_prompt = {}
    total_count_prompt = {}

    for e_type in element_types:
        # 初始化计数器
        total_correct_prompt[e_type] = 0
        total_count_prompt[e_type] = 0

        for c_type in chart_types:
            total_correct_prompt[e_type] += counters_element2chart_answer.get(f"{e_type}_{c_type}", 0)
            total_count_prompt[e_type] += counters_element2chart.get(f"{e_type}_{c_type}", 0)

    # 计算总体正确率
    overall_rates = {
        e_type: total_correct_prompt[e_type] / (total_count_prompt[e_type] * 4) if total_count_prompt[e_type] > 0 else 0
        for e_type in element_types}

    # 计算相对于original的提升百分比
    improvement_over_original = {
        e_type: ((overall_rates[e_type] - overall_rates['original'])) if overall_rates['original'] > 0 else 0 for e_type
        in element_types}

    results_df = pd.DataFrame(index=element_types, columns=['overall_rate', 'improvement_over_original (%)'])
    # 创建DataFrame以展示结果
    result_df = pd.DataFrame({
        'overall_rate': [overall_rates[p] for p in element_types],
        'improvement(%)': [improvement_over_original[p] for p in element_types]
    }, index=element_types)

    # 显示DataFrame
    print(result_df)
