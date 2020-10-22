### What should I do?

* **Review access levels**: Determine whether or not your IAM Policy actually requires access to the actions in this list.
* **Review resource access**: All of the actions in this list do not leverage resource ARN constraints. For example, a lack of resource ARN constraints would be allowing `s3:GetObject` access to `*` resources. Proper usage of resource ARN constraints would include limiting `s3:GetObject` access to a specific S3 object path, like  `aws:s3:::mybucket/*`.
