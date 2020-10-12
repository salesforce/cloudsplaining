<script>

import { Bar } from 'vue-chartjs'

export default {
  name: "SummaryFindings",
  extends: Bar,
  props: {
      inlinePolicyRisks: {
          type: Object
      },
      awsManagedPolicyRisks: {
          type: Object
      },
      customerManagedPolicyRisks: {
          type: Object
      },
  },
  computed: {
    myStyles() {
      return {
        height: "100%",
        fontSize: 16
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
          "Credentials Exposure",
          "Infrastructure Modification",
        ],
        datasets: [{
          label: "Inline Policies",
          data: Object.values(this.inlinePolicyRisks),// TODO: Fix Scaling Object.values(this.inlinePolicyRisks),
          backgroundColor: [
            "#59575c",
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
                fontSize: 16,
                defaultFontSize: 16,
            }
        },
        tooltips: {
          titleFontSize: 16,
          bodyFontSize: 16,
          footerFontSize: 16,
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
