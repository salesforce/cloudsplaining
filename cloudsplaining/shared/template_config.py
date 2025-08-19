"""Template configuration for custom guidance and appendices"""

import os
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
        if not os.path.exists(filename):
            return "default"

        try:
            content = Path(filename).read_text(encoding="utf-8")
            if content.strip():
                return self._escape_html_content(content)
            return ""
        except (OSError, UnicodeDecodeError):
            return ""

    def _escape_html_content(self, content: str) -> str:
        """Escape HTML content for JavaScript injection"""
        return (
            content.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "")
        )
