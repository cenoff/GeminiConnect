from typing import Any, List, Dict


class Analyzer:
    def __init__(self):
        self.search_keywords = [
            "Respond to the user query using the provided context",
            "generating search queries",
            "**prioritize generating 1-3 broad and relevant search queries**",
        ]
        self.meta_keywords = [
            "follow_ups",
            "Generate a concise",
            "Generate 1-3 broad tags",
            "Suggest 3-5 relevant follow-up questions",
        ]

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
                    user_msg = " ".join(
                        item.get("text", "")
                        for item in content
                        if isinstance(item, dict) and item.get("type") == "text"
                    )
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
