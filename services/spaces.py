"""
SpacesService — DigitalOcean Spaces storage backend.

Replaces CloudinaryService. Two copies of every image are stored:
  • originals/{image_id}.{ext}  — full-quality, no watermark  (for paid download)
  • optimized/{image_id}.webp   — compressed WebP + watermark  (for web display)
"""

import boto3
import io
import os
import uuid
import asyncio
import logging

from botocore.config import Config
from fastapi import UploadFile, HTTPException, status
from PIL import Image, ImageDraw, ImageFont
from schemas.auth import UserResponse

log = logging.getLogger(__name__)

# ─── S3 Client (module-level singleton) ───────────────────────────────────────
_session = boto3.session.Session()
_client = _session.client(
    "s3",
    region_name=os.getenv("SPACES_REGION"),
    endpoint_url=os.getenv("SPACES_ENDPOINT"),
    aws_access_key_id=os.getenv("SPACES_KEY"),
    aws_secret_access_key=os.getenv("SPACES_SECRET"),
    config=Config(signature_version="s3v4"),
)

BUCKET   = os.getenv("SPACES_BUCKET", "")
ENDPOINT = os.getenv("SPACES_ENDPOINT", "")


# ─── Private helpers ──────────────────────────────────────────────────────────

def _optimize_image(
    file_bytes: bytes,
    max_width: int = 1920,
    max_height: int = 1920,
    quality: int = 85,
) -> bytes:
    """Convert to WebP and resize (inplace thumbnail, no upscale)."""
    img = Image.open(io.BytesIO(file_bytes))

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGBA")
    elif img.mode != "RGB":
        img = img.convert("RGB")

    img.thumbnail((max_width, max_height), Image.LANCZOS)
    return img


def _add_watermark(img: Image.Image, text: str = "© AllEventPictures") -> Image.Image:
    """
    Bake a tiled, semi-transparent diagonal text watermark into the image.
    Returns a new RGBA image with the watermark composited in.
    """
    base = img.convert("RGBA")
    width, height = base.size

    # Create a transparent overlay the same size as the image
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Font size proportional to the shorter dimension
    font_size = max(20, min(width, height) // 18)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    # Measure text so we can tile it
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    step_x = text_w + font_size * 4
    step_y = text_h + font_size * 4

    for y in range(-height, height * 2, step_y):
        for x in range(-width, width * 2, step_x):
            draw.text(
                (x, y),
                text,
                fill=(255, 255, 255, 45),  # white, ~18 % opacity
                font=font,
            )

    # Rotate overlay 45° and composite
    rotated = overlay.rotate(45, expand=False)
    # Crop back to original size after rotation (rotate may expand)
    rotated = rotated.crop((0, 0, width, height))

    watermarked = Image.alpha_composite(base, rotated)
    return watermarked.convert("RGB")


def _encode_webp(img: Image.Image, quality: int = 85) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=quality, method=6)
    buf.seek(0)
    return buf.read()


def _put_object(key: str, body: bytes, content_type: str) -> None:
    _client.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=body,
        ACL="public-read",
        ContentType=content_type,
    )


# ─── SpacesService ────────────────────────────────────────────────────────────

