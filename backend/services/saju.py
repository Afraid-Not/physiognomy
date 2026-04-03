"""
사주팔자 계산 서비스
lunar-python 기반 사주 원국 + 오행 + 십신 + 용신 + 대운 계산
한국어 매핑 + 한국 표준시 보정 포함
"""

from dataclasses import dataclass, field
from lunar_python import Solar, EightChar


# ══════════════════════════════════════════════════
# 한국어 매핑
# ══════════════════════════════════════════════════

# 천간 (天干) 10개
GAN_KO = {
    "甲": "갑", "乙": "을", "丙": "병", "丁": "정", "戊": "무",
    "己": "기", "庚": "경", "辛": "신", "壬": "임", "癸": "계",
}

# 지지 (地支) 12개
ZHI_KO = {
    "子": "자", "丑": "축", "寅": "인", "卯": "묘", "辰": "진", "巳": "사",
    "午": "오", "未": "미", "申": "신", "酉": "유", "戌": "술", "亥": "해",
}

# 간지 전체 매핑 (예: "甲子" -> "갑자")
_ganzhi_cache: dict[str, str] = {}


def _to_ko(ganzhi: str) -> str:
    """중국어 간지 -> 한국어 간지"""
    if ganzhi in _ganzhi_cache:
        return _ganzhi_cache[ganzhi]
    result = "".join(GAN_KO.get(c, ZHI_KO.get(c, c)) for c in ganzhi)
    _ganzhi_cache[ganzhi] = result
    return result


# 오행 매핑
GAN_ELEMENT = {
    "갑": "목", "을": "목", "병": "화", "정": "화", "무": "토",
    "기": "토", "경": "금", "신": "금", "임": "수", "계": "수",
}

ZHI_ELEMENT = {
    "자": "수", "축": "토", "인": "목", "묘": "목", "진": "토", "사": "화",
    "오": "화", "미": "토", "신": "금", "유": "금", "술": "토", "해": "수",
}

# 지지 지장간 (숨은 천간)
ZHI_HIDDEN_GANS = {
    "자": ["계"],
    "축": ["기", "계", "신"],
    "인": ["갑", "병", "무"],
    "묘": ["을"],
    "진": ["무", "을", "계"],
    "사": ["병", "경", "무"],
    "오": ["정", "기"],
    "미": ["기", "정", "을"],
    "신": ["경", "임", "무"],
    "유": ["신"],
    "술": ["무", "신", "정"],
    "해": ["임", "갑"],
}

# 음양 매핑
GAN_YINYANG = {
    "갑": "양", "을": "음", "병": "양", "정": "음", "무": "양",
    "기": "음", "경": "양", "신": "음", "임": "양", "계": "음",
}

# 십신 (十神) 관계 테이블
# 일간 기준 오행과 다른 간의 오행 비교
SIPSIN_TABLE = {
    # (일간음양 == 대상음양, 오행관계) -> 십신명
    # 오행관계: same=비겁, generates=식상, generated_by=인성, controls=재성, controlled_by=관성
    ("same", True): "비견",
    ("same", False): "겁재",
    ("generates", True): "식신",
    ("generates", False): "상관",
    ("generated_by", True): "편인",
    ("generated_by", False): "정인",
    ("controls", True): "편재",
    ("controls", False): "정재",
    ("controlled_by", True): "편관",
    ("controlled_by", False): "정관",
}

# 오행 상생상극
GENERATES = {"목": "화", "화": "토", "토": "금", "금": "수", "수": "목"}
CONTROLS = {"목": "토", "토": "수", "수": "화", "화": "금", "금": "목"}

# 지지 띠 동물
ZHI_ANIMAL = {
    "자": "쥐", "축": "소", "인": "호랑이", "묘": "토끼",
    "진": "용", "사": "뱀", "오": "말", "미": "양",
    "신": "원숭이", "유": "닭", "술": "개", "해": "돼지",
}

# 12운성 (포태법)
TWELVE_STAGES = [
    "장생", "목욕", "관대", "건록", "제왕", "쇠", "병", "사", "묘", "절", "태", "양"
]

# 일간별 12운성 시작 지지 (양간 기준)
TWELVE_STAGE_START = {
    "갑": "해", "을": "오", "병": "인", "정": "유", "무": "인",
    "기": "유", "경": "사", "신": "자", "임": "신", "계": "묘",
}

ZHI_ORDER = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]


# ══════════════════════════════════════════════════
# 한국 표준시 보정
# ══════════════════════════════════════════════════

