import base64


async def convert_content(messages: list):
    gemini_contents = []

    system_parts = []
    for msg in messages:
        if msg.role == "system":
            system_parts.append(msg.content)

    if system_parts:
        combined_system = "\n\n".join(system_parts)
        gemini_contents.append(
            {"role": "user", "parts": [{"text": f"[System]: {combined_system}"}]}
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
                            image_url = item.get("image_url", {})
                            url = (
                                image_url.get("url", "")
                                if isinstance(image_url, dict)
                                else image_url
                            )

                            if url.startswith("data:"):
                                mime_type, base64_data = url.split(";base64,", 1)
                                mime_type = mime_type.replace("data:", "")
                                parts.append(
                                    {
                                        "inline_data": {
                                            "mime_type": mime_type,
                                            "data": base64_data,
                                        }
                                    }
                                )

                        elif item_type in ["file", "document"]:
                            print(f"🔍 Processing file: {item}")
                            if "text" in item:
                                parts.append({"text": f"[Document]\n{item['text']}"})

                            elif "data" in item or "content" in item:
                                data = item.get("data") or item.get("content")
                                mime = item.get("mime_type", "text/plain")

                                if mime in ["application/pdf"] or mime.startswith(
                                    ("image/", "video/", "audio/")
                                ):
                                    parts.append(
                                        {
                                            "inline_data": {
                                                "mime_type": mime,
                                                "data": data,
                                            }
                                        }
                                    )
                                else:
                                    print(
                                        f"⚠️ File without data: {item.get('name', 'unknown')}"
                                    )
                                    try:
                                        decoded = base64.b64decode(data).decode("utf-8")
                                        parts.append(
                                            {"text": f"[Document: {mime}]\n{decoded}"}
                                        )
                                    except Exception as e:
                                        print(f"Failed to read document. Error: {e}")
                                        parts.append(
                                            {
                                                "text": f"[Failed to read document of type {mime}]"
                                            }
                                        )
            else:
                parts.append({"text": content})

            if parts:
                gemini_contents.append({"role": "user", "parts": parts})

        elif role == "assistant":
            gemini_contents.append({"role": "model", "parts": [{"text": content}]})

    return gemini_contents
