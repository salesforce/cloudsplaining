"""Creates the HTML Reports"""
import os
import json
import datetime
from jinja2 import Environment, FileSystemLoader
from cloudsplaining.bin.version import __version__

app_bundle_path = os.path.join(os.path.dirname(__file__), "dist", "js", "index.js")


class HTMLReport:
    """Inject the JS files and report results into the final HTML report"""
    def __init__(self, account_id, account_name, results):
        self.account_name = account_name
        self.account_id = account_id
        self.report_generated_time = datetime.datetime.now().strftime("%Y-%m-%d")

        self.results = f"var iam_data = {json.dumps(results)}"
        with open(app_bundle_path, "r") as f:
            self.app_bundle = f.read()
        vendor_bundle_path = get_vendor_bundle_path()
        with open(vendor_bundle_path, "r") as f:
            self.vendor_bundle = f.read()

    def get_html_report(self):
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
        template_path = os.path.join(os.path.dirname(__file__))
        env = Environment(loader=FileSystemLoader(template_path))  # nosec
        template = env.get_template("template.html")
        return template.render(t=template_contents)


def get_vendor_bundle_path():
    """Finds the vendored javascript bundle even if it has a hash suffix"""
    vendor_bundle_directory = os.path.join(os.path.dirname(__file__), "dist", "js")
    file_list = [
        f for f in os.listdir(vendor_bundle_directory) if os.path.isfile(os.path.join(vendor_bundle_directory, f))
    ]
    file_list_with_full_path = []
    for file in file_list:
        if file.endswith(".js") and file.startswith("chunk-vendors."):
            file_list_with_full_path.append(
                os.path.abspath(os.path.join(vendor_bundle_directory, file))
            )
    return file_list_with_full_path[0]