# 한국 서머타임 기간 (1948~1988, UTC+10 적용 기간)
# (start_month, start_day, end_month, end_day) - 대략적 범위
_SUMMER_TIME_YEARS = {
    1948: (6, 1, 9, 12),
    1949: (4, 3, 9, 10),
    1950: (4, 1, 9, 9),
    1951: (5, 6, 9, 8),
    1955: (5, 5, 9, 8),
    1956: (5, 20, 9, 29),
    1957: (5, 5, 9, 21),
    1958: (5, 4, 9, 20),
    1959: (5, 3, 9, 19),
    1960: (5, 1, 9, 17),
    1961: (8, 10, 12, 31),  # 표준시 변경 과도기
    1987: (5, 10, 10, 11),
    1988: (5, 8, 10, 9),
}


def _adjust_korea_time(year: int, month: int, day: int, hour: int, minute: int = 0) -> tuple[int, int, int, int, int]:
    """
    한국 표준시 → 사주 계산용 태양시(진태양시) 보정

    1. 1954-03-21 ~ 1961-08-09: UTC+8:30 시기 -> 30분 더함 (UTC+9 기준으로 보정)
    2. 서머타임 적용 기간: 1시간 빼기
    3. 경도 보정: 한국 127.5°E 기준, UTC+9(135°E)와 30분 차이 -> 30분 빼기
       (사주 전문가마다 의견 다름 - 여기선 적용)
    """
    total_minutes = hour * 60 + minute

    # 서머타임 보정 (-60분)
    if year in _SUMMER_TIME_YEARS:
        sm, sd, em, ed = _SUMMER_TIME_YEARS[year]
        if (month > sm or (month == sm and day >= sd)) and (month < em or (month == em and day <= ed)):
            total_minutes -= 60

    # 1954-03-21 ~ 1961-08-09: UTC+8:30 시기 (+30분으로 UTC+9 기준 맞춤)
    if (1954, 3, 21) <= (year, month, day) <= (1961, 8, 9):
        total_minutes += 30

    # 경도 보정: 135°E(UTC+9) → 127.5°E (한국 평균) = -30분
    total_minutes -= 30

    # 날짜 넘김 처리
    if total_minutes < 0:
        total_minutes += 1440
        # 전날로 (간단한 처리 - Solar 객체가 알아서 처리)
        day -= 1
        if day < 1:
            month -= 1
            if month < 1:
                year -= 1
                month = 12
            day = 31  # Solar가 보정해줌
    elif total_minutes >= 1440:
        total_minutes -= 1440
        day += 1

    new_hour = total_minutes // 60
    new_minute = total_minutes % 60
    return year, month, day, new_hour, new_minute


# ══════════════════════════════════════════════════
# 십신 계산
# ══════════════════════════════════════════════════

def _get_element_relation(day_element: str, target_element: str) -> str:
    """일간 오행과 대상 오행의 관계"""
    if day_element == target_element:
        return "same"
    if GENERATES.get(day_element) == target_element:
        return "generates"
    if GENERATES.get(target_element) == day_element:
        return "generated_by"
    if CONTROLS.get(day_element) == target_element:
        return "controls"
    return "controlled_by"


def _get_sipsin(day_gan: str, target_gan: str) -> str:
    """일간 기준 대상 천간의 십신"""
    day_elem = GAN_ELEMENT[day_gan]
    target_elem = GAN_ELEMENT[target_gan]
    relation = _get_element_relation(day_elem, target_elem)
    same_yinyang = GAN_YINYANG[day_gan] == GAN_YINYANG[target_gan]
    return SIPSIN_TABLE[(relation, same_yinyang)]


def _get_twelve_stage(day_gan: str, zhi: str) -> str:
    """일간 기준 지지의 12운성"""
    start_zhi = TWELVE_STAGE_START[day_gan]
    start_idx = ZHI_ORDER.index(start_zhi)
    target_idx = ZHI_ORDER.index(zhi)

    is_yang = GAN_YINYANG[day_gan] == "양"
    if is_yang:
        offset = (target_idx - start_idx) % 12
    else:
        offset = (start_idx - target_idx) % 12

    return TWELVE_STAGES[offset]


# ══════════════════════════════════════════════════
# 용신 판단
# ══════════════════════════════════════════════════

