from typing import Any, List, Dict
from config import meta_keywords, search_keywords


class Analyzer:
    def __init__(self):
        self.search_keywords = search_keywords
        self.meta_keywords = meta_keywords

    async def get_user_msg(self, messages: Any):
        has_images = False
        has_pdf = False
        user_msg = ""

        for msg in reversed(messages):
            if msg.role == "user":
                content = msg.content

                if isinstance(content, list):
                    has_images = any(
                        item.get("type") == "image_url"
                        for item in content
                        if isinstance(item, dict)
                    )
                    has_pdf = any(
                        item.get("type") in ["file", "document"]
                        and item.get("mime_types") == "application/pdf"
                        for item in content
                        if isinstance(item, dict)
                    )
                    text_items = [
                        item.get("text", "")
                        for item in content
                        if isinstance(item, dict) and item.get("type") == "text"
                    ]
                    user_msg = text_items[-1] if text_items else ""
                else:
                    user_msg = content
                break
        return has_images, user_msg, has_pdf

    async def is_meta_request(self, user_msg: str) -> bool:
        return any(keyword in (user_msg or "") for keyword in self.meta_keywords)

    async def is_search_request(self, user_msg: str) -> bool:
        return any(keyword in (user_msg or "") for keyword in self.search_keywords)

    async def analyze(self, messages: List[Any]) -> Dict[str, Any]:
        has_images, user_msg, has_pdf = await self.get_user_msg(messages)
        is_meta_request = await self.is_meta_request(user_msg)
        is_search_request = await self.is_search_request(user_msg)
        return user_msg, has_images, has_pdf, is_meta_request, is_search_request
