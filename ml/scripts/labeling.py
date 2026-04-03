"""
관상 데이터 라벨링 도구.

크롤링한 이미지에 관상학적 특징 라벨을 부여합니다.
"""

import argparse
import json
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"

# 라벨 카테고리 정의
LABEL_SCHEMA = {
    "forehead": ["넓은 이마", "좁은 이마", "둥근 이마", "각진 이마", "볼록한 이마"],
    "eyes": ["봉황눈", "용눈", "원앙눈", "삼백안", "사백안", "호눈", "여우눈"],
    "nose": ["매부리코", "주먹코", "복코", "들창코", "솔개코", "매코"],
    "mouth": ["앵두입술", "일자입", "활입", "두꺼운 입술", "얇은 입술"],
    "jaw": ["각진 턱", "둥근 턱", "뾰족한 턱", "긴 턱", "짧은 턱", "이중턱"],
    "face_shape": ["계란형", "둥근형", "각진형", "긴형", "역삼각형", "마름모형"],
}


def create_label_template() -> dict:
    """빈 라벨 템플릿을 생성합니다."""
    return {category: None for category in LABEL_SCHEMA}


def save_labels(image_path: str, labels: dict, output_dir: Path) -> None:
    """
    라벨을 JSON 파일로 저장합니다.

    Args:
        image_path: 이미지 파일 경로
        labels: 라벨 딕셔너리
        output_dir: 저장 디렉토리
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    label_file = output_dir / f"{Path(image_path).stem}.json"

    label_data = {
        "image_path": str(image_path),
        "labels": labels,
    }

    with open(label_file, "w", encoding="utf-8") as f:
        json.dump(label_data, f, ensure_ascii=False, indent=2)

    print(f"라벨 저장 완료: {label_file}")


def load_labels(label_file: Path) -> dict:
    """저장된 라벨을 로드합니다."""
    with open(label_file, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="관상 데이터 라벨링 도구")
    parser.add_argument("--data-dir", type=str, default=str(DATA_DIR / "raw"), help="이미지 디렉토리")
    parser.add_argument("--output-dir", type=str, default=str(DATA_DIR / "labels"), help="라벨 저장 디렉토리")
    args = parser.parse_args()

    # TODO: GUI 또는 CLI 기반 라벨링 인터페이스 구현
    print("라벨 카테고리:")
    for category, options in LABEL_SCHEMA.items():
        print(f"  {category}: {', '.join(options)}")
    print("\nTODO: 라벨링 인터페이스 구현 필요")
