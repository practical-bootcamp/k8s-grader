import csv
import sys
from io import StringIO

import requests


def get_google_spreadsheet(spreadsheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        csv_str = response.content.decode("utf-8")
        f = StringIO(csv_str)
        spreadsheet_data = []
        reader = csv.reader(f, delimiter=",")
        next(reader, None)  # Skip the header row
        for row in reader:
            if len(row) < 4:
                continue
            name, age, gender, background = row[:4]
            if not name:
                continue
            spreadsheet_data.append(
                {"name": name, "age": age, "gender": gender, "background": background}
            )
        return spreadsheet_data
    return None


data = get_google_spreadsheet("1VdQsc9qslvd-gGhydN5dEZEX6Q5uliBQqRguJyHBZM4")
print(data)

sys.exit(0)
