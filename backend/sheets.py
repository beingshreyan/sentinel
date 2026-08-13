import os
from typing import Any

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_sheet():
    credentials_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")

    if not credentials_file:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_FILE is not configured.")

    if not sheet_id:
        raise RuntimeError("GOOGLE_SHEET_ID is not configured.")

    credentials = Credentials.from_service_account_file(
        credentials_file,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(sheet_id)

    # Uses the first worksheet in the spreadsheet.
    worksheet = spreadsheet.sheet1

    return worksheet


def append_record(record: dict[str, Any]) -> None:
    worksheet = get_sheet()

    headers = worksheet.row_values(1)

    if not headers:
        raise RuntimeError("Google Sheet does not contain a header row.")

    row = [record.get(header, "") for header in headers]

    worksheet.append_row(
        row,
        value_input_option="USER_ENTERED",
    )


def get_records() -> list[dict[str, Any]]:
    worksheet = get_sheet()

    return worksheet.get_all_records()