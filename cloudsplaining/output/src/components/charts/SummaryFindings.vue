<template>
    <Bar
        :chart-options="chartOptions"
        :chart-data="chartData"
        :height="height"
        :inline-policy-risks="inlinePolicyRisks"
        :aws-managed-policy-risks="awsManagedPolicyRisks"
        :customer-managed-policy-risks="customerManagedPolicyRisks"
    />
</template>

<script>

import {Bar} from 'vue-chartjs/legacy'
import {Chart, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale} from 'chart.js'

Chart.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
    name: 'SummaryFindings',
    components: {Bar},
    props: {
        height: {
            type: Number,
            default: 200
        },
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
    data() {
        return {
            chartData: {
                labels: [
                    "Privilege Escalation",
                    "Data Exfiltration",
                    "Resource Exposure",
                    "Credentials Exposure",
                    "Infrastructure Modification",
                ],
                datasets: [
                    {
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
                        ]
                    },
                    {
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
            chartOptions: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: "bottom",
                        labels: {
                            font: {
                                size: 16
                            }
                        }
                    },
                    tooltip: {
                        titleFont: {
                            size: 16
                        },
                        bodyFont: {
                            size: 16
                        },
                        footerFont: {
                            size: 16
                        }
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                    },
                    y: {
                        stacked: true
                    }
                }
            }
        }
    }
}

</script>

<style scoped>

</style>
