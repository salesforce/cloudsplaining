### What should I do?

* **Review access levels**: Determine whether or not your IAM Policy actually requires access to the actions in this list.
* **Review resource access**: All of the actions in this list do not leverage resource ARN constraints. For example, a lack of resource ARN constraints would be allowing `s3:GetObject` access to `*` resources. Proper usage of resource ARN constraints would include limiting `s3:GetObject` access to a specific S3 object path, like  `aws:s3:::mybucket/*`, 

If your IAM policy **does** require access to those actions, you should provide an explanation. Example requirements include:
* "User Role: This IAM Policy is used by an IAM Role that requires access to `*` resources. We have restricted the access levels appropriate to what the user needs"
* "System roles"


Your IAM policy includes the IAM actions from this list, but without any resource ARN constraints. Resource ARN constraints is the practice of setting IAM actions t


* Review the IAM actions from this list. 

For assistance, you can 

