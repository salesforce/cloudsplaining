"""Creates the HTML Reports"""

from __future__ import annotations

import datetime
import json
import os.path
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from cloudsplaining.bin.version import __version__

app_bundle_path = os.path.join(os.path.dirname(__file__), "dist", "js", "index.js")


class HTMLReport:
    """Inject the JS files and report results into the final HTML report"""

    def __init__(
        self,
        account_id: str,
        account_name: str,
        results: dict[str, dict[str, Any]],
        minimize: bool = False,
    ) -> None:
        self.account_name = account_name
        self.account_id = account_id
        self.report_generated_time = datetime.datetime.now().strftime("%Y-%m-%d")
        self.minimize = minimize
        self.results = f"var iam_data = {json.dumps(results, default=str)}"

    @property
    def app_bundle(self) -> str:
        """The Cloudsplaining Javascript application code should be loaded either from the CDN or locally,
        depending on if the user specified the --minimize option"""
        if self.minimize:
            js_url = f"https://cdn.jsdelivr.net/gh/salesforce/cloudsplaining@{__version__}/cloudsplaining/output/dist/js/index.js"
            bundle = f'<script type="text/javascript" src="{js_url}"></script>'
            return bundle
        else:
            bundle_content = Path(app_bundle_path).read_text(encoding="utf-8")
            # bundle_content = app_bundle_path.read_text(encoding="utf-8")
            bundle = f'<script type="text/javascript">\n{bundle_content}\n</script>'
            return bundle

    @property
    def vendor_bundle(self) -> str:
        """The Javascript vendor bundle should be loaded either from the CDN or locally,
        depending on if the user specified the --minimize option"""

        if self.minimize:
            js_url = f"https://cdn.jsdelivr.net/gh/salesforce/cloudsplaining@{__version__}/cloudsplaining/output/dist/js/chunk-vendors.js"
            bundle = f'<script type="text/javascript" src="{js_url}"></script>'
            return bundle
        else:
            vendor_bundle_path = get_vendor_bundle_path()
            bundle_content = Path(vendor_bundle_path).read_text(encoding="utf-8")
            # bundle_content = vendor_bundle_path.read_text(encoding="utf-8")
            bundle = f'<script type="text/javascript">\n{bundle_content}\n</script>'
            return bundle

    def get_html_report(self) -> str:
        """Returns the rendered HTML report"""
        template_contents = dict(
            vendor_bundle_js=self.vendor_bundle,
            app_bundle_js=self.app_bundle,
            # results
            results=self.results,
            # account metadata
            account_id=self.account_id,
            account_name=self.account_name,
            report_generated_time=str(self.report_generated_time),
            cloudsplaining_version=__version__,
        )
        template_path = os.path.dirname(__file__)
        env = Environment(loader=FileSystemLoader(template_path))  # noqa: S701
        template = env.get_template("template.html")
        return template.render(t=template_contents)


def get_vendor_bundle_path() -> str:
    """Finds the vendored javascript bundle even if it has a hash suffix"""
    vendor_bundle_directory = os.path.join(os.path.dirname(__file__), "dist", "js")
    file_list_with_full_path = []
    for f in os.listdir(vendor_bundle_directory):
        file_path = os.path.join(vendor_bundle_directory, f)
        if (
            os.path.isfile(file_path)
            and os.path.splitext(file_path)[-1].endswith("js")
            and os.path.splitext(f)[0].startswith("chunk-vendors")
        ):
            file_list_with_full_path.append(os.path.abspath(file_path))
    return file_list_with_full_path[0]
