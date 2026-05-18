from datetime import date
from typing import Literal

SeasonFlag = Literal["성수기", "비수기", "전환기"]


def get_season_flag(today: date | None = None) -> SeasonFlag:
    if today is None:
        today = date.today()

    year = today.year

    seasons = [
        # 복분자 생과 전환기: 6/1 ~ 6/14
        (date(year, 6, 1), date(year, 6, 14), "전환기"),
        # 복분자 생과 성수기: 6/15 ~ 7/7
        (date(year, 6, 15), date(year, 7, 7), "성수기"),
        # 블랙베리 전환기: 7/8 ~ 7/14
        (date(year, 7, 8), date(year, 7, 14), "전환기"),
        # 블랙베리 성수기: 7/15 ~ 8/31
        (date(year, 7, 15), date(year, 8, 31), "성수기"),
        # 블랙베리 시즌 종료 후 전환기: 9/1 ~ 9/7
        (date(year, 9, 1), date(year, 9, 7), "전환기"),
    ]

    for start, end, flag in seasons:
        if start <= today <= end:
            return flag

    return "비수기"


def get_season_context(today: date | None = None) -> dict:
    if today is None:
        today = date.today()

    flag = get_season_flag(today)

    return {
        "season_flag": flag,
        "date": today.isoformat(),
        "note": _get_note(today, flag),
    }


def _get_note(today: date, flag: SeasonFlag) -> str:
    month = today.month
    if flag == "성수기":
        if 6 <= month <= 7:
            return "복분자 생과 성수기"
        return "블랙베리 성수기"
    if flag == "전환기":
        if month == 6:
            return "복분자 생과 전환기 진입"
        if month in (7, 8):
            return "블랙베리 전환기"
        return "시즌 종료 전환기"
    return "비수기 — 냉동 복분자 연중 운영 (전년 동기 대비만 비교)"
