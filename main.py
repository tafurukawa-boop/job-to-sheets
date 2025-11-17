
"""
Main entry point for converting raw job text
into structured Google Sheets format.
"""

from parser import parse_job_text
import sys
import json
import gspread
from google.oauth2.service_account import Credentials

# ----------------------------------------------------
# Google Sheets 認証
# ----------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_KEY = "1tADXpRK_14oVzddU9mToDcgGXAksiMy-zj4Hg3xmXlE"   # ← あなたのシートIDに置き換える

def authorize_google():
    creds = Credentials.from_service_account_file(
        "service_account.json", scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client

# ----------------------------------------------------
# メイン処理
# ----------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("使い方: python main.py input.txt")
        return

    input_path = sys.argv[1]

    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    parsed = parse_job_text(raw_text)

    # JSON 出力
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    print("✔ 解析完了: output.json に保存しました")

    # Google Sheets に書き込み
    client = authorize_google()
    sheet = client.open_by_key(SPREADSHEET_KEY)

    # 新しいシートを作成
    title = parsed["job_title"][:50]
    try:
        ws = sheet.add_worksheet(title=title, rows="200", cols="20")
    except gspread.exceptions.APIError:
        ws = sheet.worksheet(title)
        ws.clear()

    # 1 行目
    ws.append_row(["job_title", "company", "salary", "sections"])

    # 2 行目
    ws.append_row([
        parsed["job_title"],
        parsed["company"],
        parsed["salary"],
        json.dumps(parsed["sections"], ensure_ascii=False)
    ])

    print(f"✔ Google Sheets に反映済み: {title}")


if __name__ == "__main__":
    main()
