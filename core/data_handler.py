import base64
import logging
from config import ARCHIVE_MIME_TYPES


async def process_file(item):
    data = item.get("data") or item.get("content")
    mime = item.get("mime_type", "text/plain")

    if not data:
        logging.warning(
            f"Missing data/content in file item: {item.get('type', 'unknown')}"
        )

    if not isinstance(mime, str):
        logging.error(f"Invalid mime_type: {type(mime).__name__}")
        return {"text": "[Invalid file type]"}

    if mime in ARCHIVE_MIME_TYPES:
        return {"text": "[Archive files not supported]"}

    if mime in ["application/pdf"] or mime.startswith(("image/", "video/", "audio/")):
        return {
            "inline_data": {
                "mime_type": mime,
                "data": data,
            }
        }
    else:
        try:
            decoded = base64.b64decode(data).decode("utf-8")
            return {"text": f"[Document: {mime}]\n{decoded}"}
        except (UnicodeDecodeError, ValueError, base64.binascii.Error) as e:
            logging.exception(f"Failed to read document. Error: {e}")
            return {"text": f"[Failed to read document of type {mime}]"}


async def process_img(item):
    image_url = item.get("image_url", {})
    url = image_url.get("url", "") if isinstance(image_url, dict) else image_url

    if not url or not url.startswith("data:"):
        return None

    try:
        mime_type, base64_data = url.split(";base64,", 1)
        mime_type = mime_type.replace("data:", "")
        result = {
            "inline_data": {
                "mime_type": mime_type,
                "data": base64_data,
            }
        }
    except ValueError as e:
        logging.error(f"Invalid image URL format: {e}")
        return None

    return result


async def convert_content(messages: list):
    gemini_contents = []
    system_parts = []

    for msg in messages:
        if msg.role == "system":
            system_parts.append(msg.content)

    if system_parts:
        combined_system = "\n\n".join(system_parts)
        gemini_contents.append(
            {
                "role": "user",
                "parts": [{"text": f"[System]: {combined_system}"}],
            }
        )

    for msg in messages:
        role = msg.role
        content = msg.content

        if role == "system":
            continue

        elif role == "user":
            parts = []

            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        item_type = item.get("type", "")

                        if item_type == "text":
                            text_data = item.get("text", "")
                            if text_data:
                                parts.append({"text": text_data})

                        elif item_type == "image_url":
                            result = await process_img(item)
                            if result:
                                parts.append(result)

                        elif item_type in ["file", "document"]:
                            logging.info(f"Processing file: {item}")

                            if "text" in item:
                                parts.append({"text": f"[Document]\n{item['text']}"})

                            elif "data" in item or "content" in item:
                                result = await process_file(item)
                                if result:
                                    parts.append(result)
            else:
                if not isinstance(content, str):
                    logging.error(
                        f"Unexpected content type: {type(content).__name__} in role {role}"
                    )
                    parts.append({"text": "[Invalid content format]"})
                else:
                    parts.append({"text": content})

            if parts:
                gemini_contents.append({"role": "user", "parts": parts})

        elif role == "assistant":
            gemini_contents.append({"role": "model", "parts": [{"text": content}]})

    return gemini_contents