class SpacesService:

    @staticmethod
    async def upload_image(
        image_cover: UploadFile,
        user: UserResponse,
        folder: str = "event-photo",
    ) -> dict:
        """
        Upload one image to Spaces.
        Returns:
            image_id   — UUID hex used as the shared key
            original_url  — direct URL to the original file
            optimized_url — direct URL to the watermarked WebP
            secure_url    — alias for optimized_url (backward-compat)
        """
        try:
            content = await image_cover.read()
            original_ext = (image_cover.filename or "file").rsplit(".", 1)[-1].lower() or "jpg"
            image_id = uuid.uuid4().hex

            prefix = f"{folder.strip('/')}/" if folder else ""
            original_key  = f"{prefix}originals/{image_id}.{original_ext}"
            optimized_key = f"{prefix}optimized/{image_id}.webp"

            # ── run blocking I/O in thread pool ──────────────────────────────
            def _do_upload():
                # 1. Upload original
                orig_content_type = image_cover.content_type or "application/octet-stream"
                _put_object(original_key, content, orig_content_type)

                # 2. Build optimized + watermarked WebP
                img = _optimize_image(content)
                img_wm = _add_watermark(img)
                webp_bytes = _encode_webp(img_wm)

                # 3. Upload optimized
                _put_object(optimized_key, webp_bytes, "image/webp")

            await asyncio.to_thread(_do_upload)

            original_url  = f"{ENDPOINT}/{BUCKET}/{original_key}"
            optimized_url = f"{ENDPOINT}/{BUCKET}/{optimized_key}"

            return {
                "image_id":     image_id,
                "public_id":    image_id,          # keep public_id = image_id
                "original_url": original_url,
                "optimized_url": optimized_url,
                "secure_url":   optimized_url,     # backward-compat alias
                "created_by":   user,
            }

        except Exception as exc:
            log.exception("SpacesService.upload_image failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error uploading image: {exc}",
            )

    @staticmethod
    async def upload_images(
        images: list[UploadFile],
        user: UserResponse,
        folder: str = "event-photo",
    ) -> list[dict]:
        try:
            tasks = [SpacesService.upload_image(img, user, folder=folder) for img in images]
            return await asyncio.gather(*tasks)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error uploading images: {exc}",
            )

    @staticmethod
    async def upload_image_public(
        image: UploadFile,
        folder: str = "public-uploads"
    ) -> dict:
        """
        Public endpoint for uploading images. Does not require a user string/object.
        Returns optimized_url as the primary secure_url.
        """
        try:
            content = await image.read()
            original_ext = (image.filename or "file").rsplit(".", 1)[-1].lower() or "jpg"
            image_id = uuid.uuid4().hex

            prefix = f"{folder.strip('/')}/" if folder else ""
            key = f"{prefix}{image_id}.{original_ext}"
            
            # Simple direct upload, no watermark (just as an example, or standard webp conversion)
            def _do_upload():
                orig_content_type = image.content_type or "application/octet-stream"
                # You might still want to compress it? Left simple for now as it's just public uploads
                _put_object(key, content, orig_content_type)

            await asyncio.to_thread(_do_upload)
            url = f"{ENDPOINT}/{BUCKET}/{key}"

            return {
                "public_id": image_id,
                "secure_url": url,
            }
        except Exception as exc:
            log.exception("SpacesService.upload_image_public failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error uploading image: {exc}",
            )

    @staticmethod
    def get_watermarked_url(public_id: str, folder: str = "event-photo") -> str:
        """
        Return the optimized (watermarked WebP) URL for a given image_id.
        Falls back gracefully — returns the public_id unchanged if it looks
        like an old Cloudinary ID (contains '/').
        """
        if "/" in public_id:
            # Old Cloudinary public_id — return as-is so old images still work
            return public_id
        prefix = f"{folder.strip('/')}/" if folder else ""
        return f"{ENDPOINT}/{BUCKET}/{prefix}optimized/{public_id}.webp"

    @staticmethod
    def get_original_url(public_id: str, original_url: str | None = None) -> str | None:
        """Return the stored original URL (used by download endpoint)."""
        return original_url

    @staticmethod
    async def delete_image(image_id: str, folder: str = "event-photo") -> None:
        """
        Delete both originals/ and optimized/ keys for an image.
        Silently ignores missing keys.
        """
        try:
            prefix = f"{folder.strip('/')}/" if folder else ""

            def _do_delete():
                for sub in ("originals", "optimized"):
                    resp = _client.list_objects_v2(
                        Bucket=BUCKET,
                        Prefix=f"{prefix}{sub}/{image_id}",
                    )
                    for obj in resp.get("Contents", []):
                        _client.delete_object(Bucket=BUCKET, Key=obj["Key"])

            await asyncio.to_thread(_do_delete)

        except Exception as exc:
            log.exception("SpacesService.delete_image failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting image: {exc}",
            )
