import os
from PIL import Image, ImageOps
from config import TARGET_WIDTH, TARGET_HEIGHT, MAX_FILE_SIZE_MB, JPEG_QUALITY_START

def process_image(input_path: str, output_path: str) -> bool:
    try:
        img = Image.open(input_path)
        img = ImageOps.exif_transpose(img)

        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            rgba = img.convert("RGBA")
            bg = Image.new("RGB", rgba.size, (255, 255, 255))
            bg.paste(rgba, mask=rgba.split()[3])
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        target_ratio = TARGET_WIDTH / TARGET_HEIGHT
        w, h = img.size
        current_ratio = w / h

        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))

        img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)

        quality = JPEG_QUALITY_START
        while quality >= 40:
            img.save(output_path, "JPEG", quality=quality, optimize=True)
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            if size_mb <= MAX_FILE_SIZE_MB:
                return True
            quality -= 10

        return True
    except Exception as e:
        print(f"[process] failed for {input_path}: {e}")
        return False