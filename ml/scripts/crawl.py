"""
관상 학습 데이터 크롤링 스크립트.

얼굴 이미지 데이터셋을 수집합니다.
사용 전 저작권 및 개인정보보호 관련 법률을 확인하세요.
"""

import argparse
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"


async def crawl_images(source: str, max_count: int = 100) -> None:
    """
    이미지 데이터를 크롤링합니다.

    Args:
        source: 크롤링 소스 URL 또는 데이터셋 이름
        max_count: 최대 수집 이미지 수
    """
    output_dir = DATA_DIR / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    # TODO: 크롤링 로직 구현
    # - 공개 데이터셋 다운로드 (CelebA, FFHQ 등)
    # - 또는 허가된 웹사이트에서 이미지 수집
    print(f"크롤링 소스: {source}")
    print(f"최대 수집 수: {max_count}")
    print(f"저장 경로: {output_dir}")
    print("TODO: 크롤링 로직 구현 필요")


if __name__ == "__main__":
    import asyncio

    parser = argparse.ArgumentParser(description="관상 학습 데이터 크롤링")
    parser.add_argument("--source", type=str, required=True, help="크롤링 소스")
    parser.add_argument("--max-count", type=int, default=100, help="최대 수집 수")
    args = parser.parse_args()

    asyncio.run(crawl_images(args.source, args.max_count))
