## JavaScript Contributions

We use [Vue.js](https://vuejs.org/) and all UI source code is under the directory [/cloudsplaining/output/](/cloudsplaining/output/).

If you are new to JavaScript, consider learning the basics of JavaScript first - and then dive into [the Vue.js documentation](https://vuejs.org/v2/guide/), which is quite good.

If you're a backend developer by trade and relatively new to JavaScript, consider installing NodeJS first and perhaps writing some unit tests - that is an excellent way to get functional and dirty with JavaScript.

If you would like to contribute but are having trouble getting started, try reaching out to us over Gitter, or contact me on Twitter [@kmcquade3](https://twitter.com/kmcquade3).

### Getting started

We use Node v14.5.0. I suggest using Node version manager for managing multiple Node installations. This is suggested but not required. Instructions can be found [here](https://medium.com/@jamesauble/install-nvm-on-mac-with-brew-adb921fb92cc).

* Check the Node version matches v14.5.0

```bash
node --version

# should return:
# v14.5.0
```

* Install dependencies from the root directory

```bash
npm install
```

We've already preconfigured several `npm` commands to be run inside the package.json file, so you don't have to remember to use `vue-cli-service serve --mode development`, for example - you can just use `npm serve`.


* Spin up a local version of the report, using sample data.
  
```bash
npm serve
```

You can then access the application over [http://localhost:8080](http://localhost:8080).

* Run unit tests

```bash
npm test
```

* Build the most updated Javascript bundle

```bash
npm build
```

### Adding new JavaScript utility functions: Checklist

- [ ] Add a new `.js` file under [/cloudsplaining/output/src/util](/cloudsplaining/output/src/util/). This should contain your JavaScript functions.
   * Add your function in this code. See other files in that folder for an example.
   * Ensure that there is an `exports myfunction = myfunction;` line at the end of the file 
  
- [ ] Add a new `.js` file under [/cloudsplaining/output/src/test](/cloudsplaining/output/src/test/). 
   * Use this to store your unit tests. See other files in that directory for examples.
 
### Adding new Vue Component: Checklist

- [ ] Add a new file under [/cloudsplaining/output/src/components](/cloudsplaining/output/src/components/).
- [ ] Ensure that the component is imported in the [App.vue](/cloudsplaining/output/src/App.vue) file.
- [ ] Ensure that the component is added as a component in the component listing in the [App.vue](/cloudsplaining/output/src/App.vue) file.
- [ ] Ensure that the component is leveraged in the HTML `template` within that [App.vue](/cloudsplaining/output/src/App.vue) file.
- [ ] Ensure that unit tests run successfully

### Building the report for testing

- [ ] Step 1: Make sure it builds successfully locally first with `npm serve` 

```bash
npm serve
# You can then access the application over http://localhost:8080
``` 

- [ ] Step 2: Build new JavaScript bundle files

```bash
npm build
```

This generates JavaScript files that are bundled with [webpack](https://cli.vuejs.org/guide/webpack.html). 

The JavaScript file at [/cloudsplaining/output/dist/index.bundle.js](/tmp/index.bundle.js) contains the **bundled application code**. The JavaScript file at [/cloudsplaining/output/dist/js/chunk-vendors.js](/cloudsplaining/output/dist/js/chunk-vendors.js) contains a bundle of  **all required dependencies** that would other wise be under the `/node_modules/` directory.

The `npm build` command will also generate a file titled `index.html` at  [/cloudsplaining/output/dist/index.html](/cloudsplaining/output/dist/index.html). However, Cloudsplaining does not actually use that file, since that file assumes that the JavaScript is available at local relative paths. Instead, Cloudsplaining injects the **contents** of the `index.bundle.js` file (the application code) and the `chunk-vendors.js` file (the dependencies) into a nearly identical file - [template.html](/cloudsplaining/output/template.html) - along with the results of the Cloudsplaining scan. The relevant sections of the [template.html](/cloudsplaining/output/template.html) file look like this:

```html
<!-- built files will be auto injected -->
<script>
// We declare these variables first - yes, with var - so that we can use Global Variables to our advantage. The application code knows that when `isLocalExample` is set to true, that it should use the sample results data as the IAM data to use for the report. When isLocalExample is set to false (which is always the case when this template.html file is used), it will use the IAM data that is injected inline later in this file.  
    var isLocalExample = false;
    var account_id;
    var account_name;
    var report_generated_time;
    var cloudsplaining_version;
    <!-- NOTE: Cloudsplaining uses Jinja2 templates to inject these values that are supplied at `cloudsplaining scan` time -->
    account_id = "{{ t.account_id }}";
    account_name = "{{ t.account_name }}";
    report_generated_time = "{{ t.report_generated_time }}";
    cloudsplaining_version = "{{ t.cloudsplaining_version }}";

    <!-- NOTE: This will inject "var iam_data = {json.dumps(results)}", with results being the JSON dictionary that stores the Cloudsplaining output-->
    {{ t.results }}

</script>
<-- NOTE: The **contents** of the `chunk-vendors.js` file, which contains the javascript code for third party dependencies (compiled with webpack) is injected here-->
<script>
    {{ t.vendor_bundle_js }}
</script>
<-- NOTE: The **contents** of the `index.bundle.js` file, which contains the application code (compiled with webpack) is injected here-->
<script>
    {{ t.app_bundle_js }}
</script>
``` 

- [ ] Step 3: Create the new sample report

```bash
python3 ./utils/generate_example_report.py
```  

This will generate a new report at `/index.html`.
