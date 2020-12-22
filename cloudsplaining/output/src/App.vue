<template>
    <div id="main">
        <b-navbar toggleable="md" variant="faded">
            <b-navbar-brand to="/summary">
                Cloudsplaining
            </b-navbar-brand>
            <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

            <b-collapse id="nav-collapse" is-nav>
                <b-navbar-nav>
                    <b-nav-item to="/customer-policies">Customer Policies</b-nav-item>
                    <b-nav-item to="/inline-policies">Inline Policies</b-nav-item>
                    <b-nav-item to="/aws-policies">AWS Policies</b-nav-item>
                    <b-nav-item to="/iam-principals">IAM Principals</b-nav-item>
                    <b-nav-item to="/guidance">Guidance</b-nav-item>
                    <b-nav-item to="/appendices">Appendices</b-nav-item>
                    <!-- <b-nav-item to="/task-table">Task Table Demo</b-nav-item> -->
                </b-navbar-nav>
                <b-navbar-nav class="ml-auto">
                    <b-nav-text><strong>Account ID:</strong> {{ account_id }} | <strong>Account Name:</strong> {{ account_name }}</b-nav-text>
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>

        <b-container class="mt-3 pb-3 report">
            <b-tabs nav-class="d-none">
                <router-view />
<!--                <b-tab key="task-table">-->
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
<!--                </b-tab>-->
            </b-tabs>
        </b-container>
        <b-container>
            <b-row class="mt-5">
                <b-col class="text-center text-muted">
                    Report Generated: {{ report_generated_time }} &diamond;
                    Cloudsplaining version:
                    <b-link href="https://github.com/salesforce/cloudsplaining">{{ cloudsplaining_version }}</b-link>
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
    const managedPoliciesUtil = require('./util/managed-policies');
    const inlinePoliciesUtil = require('./util/inline-policies');
    const taskTableUtil = require('./util/task-table');
    const sampleData = require('./sampleData');

    console.log(`process.env.NODE_ENV: ${process.env.NODE_ENV}`)

    // This conditionally loads the local sample data if you are developing, but not if you are viewing the report

    // eslint-disable-next-line no-undef
    if ((process.env.NODE_ENV === "development") || (isLocalExample === true)) {
        // eslint-disable-next-line no-undef
        console.log(`isLocalExample is set to: ${isLocalExample}`)
        console.log(`process.env.NODE_ENV: ${process.env.NODE_ENV}`)
        console.log(`Note: a report generated with the Python template will not have isLocalExample set to True, because that uses a separate template.html file, which has isLocalExample set to False.`)
        // eslint-disable-next-line no-unused-vars,no-undef
        iam_data = sampleData.sample_iam_data;
        // eslint-disable-next-line no-undef
        console.log(`IAM Data keys inside the development if statement: ${Object.keys(iam_data)}`);
        // eslint-disable-next-line no-unused-vars,no-undef
        account_id = "12345678912";
        // eslint-disable-next-line no-unused-vars,no-undef
        account_name = "example";
        // eslint-disable-next-line no-unused-vars,no-undef
        report_generated_time = "2020-09-01";
        // eslint-disable-next-line no-unused-vars,no-undef
        cloudsplaining_version = "0.2.2";
    }
    else {
        // eslint-disable-next-line no-undef
        console.log(`isLocalExample is set to: ${isLocalExample}`)
    }

    // eslint-disable-next-line no-undef
    console.log(`IAM Data keys outside of the NODE_ENV if statements: ${Object.keys(iam_data)}`);


    function getManagedPolicyNameMapping(managedBy) {
        // eslint-disable-next-line no-undef
        return managedPoliciesUtil.getManagedPolicyNameMapping(iam_data, managedBy)
    }

    function getInlinePolicyNameMapping() {
        // eslint-disable-next-line no-undef
        return inlinePoliciesUtil.getInlinePolicyNameMapping(iam_data)
    }

    function getTaskTableMapping(managedBy) {
        // eslint-disable-next-line no-undef
        return taskTableUtil.getTaskTableMapping(iam_data, managedBy)
    }


    export default {
        name: 'App',
        mounted: function()
        {
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
            };
        },
        computed: {
            iam_data() {
                return this.sharedState
            }
        },
        methods: {
            getManagedPolicyNameMapping: function (managedBy) {
                return getManagedPolicyNameMapping(managedBy)
            },
            getInlinePolicyNameMapping: function () {
                return getInlinePolicyNameMapping()
            },
            getTaskTableMapping: function (managedBy) {
                return getTaskTableMapping(managedBy)
            },
            scrollFix: function(hashbang)
            {
                location.hash = hashbang;
            }
        },
        provide() {
            return {
                iam_data: this.iam_data,
                getManagedPolicyNameMapping: this.getManagedPolicyNameMapping,
                getInlinePolicyNameMapping: this.getInlinePolicyNameMapping,
            }
        }
    }
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
