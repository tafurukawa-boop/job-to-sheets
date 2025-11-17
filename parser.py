import re
import html

# -------------------------------------------------
# Job Text Parser
# -------------------------------------------------

HEADERS = [
    "勤務地","仕事内容","応募資格","勤務時間","勤務時間詳細","勤務形態",
    "求めている人材","休日休暇","勤務地所在地","交通アクセス","交通・アクセス",
    "給与","給与詳細","給与例","試用期間","待遇","待遇・福利厚生",
    "社会保険","職場環境","選考フロー","選考プロセス",
    "キャッチコピー","アピールポイント","雇用形態","＼こんな方にもオススメ／",
    "掲載企業名","応募受付先電話番号","採用担当者名","担当者名",
    "企業情報（備考）","採用HP","代表電話番号","代表者番号",
    "企業名","本社所在地","業種","代表者名","お問い合わせ電話番号",
    # 新規追加
    "資格","アクセス","応募方法"
]


def clean_text(text: str) -> str:
    """事前クリーニング"""
    cleaned = html.unescape(text)
    cleaned = re.sub(r'["“”]', '', cleaned)
    cleaned = re.sub(r'&nbsp;?', ' ', cleaned)
    cleaned = re.sub(r'[\u3000\r]', ' ', cleaned)
    cleaned = re.sub(r'\n{4,}', '\n\n\n', cleaned)
    return cleaned.strip()


def detect_company_and_salary(lines):
    """冒頭10行から会社名＆給与を抽出"""
    company_line, pay_line = "", ""
    for i in range(1, min(10, len(lines))):
        if not company_line and re.search(r"(株式会社|有限会社)", lines[i]):
            company_line = lines[i]
        if not pay_line and re.search(r"(時給|月給|年収|日給)", lines[i]):
            pay_line = lines[i]
        if company_line and pay_line:
            break
    return company_line, pay_line


def extract_sections(cleaned):
    """見出しごとにセクションを抽出"""
    pattern = r"(?m)^[ \t　]*(?P<header>(" + "|".join(map(re.escape, HEADERS)) + r"))([ 　:：].*|\n|$)"
    matches = list(re.finditer(pattern, cleaned))

    structured = {}

    for i, m in enumerate(matches):
        header = m.group("header")
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned)
        section_text = cleaned[start:end].strip()
        section_text = re.sub(r'\n{4,}', '\n\n\n', section_text)
        structured[header] = section_text

    return structured, matches


def parse_job_text(text: str) -> dict:
    """求人テキスト → 辞書へ変換（JobParserの中心）"""

    cleaned = clean_text(text)
    lines = [l.strip() for l in cleaned.splitlines() if l.strip()]

    job_title = re.sub(r'[\\/*?[\]:]', '', lines[0]) if lines else "求人情報"
    company_line, pay_line = detect_company_and_salary(lines)

    sections, matches = extract_sections(cleaned)

    result = {
        "job_title": job_title,
        "company": company_line,
        "salary": pay_line,
        "sections": sections
    }

    return result

