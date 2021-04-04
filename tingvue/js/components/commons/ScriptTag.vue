<template>
    <div><VueScriptComponent :script="'<script>' + script + '</script>'"/></div>
</template>
<script>
    import VueScriptComponent from 'vue-script-component'
    export default {
        name: 'script-tag',
        components: {VueScriptComponent},
        props: {
            script: {
                type: String,
                required: true,
            }    
        },
    }
</script>