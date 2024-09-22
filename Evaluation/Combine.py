from pathlib import Path

combined_results_dir = 'results/'

file_paths = []


for file_path in Path(combined_results_dir).glob('*.json'):

    if file_path.name != 'total_results.json':
        file_paths.append(file_path)

sorted_file_paths = sorted(file_paths)

total_data = []


for file_path in sorted_file_paths:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        total_data.extend(data)


total_results_dir = 'results/'
total_results_path = os.path.join(total_results_dir, 'total_results.json')


os.makedirs(total_results_dir, exist_ok=True)


with open(total_results_path, 'w', encoding='utf-8') as file:
    json.dump(total_data, file, ensure_ascii=False, indent=4)

print(f"All files are combined into {total_results_path}.")
