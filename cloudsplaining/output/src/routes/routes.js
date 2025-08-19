import Vue from 'vue'
import Router from 'vue-router'
import Summary from '../views/Summary';
import CustomerPolicies from '../views/CustomerPolicies';
import InlinePolicies from '../views/InlinePolicies';
import AwsPolicies from '../views/AwsPolicies';
import IamPrincipals from '../views/IamPrincipals';

Vue.use(Router)

/**
 * Enable anchor-links in Vue-Router.
 *
 * If a link has a hash (e.g. /inline-policies#MyPolicy)
 * Vue-Router acts like a browser and jumps to the element with
 * the selector (id) matching the URL fragment.
 *
 * @param to
 * @param from
 * @param savedPosition
 * @returns {Promise<unknown>|boolean|*}
 */
const scrollStrategy = function (to, from, savedPosition) {
    if (savedPosition) return savedPosition;
    if (!to.hash) return false

    const position = {};

    if (to.hash) {
        position.selector = to.hash
    }
    return position;
}

const routes = [
    {path: '/summary', component: Summary},
    {path: '/customer-policies', component: CustomerPolicies},
    {path: '/inline-policies', component: InlinePolicies},
    {path: '/aws-policies', component: AwsPolicies},
    {path: '/iam-principals', component: IamPrincipals},
];

if (window.show_guidance_nav === "True") {
    routes.push({path: '/guidance', component: () => import('../views/Guidance')});
}

if (window.show_appendices_nav === "True") {
    routes.push({path: '/appendices', component: () => import('../views/Appendices')});
}

routes.push(
    {path: '/', redirect: '/summary'},
    {path: '**', redirect: '/summary'}
);


export default new Router({
    mode: 'hash',
    scrollStrategy,
    routes
})
