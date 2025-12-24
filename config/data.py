import json
file_path = 'config\\config.json'

def get_data(*params):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    return {p: data[p] for p in params}
