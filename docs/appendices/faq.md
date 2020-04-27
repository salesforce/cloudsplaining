# FAQ

* Will it scan all policies by default?

No, it will only scan policies that are attached to IAM principals.

* Will the download command download all policy versions?

Not by default. If you want to do this, specify the `--include-non-default-policy-versions` flag. Note that the `scan` tool does not currently operate on non-default versions.
