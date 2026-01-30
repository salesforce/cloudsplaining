import { createRouter, createWebHashHistory } from 'vue-router'
import Summary from '../views/Summary';
import CustomerPolicies from '../views/CustomerPolicies';
import InlinePolicies from '../views/InlinePolicies';
import AwsPolicies from '../views/AwsPolicies';
import IamPrincipals from '../views/IamPrincipals';
import Guidance from '../views/Guidance';
import Appendices from '../views/Appendices';

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
const scrollBehavior = function (to, from, savedPosition) {
    if (savedPosition) {
        return savedPosition;
    }
    if (!to.hash) {
        return false;
    }
    return {
        el: to.hash
    };
}

const routes = [
    {path: '/summary', component: Summary},
    {path: '/customer-policies', component: CustomerPolicies},
    {path: '/inline-policies', component: InlinePolicies},
    {path: '/aws-policies', component: AwsPolicies},
    {path: '/iam-principals', component: IamPrincipals},
];

if (typeof window !== 'undefined' && window.show_guidance_nav === "True") {
    routes.push({path: '/guidance', component: Guidance});
}

if (typeof window !== 'undefined' && window.show_appendices_nav === "True") {
    routes.push({path: '/appendices', component: Appendices});
}

routes.push(
    {path: '/', redirect: '/summary'},
    {path: '/:pathMatch(.*)*', redirect: '/summary'}
);

export default createRouter({
    history: createWebHashHistory(),
    scrollBehavior,
    routes
});
