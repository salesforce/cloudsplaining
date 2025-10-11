"""Template configuration for custom guidance and appendices"""

import json
from pathlib import Path


class TemplateConfig:
    """Detects and processes custom guidance and appendices files"""

    def __init__(self) -> None:
        self.guidance_content = self._get_guidance_content()
        self.appendices_content = self._get_appendices_content()
        self.show_guidance_nav = self.guidance_content != ""
        self.show_appendices_nav = self.appendices_content != ""

    def _get_guidance_content(self) -> str:
        """Get custom guidance content or default"""
        return self._get_custom_content("custom-guidance.html")

    def _get_appendices_content(self) -> str:
        """Get custom appendices content or default"""
        return self._get_custom_content("custom-appendices.html")

    def _get_custom_content(self, filename: str) -> str:
        """Get custom content from file or return default/empty"""
        if not filename or "/" in filename or "\\" in filename or ".." in filename:
            return "default"

        file_path = Path(filename)
        if not file_path.exists():
            return "default"

        try:
            content = file_path.read_text(encoding="utf-8").strip()
            if content:
                json_str = json.dumps(content)
                return json_str[1:-1]
            return ""
        except (OSError, UnicodeDecodeError):
            return ""
