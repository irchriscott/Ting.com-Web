const String = {

    methods: {
        capitalize(text){
            return text.replace(text.charAt(0), text.charAt(0).toUpperCase())
        },
        randomString(length) {
            var chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            var result = '';
            for (var i = length; i > 0; --i) result += chars[Math.floor(Math.random() * chars.length)];
            return result;
        }
    }
}

export default String