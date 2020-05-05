# Troubleshooting

**I followed the installation instructions but can't execute the program via command line at all. What do I do?**

This is likely an issue with your PATH. Your PATH environment variable is not considering the binary packages installed by `pip3`. On a Mac, you can likely fix this by entering the command below, depending on the versions you have installed. YMMV.

```bash
export PATH=$HOME/Library/Python/3.7/bin/:$PATH
```

**I followed the installation instructions but I am receiving a `ModuleNotFoundError` that says `No module named policy_sentry.analysis.expand`. What should I do?**

Try upgrading to the latest version of Cloudsplaining. This error was fixed in version 0.0.10.
