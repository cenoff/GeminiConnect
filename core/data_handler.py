import base64
import logging

ARCHIVE_MIME_TYPES = {
    "application/zip",
    "application/x-rar",
    "application/x-7z-compressed",
}


async def process_file(item):
    data = item.get("data") or item.get("content")
    mime = item.get("mime_type", "text/plain")

    if mime in ARCHIVE_MIME_TYPES:
        return {"text": "[Archive files not supported]"}

    if mime in ["application/pdf"] or mime.startswith(("image/", "video/", "audio/")):
        result = {
            "inline_data": {
                "mime_type": mime,
                "data": data,
            }
        }
    else:
        try:
            decoded = base64.b64decode(data).decode("utf-8")
            result = {"text": f"[Document: {mime}]\n{decoded}"}
        except (UnicodeDecodeError, ValueError, base64.binascii.Error) as e:
            logging.error(f"Failed to read document. Error: {e}")
            result = {"text": f"[Failed to read document of type {mime}]"}
    return result


async def process_img(item):
    image_url = item.get("image_url", {})
    url = image_url.get("url", "") if isinstance(image_url, dict) else image_url

    if not url.startswith(""):
        return None

    if url.startswith("data:"):
        mime_type, base64_data = url.split(";base64,", 1)
        mime_type = mime_type.replace("data:", "")
        result = {
            "inline_data": {
                "mime_type": mime_type,
                "data": base64_data,
            }
        }
    return result


async def convert_content(messages: list):
    gemini_contents = []
    system_parts = []

    for msg in messages:
        if msg.role == "system":
            system_parts.append(msg.content)
        elif msg.role == "user":
            if system_parts:
                combined_system = "\n\n".join(system_parts)
                gemini_contents.append(
                    {
                        "role": "user",
                        "parts": [{"text": f"[System]: {combined_system}"}],
                    }
                )
                system_parts = []

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
                            logging.info(f"🔍 Processing file: {item}")

                            if "text" in item:
                                parts.append({"text": f"[Document]\n{item['text']}"})

                            elif "data" in item or "content" in item:
                                result = await process_file(item)
                                if result:
                                    parts.append(result)
            else:
                parts.append({"text": content})

            if parts:
                gemini_contents.append({"role": "user", "parts": parts})

        elif role == "assistant":
            gemini_contents.append({"role": "model", "parts": [{"text": content}]})

    return gemini_contents


####################################################################################################################################


# async def convert_content(messages: list):
#     gemini_contents = []

#     system_parts = []
#     for msg in messages:
#         if msg.role == "system":
#             system_parts.append(msg.content)

#     if system_parts:
#         combined_system = "\n\n".join(system_parts)
#         gemini_contents.append(
#             {"role": "user", "parts": [{"text": f"[System]: {combined_system}"}]}
#         )

#     for msg in messages:
#         role = msg.role
#         content = msg.content

#         if role == "system":
#             continue

#         elif role == "user":
#             parts = []

#             if isinstance(content, list):
#                 for item in content:
#                     if isinstance(item, dict):
#                         item_type = item.get("type", "")

#                         if item_type == "text":
#                             text_data = item.get("text", "")
#                             if text_data:
#                                 parts.append({"text": text_data})

#                         elif item_type == "image_url":
#                             image_url = item.get("image_url", {})
#                             url = (
#                                 image_url.get("url", "")
#                                 if isinstance(image_url, dict)
#                                 else image_url
#                             )

#                             if url.startswith("data:"):
#                                 mime_type, base64_data = url.split(";base64,", 1)
#                                 mime_type = mime_type.replace("data:", "")
#                                 parts.append(
#                                     {
#                                         "inline_data": {
#                                             "mime_type": mime_type,
#                                             "data": base64_data,
#                                         }
#                                     }
#                                 )

#                         elif item_type in ["file", "document"]:
#                             print(f"🔍 Processing file: {item}")
#                             if "text" in item:
#                                 parts.append({"text": f"[Document]\n{item['text']}"})

#                             elif "data" in item or "content" in item:
#                                 data = item.get("data") or item.get("content")
#                                 mime = item.get("mime_type", "text/plain")

#                                 if mime in ["application/pdf"] or mime.startswith(
#                                     ("image/", "video/", "audio/")
#                                 ):
#                                     parts.append(
#                                         {
#                                             "inline_data": {
#                                                 "mime_type": mime,
#                                                 "data": data,
#                                             }
#                                         }
#                                     )
#                                 else:
#                                     print(
#                                         f"⚠️ File without data: {item.get('name', 'unknown')}"
#                                     )
#                                     try:
#                                         decoded = base64.b64decode(data).decode("utf-8")
#                                         parts.append(
#                                             {"text": f"[Document: {mime}]\n{decoded}"}
#                                         )
#                                     except Exception as e:
#                                         print(f"Failed to read document. Error: {e}")
#                                         parts.append(
#                                             {
#                                                 "text": f"[Failed to read document of type {mime}]"
#                                             }
#                                         )
#             else:
#                 parts.append({"text": content})

#             if parts:
#                 gemini_contents.append({"role": "user", "parts": parts})

#         elif role == "assistant":
#             gemini_contents.append({"role": "model", "parts": [{"text": content}]})

