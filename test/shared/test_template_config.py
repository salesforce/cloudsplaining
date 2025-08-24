import unittest
import os
import tempfile
from pathlib import Path
from cloudsplaining.shared.template_config import TemplateConfig


class TemplateConfigTestCase(unittest.TestCase):
    def setUp(self):
        """Set up temporary directory for each test"""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up after each test"""
        os.chdir(self.original_cwd)

    def test_no_custom_files_returns_default(self):
        """KEY TEST: When no custom files exist, should return default content"""
        config = TemplateConfig()

        self.assertEqual(config.guidance_content, "default")
        self.assertEqual(config.appendices_content, "default")
        self.assertTrue(config.show_guidance_nav)
        self.assertTrue(config.show_appendices_nav)

    def test_custom_files_with_content(self):
        """KEY TEST: Custom files with content should be processed correctly"""
        Path("custom-guidance.html").write_text("<h1>Custom Guidance</h1>", encoding="utf-8")
        Path("custom-appendices.html").write_text("<h1>Custom Appendices</h1>", encoding="utf-8")

        config = TemplateConfig()

        self.assertEqual(config.guidance_content, "<h1>Custom Guidance</h1>")
        self.assertEqual(config.appendices_content, "<h1>Custom Appendices</h1>")
        self.assertTrue(config.show_guidance_nav)
        self.assertTrue(config.show_appendices_nav)

    def test_empty_custom_files_hide_navigation(self):
        """KEY TEST: Empty custom files should completely exclude sections"""
        Path("custom-guidance.html").write_text("", encoding="utf-8")
        Path("custom-appendices.html").write_text("   ", encoding="utf-8")

        config = TemplateConfig()

        self.assertEqual(config.guidance_content, "")
        self.assertEqual(config.appendices_content, "")
        self.assertFalse(config.show_guidance_nav)
        self.assertFalse(config.show_appendices_nav)

    def test_javascript_string_escaping(self):
        """KEY TEST: HTML content should be properly escaped for JavaScript injection"""
        content_with_special_chars = '<h1>Test "quoted" content</h1>\n<p>New line</p>'
        Path("custom-guidance.html").write_text(content_with_special_chars, encoding="utf-8")

        config = TemplateConfig()

        self.assertIn('\\"', config.guidance_content)
        self.assertIn("\\n", config.guidance_content)
        self.assertNotIn("\n", config.guidance_content)

    def test_mixed_scenario_one_custom_one_default(self):
        """KEY TEST: Should handle mixed scenario with one custom file and one default"""
        Path("custom-guidance.html").write_text("<h1>Only Guidance</h1>", encoding="utf-8")

        config = TemplateConfig()

        self.assertEqual(config.guidance_content, "<h1>Only Guidance</h1>")
        self.assertEqual(config.appendices_content, "default")
        self.assertTrue(config.show_guidance_nav)
        self.assertTrue(config.show_appendices_nav)
