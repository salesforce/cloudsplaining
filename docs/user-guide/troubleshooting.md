# Troubleshooting

### Running the command (Path issues)

* *I followed the installation instructions but can't execute the program via command line. What do I do?*

This is likely an issue with your PATH. Your PATH environment variable is not considering the binary packages installed by `pip3`. On a Mac, you can likely fix this by entering the command below, depending on the versions you have installed. YMMV.

```bash
# Python 3.7
export PATH=$HOME/Library/Python/3.7/bin/:$PATH
# Python 3.8
export PATH=$HOME/Library/Python/3.8/bin/:$PATH
```