def _determine_yongsin(element_counts: dict[str, int], day_element: str) -> dict:
    """
    오행 균형 기반 용신/희신 판단 (간략화)
    일간 오행의 강약을 판단하고, 부족한 오행을 용신으로 설정
    """
    total = sum(element_counts.values())
    day_count = element_counts.get(day_element, 0)

    # 일간 강약 판단
    # 일간과 같은 오행 + 일간을 생하는 오행 = 아군
    generating_element = [k for k, v in GENERATES.items() if v == day_element][0]
    ally_count = day_count + element_counts.get(generating_element, 0)

    is_strong = ally_count > total / 2

    if is_strong:
        # 신강: 설기(식상), 재성, 관성이 용신
        yongsin_element = GENERATES[day_element]  # 식상 (설기)
        heesin_element = GENERATES[yongsin_element]  # 재성
        description = "신강(身强) - 일간의 기운이 강하여 설기가 필요합니다"
    else:
        # 신약: 인성, 비겁이 용신
        yongsin_element = generating_element  # 인성 (생아)
        heesin_element = day_element  # 비겁
        description = "신약(身弱) - 일간의 기운이 약하여 도움이 필요합니다"

    return {
        "is_strong": is_strong,
        "strength": "신강" if is_strong else "신약",
        "description": description,
        "yongsin": yongsin_element,
        "heesin": heesin_element,
        "yongsin_label": f"용신: {yongsin_element}({_element_hanja(yongsin_element)})",
        "heesin_label": f"희신: {heesin_element}({_element_hanja(heesin_element)})",
    }


def _element_hanja(element: str) -> str:
    return {"목": "木", "화": "火", "토": "土", "금": "金", "수": "水"}[element]


# ══════════════════════════════════════════════════
# 메인 분석 함수
# ══════════════════════════════════════════════════

@dataclass
class Pillar:
    """사주 한 기둥"""
    gan: str          # 천간 (한국어)
    zhi: str          # 지지 (한국어)
    ganzhi: str       # 간지 (한국어)
    gan_element: str  # 천간 오행
    zhi_element: str  # 지지 오행
    gan_yinyang: str  # 천간 음양
    sipsin: str       # 십신 (일간 기준)
    twelve_stage: str  # 12운성 (일간 기준)
    hidden_gans: list[dict] = field(default_factory=list)  # 지장간


@dataclass
class SajuResult:
    """사주 분석 전체 결과"""
    # 입력 정보
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    birth_minute: int
    gender: str  # "male" or "female"
    lunar_date: str

    # 사주 원국 (4기둥)
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar

    # 오행 분석
    element_counts: dict[str, int]
    element_percentages: dict[str, float]
    day_element: str

    # 용신
    yongsin: dict

    # 십신 요약
    sipsin_summary: dict[str, int]

    # 대운
    dayun_list: list[dict]

    # 띠
    animal: str

    def to_dict(self) -> dict:
        return {
            "birth_info": {
                "year": self.birth_year,
                "month": self.birth_month,
                "day": self.birth_day,
                "hour": self.birth_hour,
                "minute": self.birth_minute,
                "gender": self.gender,
                "lunar_date": self.lunar_date,
                "animal": self.animal,
            },
            "pillars": {
                "year": _pillar_dict(self.year_pillar),
                "month": _pillar_dict(self.month_pillar),
                "day": _pillar_dict(self.day_pillar),
                "hour": _pillar_dict(self.hour_pillar),
            },
            "elements": {
                "counts": self.element_counts,
                "percentages": self.element_percentages,
                "day_element": self.day_element,
            },
            "yongsin": self.yongsin,
            "sipsin_summary": self.sipsin_summary,
            "dayun": self.dayun_list,
        }


def _pillar_dict(p: Pillar) -> dict:
    return {
        "gan": p.gan,
        "zhi": p.zhi,
        "ganzhi": p.ganzhi,
        "gan_element": p.gan_element,
        "zhi_element": p.zhi_element,
        "gan_yinyang": p.gan_yinyang,
        "sipsin": p.sipsin,
        "twelve_stage": p.twelve_stage,
        "hidden_gans": p.hidden_gans,
    }


