window._ = require('lodash');

window.Vue = require('vue');
window.$ = window.jQuery = require('./../../tingstatics/assets/js/jquery-2.2.4.min');

Vue.component('style-tag', require('./components/commons/StyleTag.vue').default);
Vue.component('script-tag', require('./components/commons/ScriptTag.vue').default);

Vue.component('discovery', require('./components/user/Discovery.vue').default);

import String from './components/mixins/String'
import Toast from './components/mixins/Toast'

window.onload = function() {
    const app = new Vue({
        el: '#ting-app',
        mixins: [ String, Toast ],
        data() {
            return {}
        },
        mounted() {
            let app = this; 
        },
        methods: {
           
        }
    });
}