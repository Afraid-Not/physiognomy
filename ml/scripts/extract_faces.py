"""
분할 압축에서 무표정 정면 중간조명 이미지만 추출
패턴: image/Fxxxx/Fxxxx_01_1_M.png → 피험자당 1장
"""

import subprocess
import shutil
from pathlib import Path

BZ_EXE = r"C:\Program Files\Bandizip\bz.exe"
BASE_DIR = Path(r"D:\dev\physiognomy")
OUTPUT_DIR = BASE_DIR / "ml" / "data" / "face-image-aihub"

ARCHIVES = [
    {
        "zip": BASE_DIR / "026.안면 랜드마크 데이터" / "3.개방데이터" / "1.데이터" / "Training" / "01.원천데이터" / "TS.zip",
        "list": str(BASE_DIR / "ml" / "data" / "train_files.txt"),
        "label": "Training",
    },
    {
        "zip": BASE_DIR / "026.안면 랜드마크 데이터" / "3.개방데이터" / "1.데이터" / "Validation" / "01.원천데이터" / "VS.zip",
        "list": str(BASE_DIR / "ml" / "data" / "val_files.txt"),
        "label": "Validation",
    },
]


def build_file_list(zip_path, list_path):
    """zip에서 _01_1_M.png 파일 목록 추출"""
    result = subprocess.run(
        [BZ_EXE, "l", str(zip_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    files = [
        line.split()[-1]
        for line in result.stdout.splitlines()
        if "_01_1_M.png" in line and "image" in line
    ]
    Path(list_path).write_text("\n".join(files), encoding="utf-8")
    return files


def extract_batch(zip_path, files, out_dir):
    """파일 목록을 50개씩 배치로 추출"""
    batch_size = 50
    extracted = 0

    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        cmd = [BZ_EXE, "x", f"-o:{out_dir}", "-y", "-aoa", str(zip_path)] + batch
        subprocess.run(cmd, capture_output=True, timeout=300)
        extracted += len(batch)
        print(f"  {extracted}/{len(files)} extracted...", flush=True)

    return extracted


def flatten_images(label_dir):
    """image/Fxxxx/ 구조를 flat하게 정리"""
    image_dir = label_dir / "image"
    if not image_dir.exists():
        return 0

    count = 0
    for png in image_dir.rglob("*.png"):
        dest = label_dir / png.name
        png.rename(dest)
        count += 1

    shutil.rmtree(image_dir)
    return count


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for archive in ARCHIVES:
        zip_path = archive["zip"]
        label = archive["label"]
        out_dir = OUTPUT_DIR / label

        if not zip_path.exists():
            print(f"[SKIP] {label}: {zip_path} not found")
            continue

        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"[{label}] Building file list...")
        files = build_file_list(zip_path, archive["list"])
        print(f"[{label}] Found {len(files)} files to extract")

        print(f"[{label}] Extracting...")
        extract_batch(zip_path, files, out_dir)

        print(f"[{label}] Flattening...")
        count = flatten_images(out_dir)
        print(f"[{label}] Done: {count} images\n")

    # 결과 요약
    total = 0
    for d in sorted(OUTPUT_DIR.iterdir()):
        if d.is_dir():
            c = len(list(d.glob("*.png")))
            print(f"  {d.name}: {c} images")
            total += c
    print(f"\nTotal: {total} images")
