<template>
    <div><VueScriptComponent :script="'<style type=\'text/css\'>' + css + '</style>'"/></div>
</template>
<script>
    import VueScriptComponent from 'vue-script-component'
    export default {
        name: 'style-tag',
        components: {VueScriptComponent},
        props: {
            css: {
                type: String,
                required: true,
            }    
        },
    }
</script>