def analyze_saju(
    year: int, month: int, day: int,
    hour: int, minute: int = 0,
    gender: str = "male",
    apply_timezone_correction: bool = True,
) -> SajuResult:
    """
    생년월일시 → 사주팔자 분석 결과

    Parameters:
        year, month, day, hour, minute: 양력 생년월일시
        gender: "male" or "female"
        apply_timezone_correction: 한국 표준시 보정 적용 여부
    """
    # 표준시 보정
    if apply_timezone_correction:
        y, m, d, h, mi = _adjust_korea_time(year, month, day, hour, minute)
    else:
        y, m, d, h, mi = year, month, day, hour, minute

    # lunar-python 사주 계산
    solar = Solar.fromYmdHms(y, m, d, h, mi, 0)
    lunar = solar.getLunar()
    eight = lunar.getEightChar()

    # 한국어 간지 변환
    year_gz = _to_ko(eight.getYear())
    month_gz = _to_ko(eight.getMonth())
    day_gz = _to_ko(eight.getDay())
    hour_gz = _to_ko(eight.getTime())

    year_gan, year_zhi = year_gz[0], year_gz[1]
    month_gan, month_zhi = month_gz[0], month_gz[1]
    day_gan, day_zhi = day_gz[0], day_gz[1]
    hour_gan, hour_zhi = hour_gz[0], hour_gz[1]

    # 십신 계산 (일간 기준)
    def make_pillar(gan: str, zhi: str, ganzhi: str) -> Pillar:
        sipsin = _get_sipsin(day_gan, gan)
        twelve_stage = _get_twelve_stage(day_gan, zhi)
        hidden = []
        for hg in ZHI_HIDDEN_GANS.get(zhi, []):
            hidden.append({
                "gan": hg,
                "element": GAN_ELEMENT[hg],
                "sipsin": _get_sipsin(day_gan, hg),
            })
        return Pillar(
            gan=gan, zhi=zhi, ganzhi=ganzhi,
            gan_element=GAN_ELEMENT[gan],
            zhi_element=ZHI_ELEMENT[zhi],
            gan_yinyang=GAN_YINYANG[gan],
            sipsin=sipsin,
            twelve_stage=twelve_stage,
            hidden_gans=hidden,
        )

    yp = make_pillar(year_gan, year_zhi, year_gz)
    mp = make_pillar(month_gan, month_zhi, month_gz)
    dp = make_pillar(day_gan, day_zhi, day_gz)
    hp = make_pillar(hour_gan, hour_zhi, hour_gz)

    # 오행 집계 (천간 4 + 지지 4 = 8글자)
    all_elements = [
        GAN_ELEMENT[year_gan], GAN_ELEMENT[month_gan],
        GAN_ELEMENT[day_gan], GAN_ELEMENT[hour_gan],
        ZHI_ELEMENT[year_zhi], ZHI_ELEMENT[month_zhi],
        ZHI_ELEMENT[day_zhi], ZHI_ELEMENT[hour_zhi],
    ]
    element_counts = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
    for e in all_elements:
        element_counts[e] += 1
    total = sum(element_counts.values())
    element_pct = {k: round(v / total * 100, 1) for k, v in element_counts.items()}

    # 용신 판단
    yongsin = _determine_yongsin(element_counts, GAN_ELEMENT[day_gan])

    # 십신 요약
    sipsin_counts: dict[str, int] = {}
    for p in [yp, mp, dp, hp]:
        sipsin_counts[p.sipsin] = sipsin_counts.get(p.sipsin, 0) + 1
        for hg in p.hidden_gans:
            sipsin_counts[hg["sipsin"]] = sipsin_counts.get(hg["sipsin"], 0) + 1

    # 대운 계산
    is_male = 1 if gender == "male" else 0
    yun = eight.getYun(is_male)
    dayun_list = []
    for da_yun in yun.getDaYun():
        gz = da_yun.getGanZhi()
        if not gz:  # 첫 번째 (현재 대운 전)
            continue
        ko_gz = _to_ko(gz)
        dayun_list.append({
            "start_age": da_yun.getStartAge(),
            "end_age": da_yun.getEndAge(),
            "ganzhi": ko_gz,
            "gan": ko_gz[0],
            "zhi": ko_gz[1],
            "gan_element": GAN_ELEMENT[ko_gz[0]],
            "zhi_element": ZHI_ELEMENT[ko_gz[1]],
            "sipsin": _get_sipsin(day_gan, ko_gz[0]),
        })

    # 음력 날짜 (한국어 표시용)
    lunar_year = lunar.getYear()
    lunar_month = abs(lunar.getMonth())
    lunar_day = lunar.getDay()
    leap_prefix = "(윤)" if lunar.getMonth() < 0 else ""
    lunar_str = f"음력 {lunar_year}년 {leap_prefix}{lunar_month}월 {lunar_day}일"

    # 띠
    animal = ZHI_ANIMAL[year_zhi]

    return SajuResult(
        birth_year=year, birth_month=month, birth_day=day,
        birth_hour=hour, birth_minute=minute,
        gender=gender,
        lunar_date=lunar_str,
        year_pillar=yp, month_pillar=mp, day_pillar=dp, hour_pillar=hp,
        element_counts=element_counts,
        element_percentages=element_pct,
        day_element=GAN_ELEMENT[day_gan],
        yongsin=yongsin,
        sipsin_summary=sipsin_counts,
        dayun_list=dayun_list,
        animal=animal,
    )
