<script>

import { Bar } from 'vue-chartjs'

export default {
  name: "SummaryFindings",
  extends: Bar,
  props: ["inlinePolicyRisks", "awsManagedPolicyRisks", "customerManagedPolicyRisks"],
  computed: {
    myStyles() {
      return {
        height: "100%",
          fontSize: 14
      }
    }
  },
  data: function () {
    return {
      chartData: {
        labels: [
          "Privilege Escalation",
          "Data Exfiltration",
          "Resource Exposure",
          "Infrastructure Modification"
        ],
        datasets: [{
          label: "Inline Policies",
          data: Object.values(this.inlinePolicyRisks),// TODO: Fix Scaling Object.values(this.inlinePolicyRisks),
          backgroundColor: [
            "#59575c",
            "#59575c",
            "#59575c",
            "#59575c",
          ]
        },
          {
            label: "AWS-managed Policies",
            data: Object.values(this.awsManagedPolicyRisks), // TODO: Fix scaling for dynamic values Object.values(this.managedPolicyRisks)
            backgroundColor: [
              "#215ca0",
              "#215ca0",
              "#215ca0",
              "#215ca0",
              "#215ca0",
            ]
          },{
            label: "Customer-managed Policies",
            data: Object.values(this.customerManagedPolicyRisks), // TODO: Fix scaling for dynamic values Object.values(this.managedPolicyRisks)
            backgroundColor: [
              "#00857d",
              "#00857d",
              "#00857d",
              "#00857d",
              "#00857d",
            ]
          }
          ]
      },
      options: {
        responsive: true,
        legend: {
            display: true,
            position: "bottom",
            labels: {
                fontSize: 14,
                defaultFontSize: 14,
            }
        },
        tooltips: {
          titleFontSize: 14,
          bodyFontSize: 14,
          footerFontSize: 14,
        },
        scales: {
          xAxes: [{
            stacked: true,
          }],
          yAxes: [{
            stacked: true
          }]
        },

      }
    }
  },
  mounted() {
    this.renderChart(this.chartData, this.options)
  }
}
</script>

<style scoped>

</style>
