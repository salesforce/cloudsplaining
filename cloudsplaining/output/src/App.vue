<template>
    <div id="main">
        <b-navbar toggleable="md" variant="faded">
            <b-navbar-brand to="/summary"> Cloudsplaining </b-navbar-brand>
            <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

            <b-collapse id="nav-collapse" is-nav>
                <b-navbar-nav>
                    <b-nav-item to="/customer-policies"
                        >Customer Policies</b-nav-item
                    >
                    <b-nav-item to="/inline-policies"
                        >Inline Policies</b-nav-item
                    >
                    <b-nav-item to="/aws-policies">AWS Policies</b-nav-item>
                    <b-nav-item to="/iam-principals">IAM Principals</b-nav-item>
                    <b-nav-item v-if="show_guidance_nav" to="/guidance"
                        >Guidance</b-nav-item
                    >
                    <b-nav-item v-if="show_appendices_nav" to="/appendices"
                        >Appendices</b-nav-item
                    >
                    <!-- <b-nav-item to="/task-table">Task Table Demo</b-nav-item> -->
                </b-navbar-nav>
                <b-navbar-nav class="ml-auto">
                    <!-- START NEW ADDITION: CSV Export Button -->
                    <b-nav-item @click="exportToCSV" class="mr-2">
                        <i class="fas fa-file-csv"></i> Export CSV
                </b-nav-item>
                <!-- END NEW ADDITION -->
                <b-nav-text
                    ><strong>Account ID:</strong> {{ account_id }} |
                    <strong>Account Name:</strong>
                    {{ account_name }}</b-nav-text
                >
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>

        <b-container class="mt-3 pb-3 report">
            <b-tabs nav-class="d-none">
                <router-view />
                <!-- <b-tab key="task-table">-->
                <!--                    <br>-->
                <!--                    <h3>Tasks (demo WIP)</h3>-->
                <!--                    <br>-->
                <!--&lt;!&ndash;                    <h3>Customer-Managed Policies</h3>&ndash;&gt;-->
                <!--&lt;!&ndash;                    <TaskTable managedBy="Customer" v-bind:items_mapping="getTaskTableMapping('Customer')"/>&ndash;&gt;-->
                <!--&lt;!&ndash;                    <br>&ndash;&gt;-->
                <!--                    &lt;!&ndash;TODO: Figure out the overlap issue where the two tables results in a double info field in Customer policies&ndash;&gt;-->
                <!--                    <h3>AWS-Managed Policies</h3>-->
                <!--                    <TaskTable managedBy="AWS" v-bind:items_mapping="getTaskTableMapping('AWS')"/>-->
                <!--                    &lt;!&ndash;TODO: Task table for Inline Policies&ndash;&gt;-->
                <!--&lt;!&ndash;                    <h3>Inline Policies</h3>&ndash;&gt;-->
                <!--&lt;!&ndash;                    <TaskTable v-bind:policyNameMapping="getInlinePolicyNameMapping()"/>&ndash;&gt;-->
                <!--                </b-tab> -->
            </b-tabs>
        </b-container>
        <b-container>
            <b-row class="mt-5">
                <b-col class="text-center text-muted">
                    Report Generated: {{ report_generated_time }} &diamond;
                    Cloudsplaining version:
                    <b-link
                        href="https://github.com/salesforce/cloudsplaining"
                        >{{ cloudsplaining_version }}</b-link
                    >
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
const managedPoliciesUtil = require("./util/managed-policies");
const inlinePoliciesUtil = require("./util/inline-policies");
const taskTableUtil = require("./util/task-table");
const sampleData = require("./sampleData");

console.log(`process.env.NODE_ENV: ${process.env.NODE_ENV}`);

// This conditionally loads the local sample data if you are developing, but not if you are viewing the report

// eslint-disable-next-line no-undef
if (process.env.NODE_ENV === "development" || isLocalExample === true) {
    // eslint-disable-next-line no-undef
    console.log(`isLocalExample is set to: ${isLocalExample}`);
    console.log(`process.env.NODE_ENV: ${process.env.NODE_ENV}`);
    console.log(
        `Note: a report generated with the Python template will not have isLocalExample set to True, because that uses a separate template.html file, which has isLocalExample set to False.`
    );
    // eslint-disable-next-line no-unused-vars,no-undef
    iam_data = sampleData.sample_iam_data;

    console.log(
        `IAM Data keys inside the development if statement: ${Object.keys(
            // eslint-disable-next-line no-undef
            iam_data
        )}`
    );
    // eslint-disable-next-line no-unused-vars,no-undef
    account_id = "12345678912";
    // eslint-disable-next-line no-unused-vars,no-undef
    account_name = "example";
    // eslint-disable-next-line no-unused-vars,no-undef
    report_generated_time = "2020-09-01";
    // eslint-disable-next-line no-unused-vars,no-undef
    cloudsplaining_version = "0.2.2";
} else {
    // eslint-disable-next-line no-undef
    console.log(`isLocalExample is set to: ${isLocalExample}`);
}

console.log(
    `IAM Data keys outside of the NODE_ENV if statements: ${Object.keys(
        // eslint-disable-next-line no-undef
        iam_data
    )}`
);

