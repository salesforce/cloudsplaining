"""Template configuration for custom guidance and appendices"""
import os
from pathlib import Path


class TemplateConfig:
    """Detects and processes custom guidance and appendices files"""

    def __init__(self):
        self.guidance_content = self._get_guidance_content()
        self.appendices_content = self._get_appendices_content()
        self.show_guidance_nav = self.guidance_content != ""
        self.show_appendices_nav = self.appendices_content != ""

    def _get_guidance_content(self) -> str:
        """Get custom guidance content or default"""
        custom_file = "custom-guidance.html"
        if os.path.exists(custom_file):
            content = Path(custom_file).read_text(encoding="utf-8")
            if content.strip():
                return content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
            return ""
        return "default"

    def _get_appendices_content(self) -> str:
        """Get custom appendices content or default"""
        custom_file = "custom-appendices.html"
        if os.path.exists(custom_file):
            content = Path(custom_file).read_text(encoding="utf-8")
            if content.strip():
                return content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
            return ""
        return "default"
