import iziToast from 'izitoast'

const Toast = {

    methods: {
        showErrorMessage(id, message) {
            iziToast.error({
                id: id,
                timeout: 10000,
                title: 'Error',
                message: message,
                position: 'bottomLeft',
                transitionIn: 'bounceInLeft',
                close: false,
            });
        },
        showSuccessMessage(id, message) {
            iziToast.success({
                id: id,
                timeout: 10000,
                title: 'Success',
                message: message,
                position: 'bottomLeft',
                transitionIn: 'bounceInLeft',
                close: false,
            });
        },        
        showInfoMessage(id, message) {
            iziToast.info({
                id: id,
                timeout: 10000,
                title: 'Info',
                message: message,
                position: 'bottomLeft',
                transitionIn: 'bounceInLeft',
                close: false,
            });
        }
    }
};

export default Toast;