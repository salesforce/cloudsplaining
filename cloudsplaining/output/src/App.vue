<template>
    <div id="main">

        <b-navbar toggleable="md" variant="faded">
            <b-navbar-brand href="#" @click="activeSection = 0">
                <img src="https://placekitten.com/g/30/30" class="d-inline-block align-top" alt="Kitten">
                Cloudsplaining
            </b-navbar-brand>
            <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

            <b-collapse id="nav-collapse" is-nav>
                <b-navbar-nav>
                    <b-nav-item
                            :active="activeSection === 'custom-policies'"
                            @click="activeSection = 1"
                            href="#">Customer Policies
                    </b-nav-item>
                    <b-nav-item
                            :active="activeSection === 'inline-policies'"
                            @click="activeSection = 2"
                            href="#">Inline Policies
                    </b-nav-item>
                    <b-nav-item
                            :active="activeSection === 'aws-policies'"
                            @click="activeSection = 3"
                            href="#">AWS Policies
                    </b-nav-item>
                    <b-nav-item
                            :active="activeSection === 'iam-principals'"
                            @click="activeSection = 4"
                            href="#">IAM Principals
                    </b-nav-item>
                    <b-nav-item
                            :active="activeSection === 'guidance'"
                            @click="activeSection = 5"
                            href="#">Guidance
                    </b-nav-item>
                    <b-nav-item
                            :active="activeSection === 'appendices'"
                            @click="activeSection = 6"
                            href="#">Appendices
                    </b-nav-item>
                    <b-nav-item
                            :active="activeSection === 'task-table'"
                            @click="activeSection = 7"
                            href="#">Task Table Demo
                    </b-nav-item>


                </b-navbar-nav>
                <b-navbar-nav class="ml-auto">
                    <b-nav-text><strong>Account ID:</strong> {{ account_id }} | <strong>Account Name:</strong> {{ account_name }}</b-nav-text>
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>

        <b-container class="mt-3 pb-3 report">
            <b-tabs v-model="activeSection" nav-class="d-none">
                <b-tab key="summary">
                    <Summary v-bind:iam_data="iam_data" :policy-filter="policyFilter"/>
                </b-tab>
                <b-tab key="custom-policies">
                    <h3>Customer-Managed Policies</h3>
                    <PolicyTable v-bind:policyNameMapping="getManagedPolicyNameMapping('Customer')"/>
                    <ManagedPolicies v-bind:iam_data="iam_data" managedBy="Customer"/>
                </b-tab>
                <b-tab key="inline-policies">
                    <h3>Inline Policies</h3>
                    <PolicyTable v-bind:policyNameMapping="getInlinePolicyNameMapping()"/>
                    <InlinePolicies v-bind:iam_data="iam_data"/>
                </b-tab>
                <b-tab key="aws-policies">
                    <h3>AWS-Managed Policies</h3>
                    <PolicyTable v-bind:policyNameMapping="getManagedPolicyNameMapping('AWS')"/>
                    <ManagedPolicies v-bind:iam_data="iam_data" managedBy="AWS"/>
                </b-tab>
                <b-tab key="iam-principals">
                    <Principals v-bind:iam_data="iam_data"/>
                </b-tab>
                <b-tab key="guidance">
                    <Guidance/>
                </b-tab>
                <b-tab id="appendices">
                    <Glossary/>
                </b-tab>
                <b-tab key="task-table">
                    <br>
                    <h3>Tasks (demo WIP)</h3>
                    <br>
                    <!--          <h3>Customer-Managed Policies</h3>-->
                    <!--          <TaskTable managedBy="Customer" v-bind:items_mapping="getTaskTableMapping('Customer')"/>-->
                    <!--          <br>-->
                    <!--          TODO: Figure out the overlap issue where the two tables results in a double info field in Customer policies-->
                    <h3>AWS-Managed Policies</h3>
                    <TaskTable managedBy="AWS" v-bind:items_mapping="getTaskTableMapping('AWS')"/>
                    <!--TODO: Task table for Inline Policies-->
                    <!--          <h3>Inline Policies</h3>-->
                    <!--          <TaskTable v-bind:policyNameMapping="getInlinePolicyNameMapping()"/>-->
                </b-tab>


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
    import Summary from './components/Summary.vue';
    import ManagedPolicies from './components/ManagedPolicies';
    import InlinePolicies from './components/InlinePolicies'
    import Principals from './components/Principals'
    import Guidance from './components/Guidance'
    import Glossary from './components/Glossary'
    import PolicyTable from './components/PolicyTable'
    import TaskTable from './components/TaskTable'

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
        console.log(`Note: a report generated with the Python template will not have isLocalExample set to True, because that uses a separate template.html file, which has isLocalExample set to False.`)
        // eslint-disable-next-line no-unused-vars,no-undef
        iam_data = sampleData.sample_iam_data;
        // eslint-disable-next-line no-undef
        console.log(`IAM Data keys: ${Object.keys(iam_data)}`);
        // eslint-disable-next-line no-unused-vars,no-undef
        account_id = "12345678912";
        // eslint-disable-next-line no-unused-vars,no-undef
        account_name = "example";
        // eslint-disable-next-line no-unused-vars,no-undef
        report_generated_time = "2020-09-01";
        // eslint-disable-next-line no-unused-vars,no-undef
        cloudsplaining_version = "0.2.0";
    }
    else {
        // eslint-disable-next-line no-undef
        console.log(`isLocalExample is set to: ${isLocalExample}`)
    }

    // eslint-disable-next-line no-undef
    console.log(`IAM Data keys: ${iam_data}`);


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
        components: {
            Summary,
            ManagedPolicies,
            InlinePolicies,
            Principals,
            Guidance,
            Glossary,
            PolicyTable,
            TaskTable
        },

        data() {
            return {
                // eslint-disable-next-line no-undef
                sharedState: iam_data,
                policyFilter: "none",
                activeSection: 0,
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
</style>
