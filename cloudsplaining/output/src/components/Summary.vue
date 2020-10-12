<template>
  <div class="report">
    <b-row class="mb-3">
      <b-col>
        <h3>Executive Summary</h3>
        <p>
          This report contains the security assessment results from
          <a href="https://github.com/salesforce/cloudsplaining" rel="noreferrer">Cloudsplaining</a>, which maps out the IAM risk
          landscape in a report.</p>
        <p>
          The assessment identifies where resource ARN constraints are not used and identifies other risks
          in IAM policies:
        </p>
          <ul>
            <li>Privilege Escalation</li>
            <li>Resource Exposure</li>
            <li>Infrastructure Modification</li>
            <li>Data Exfiltration</li>
          </ul>
        <p>
          Remediating these issues, where necessary, will help to limit the blast radius in the case of compromised AWS
          credentials.
        </p>
      </b-col>

    </b-row>

    <b-row class="mb-3">
      <b-col lg="8">
        <div style="" class="d-none d-sm-block">
          <summary-findings
              :inline-policy-risks="inlinePolicyRisks"
              :customer-managed-policy-risks="customerManagedPolicyRisks"
              :aws-managed-policy-risks="awsManagedPolicyRisks"
              :height="200"
          ></summary-findings>
        </div>
      </b-col>
      <b-col>
        <b-table-simple small responsive>
          <b-thead head-variant="dark">
            <b-tr>
              <b-th>Risk</b-th>
              <b-th>Instances</b-th>
              <b-th>Severity</b-th>
            </b-tr>
          </b-thead>
          <b-tbody>
            <b-tr>
              <b-th>Privilege Escalation</b-th>
              <b-td>{{ policyRisks.PrivilegeEscalation }}</b-td>
              <b-td>high</b-td>
            </b-tr>
            <b-tr>
              <b-th>Data Exfiltration</b-th>
              <b-td>{{ policyRisks.DataExfiltration }}</b-td>
              <b-td>med</b-td>
            </b-tr>
            <b-tr>
              <b-th>Resource Exposure</b-th>
              <b-td>{{ policyRisks.ResourceExposure }}</b-td>
              <b-td>med</b-td>
            </b-tr>
            <b-tr>
              <b-th>Credentials Exposure</b-th>
              <b-td>{{ policyRisks.CredentialsExposure }}</b-td>
              <b-td>med</b-td>
            </b-tr>
            <b-tr>
              <b-th>Infrastructure Modification</b-th>
              <b-td>{{ policyRisks.InfrastructureModification }}</b-td>
              <b-td>low</b-td>
            </b-tr>

          </b-tbody>
        </b-table-simple>
      </b-col>

    </b-row>

  </div>
</template>
<script>
// var md = require('markdown-it')({
//     html: true,
//     linkify: true,
//     typographer: true
// });
// import summaryRaw from "../assets/summary.md";
import SummaryFindings from "./charts/SummaryFindings";

// const summary = md.render(summaryRaw);

import {policyViolations} from "../util/other"

export default {
  name: "Summary",
  props: {
    iam_data: Object,
    policyFilter: String
  },
  components: {
    SummaryFindings
  },
  computed: {
    // summary() {
    //     return summary;
    // },
    inlinePolicyRisks() {
      return policyViolations(Object.assign(this.iam_data["inline_policies"]))
    },
    customerManagedPolicyRisks() {
      return policyViolations(Object.assign(this.iam_data["customer_managed_policies"]))
    },
    awsManagedPolicyRisks() {
      return policyViolations(Object.assign(this.iam_data["aws_managed_policies"]))
    },
    policyRisks() {

      if (this.policyFilter === "inlinePolicies") {
        return this.inlinePolicyRisks
      }

      if (["custManaged"].indexOf(this.policyFilter) !== -1) {
        return this.customerManagedPolicyRisks;
      }

      if (["awsManaged"].indexOf(this.policyFilter) !== -1) {
        return this.awsManagedPolicyRisks;
      }

      return {
        "PrivilegeEscalation":
            this.inlinePolicyRisks.PrivilegeEscalation
            + this.awsManagedPolicyRisks.PrivilegeEscalation
            + this.customerManagedPolicyRisks.PrivilegeEscalation,
        "DataExfiltration": this.inlinePolicyRisks.DataExfiltration
            + this.awsManagedPolicyRisks.DataExfiltration
            + this.customerManagedPolicyRisks.DataExfiltration,
        "ResourceExposure":
            this.inlinePolicyRisks.ResourceExposure
            + this.awsManagedPolicyRisks.ResourceExposure
            + this.customerManagedPolicyRisks.ResourceExposure,
        "CredentialsExposure":
            this.inlinePolicyRisks.CredentialsExposure
            + this.awsManagedPolicyRisks.CredentialsExposure
            + this.customerManagedPolicyRisks.CredentialsExposure,
        "InfrastructureModification":
            this.inlinePolicyRisks.InfrastructureModification
            + this.awsManagedPolicyRisks.InfrastructureModification
            + this.customerManagedPolicyRisks.InfrastructureModification
      }
    },

  }
}
</script>

<style scoped>

</style>
