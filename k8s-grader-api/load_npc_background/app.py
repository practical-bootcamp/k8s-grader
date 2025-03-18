import logging
import os

from common.database import save_npc_background
from common.google_spreadsheet import get_npc_background_google_spreadsheet
from common.handler import text_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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

    npc_backgrounds = get_npc_background_google_spreadsheet(sheet_id)
    if not npc_backgrounds:
        return text_response("Failed to download Google Sheet")

    for npc in npc_backgrounds:
        save_npc_background(npc["name"], npc["age"], npc["gender"], npc["background"])

    return text_response("Updated NPC backgrounds!")
