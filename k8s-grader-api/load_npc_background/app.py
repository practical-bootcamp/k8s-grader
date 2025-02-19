import csv
import logging
import os
from io import StringIO

import requests
from common.database import save_npc_background
from common.handler import text_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


def lambda_handler(event, context):  # pylint: disable=W0613
    query_params = event.get("queryStringParameters")
    if not query_params:
        return text_response("Secret or sheet_id parameter is missing.")
    secret = query_params.get("secret")
    sheet_id = query_params.get("sheet_id")
    if not secret or not sheet_id:
        return text_response("Secret or sheet_id parameter is missing.")

    if secret != os.getenv("SecretHash"):
        return text_response("Invalid secret")

    npc_backgrounds = get_google_spreadsheet(sheet_id)
    if not npc_backgrounds:
        return text_response("Failed to download Google Sheet")

    for npc in npc_backgrounds:
        save_npc_background(npc["name"], npc["age"], npc["gender"], npc["background"])

    return text_response("Updated")
