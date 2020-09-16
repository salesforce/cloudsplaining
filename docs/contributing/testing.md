# Testing


##  Local Unit Testing and Integration Testing

We highly suggest that you run all the tests before pushing a significant commit. It would be painful to copy/paste all of those lines above - so we’ve compiled a test script in the utils folder.

Just run this from the root of the repository:


```bash
./utils/run_tests.sh
```

It will execute all of the tests that would normally be run during the GitHub actions build. If you want to see if it will pass the tests in GitHub actions, you can just run that quick command on your machine.