function getManagedPolicyNameMapping(managedBy) {
    // eslint-disable-next-line no-undef
    return managedPoliciesUtil.getManagedPolicyNameMapping(iam_data, managedBy);
}

function getInlinePolicyNameMapping() {
    // eslint-disable-next-line no-undef
    return inlinePoliciesUtil.getInlinePolicyNameMapping(iam_data);
}

function getTaskTableMapping(managedBy) {
    // eslint-disable-next-line no-undef
    return taskTableUtil.getTaskTableMapping(iam_data, managedBy);
}

export default {
    name: "App",
    mounted: function () {
        // Workaround for handling anchors when vue-router is in hash mode
        // https://stackoverflow.com/a/45206192
        setTimeout(() => this.scrollFix(this.$route.hash), 1);
    },
    data() {
        return {
            // eslint-disable-next-line no-undef
            sharedState: iam_data,
            // eslint-disable-next-line no-undef
            account_id: account_id,
            // eslint-disable-next-line no-undef
            account_name: account_name,
            // eslint-disable-next-line no-undef
            report_generated_time: report_generated_time,
            // eslint-disable-next-line no-undef
            cloudsplaining_version: cloudsplaining_version,
            // eslint-disable-next-line no-undef
            show_guidance_nav: show_guidance_nav === "True",
            // eslint-disable-next-line no-undef
            show_appendices_nav: show_appendices_nav === "True",
        };
    },
    computed: {
        iam_data() {
            return this.sharedState;
        },
    },
    methods: {
        getManagedPolicyNameMapping: function (managedBy) {
            return getManagedPolicyNameMapping(managedBy);
        },
        getInlinePolicyNameMapping: function () {
            return getInlinePolicyNameMapping();
        },
        getTaskTableMapping: function (managedBy) {
            return getTaskTableMapping(managedBy);
        },
        scrollFix: function (hashbang) {
            location.hash = hashbang;
        },
        csvEscape(field) {
            if (field == null) {
                return '""';
            }
            // Convert to string and replace double quotes with two double quotes
            let str = String(field);
            str = str.replace(/"/g, '""'); 
            // Always wrap in double quotes to handle commas, semicolons, and escaped double quotes
            return `"${str}"`;
        },
        exportToCSV() {
            // Headers requested in issue #186 for Privilege Escalation findings
            const headers = [
                "Account", 
                "Principal Name", 
                "Principal Type", 
                "Policy Name(s)", 
                "Policy Type", 
                "Privesc Methods Identified"
            ];
            
            // This array will hold the flattened data rows, starting with headers
            let csvRows = [headers.map(h => this.csvEscape(h)).join(',')];
            const accountId = this.account_id;
            const data = this.iam_data;
            
            // Principal types to iterate through
            const principalTypes = ["Roles", "Users", "Groups"];

            principalTypes.forEach(principalType => {
                // Determine singular type name for the CSV column (e.g., "Role" from "Roles")
                const singularPrincipalType = principalType.slice(0, -1); 
                const principals = data[principalType] || {};

                for (const principalName in principals) {
                    const principal = principals[principalName];
                    
                    // Check if this principal has any privilege escalation findings
                    if (principal.findings.privilege_escalation && 
                        principal.findings.privilege_escalation.methods_identified &&
                        principal.findings.privilege_escalation.methods_identified.length > 0) {
                        
                        // Join methods with a semicolon to avoid conflicts with CSV commas
                        const privescMethods = principal.findings.privilege_escalation.methods_identified.join('; ');
                        const policies = principal.policies || {};
                        
                        let policyNames = [];
                        let policyTypes = [];
                        
                        // Collect policy names and types
                        for (const policyName in policies) {
                            const policy = policies[policyName];
                            policyNames.push(policyName);
                            // Determine policy type (Inline vs Managed)
                            if (policy.is_inline) {
                                policyTypes.push("Inline");
                            } else {
                                policyTypes.push("Managed");
                            }
                        }
                        
                        // Deduplicate and join policy types
                        const uniquePolicyTypes = [...new Set(policyTypes)].join('; ');

                        // Build the row array
                        const row = [
                            accountId,
                            principalName,
                            singularPrincipalType, 
                            policyNames.join('; '),
                            uniquePolicyTypes,
                            privescMethods
                        ];
                        
                        // Join and escape all fields for the CSV row
                        csvRows.push(row.map(field => this.csvEscape(field)).join(','));
                    }
                }
            });

            // Trigger the download of the CSV file
            const csvContent = csvRows.join('\n');
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement("a");
            
            if (link.download !== undefined) { 
                const url = URL.createObjectURL(blob);
                link.setAttribute("href", url);
                // Set the filename
                link.setAttribute("download", `cloudsplaining-privesc-export-${Date.now()}.csv`);
                
                // Programmatically click the link to start the download
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                console.error("Browser does not support direct CSV download.");
                alert("Your browser does not support downloading CSV files directly.");
            }
        },
        // END NEW ADDITION
    },
    provide() {
        return {
            iam_data: this.iam_data,
            getManagedPolicyNameMapping: this.getManagedPolicyNameMapping,
            getInlinePolicyNameMapping: this.getInlinePolicyNameMapping,
        };
    },
};
</script>

<style>
#main {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: left;
    color: #2c3e50;
}

.router-link-exact-active {
    font-weight: bold;
}
</style>
