import base64
from io import BytesIO
from PIL import Image

def get_data_url(img):
    b64 = base64.b64encode(img['bytes']).decode("ascii")
    data_url = f"data:image/jpeg;base64,{b64}"
    return data_url

from PIL import Image
from io import BytesIO
import base64

def process_hf_image(hf_image):
    """Process Hugging Face image object to PIL Image"""
    try:
        if isinstance(hf_image, Image.Image):
            return hf_image
        else:
            # If it's a path or other format, try to open it
            return Image.open(hf_image)
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def pil_to_base64(img: Image.Image, *, img_format="PNG", add_data_uri=False, quality=95):
    """
    Take a PIL.Image (e.g., the output of process_hf_image) and return Base64.
    """
    if img is None:
        return None

    # JPEG can't handle transparency or palette directly
    if img_format.upper() == "JPEG" and img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGB")

    buf = BytesIO()
    save_kwargs = {}
    if img_format.upper() == "JPEG":
        save_kwargs.update(dict(quality=quality, optimize=True))
    img.save(buf, format=img_format.upper(), **save_kwargs)

    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    if add_data_uri:
        return f"data:image/{img_format.lower()};base64,{b64}"
    return b64

# Optional convenience wrapper: do both steps at once
def hf_image_to_base64(hf_image, **kwargs):
    """
    Runs process_hf_image(hf_image) then pil_to_base64(...) on the result.
    """
    pil_img = process_hf_image(hf_image)
    return pil_to_base64(pil_img, **kwargs)

# --- Example usage ---
# pil_img = process_hf_image("/path/to/img.png")
# b64_png = pil_to_base64(pil_img)  # plain base64 PNG
# b64_jpeg_uri = pil_to_base64(pil_img, img_format="JPEG", add_data_uri=True)
# # or one-liner:
# b64_auto = hf_image_to_base64("/path/to/img.png", img_format="PNG")
