from pathlib import Path
from PIL import Image

image_dir = Path("uploads/temp/images/test")

for image_path in sorted(image_dir.glob("*.jpg")):
    img = Image.open(image_path)

    print(
        f"{image_path.name:12} | "
        f"{img.width}x{img.height} | "
        f"{image_path.stat().st_size / 1024:.1f} KB"
    )