#     return gemini_contents


# ####################################################################################################################################
# from typing import List, Dict, Any, Optional  # noqa: E402
# import logging

# logger = logging.getLogger(__name__)

# # Константы
# BINARY_MIME_TYPES = {"application/pdf"}
# MEDIA_MIME_PREFIXES = ("image/", "video/", "audio/")


# class MessageConverter:
#     """Конвертер сообщений в формат Gemini API"""

#     @staticmethod
#     async def convert_content(messages: List[Any]) -> List[Dict[str, Any]]:
#         """Основной метод конвертации"""
#         gemini_contents = []
#         system_messages = []

#         for msg in messages:
#             role = msg.role

#             if role == "system":
#                 system_messages.append(msg.content)
#             elif role == "user":
#                 if system_messages:
#                     # Добавляем системные сообщения перед первым user сообщением
#                     gemini_contents.append(
#                         MessageConverter._create_system_message(system_messages)
#                     )
#                     system_messages = []

#                 user_msg = MessageConverter._process_user_message(msg.content)
#                 if user_msg:
#                     gemini_contents.append(user_msg)

#             elif role == "assistant":
#                 gemini_contents.append(
#                     {"role": "model", "parts": [{"text": msg.content}]}
#                 )

#         return gemini_contents

#     @staticmethod
#     def _create_system_message(system_parts: List[str]) -> Dict[str, Any]:
#         """Создает системное сообщение"""
#         combined = "\n\n".join(system_parts)
#         return {"role": "user", "parts": [{"text": f"[System]: {combined}"}]}

#     @staticmethod
#     def _process_user_message(content: Any) -> Optional[Dict[str, Any]]:
#         """Обрабатывает пользовательское сообщение"""
#         if isinstance(content, str):
#             return {"role": "user", "parts": [{"text": content}]}

#         if not isinstance(content, list):
#             return None

#         parts = []
#         for item in content:
#             part = MessageConverter._process_content_item(item)
#             if part:
#                 parts.append(part)

#         return {"role": "user", "parts": parts} if parts else None

#     @staticmethod
#     def _process_content_item(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
#         """Обрабатывает один элемент контента"""
#         if not isinstance(item, dict):
#             return None

#         item_type = item.get("type", "")

#         processors = {
#             "text": MessageConverter._process_text,
#             "image_url": MessageConverter._process_image,
#             "file": MessageConverter._process_file,
#             "document": MessageConverter._process_file,
#         }

#         processor = processors.get(item_type)
#         return processor(item) if processor else None

#     @staticmethod
#     def _process_text(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
#         """Обрабатывает текстовый элемент"""
#         text = item.get("text", "")
#         return {"text": text} if text else None

#     @staticmethod
#     def _process_image(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
#         """Обрабатывает изображение"""
#         image_url = item.get("image_url", {})
#         url = image_url.get("url", "") if isinstance(image_url, dict) else image_url

#         if not url.startswith("data:"):
#             return None

#         try:
#             mime_type, base64_data = url.split(";base64,", 1)
#             mime_type = mime_type.replace("data:", "")
#             return MessageConverter._create_inline_data(mime_type, base64_data)
#         except ValueError:
#             logger.warning(f"Invalid image URL format: {url[:50]}...")
#             return None

#     @staticmethod
#     def _process_file(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
#         """Обрабатывает файл/документ"""
#         # Если есть готовый текст
#         if "text" in item:
#             return {"text": f"[Document]\n{item['text']}"}

#         # Если есть данные
#         data = item.get("data") or item.get("content")
#         if not data:
#             logger.warning(f"File without data: {item.get('name', 'unknown')}")
#             return None

#         mime_type = item.get("mime_type", "text/plain")

#         # Бинарные файлы
#         if MessageConverter._is_binary_mime(mime_type):
#             return MessageConverter._create_inline_data(mime_type, data)

#         # Текстовые файлы
#         return MessageConverter._decode_text_file(data, mime_type)

#     @staticmethod
#     def _is_binary_mime(mime_type: str) -> bool:
#         """Проверяет, является ли MIME тип бинарным"""
#         return mime_type in BINARY_MIME_TYPES or any(
#             mime_type.startswith(prefix) for prefix in MEDIA_MIME_PREFIXES
#         )

#     @staticmethod
#     def _create_inline_data(mime_type: str, data: str) -> Dict[str, Any]:
#         """Создает inline_data структуру"""
#         return {
#             "inline_data": {
#                 "mime_type": mime_type,
#                 "data": data,
#             }
#         }

#     @staticmethod
#     def _decode_text_file(data: str, mime_type: str) -> Dict[str, Any]:
#         """Декодирует текстовый файл"""
#         try:
#             decoded = base64.b64decode(data).decode("utf-8")
#             return {"text": f"[Document: {mime_type}]\n{decoded}"}
#         except Exception as e:
#             logger.error(f"Failed to decode document: {e}")
#             return {"text": f"[Failed to read document of type {mime_type}]"}


# # Для обратной совместимости
# async def convert_content(messages: List[Any]) -> List[Dict[str, Any]]:
#     """Обертка для обратной совместимости"""
#     return await MessageConverter.convert_content(messages)
