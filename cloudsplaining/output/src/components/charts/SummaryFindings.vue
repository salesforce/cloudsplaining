<script>

import { Bar } from 'vue-chartjs'

export default {
  name: "SummaryFindings",
  extends: Bar,
  props: ["inlinePolicyRisks", "managedPolicyRisks"],
  computed: {
    myStyles() {
      return {
        height: "100%"
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
            "#f87979",
            "#f87979",
            "#f87979",
            "#f87979",
          ]
        },
          {
            label: "Managed Policies",
            data: Object.values(this.managedPolicyRisks), // TODO: Fix scaling for dynamic values Object.values(this.managedPolicyRisks)
            backgroundColor: [
              "#2247c6",
              "#2247c6",
              "#2247c6",
              "#2247c6",
              "#2247c6",
            ]
          }]
      },
      options: {
        responsive: true,
        legend: {display: true, position: "bottom"},
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
