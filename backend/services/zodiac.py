"""
별자리 분석 서비스 - 태양궁 / 달궁 / 상승궁 계산
kerykeion 라이브러리 (Swiss Ephemeris 기반)
"""

from kerykeion import AstrologicalSubject

# 영문 → 한글 별자리명 (전체명 + kerykeion 약어 모두 지원)
ZODIAC_SIGNS_KO: dict[str, str] = {
    "Aries": "양자리",      "Ari": "양자리",
    "Taurus": "황소자리",   "Tau": "황소자리",
    "Gemini": "쌍둥이자리", "Gem": "쌍둥이자리",
    "Cancer": "게자리",     "Can": "게자리",
    "Leo": "사자자리",      "Leo": "사자자리",
    "Virgo": "처녀자리",    "Vir": "처녀자리",
    "Libra": "천칭자리",    "Lib": "천칭자리",
    "Scorpio": "전갈자리",  "Sco": "전갈자리",
    "Sagittarius": "사수자리", "Sag": "사수자리",
    "Capricorn": "염소자리",   "Cap": "염소자리",
    "Aquarius": "물병자리",    "Aqu": "물병자리",
    "Pisces": "물고기자리",    "Pis": "물고기자리",
}

ZODIAC_ELEMENTS: dict[str, str] = {
    "양자리": "불", "사자자리": "불", "사수자리": "불",
    "황소자리": "흙", "처녀자리": "흙", "염소자리": "흙",
    "쌍둥이자리": "바람", "천칭자리": "바람", "물병자리": "바람",
    "게자리": "물", "전갈자리": "물", "물고기자리": "물",
}

ZODIAC_MODALITIES: dict[str, str] = {
    "양자리": "활동궁", "게자리": "활동궁", "천칭자리": "활동궁", "염소자리": "활동궁",
    "황소자리": "고정궁", "사자자리": "고정궁", "전갈자리": "고정궁", "물병자리": "고정궁",
    "쌍둥이자리": "변통궁", "처녀자리": "변통궁", "사수자리": "변통궁", "물고기자리": "변통궁",
}

ZODIAC_SYMBOLS: dict[str, str] = {
    "양자리": "♈", "황소자리": "♉", "쌍둥이자리": "♊",
    "게자리": "♋", "사자자리": "♌", "처녀자리": "♍",
    "천칭자리": "♎", "전갈자리": "♏", "사수자리": "♐",
    "염소자리": "♑", "물병자리": "♒", "물고기자리": "♓",
}

ZODIAC_DATE_RANGES: dict[str, str] = {
    "양자리": "3/21 - 4/19",
    "황소자리": "4/20 - 5/20",
    "쌍둥이자리": "5/21 - 6/20",
    "게자리": "6/21 - 7/22",
    "사자자리": "7/23 - 8/22",
    "처녀자리": "8/23 - 9/22",
    "천칭자리": "9/23 - 10/22",
    "전갈자리": "10/23 - 11/21",
    "사수자리": "11/22 - 12/21",
    "염소자리": "12/22 - 1/19",
    "물병자리": "1/20 - 2/18",
    "물고기자리": "2/19 - 3/20",
}

# 지배 행성
ZODIAC_RULERS: dict[str, str] = {
    "양자리": "화성", "황소자리": "금성", "쌍둥이자리": "수성",
    "게자리": "달", "사자자리": "태양", "처녀자리": "수성",
    "천칭자리": "금성", "전갈자리": "명왕성", "사수자리": "목성",
    "염소자리": "토성", "물병자리": "천왕성", "물고기자리": "해왕성",
}


def _sign_info(sign_en: str, degree: float) -> dict:
    sign_ko = ZODIAC_SIGNS_KO.get(sign_en, sign_en)
    return {
        "sign_en": sign_en,
        "sign_ko": sign_ko,
        "element": ZODIAC_ELEMENTS.get(sign_ko, ""),
        "modality": ZODIAC_MODALITIES.get(sign_ko, ""),
        "symbol": ZODIAC_SYMBOLS.get(sign_ko, ""),
        "date_range": ZODIAC_DATE_RANGES.get(sign_ko, ""),
        "ruler": ZODIAC_RULERS.get(sign_ko, ""),
        "degree": round(degree, 2),
    }


def calculate_zodiac(
    birth_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: int,
    birth_minute: int,
    latitude: float,
    longitude: float,
    timezone: str = "Asia/Seoul",
) -> dict:
    """
    태양궁 / 달궁 / 상승궁 계산
    latitude: 위도 (양수 = 북위)
    longitude: 경도 (양수 = 동경)
    timezone: IANA 타임존 문자열 (예: "Asia/Seoul")
    """
    subject = AstrologicalSubject(
        name="User",
        year=birth_year,
        month=birth_month,
        day=birth_day,
        hour=birth_hour,
        minute=birth_minute,
        lng=longitude,
        lat=latitude,
        tz_str=timezone,
        online=False,
    )

    # kerykeion 4.x: subject.sun.sign / subject.sun.position
    # kerykeion 3.x: subject.sun["sign"]
    try:
        sun_sign = subject.sun.sign
        sun_deg = float(subject.sun.position)
        moon_sign = subject.moon.sign
        moon_deg = float(subject.moon.position)
        asc_sign = subject.first_house.sign
        asc_deg = float(subject.first_house.position)
    except AttributeError:
        sun_sign = subject.sun["sign"]
        sun_deg = float(subject.sun.get("position", 0))
        moon_sign = subject.moon["sign"]
        moon_deg = float(subject.moon.get("position", 0))
        asc_sign = subject.first_house["sign"]
        asc_deg = float(subject.first_house.get("position", 0))

    return {
        "sun": _sign_info(sun_sign, sun_deg),
        "moon": _sign_info(moon_sign, moon_deg),
        "ascendant": _sign_info(asc_sign, asc_deg),
    }
