"""
타로 카드 데이터 + 쓰리카드 스프레드 뽑기 서비스
메이저 아르카나 22장, 과거/현재/미래 3장
"""

import random
from dataclasses import dataclass, field


@dataclass
class TarotCard:
    number: int
    name_ko: str
    name_en: str
    upright: str          # 정방향 키워드
    reversed: str         # 역방향 키워드
    element: str          # 연관 원소 (풍/화/수/토)
    traits: dict[str, float] = field(default_factory=dict)  # hero matching traits
    meanings: dict[str, dict[str, str]] = field(default_factory=dict)  # 카테고리별 정/역 해석


@dataclass
class DrawnCard:
    card: TarotCard
    position: str         # "과거" | "현재" | "미래"
    is_reversed: bool

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "card_number": self.card.number,
            "card_name": self.card.name_ko,
            "card_name_en": self.card.name_en,
            "is_reversed": self.is_reversed,
            "upright_keywords": self.card.upright,
            "reversed_keywords": self.card.reversed,
            "element": self.card.element,
            "meaning": self.card.meanings.get(
                _current_category, {}
            ).get("reversed" if self.is_reversed else "upright", ""),
            "traits": self.card.traits,
        }


@dataclass
class TarotSpread:
    category: str         # "연애" | "재물" | "직업" | "건강" | "오늘의 운세"
    cards: list[DrawnCard]

    def to_dict(self) -> dict:
        global _current_category
        _current_category = self.category
        return {
            "category": self.category,
            "cards": [c.to_dict() for c in self.cards],
        }


# 카테고리별 meaning 접근용 임시 변수
_current_category: str = ""

CATEGORIES = ["연애", "재물", "직업", "건강", "오늘의 운세"]

# ── 22장 메이저 아르카나 ──

