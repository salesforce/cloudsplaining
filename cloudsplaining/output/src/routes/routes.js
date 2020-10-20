import Vue from 'vue'
import Router from 'vue-router'
import Summary from '../views/Summary';
import CustomerPolicies from '../views/CustomerPolicies';
import InlinePolicies from '../views/InlinePolicies';
import AwsPolicies from '../views/AwsPolicies';
import IamPrincipals from '../views/IamPrincipals';
import Guidance from '../views/Guidance';
import Appendices from '../views/Appendices';

Vue.use(Router)
export default new Router({
  routes: [
    { path: '/summary', component: Summary },
    { path: '/customer-policies', component: CustomerPolicies },
    { path: '/inline-policies', component: InlinePolicies },
    { path: '/aws-policies', component: AwsPolicies },
    { path: '/iam-principals', component: IamPrincipals },
    { path: '/guidance', component: Guidance },
    { path: '/appendices', component: Appendices },
    { path: '/', redirect: '/summary' },
    { path: '**', redirect: '/summary' } 
  ]
})