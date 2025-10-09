### Multi-Policy Privilege Escalation Detection

**Previous Limitation:**  
Cloudsplaining analyzed each IAM policy independently, missing privilege escalation risks that arise only from the combination of multiple policies attached to a single principal.

**New Capability:**  
Cloudsplaining now supports *principal-centric* privilege escalation analysis.  
All attached and inline policies are merged before evaluation, enabling detection of composite escalation paths.