MAJOR_ARCANA: list[TarotCard] = [
    TarotCard(
        number=0, name_ko="바보", name_en="The Fool",
        upright="새로운 시작, 자유, 순수, 모험",
        reversed="무모함, 경솔, 방향 상실",
        element="풍",
        traits={"creativity": 0.9, "charm": 0.7, "wisdom": 0.3, "career": 0.4, "wealth": 0.3},
        meanings={
            "연애": {"upright": "설레는 새 만남이나 관계의 새 시작이 다가옵니다. 두려움 없이 마음을 열어보세요.", "reversed": "감정에 솔직하지 못하거나 경솔한 판단으로 관계가 흔들릴 수 있습니다."},
            "재물": {"upright": "새로운 투자 기회나 수입원이 나타날 수 있습니다. 과감하게 시도해보세요.", "reversed": "충동적인 소비나 무계획적 투자에 주의하세요."},
            "직업": {"upright": "새로운 커리어 방향이나 프로젝트가 기다리고 있습니다. 도전을 두려워하지 마세요.", "reversed": "방향성 없이 이직이나 전환을 서두르면 후회할 수 있습니다."},
            "건강": {"upright": "활력이 넘치고 새로운 건강 습관을 시작하기 좋은 때입니다.", "reversed": "무리한 활동이나 건강 관리 소홀에 주의하세요."},
            "오늘의 운세": {"upright": "오늘은 새로운 시작에 좋은 날입니다. 열린 마음으로 기회를 맞이하세요.", "reversed": "성급한 결정을 피하고, 한 번 더 생각해보는 여유가 필요합니다."},
        },
    ),
    TarotCard(
        number=1, name_ko="마법사", name_en="The Magician",
        upright="의지력, 창조, 자신감, 집중",
        reversed="속임수, 미숙함, 능력 낭비",
        element="풍",
        traits={"creativity": 0.9, "wisdom": 0.8, "career": 0.8, "leadership": 0.7, "technical": 0.8},
        meanings={
            "연애": {"upright": "당신의 매력이 빛나는 시기입니다. 적극적으로 마음을 표현하면 좋은 결과가 있습니다.", "reversed": "겉과 속이 다른 상대를 조심하세요. 진실된 감정인지 확인이 필요합니다."},
            "재물": {"upright": "재능과 능력을 활용해 수입을 늘릴 수 있는 기회가 옵니다.", "reversed": "과대평가된 투자나 사기에 주의하세요. 꼼꼼한 확인이 필요합니다."},
            "직업": {"upright": "당신의 전문성이 인정받는 시기입니다. 새 프로젝트에서 주도적 역할을 맡게 됩니다.", "reversed": "능력을 제대로 발휘하지 못하고 있습니다. 집중력을 되찾으세요."},
            "건강": {"upright": "정신적 에너지가 충만합니다. 새로운 건강법을 배우기 좋은 때입니다.", "reversed": "스트레스로 인한 집중력 저하에 주의하세요."},
            "오늘의 운세": {"upright": "의지와 집중력이 강한 날입니다. 중요한 일을 추진하기 좋습니다.", "reversed": "계획이 흐트러지기 쉬운 날입니다. 본질에 집중하세요."},
        },
    ),
    TarotCard(
        number=2, name_ko="여사제", name_en="The High Priestess",
        upright="직관, 지혜, 내면의 소리, 비밀",
        reversed="억압된 감정, 표면적 판단, 비밀 노출",
        element="수",
        traits={"wisdom": 0.9, "balance": 0.7, "charm": 0.6, "support": 0.6, "creativity": 0.5},
        meanings={
            "연애": {"upright": "직관을 믿으세요. 상대의 진심이 느껴질 때 그 감각을 따르면 됩니다.", "reversed": "감정을 숨기거나 직관을 무시하면 오해가 생길 수 있습니다."},
            "재물": {"upright": "당장 눈에 보이지 않는 기회가 있습니다. 직감을 따르되 신중하게 판단하세요.", "reversed": "숨겨진 비용이나 보이지 않는 손실에 주의하세요."},
            "직업": {"upright": "조용히 실력을 쌓는 시기입니다. 때가 되면 자연스럽게 인정받게 됩니다.", "reversed": "중요한 정보를 놓치고 있을 수 있습니다. 주변을 잘 살피세요."},
            "건강": {"upright": "명상이나 요가 등 내면의 평화를 찾는 활동이 도움됩니다.", "reversed": "무시해온 건강 신호에 귀를 기울이세요."},
            "오늘의 운세": {"upright": "직관이 예리한 날입니다. 내면의 소리에 귀 기울이세요.", "reversed": "겉보기에 속지 말고 본질을 파악하려 노력하세요."},
        },
    ),
    TarotCard(
        number=3, name_ko="여황제", name_en="The Empress",
        upright="풍요, 모성, 아름다움, 자연",
        reversed="과보호, 의존, 창조력 저하",
        element="토",
        traits={"charm": 0.9, "wealth": 0.8, "love": 0.9, "support": 0.8, "balance": 0.7},
        meanings={
            "연애": {"upright": "사랑이 풍요로운 시기입니다. 따뜻한 감정이 오가고 관계가 깊어집니다.", "reversed": "과도한 집착이나 의존이 관계를 질식시킬 수 있습니다."},
            "재물": {"upright": "물질적 풍요가 다가옵니다. 투자나 사업에서 결실을 맺을 때입니다.", "reversed": "사치나 과소비에 주의하세요. 절제가 필요한 시기입니다."},
            "직업": {"upright": "창의적인 프로젝트에서 좋은 성과를 거둡니다. 협업이 특히 유리합니다.", "reversed": "창의력이 막혀 있다면 환경을 바꿔보세요."},
            "건강": {"upright": "건강 상태가 좋고 활력이 넘칩니다. 자연 속 활동이 도움됩니다.", "reversed": "과식이나 과음에 주의하세요. 절제된 생활이 필요합니다."},
            "오늘의 운세": {"upright": "풍요롭고 따뜻한 하루가 될 것입니다. 주변 사람들과의 교류를 즐기세요.", "reversed": "남에게 너무 많이 베풀다가 자신이 지칠 수 있습니다."},
        },
    ),
    TarotCard(
        number=4, name_ko="황제", name_en="The Emperor",
        upright="권위, 안정, 구조, 리더십",
        reversed="독재, 경직, 통제욕",
        element="화",
        traits={"leadership": 0.9, "authority": 0.9, "career": 0.9, "wealth": 0.8, "business": 0.8},
        meanings={
            "연애": {"upright": "안정적이고 든든한 관계를 만들 수 있습니다. 책임감 있는 태도가 매력입니다.", "reversed": "지나친 통제욕이 관계를 경직시킬 수 있습니다. 상대를 존중하세요."},
            "재물": {"upright": "체계적인 재무 관리로 안정적인 자산을 쌓을 수 있습니다.", "reversed": "과도한 통제나 보수적 접근이 기회를 놓치게 할 수 있습니다."},
            "직업": {"upright": "승진이나 리더 역할을 맡을 기회가 옵니다. 자신감을 가지세요.", "reversed": "너무 경직된 방식은 팀원과의 갈등을 초래합니다."},
            "건강": {"upright": "규칙적인 생활과 운동으로 건강을 유지하기 좋은 때입니다.", "reversed": "과로나 스트레스를 방치하면 건강이 악화될 수 있습니다."},
            "오늘의 운세": {"upright": "리더십을 발휘할 기회가 있는 날입니다. 결단력 있게 행동하세요.", "reversed": "너무 고집을 부리면 주변과 마찰이 생길 수 있습니다."},
        },
    ),
    TarotCard(
        number=5, name_ko="교황", name_en="The Hierophant",
        upright="전통, 가르침, 신뢰, 도덕",
        reversed="독단, 형식주의, 새로운 시각 필요",
        element="토",
        traits={"wisdom": 0.9, "support": 0.8, "authority": 0.7, "balance": 0.7, "leadership": 0.6},
        meanings={
            "연애": {"upright": "진지한 만남이나 결혼 등 전통적인 관계 발전이 기대됩니다.", "reversed": "형식에 얽매인 관계에서 벗어나 진정한 감정을 찾아보세요."},
            "재물": {"upright": "안정적이고 검증된 방법으로 재물을 모으는 것이 좋습니다.", "reversed": "관습적인 방법만 고집하면 새로운 기회를 놓칩니다."},
            "직업": {"upright": "멘토나 선배의 조언이 큰 도움이 됩니다. 배움의 자세를 가지세요.", "reversed": "기존 방식에만 의존하지 말고 새로운 접근을 시도해보세요."},
            "건강": {"upright": "전문가의 조언을 따르는 것이 좋습니다. 정기 검진을 받아보세요.", "reversed": "건강에 대한 잘못된 상식이나 미신에 의존하지 마세요."},
            "오늘의 운세": {"upright": "조언을 구하기 좋은 날입니다. 경험 많은 사람의 이야기에 귀 기울이세요.", "reversed": "남의 말에 휘둘리지 말고 자신의 판단도 중요합니다."},
        },
    ),
    TarotCard(
        number=6, name_ko="연인", name_en="The Lovers",
        upright="사랑, 조화, 선택, 유대",
        reversed="불화, 유혹, 잘못된 선택",
        element="풍",
        traits={"love": 0.95, "charm": 0.9, "balance": 0.7, "creativity": 0.5, "support": 0.6},
        meanings={
            "연애": {"upright": "운명적인 만남이나 깊은 사랑의 시기입니다. 진정한 소울메이트를 만날 수 있습니다.", "reversed": "갈등이나 유혹에 빠질 수 있습니다. 진정으로 원하는 것이 무엇인지 생각해보세요."},
            "재물": {"upright": "파트너십을 통한 재물 운이 좋습니다. 합작 투자를 고려해보세요.", "reversed": "금전 문제로 인한 관계 갈등에 주의하세요."},
            "직업": {"upright": "협업이나 파트너십이 빛을 발하는 시기입니다. 좋은 동료를 만납니다.", "reversed": "직장 내 인간관계 갈등에 주의하세요. 선택의 기로에 설 수 있습니다."},
            "건강": {"upright": "마음의 안정이 신체 건강에도 좋은 영향을 줍니다.", "reversed": "감정적 스트레스가 건강에 악영향을 미칠 수 있습니다."},
            "오늘의 운세": {"upright": "사랑과 조화가 가득한 날입니다. 소중한 사람과 시간을 보내세요.", "reversed": "중요한 선택 앞에서 감정에 휩쓸리지 않도록 주의하세요."},
        },
    ),
    TarotCard(
        number=7, name_ko="전차", name_en="The Chariot",
        upright="승리, 의지, 전진, 결단",
        reversed="방향 상실, 공격성, 좌절",
        element="수",
        traits={"career": 0.9, "leadership": 0.8, "authority": 0.7, "business": 0.7, "technical": 0.5},
        meanings={
            "연애": {"upright": "적극적으로 다가가면 좋은 결과가 있습니다. 망설이지 마세요.", "reversed": "너무 밀어붙이면 역효과가 날 수 있습니다. 상대의 속도를 존중하세요."},
            "재물": {"upright": "강한 의지로 목표한 재물을 달성할 수 있습니다. 추진력이 중요합니다.", "reversed": "무리한 투자나 성급한 결정이 손실로 이어질 수 있습니다."},
            "직업": {"upright": "승진이나 성과를 이루는 시기입니다. 자신감을 갖고 밀고 나가세요.", "reversed": "과도한 경쟁심이 동료와의 관계를 해칠 수 있습니다."},
            "건강": {"upright": "체력이 좋고 운동 목표를 달성하기 좋은 시기입니다.", "reversed": "무리한 운동이나 과로에 주의하세요."},
            "오늘의 운세": {"upright": "목표를 향해 힘차게 전진할 수 있는 날입니다. 승리가 가까이 있습니다.", "reversed": "너무 서두르면 방향을 잃을 수 있습니다. 잠시 멈추고 점검하세요."},
        },
    ),
    TarotCard(
        number=8, name_ko="힘", name_en="Strength",
        upright="용기, 인내, 내면의 힘, 자기 통제",
        reversed="자기 의심, 나약함, 분노 폭발",
        element="화",
        traits={"balance": 0.8, "leadership": 0.7, "support": 0.7, "wisdom": 0.6, "career": 0.6},
        meanings={
            "연애": {"upright": "부드러운 강인함으로 관계를 이끌 수 있습니다. 인내가 사랑을 깊게 합니다.", "reversed": "감정 조절이 어려워 관계에 금이 갈 수 있습니다."},
            "재물": {"upright": "꾸준한 노력이 결실을 맺습니다. 인내심을 갖고 기다리세요.", "reversed": "조급함이 잘못된 재무 결정으로 이어질 수 있습니다."},
            "직업": {"upright": "어려운 상황에서도 침착하게 대처하면 인정받게 됩니다.", "reversed": "자신감 부족으로 기회를 놓칠 수 있습니다. 용기를 가지세요."},
            "건강": {"upright": "정신력이 강한 시기입니다. 꾸준한 운동 습관이 큰 효과를 발휘합니다.", "reversed": "스트레스를 억지로 참지 말고 적절히 해소하세요."},
            "오늘의 운세": {"upright": "내면의 힘이 빛나는 날입니다. 자신을 믿고 도전하세요.", "reversed": "자기 의심에 빠지기 쉬운 날입니다. 작은 성공에서 자신감을 찾으세요."},
        },
    ),
    TarotCard(
        number=9, name_ko="은둔자", name_en="The Hermit",
        upright="성찰, 고독, 내면 탐구, 지혜 추구",
        reversed="고립, 외로움, 현실 회피",
        element="토",
        traits={"wisdom": 0.95, "technical": 0.7, "balance": 0.6, "creativity": 0.5, "support": 0.3},
        meanings={
            "연애": {"upright": "혼자만의 시간이 필요한 때입니다. 자신을 먼저 이해해야 진정한 사랑을 만납니다.", "reversed": "지나친 고립이 외로움을 키울 수 있습니다. 마음을 열어보세요."},
            "재물": {"upright": "조용히 공부하고 연구하는 것이 장기적 재물 운에 도움됩니다.", "reversed": "현실을 직시하지 않으면 재정 상황이 악화될 수 있습니다."},
            "직업": {"upright": "혼자 깊이 연구하거나 전문성을 키우기 좋은 시기입니다.", "reversed": "팀워크를 무시하면 고립될 수 있습니다. 소통을 잊지 마세요."},
            "건강": {"upright": "심신 안정을 위한 명상이나 산책이 도움됩니다.", "reversed": "사회적 고립이 정신 건강에 부정적 영향을 줄 수 있습니다."},
            "오늘의 운세": {"upright": "내면을 돌아보기 좋은 날입니다. 조용한 시간이 큰 깨달음을 줍니다.", "reversed": "너무 자신만의 세계에 갇히지 마세요. 밖으로 나가보세요."},
        },
    ),
    TarotCard(
        number=10, name_ko="운명의 수레바퀴", name_en="Wheel of Fortune",
        upright="행운, 변화, 전환점, 운명",
        reversed="불운, 저항, 통제 불능",
        element="화",
        traits={"wealth": 0.8, "career": 0.7, "charm": 0.6, "balance": 0.5, "creativity": 0.6},
        meanings={
            "연애": {"upright": "운명적인 만남이나 관계의 전환점이 찾아옵니다.", "reversed": "변화에 저항하면 관계가 정체될 수 있습니다."},
            "재물": {"upright": "재물 운이 상승하는 시기입니다. 기회를 놓치지 마세요.", "reversed": "예상치 못한 지출이나 손실에 대비하세요."},
            "직업": {"upright": "커리어에 중요한 전환점이 옵니다. 변화를 두려워하지 마세요.", "reversed": "불확실한 상황에서 조급하게 결정하지 마세요."},
            "건강": {"upright": "건강 상태가 호전되는 시기입니다. 좋은 습관이 몸에 밸 때입니다.", "reversed": "건강 관리를 소홀히 하면 급격히 나빠질 수 있습니다."},
            "오늘의 운세": {"upright": "행운이 찾아오는 날입니다. 기회가 오면 망설이지 마세요.", "reversed": "예상치 못한 변수가 생길 수 있습니다. 유연하게 대처하세요."},
        },
    ),
    TarotCard(
        number=11, name_ko="정의", name_en="Justice",
        upright="공정, 균형, 진실, 책임",
        reversed="불공정, 편견, 회피",
        element="풍",
        traits={"authority": 0.8, "balance": 0.9, "wisdom": 0.7, "career": 0.7, "leadership": 0.6},
        meanings={
            "연애": {"upright": "공정하고 균형 잡힌 관계를 만들 수 있습니다. 서로를 존중하세요.", "reversed": "관계에서 불균형이나 불공정함을 느낄 수 있습니다."},
            "재물": {"upright": "정당한 노력에 대한 보상이 따릅니다. 공정한 거래를 하세요.", "reversed": "불공정한 계약이나 손해를 볼 수 있으니 서류를 꼼꼼히 확인하세요."},
            "직업": {"upright": "정당한 평가를 받게 됩니다. 공정하게 행동하면 인정받습니다.", "reversed": "직장 내 불공정한 대우에 대해 목소리를 낼 필요가 있습니다."},
            "건강": {"upright": "생활의 균형이 건강의 핵심입니다. 일과 휴식의 밸런스를 맞추세요.", "reversed": "편향된 생활 습관이 건강을 해칠 수 있습니다."},
            "오늘의 운세": {"upright": "공정하고 올바른 판단을 할 수 있는 날입니다.", "reversed": "편견 없이 상황을 바라보려 노력하세요."},
        },
    ),
    TarotCard(
        number=12, name_ko="매달린 사람", name_en="The Hanged Man",
        upright="희생, 새 관점, 기다림, 내려놓음",
        reversed="무의미한 희생, 지연, 이기심",
        element="수",
        traits={"wisdom": 0.7, "balance": 0.5, "creativity": 0.6, "support": 0.5, "charm": 0.3},
        meanings={
            "연애": {"upright": "잠시 멈추고 관계를 다른 시각으로 바라보세요. 새로운 이해가 생깁니다.", "reversed": "무의미한 기다림에 시간을 낭비하고 있을 수 있습니다."},
            "재물": {"upright": "당장의 이익보다 장기적 관점에서 판단하는 것이 유리합니다.", "reversed": "지연되는 수입에 좌절하지 마세요. 하지만 현실적 대안도 필요합니다."},
            "직업": {"upright": "다른 관점에서 문제를 바라보면 해결책이 보입니다. 발상의 전환이 필요합니다.", "reversed": "정체된 상황에서 벗어나려면 적극적인 행동이 필요합니다."},
            "건강": {"upright": "휴식이 필요한 시기입니다. 몸이 보내는 신호에 귀 기울이세요.", "reversed": "건강 문제를 방치하면 악화될 수 있습니다."},
            "오늘의 운세": {"upright": "서두르지 말고 기다리는 것이 현명한 날입니다.", "reversed": "답답한 상황이지만, 포기보다는 관점을 바꿔보세요."},
        },
    ),
    TarotCard(
        number=13, name_ko="죽음", name_en="Death",
        upright="변환, 끝과 시작, 재탄생, 전환",
        reversed="변화 거부, 정체, 집착",
        element="수",
        traits={"creativity": 0.6, "wisdom": 0.5, "balance": 0.4, "authority": 0.3, "charm": 0.2},
        meanings={
            "연애": {"upright": "관계의 큰 변화가 옵니다. 끝남이 곧 새로운 시작일 수 있습니다.", "reversed": "끝난 관계에 집착하면 새로운 사랑을 만날 수 없습니다."},
            "재물": {"upright": "기존 수입원이 변화하지만, 새로운 기회가 열립니다.", "reversed": "변화를 거부하면 재정적 정체가 계속됩니다."},
            "직업": {"upright": "커리어의 큰 전환기입니다. 과거를 내려놓고 새 길을 받아들이세요.", "reversed": "편안한 현상 유지에 안주하면 성장이 멈춥니다."},
            "건강": {"upright": "나쁜 습관을 버리고 새로운 건강 루틴을 시작할 때입니다.", "reversed": "건강에 해로운 습관을 고치지 않으면 문제가 생깁니다."},
            "오늘의 운세": {"upright": "무언가가 끝나고 새롭게 시작하는 날입니다. 변화를 받아들이세요.", "reversed": "변화를 두려워하지 마세요. 저항할수록 힘들어집니다."},
        },
    ),
    TarotCard(
        number=14, name_ko="절제", name_en="Temperance",
        upright="균형, 조화, 인내, 절제",
        reversed="불균형, 과도함, 조급함",
        element="화",
        traits={"balance": 0.95, "wisdom": 0.7, "support": 0.7, "love": 0.6, "career": 0.6},
        meanings={
            "연애": {"upright": "서로 맞춰가는 조화로운 관계를 만들 수 있습니다. 인내가 열매를 맺습니다.", "reversed": "감정의 기복이 심해 관계에 어려움이 있을 수 있습니다."},
            "재물": {"upright": "절제된 소비와 균형 잡힌 재무 관리가 좋은 결과를 가져옵니다.", "reversed": "충동 구매나 과도한 지출에 주의하세요."},
            "직업": {"upright": "꾸준하고 균형 잡힌 업무 태도가 인정받습니다.", "reversed": "일에 치우쳐 삶의 균형이 깨질 수 있습니다."},
            "건강": {"upright": "규칙적인 생활과 적절한 운동이 건강의 비결입니다.", "reversed": "과음, 과식 등 절제력 부족이 건강을 해칩니다."},
            "오늘의 운세": {"upright": "균형과 조화를 유지하기 좋은 날입니다. 모든 것에 적당히.", "reversed": "한쪽으로 치우치기 쉬운 날입니다. 균형을 의식하세요."},
        },
    ),
    TarotCard(
        number=15, name_ko="악마", name_en="The Devil",
        upright="유혹, 집착, 물질주의, 속박",
        reversed="해방, 자각, 집착에서 벗어남",
        element="토",
        traits={"wealth": 0.6, "charm": 0.7, "business": 0.5, "authority": 0.4, "balance": 0.2},
        meanings={
            "연애": {"upright": "강렬한 끌림이 있지만 건강하지 않은 관계일 수 있습니다. 집착에 주의하세요.", "reversed": "집착에서 벗어나 자유로운 사랑을 찾게 됩니다."},
            "재물": {"upright": "물질적 욕심이 판단을 흐릴 수 있습니다. 탐욕에 빠지지 마세요.", "reversed": "재물에 대한 집착에서 벗어나면 오히려 자유로워집니다."},
            "직업": {"upright": "일에 지나치게 매여 있지 않은지 점검하세요. 번아웃 위험이 있습니다.", "reversed": "억압된 직장 환경에서 벗어날 용기를 가지세요."},
            "건강": {"upright": "중독성 있는 습관(음주, 흡연 등)에 주의하세요.", "reversed": "나쁜 습관을 끊을 수 있는 전환점이 옵니다."},
            "오늘의 운세": {"upright": "유혹에 빠지기 쉬운 날입니다. 충동적 결정을 경계하세요.", "reversed": "묶여있던 것에서 벗어나는 해방감을 느낄 수 있습니다."},
        },
    ),
    TarotCard(
        number=16, name_ko="탑", name_en="The Tower",
        upright="붕괴, 급변, 충격, 깨달음",
        reversed="변화 회피, 두려움, 서서히 무너짐",
        element="화",
        traits={"creativity": 0.4, "wisdom": 0.3, "authority": 0.2, "balance": 0.1, "career": 0.2},
        meanings={
            "연애": {"upright": "관계에 큰 충격이 올 수 있지만, 이를 통해 진실이 드러납니다.", "reversed": "불안정한 관계를 무시하면 더 큰 파국이 올 수 있습니다."},
            "재물": {"upright": "예상치 못한 재정적 타격이 있을 수 있습니다. 대비하세요.", "reversed": "서서히 악화되는 재정 상황을 방치하지 마세요."},
            "직업": {"upright": "갑작스러운 변화나 구조조정이 있을 수 있습니다. 하지만 새로운 기회이기도 합니다.", "reversed": "직장의 불안 요소를 무시하면 더 큰 문제로 발전합니다."},
            "건강": {"upright": "갑작스러운 건강 문제에 주의하세요. 검진을 받아보세요.", "reversed": "무시해온 건강 경고를 더 이상 방치하면 안 됩니다."},
            "오늘의 운세": {"upright": "예상치 못한 일이 생길 수 있지만, 그 속에서 깨달음을 얻습니다.", "reversed": "변화가 두려워도 미리 대비하는 것이 중요합니다."},
        },
    ),
    TarotCard(
        number=17, name_ko="별", name_en="The Star",
        upright="희망, 영감, 치유, 평화",
        reversed="절망, 자신감 상실, 방향 상실",
        element="풍",
        traits={"charm": 0.8, "creativity": 0.8, "love": 0.7, "wisdom": 0.7, "balance": 0.8},
        meanings={
            "연애": {"upright": "희망찬 사랑의 에너지가 가득합니다. 아름다운 만남이 기다립니다.", "reversed": "사랑에 대한 희망을 잃지 마세요. 지금은 회복의 시간입니다."},
            "재물": {"upright": "밝은 재물 전망이 보입니다. 희망을 갖고 꾸준히 노력하세요.", "reversed": "비관적 태도가 기회를 멀리 밀어낼 수 있습니다."},
            "직업": {"upright": "영감이 넘치는 시기입니다. 창의적 아이디어가 빛을 발합니다.", "reversed": "커리어에 대한 자신감을 되찾을 필요가 있습니다."},
            "건강": {"upright": "심신이 치유되는 시기입니다. 회복력이 좋아지고 있습니다.", "reversed": "정신적 피로가 누적되고 있습니다. 자기 관리가 필요합니다."},
            "오늘의 운세": {"upright": "희망과 영감이 가득한 날입니다. 꿈을 향해 한 걸음 나아가세요.", "reversed": "잠시 지치더라도 포기하지 마세요. 빛은 반드시 옵니다."},
        },
    ),
    TarotCard(
        number=18, name_ko="달", name_en="The Moon",
        upright="불안, 환상, 직관, 무의식",
        reversed="혼란 해소, 진실 발견, 두려움 극복",
        element="수",
        traits={"creativity": 0.7, "wisdom": 0.5, "charm": 0.5, "balance": 0.3, "love": 0.4},
        meanings={
            "연애": {"upright": "감정이 불안정하고 상대의 진심이 불확실합니다. 직관을 믿되 확인도 하세요.", "reversed": "오해가 풀리고 관계의 진실이 드러납니다."},
            "재물": {"upright": "재정 상황이 불투명합니다. 중요한 투자 결정은 미루는 것이 좋습니다.", "reversed": "불안했던 재정 상황이 서서히 해결됩니다."},
            "직업": {"upright": "직장에서 보이지 않는 갈등이 있을 수 있습니다. 경계를 놓지 마세요.", "reversed": "혼란스러웠던 업무 상황이 정리됩니다."},
            "건강": {"upright": "불면증이나 불안 증세에 주의하세요. 정신 건강 관리가 중요합니다.", "reversed": "심리적 불안이 해소되면서 건강이 회복됩니다."},
            "오늘의 운세": {"upright": "불안감이 느껴질 수 있는 날입니다. 감정에 휘둘리지 말고 침착하게.", "reversed": "안개가 걷히듯 상황이 명확해지는 날입니다."},
        },
    ),
    TarotCard(
        number=19, name_ko="태양", name_en="The Sun",
        upright="성공, 기쁨, 활력, 긍정",
        reversed="일시적 좌절, 자만, 에너지 저하",
        element="화",
        traits={"charm": 0.9, "career": 0.9, "wealth": 0.9, "love": 0.8, "leadership": 0.8, "creativity": 0.8},
        meanings={
            "연애": {"upright": "밝고 행복한 사랑의 시기입니다. 함께하는 모든 순간이 즐겁습니다.", "reversed": "사랑의 기쁨이 일시적으로 가려질 수 있지만, 곧 회복됩니다."},
            "재물": {"upright": "재물 운이 최고조입니다. 노력이 빛나는 보상으로 돌아옵니다.", "reversed": "과시적 소비에 주의하세요. 겸손이 부를 지킵니다."},
            "직업": {"upright": "커리어의 정점에 가까워지고 있습니다. 성과가 빛나는 시기입니다.", "reversed": "자만하지 않으면 곧 다시 빛날 수 있습니다."},
            "건강": {"upright": "활력이 넘치고 건강 상태가 매우 좋습니다. 에너지를 만끽하세요.", "reversed": "과도한 활동으로 체력이 소진될 수 있습니다. 적절한 휴식도 필요합니다."},
            "오늘의 운세": {"upright": "모든 것이 밝고 긍정적인 최고의 하루입니다. 자신감을 갖고 행동하세요.", "reversed": "약간의 흐림이 있지만, 기본적으로 좋은 날입니다."},
        },
    ),
    TarotCard(
        number=20, name_ko="심판", name_en="Judgement",
        upright="각성, 부활, 결단, 소명",
        reversed="자기 비판, 후회, 결정 회피",
        element="화",
        traits={"wisdom": 0.8, "authority": 0.7, "career": 0.7, "leadership": 0.6, "balance": 0.6},
        meanings={
            "연애": {"upright": "과거의 관계를 되돌아보고 새로운 결단을 내릴 때입니다.", "reversed": "지난 연애의 후회에서 벗어나야 새 사랑을 만납니다."},
            "재물": {"upright": "과거의 투자나 노력이 결실을 맺는 시기입니다.", "reversed": "과거의 재정적 실수에 대한 후회보다 현재에 집중하세요."},
            "직업": {"upright": "소명을 발견하거나 중요한 커리어 결정을 내리게 됩니다.", "reversed": "결정을 미루면 기회가 사라질 수 있습니다."},
            "건강": {"upright": "건강에 대한 각성의 시기입니다. 생활 습관을 바꿀 좋은 때입니다.", "reversed": "건강 문제를 모른 척하면 나중에 후회합니다."},
            "오늘의 운세": {"upright": "중요한 깨달음이나 결정의 순간이 올 수 있습니다.", "reversed": "과거에 얽매이지 말고 현재에 집중하세요."},
        },
    ),
    TarotCard(
        number=21, name_ko="세계", name_en="The World",
        upright="완성, 성취, 통합, 여행",
        reversed="미완성, 지연, 목표 부재",
        element="토",
        traits={"career": 0.9, "wealth": 0.9, "wisdom": 0.8, "balance": 0.9, "leadership": 0.7, "creativity": 0.7},
        meanings={
            "연애": {"upright": "완전하고 성숙한 사랑을 이루는 시기입니다. 서로에게 최고의 파트너가 됩니다.", "reversed": "관계의 완성을 서두르지 마세요. 아직 더 성장할 부분이 있습니다."},
            "재물": {"upright": "재물 운이 완성되는 시기입니다. 목표했던 자산을 이루게 됩니다.", "reversed": "목표에 거의 도달했지만 마지막 마무리가 부족합니다."},
            "직업": {"upright": "커리어의 큰 성취를 이루는 시기입니다. 모든 노력이 결실을 맺습니다.", "reversed": "거의 다 왔지만 마무리가 약합니다. 끝까지 최선을 다하세요."},
            "건강": {"upright": "신체와 정신이 조화를 이루는 좋은 상태입니다.", "reversed": "건강 관리의 마지막 한 걸음이 부족합니다. 꾸준히 유지하세요."},
            "오늘의 운세": {"upright": "모든 것이 완성되고 만족스러운 하루가 됩니다. 성취를 축하하세요.", "reversed": "아쉬운 부분이 있지만, 전체적으로는 좋은 날입니다."},
        },
    ),
]


POSITIONS = ["과거", "현재", "미래"]


def draw_three_card_spread(category: str) -> TarotSpread:
    """3장의 카드를 무작위로 뽑아 쓰리카드 스프레드를 생성"""
    if category not in CATEGORIES:
        raise ValueError(f"지원하지 않는 카테고리: {category}. 가능한 값: {CATEGORIES}")

    selected = random.sample(MAJOR_ARCANA, 3)
    cards = [
        DrawnCard(
            card=card,
            position=POSITIONS[i],
            is_reversed=random.random() < 0.5,
        )
        for i, card in enumerate(selected)
    ]
    return TarotSpread(category=category, cards=cards)
