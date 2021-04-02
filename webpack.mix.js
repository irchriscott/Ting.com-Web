const mix = require('laravel-mix');

mix.setPublicPath('tingstatics/assets');
mix.js('tingvue/js/tingapp.js', 'tingstatics/assets/js');
