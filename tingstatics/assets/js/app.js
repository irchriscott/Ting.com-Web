/*  THIS JS SHEET BELONGS TO TING.COM
    Author: Ir Christian Scott -> Code Pipes Solutions
    Date : 23 April 2019
*/

const SHOW_ORDERS = 'show_orders'
const SHOW_PLACEMENTS = 'show_placements'
const use_old = false;

let markers = [];

$(document).ready(function(){

    new Swiper('.blog-slider', {
        spaceBetween: 30,
        effect: 'fade',
        loop: true,
        autoplay: {
            delay: 10000,
        },
        mousewheel: false,
        pagination: {
            el: '.blog-slider__pagination',
            clickable: true,
        }
    });

    new Swiper('.ting-promotions-container', {
        spaceBetween: 30,
        effect: 'fade',
        loop: true,
        autoplay: {
            delay: 10000,
        },
        mousewheel: false,
        pagination: {
            el: '.ting-promotions-pagination',
            clickable: true,
        }
    });

    $('.active-testimonial').owlCarousel({
        items: 2,
        loop: true,
        margin: 20,
        dots: true,
        autoplay: true,
        nav: true,
        navText: ["<span class='lnr lnr-arrow-up'></span>", "<span class='lnr lnr-arrow-down'></span>"],        
        responsive: {
            0: { items: 1 },
            480: { items: 1 },
            768: { items: 2 }
        }
    });

    loadtingdotcom();

    $("#ting-open-add-restaurant-location").click(function (e) {
        
        e.preventDefault();
        
        getUserCurrentLocation("ting-restaurant-latitude", "ting-restaurant-longitude", "ting-search-location-input", "ting-restaurant-town", "ting-restaurant-country", "ting-search-location-input-else", "ting-restaurant-place-id", "ting-restaurant-region", "ting-restaurant-road");
        
        setTimeout(function () {
            initializeRestaurantMap("ting-restaurant-latitude", "ting-restaurant-longitude", "ting-search-location-input", "ting-search-location-input-else", "ting-restaurant-place-id", "ting-restaurant-region", "ting-restaurant-road", "ting-restaurant-map-container", true, "");
        }, 1000);

        $("#ting-add-new-branch").modal('show');

        $("#ting-add-restaurant-location").modal({
            closable: false,
            onDeny: function () {
                $("#ting-add-new-restaurant").click();
            },
            onApprove: function () {
                $("#ting-search-location-input").val($("#ting-search-location-input-else").val());
                $("#ting-add-new-restaurant").click();
            }
        }).modal('show');
    });

    $("#ting-open-add-user-location").click(function (e) {
        
        e.preventDefault();
        
        setTimeout(function () {
            initializeRestaurantMap("ting-lat", "ting-long", "ting-addr", "ting-user-address", "ting-place", "ting-region", "ting-road", "ting-user-map-container", true, "");
        }, 1000);

        $("#ting-add-restaurant-location").modal({
            closable: false,
            onDeny: function () {
                $("#ting-open-user-registration").click();
            },
            onApprove: function () {
                $("#ting-addr").val($("#ting-user-address").val());
                $("#ting-open-user-registration").click();
            }
        }).modal('show');
    });

    $("#ting-admin-forgot-password").click(function(e){
        e.preventDefault();
        $("#ting-admin-forgot-password-modal").modal({
            closable: false,
            onDeny: function () {
                $("#ting-admin-login").click();
            },
            onApprove: function () {}
        }).modal('show');
    });

    $("#ting-user-forgot-password").click(function(e){
        e.preventDefault();
        $("#ting-user-forgot-password-modal").modal({
            closable: false,
            onDeny: function () {
                $("#ting-user-login").click();
            },
            onApprove: function () {}
        }).modal('show');
    });

    $("#ting-open-user-registration").click(function(e){
        e.preventDefault();
        $("#ting-user-registration-modal").modal({
            closable:false,
            onDeny: function(){
                $("#ting-user-login").click();
            },
            onApprove: function(){},
            onShow: function(){
                let today = new Date();
                $("#ting-date-of-birth").calendar({
                    type: 'date',
                    maxDate: new Date(today.getFullYear(), today.getMonth(), today.getDate() - 1),
                    monthFirst: false,
                    formatter: {
                        date: function (date, settings) {
                            if (!date) return '';
                            var day = date.getDate();
                            var month = date.getMonth() + 1;
                            var year = date.getFullYear();
                            return year + '-' + month + '-' + day;
                        }
                    }
                });
            }
        }).modal("show");
    });

    var today = new Date();

    $("#ting-date-of-birth").calendar({
        type: 'date',
        maxDate: new Date(today.getFullYear(), today.getMonth(), today.getDate() - 1),
        monthFirst: false,
        formatter: {
            date: function (date, settings) {
                if (!date) return '';
                var day = date.getDate();
                var month = date.getMonth() + 1;
                var year = date.getFullYear();
                return year + '-' + month + '-' + day;
            }
        }
    });

    $("#ting-add-new-restaurant").openModal();
    $("#ting-add-restaurant-location").openModal();
    $("#ting-add-new-category").openModal();
    $("#ting-add-new-package").openModal();
    $("#ting-admin-login").openModal();
    $("#ting-admin-edit-restau-profile").openModal();
    $("#ting-admin-edit-restau-config").openModal();
    $("#ting-admin-edit-profile").openModal();
    $("#ting-admin-add-new-administrator").openModal();
    $("#ting-admin-add-new-category").openModal();
    $(".ting-open-ajax-modal").openModal();
    $("#ting-admin-add-new-menu-food").openModal();
    $("#ting-admin-add-new-menu-drink").openModal();
    $("#ting-admin-add-new-menu-dish").openModal();
    $("#ting-admin-add-new-branch").openModal();
    $("#ting-admin-add-new-table").openModal();
    $("#ting-admin-add-new-promotion").openModal();
    $("#ting-user-login").openModal();
    $("#ting-edit-email-address").openModal();
    $("#ting-edit-password").openModal();
    $("#ting-admin-edit-branch-profile").openModal();
    $("#ting-admin-edit-restau-categories").openModal();

    $("#ting-map-form").submit(function(e){
        e.preventDefault();
    });

    $("#ting-search-location-input-else").searchLocationByAddress("ting-restaurant-latitude", "ting-restaurant-longitude", "ting-search-location-input", "ting-search-location-input-else", "ting-restaurant-place-id", "ting-restaurant-region", "ting-restaurant-road", "ting-restaurant-map-container", true, "")
    $("#ting-user-address").searchLocationByAddress("ting-lat", "ting-long", "ting-addr", "ting-user-address", "ting-region", "ting-road", "ting-place", "ting-user-map-container", true, "")

    $("select.dropdown, .dropdown").dropdown("hide");
    $("div.rating, .rating, .ui.rating").rating("disable");
    $(".ting-popup").popup();

    $("#ting-new-restaurant-form").submitFormAjax();
    $("#ting-new-category-form").submitFormAjax();
    $("#ting-new-package-form").submitFormAjax();
    $("#ting-admin-login-form").submitFormAjax();
    $("#ting-user-login-form").submitFormAjax();
    $("#ting-activate-licence-key").submitFormAjax();
    $("#ting-admin-edit-restaurant-form").submitFormAjax();
    $("#ting-admin-config-restaurant-form").submitFormAjax();
    $("#ting-admin-edit-profile-form").submitFormAjax();
    $("#ting-admin-change-password-form").submitFormAjax();
    $("#ting-add-administrator-profile-form").submitFormAjax();
    $("#ting-add-category-form").submitFormAjax();
    $("#ting-add-menu-food-form").submitFormAjax();
    $("#ting-admin-reset-password").submitFormAjax();
    $("#ting-user-reset-password").submitFormAjax();
    $("#ting-add-menu-drink-form").submitFormAjax();
    $("#ting-add-menu-dish-form").submitFormAjax();
    $("#ting-add-branch-form").submitFormAjax();
    $("#ting-add-table-form").submitFormAjax();
    $("#ting-add-promotion-form").submitFormAjax();
    $("#ting-admin-branch-profile-form").submitFormAjax();
    $("#ting-admin-edit-categories-form").submitFormAjax();

    $("#ting-user-registration-form").submit(function(e){
        e.preventDefault();
        var action = $(this).attr("action");
        var method = $(this).attr("method");
        var data = new FormData($(this)[0]);
        let button = $(this).find("button[type=submit]");
        let loader = $(this).find(".ting-loader");
        $.ajax({
            xhr: function () {
                var xhr = new window.XMLHttpRequest();
                button.attr("disabled", "disabled");
                if(loader != null) loader.show();
                return xhr;
            },
            beforeSend: function( xhr ) {
                data.append("country", $("#ting-country").val());
                data.append("town", $("#ting-town").val());
                data.append("address", $("#ting-addr").val());
                data.append("longitude", $("#ting-long").val());
                data.append("latitude", $("#ting-lat").val());
                data.append("type", "Home");
                data.append("link", window.location.href);
            },
            type: method,
            url: action,
            data: data,
            processData: false,
            contentType: false,
            success: function(response){
                if(response.type == "success" || response.type == "info"){
                    showSuccessMessage(response.type, response.message);
                    if(loader != null) loader.hide();
                    button.removeAttr("disabled");
                    if(response.redirect != null) window.location = response.redirect;
                } else {
                    button.removeAttr("disabled");
                    if(loader != null) loader.hide();
                    showErrorMessage(response.type, response.message);
                    if(response.msgs.length > 0){
                        response.msgs.forEach(msg => {
                            var title = capitalize(msg[0])
                            msg[1].forEach(err => {
                                showErrorMessage(randomString(10), `<b>${title} : </b> ${err}`);
                            });
                        });
                    }
                }
            },
            error: function(_, t, e){
                button.removeAttr("disabled");
                if(loader != null) loader.hide();
                showErrorMessage(t, e);
            }
        });
    });

    $("#ting-edit-email-address-form").submitFormAjax();
    $("#ting-edit-password-form").submitFormAjax();
    $("#ting-edit-private-profile").submitFormAjax();
    $("#ting-edit-public-profile").submitFormAjax();

    $("#ting-session-profile-image-update").submitProfileImage();

    $("#ting-open-profile-img-input").click(function(e){
        e.preventDefault();
        $("#ting-profile-img-input").click();
    });

    $("#ting-profile-img-input").change(function(){ updateProfileImage(this);});

    $("#ting-single-image-input").change(function(e){ singleImagePreview(this, "ting-single-image-preview"); });

    $("#ting-multiple-image-input").change(function(e){ multipleImagesPreview(this, $(".ting-item-images-preview"));});

    $(".ting-textarea-froala-editor").setFroalaEditor();

    $(window).scroll(function(){
        if($(this).scrollTop() >= 23){$(".ting-user-top-fixed-menu").show();} 
        else {$(".ting-user-top-fixed-menu").hide();}
        if($(this).scrollTop() >= 1004){$("#ting-menus-sticky").addClass("ting-fix-left").css("width", $("#ting-menus-sticky").width() + "px !important;");} 
        else {$("#ting-menus-sticky").removeClass("ting-fix-left").removeAttr("style");}
    });

    $(".ting-cuisine-item").hover(function(){
        $(this).find(".ting-cuisine-about").animate({"bottom": "0px"}, 200);
    }, function(){$(this).find(".ting-cuisine-about").animate({"bottom": "-54px"}, 200);});

    $("#ting-cuisines-carousel").navigateCuisines();

    if(getCookie(SHOW_PLACEMENTS) == 1) {
        $("#ting-admin-placements-panel-dashboard").show();
        $("#ting-maximize-placements").hide();
    } else {
        $("#ting-admin-placements-panel-dashboard").hide();
        $("#ting-maximize-placements").show();
    }

    updateAdminContainer();

    if(getCookie(SHOW_ORDERS) == 1) {
        $("#ting-admin-orders-panel-dashboard").show();
        $("#ting-maximize-orders").hide();
    } else {
        $("#ting-admin-orders-panel-dashboard").hide();
        $("#ting-maximize-orders").show();
    }

    $("#ting-minimize-placements").click(function() {
        toogleShowPlacements();
    });

    $("#ting-maximize-placements").click(function() {
        toogleShowPlacements();
    });

    $("#ting-minimize-orders").click(function() {
        toogleShowOrders();
    });

    $("#ting-maximize-orders").click(function() {
        toogleShowOrders();
    });

    $(document).on("keyup", function(e){
        if(e.keyCode === 27) {
            $("#ting-search-overlay, #ting-search-container, #ting-search-form-spinner").hide();
            $("html, body").removeClass("ting-hide-sb");
        }
        if((e.shiftKey || e.altKey) && e.keyCode === 83){
            $("#ting-search-overlay, #ting-search-container").show().find("input").focus();
            $("html, body").addClass("ting-hide-sb");
        }
    });

    $("#ting-seach-toggle").click(function(e){
        e.stopPropagation();
        e.preventDefault();
        $("#ting-search-overlay, #ting-search-container").show().find("input").focus();
        $("html, body").addClass("ting-hide-sb");
    });
    $("#ting-search-container-sub").click(function(e) {
        e.stopPropagation();
    });
    $("#ting-search-overlay, #ting-search-container").click(function(e){
        e.preventDefault();
        $("#ting-search-overlay").hide();
        $("#ting-search-container, #ting-search-form-spinner").hide();
        $("html, body").removeClass("ting-hide-sb");
    });
     $("#ting-live-search").tingLiveSeacrh();
    $(".ting-search-results-all .ting-search-data").click(function(){window.location = $(this).attr("data-url");});
});

function toogleShowPlacements() {
    if(getCookie(SHOW_PLACEMENTS) == 1) {
        $("#ting-admin-placements-panel-dashboard").slideUp(300);
        $("#ting-maximize-placements").fadeIn();
        setCookie(SHOW_PLACEMENTS, 0, 30);
    } else {
        $("#ting-admin-placements-panel-dashboard").slideDown(300);
        $("#ting-maximize-placements").fadeOut();
        setCookie(SHOW_PLACEMENTS, 1, 30);
    }
    updateAdminContainer();
}

function toogleShowOrders() {
    if(getCookie(SHOW_ORDERS) == 1) {
        $("#ting-admin-orders-panel-dashboard").slideUp(300);
        $("#ting-maximize-orders").fadeIn();
        setCookie(SHOW_ORDERS, 0, 30);
    } else {
        $("#ting-admin-orders-panel-dashboard").slideDown(300);
        $("#ting-maximize-orders").fadeOut();
        setCookie(SHOW_ORDERS, 1, 30);
    }
    updateAdminContainer();
}

function updateAdminContainer() {
    var can_show_placements = getCookie(SHOW_PLACEMENTS) == 1;
    var can_show_orders = getCookie(SHOW_ORDERS) == 1;
    var container = $("#ting-admin-content-panel-dashboard");
    var order_pannels = $(".ting-admin-orders-panel");
    if(container.length > 0) {
        if(container.attr("data-placement").toLowerCase() != "true" && order_pannels.length < 2) {
            if(can_show_orders) { container.removeClass("twelve").attr("class", "sixteen " + container.attr("class")); }
            else { container.removeClass("sixteen").attr("class", "twelve " + container.attr("class")); }
        } else {
            if(can_show_orders && can_show_placements) {
                container.removeClass("sixteen").removeClass("twelve").attr("class", "eight " + container.attr("class"));
            } else if(can_show_placements || can_show_orders) {
                container.removeClass("sixteen").removeClass("eight").attr("class", "twelve " + container.attr("class"));
            } else if (!can_show_placements && !can_show_orders){ 
                container.removeClass("eight").removeClass("twelve").attr("class", "sixteen " + container.attr("class")); 
            } else {}
        }
        try { reflowCharts(); } catch(e) {}
    }
}

function loadtingdotcom(){

    if (!navigator.geolocation) {
        $.getJSON('https://ipapi.co/json/', function(data) {
            tingdotcom(data.latitude, data.longitude, data.address, data.country_name, data.city, data.region, "")
        }).error(function(_, t, e){tingdotcom(0, 0, "", "", "", "", "");});
        return showErrorMessage('error_geolocation', 'Geolocation not supported by your browser');
    }
    navigator.geolocation.getCurrentPosition(function (position) {
        try{
            var geocoder = new google.maps.Geocoder();
            var location = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);

            geocoder.geocode({ 'latLng': location }, function (results, status) {

                if (status == google.maps.GeocoderStatus.OK) {
                    var length = results[0].address_components.length
                    var country = getaddresstype(results[0].address_components, "country")
                    var town_1 = getaddresstype(results[0].address_components, "administrative_area_level_2")
                    var town_2 = getaddresstype(results[0].address_components, "locality")
                    var region_1 = getaddresstype(results[0].address_components, "sublocality_level_1")
                    var region_2 = getaddresstype(results[0].address_components, "sublocality_level_2")
                    var road = getaddresstype(results[0].address_components, "route")
                    var region = region_2 !== undefined && region_2 !== null && region_2 != "Unknown" ? region_2 : region_1
                    var town = town_1 !== undefined && town_1 !== null && town_1 != "Unknown" ? town_1 : town_2
                    tingdotcom(position.coords.latitude, position.coords.longitude, results[0].formatted_address, country, town, region, road)
                }
            });
        } catch(e){
            $.getJSON('https://ipapi.co/json/', function(data) {
                tingdotcom(data.latitude, data.longitude, data.address, data.country_name, data.city, data.region, "")
            }).error(function(_, t, e){tingdotcom(0, 0, "", "", "", "", "");});
        }
        
    }, function (e) { 

        $.getJSON('https://ipapi.co/json/', function(data) {
            tingdotcom(data.latitude, data.longitude, data.address, data.country_name, data.city, data.region, "")
        }).error(function(_, t, e){tingdotcom(0, 0, "", "", "", "", "");});

    }, {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
    });
}

function getaddresstype(d, t) {
    if(d.length > 0) {
        for (var i = 0; i < d.length; i++) {
            if(d[i].types.includes(t)) { return d[i].long_name } 
        }
        return "Unknown"
    } else { return "Unknown" }
}

function tingdotcom(lat, long, addr, cntr, twn, reg, rd){

    if(typeof cntr == 'object'){cntr = cntr.long_name}
    if(typeof twn == 'object'){twn = twn.long_name}

    var state = window.__TING__Link;
    var session = window.__TING__Session;
    var sloc = {};

    if (state != null && state != undefined && typeof state == 'object'){

        if(state.type == "global"){

            if(state.name == "restaurants"){

                var branches = window.__TING__Restaurants
                var usl = $("#ting-user-locations");
                usl.empty();
                usl.append(`<option value="0">Current Location</option>`);

                var fbs = [];

                var fb__values = { availability: [], cuisines: [], services: [],
                                   specials: [], types: [], ratings: [] };

                var usa = {lat: lat, lng: long}; sloc = usa;
                branches = newBranches(branches, usa);
                var branches__else = newBranches(window.__TING__Restaurants, usa, false);

                var c = $("#ting-restaurants-list");
                var g = $(`<div class="ui grid" style="position: relative;"></div>`);
                var r = $(`<div class="row" style="position: relative;"></div>`);
                var fc = $(`<div class="col-lg-4"></div>`);
                var rc = $(`<div class="col-lg-8" style="padding-right: 0;"></div>`);
                var md = $(`<div class="ting-cnt-item"></div>`);
                rc.append(md);

                var pag__p = [];
                var pag__s = 0;
                var pag__m = 15;
                var pag__cont = $(`<div class="ui right floated pagination menu"></div>`);
                rc.append(pag__cont);

                var fcd = $(`<div class="ui ting-filter-by"></div>`);
                var hf = `<h4 style="text-transform:uppercase; font-weight:100;">Search Restaurant</h4><hr/>`;
                fcd.append(hf);
                var cd = $(`<select name="country" id="ting-restaurant-filter-country" class="ui dropdown"></select>`);
                cd.append(`<option value="all">All</option>`);
                cd.append(`<option value="${cntr}">Current</option>`);
                var cntrs = window.__TING__Countries;
                for(var k = 0; k < cntrs.length; k++){cd.append(`<option value="${cntrs[k].country.toLowerCase()}">${cntrs[k].country}</option>`);}
                    
                var f = $(`<form class="ui form" action="${window.__TING__URL_Filter_Restaurants}" method="GET"></form>`);
                f.append(`<div class="field">
                                <label>Restaurant Or Branch Name :</label>
                                <input type="text" id="ting-restaurant-filter-name" name="name" placeholder="Restaurant Or Branch Name" autocomplete="off" />
                            </div>`);
                var cdc = $(`<div class="field"></div>`);
                cdc.append(`<label>Select Country</label>`);
                cdc.append(cd);
                f.append(cdc).append(`<script>$("select").dropdown()</script>`);
                f.append(`<button class="ui button medium primary fluid" type="submit">${"Search".toUpperCase()}</button>`);
                    
                fcd.append(f);fc.append(fcd).append(`<br/>`);
                var hff = `<h4 style="text-transform:uppercase; font-weight:100;">Filter By</h4><hr/>`;
                var fbc = $(`<div class="ui ting-filter-by"></div>`);

                f.submit(function(e){ 
                    e.preventDefault(); searchfilterbranches();
                    $.ajax({
                        type: "GET", url: window.__TING__URL_Load_Filters_Data,
                        data: {
                            query: $("body").find("#ting-restaurant-filter-name").val(),
                            country: $("body").find("#ting-restaurant-filter-country").val() 
                        },
                        success: function(res){
                            fbc.empty();
                            window.__TING__Filters = res;
                            updateFilters(res);
                        }, error: function(_, t, e){showErrorMessage(t, e);}
                    })
                });

                var filtercbx = function(t, v, gv, q, c=false){
                    return `<label class="ting-checkbox-container">
                                ${t}
                                <span class="ting-checkbox-quantity">${numerilize(q, gv, 0)}</span>
                                <input type="checkbox" value="${v}" data-g-value="${gv}" ${c ? `checked` : ``}>
                                <span class="ting-checkbox-checkmark"></span>
                            </label>`;
                };

                var fb__hr = `<hr>`; var fb__h5__st = `style="font-size:15px; margin-bottom:1rem !important; text-transform: uppercase;"`;

                var filters = window.__TING__Filters;

                function updateFilters(filters) {
                    
                    fbc.empty();
                    fbc.append(hff)

                    var fb__availability = `<h5 ${fb__h5__st}>Availability</h5>`;
                    var fb__a__a = $(filtercbx("Not Available", false, "avail", branches.filter(function(b){return b.isAvailable == false}).length));
                    var fb__a__b = $(filtercbx("Opened", "opened", "avail", branches.filter(function(b){
                        if(b.isAvailable == true){
                            var s = statusWorkTime(b.restaurant.opening, b.restaurant.closing);
                            return s.st == "opened";
                        }
                        return false
                    }).length));
                    var fb__a__c = $(filtercbx("Closed", "closed", "avail",  branches.filter(function(b){
                        if(b.isAvailable == true){
                            var s = statusWorkTime(b.restaurant.opening, b.restaurant.closing);
                            return s.st == "closed";
                        }
                        return false
                    }).length));
                    //fbc.append([fb__availability, fb__a__a, fb__a__b, fb__a__c, fb__hr]);

                    fbc.append(fb__availability);
                    filters.availability.forEach(function(a) {
                        fbc.append($(filtercbx(a.title, a.id, "availability", a.count, fb__values.availability.includes(a.id))))
                    });
                    fbc.append(fb__hr);

                    var fb__distance = `<h5 ${fb__h5__st}>Distance From Location</h5>`;
                    var fb__d__1 = $(filtercbx("Less than 1 Km", 1, "dist", branches.filter(function(b){return b.dist <= 1}).length));
                    var fb__d__3 = $(filtercbx("Less than 3 Km", 3, "dist", branches.filter(function(b){return b.dist <= 3}).length));
                    var fb__d__5 = $(filtercbx("Less than 5 Km", 5, "dist", branches.filter(function(b){return b.dist <= 5}).length));
                    var fb__d__10 = $(filtercbx("Less than 10 Km", 10, "dist", branches.filter(function(b){return b.dist <= 10}).length));
                    fbc.append([fb__distance, fb__d__1, fb__d__3, fb__d__5, fb__d__10, fb__hr]);

                    var fb__cuisine =  `<h5 ${fb__h5__st}>Cuisines</h5>`;
                    fbc.append(fb__cuisine);
                    var r_cuisine = window.__TING__Cuisines;
                    filters.cuisines.forEach(function(c) {
                        fbc.append($(filtercbx(c.title, c.id, "cuisines", c.count, fb__values.cuisines.includes(c.id))))
                    });
                    fbc.append(fb__hr);
                    
                    var fb__service =  `<h5 ${fb__h5__st}>Services</h5>`;
                    fbc.append(fb__service);
                    var r_sers = window.__TING__Services;
                    filters.services.forEach(function(s) {
                        fbc.append($(filtercbx(s.title, s.id, "services", s.count, fb__values.services.includes(s.id))))
                    });
                    fbc.append(fb__hr);

                    var fb__specials =  `<h5 ${fb__h5__st}>Specials</h5>`;
                    fbc.append(fb__specials);
                    var r_specs = window.__TING__Specials;
                    filters.specials.forEach(function(s) {
                        fbc.append($(filtercbx(s.title, s.id, "specials", s.count, fb__values.specials.includes(s.id))))
                    });
                    fbc.append(fb__hr);

                    var fb__types = `<h5 ${fb__h5__st}>Types</h5>`
                    fbc.append(fb__types);
                    var r_types = window.__TING__Types;
                    filters.types.forEach(function(t) {
                        fbc.append($(filtercbx(t.title, t.id, "types", t.count, fb__values.types.includes(t.id))))
                    });
                    fbc.append(fb__hr);

                    var fb__chair_type = `<h5 ${fb__h5__st}>Chair Type</h5>`;
                    var fb__ct__iron = $(filtercbx("Iron", "iron", "chairt", branches.filter(function(b){return b.tables.iron > 0}).length));
                    var fb__ct__wooden = $(filtercbx("Wooden", "wooden", "chairt", branches.filter(function(b){return b.tables.wooden > 0}).length));
                    var fb__ct__plastic = $(filtercbx("Plastic", "plastic", "chairt", branches.filter(function(b){return b.tables.plastic > 0}).length));
                    var fb__ct__couch = $(filtercbx("Couch", "couch", "chairt", branches.filter(function(b){return b.tables.couch > 0}).length));
                    var fb__ct__mixture = $(filtercbx("Mixture", "mix", "chairt", branches.filter(function(b){return b.tables.mixture > 0}).length));
                    //fbc.append([fb__chair_type, fb__ct__iron, fb__ct__wooden, fb__ct__plastic, fb__ct__couch, fb__ct__mixture, fb__hr]);
                    
                    var fb__table_location = `<h5 ${fb__h5__st}>Table Location</h5>`;
                    var fb__t__inside = $(filtercbx("Inside", "inside", "tabloc", branches.filter(function(b){return b.tables.inside > 0}).length));
                    var fb__t__outside = $(filtercbx("Outside", "outside", "tabloc", branches.filter(function(b){return b.tables.outside > 0}).length));
                    var fb__t__balcony = $(filtercbx("Balcony", "balcony", "tabloc", branches.filter(function(b){return b.tables.balcony > 0}).length));
                    var fb__t__rooftop = $(filtercbx("Rooftop", "rooftop", "tabloc", branches.filter(function(b){return b.tables.rooftop > 0}).length));
                    //fbc.append([fb__table_location, fb__t__inside, fb__t__outside, fb__t__balcony, fb__t__rooftop, fb__hr]);

                    var fb__star_rating = `<h5 ${fb__h5__st}>Ratings</h5>`;
                    var fb__s__1 = $(filtercbx("1 Star", "-1,1.5", "star", branches.filter(function(b){return b.reviews.average <= 1.5}).length));
                    var fb__s__2 = $(filtercbx("2 Stars", "1.5,2", "star", branches.filter(function(b){return b.reviews.average > 1.5 && b.reviews.average <= 2.5}).length));
                    var fb__s__3 = $(filtercbx("3 Stars", "2.5,3.5", "star", branches.filter(function(b){return b.reviews.average > 2.5 && b.reviews.average <= 3.5}).length));
                    var fb__s__4 = $(filtercbx("4 Stars", "3.5,4.5", "star", branches.filter(function(b){return b.reviews.average > 3.5 && b.reviews.average <= 4.5}).length));
                    var fb__s__5 = $(filtercbx("5 Stars", "4.5,5", "star", branches.filter(function(b){return b.reviews.average > 4.5}).length));
                    //fbc.append([fb__star_rating, fb__s__1, fb__s__2, fb__s__3, fb__s__4, fb__s__5, fb__hr]);

                    fbc.append(fb__star_rating);
                    filters.ratings.forEach(function(r) {
                        fbc.append($(filtercbx(r.title, r.id, "ratings", r.count, fb__values.ratings.includes(r.id))))
                    });
                    fbc.append(fb__hr);

                    var fb__reviews = `<h5 ${fb__h5__st}>Reviews</h5>`;
                    var fb__r__100 = $(filtercbx("- 100", "-1,100", "reviews", branches.filter(function(b){return b.reviews.count <= 100}).length));
                    var fb__r__500 = $(filtercbx("101 - 500", "100,500", "reviews", branches.filter(function(b){return b.reviews.count > 100 && b.reviews.count <= 500}).length));
                    var fb__r__1000 = $(filtercbx("501 - 1000", "500,1000", "reviews", branches.filter(function(b){return b.reviews.count > 500 && b.reviews.count <= 1000}).length));
                    var fb__r__5000 = $(filtercbx("1001 - 5000", "100,5000", "reviews", branches.filter(function(b){return b.reviews.count > 1000 && b.reviews.count <= 5000}).length));
                    var fb__r__more = $(filtercbx("5001 -", "5000,100000000000", "reviews", branches.filter(function(b){return b.reviews.count > 5000}).length));
                    //fbc.append([fb__reviews, fb__r__100, fb__r__500, fb__r__1000, fb__r__5000, fb__r__more]);

                    fbc.find(".ting-checkbox-container input").click(function(){
                        var v = {val: $(this).val(), gval: $(this).attr("data-g-value")}
                        var c = fbs.find(function(f){return f.val == v.val && f.gval == v.gval})
                        if($(this).is(":checked") == true){if(fbs.includes(v) == false){fbs.push(v)}}
                        else{if(c !== undefined){fbs = fbs.filter(function(f){return f != c})}}
                        pag__s = 0;
                        if($(this).is(":checked") == true){if(fb__values[v.gval].includes(v.val) == false){fb__values[v.gval].push(parseInt(v.val))}}
                        else{fb__values[v.gval].splice(fb__values[v.gval].indexOf(parseInt(v.val), 1));}
                        if(use_old) {
                            branches = filterbranches(branches__else, fbs, false);
                            branches.sort(compare);
                            createpags(branches, true);
                            if(branches.length > 0){getRestaurantList(branches.sort(compare).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)), sloc, 1);}
                            else {getRestaurantList(branches.sort(compare), sloc, 1);}
                        } else { searchfilterbranches(); }
                    });

                    fc.append(fbc);
                }

                updateFilters(filters);

                r.append(fc).append(rc);
                g.html(r); c.html(g);

                if (!isObjEmpty(session)){
                    var _uas = session.addresses
                    if(_uas.count > 0){
                        for(var _a = 0; _a < _uas.count; _a++){
                            usl.append(`<option value="${_uas.addresses[_a].id}">${_uas.addresses[_a].type} - ${_uas.addresses[_a].address}</option>`);
                        }
                    }
                }

                usl.change(function(e){
                    e.preventDefault();
                    var _av = $(this).val()
                    if(_av == 0){usa = {lat: lat, lng: long}; sloc = usa;}
                    else {var _sa = session.addresses.addresses.find(function(a){return a.id == _av});
                    usa = {lat: parseFloat(_sa.latitude), lng: parseFloat(_sa.longitude)};}
                    sloc = usa;
                    pag__s = 0;
                    branches = newBranches(branches__else, usa, use_old);
                    if(use_old) {
                        createpags(branches, true);
                        branches.sort(compare);
                        if(branches.length > 0){getRestaurantList(branches.sort(compare).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)), usa, 1);}
                        else {getRestaurantList(branches.sort(compare), usa, 1);}
                    } else { getRestaurantList(branches.sort(compare), usa, 1); }
                    branchesmaps(branches, usa, false);
                });

                createpags(branches, false, window.__TING__Num_Pages, 1);
                branches.sort(compare);
                if(use_old){
                    if(branches.length > 0){getRestaurantList(branches.sort(compare).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)), usa, 1);}
                    else {getRestaurantList(branches.sort(compare), usa, 1);}
                } else { searchfilterbranches(); }
                branchesmaps(branches, usa, false);

                function searchfilterbranches(page=0){
                    var _dt = new FormData();
                    _dt.append("query", $("body").find("#ting-restaurant-filter-name").val())
                    _dt.append("country", $("body").find("#ting-restaurant-filter-country").val())
                    _dt.append("csrfmiddlewaretoken", window.__TING__Token);
                    _dt.append("filters", JSON.stringify(fb__values));
                    var _url = window.__TING__URL_Filter_Restaurants;
                    md.html(loader);
                    $.ajax({
                        type: "POST", url: _url, data: _dt,
                        processData: false, contentType: false,
                        success: function(res){var r = res[2];
                            window.__TING__Restaurants = r;
                            window.__TING__Num_Pages = r[0];
                            branches__else = r; branches = r;
                            if(use_old){
                                pag__s = 0;createpags(r, true);r.sort(compare);
                                if(r.length > 0){getRestaurantList(newBranches(r, sloc, use_old).sort(compare).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)), sloc, 1);}
                                else {getRestaurantList(newBranches(r, sloc, use_old).sort(compare), sloc, 1);}
                            } else { createpags(r, true, r[0], r[1]); getRestaurantList(newBranches(r, sloc, use_old).sort(compare), sloc, 1); }
                            branchesmaps(newBranches(r, sloc, use_old), sloc, false);
                            updateFilters(window.__TING__Filters);
                        }, error: function(_, t, e){showErrorMessage(t, e);}
                    });
                }

                function createpags(brchs, ev, pgs=0, spg=0){
                    if(use_old) {
                        if(brchs.length > 0){
                            var pag__n = Math.floor(brchs.length / pag__m);
                            var pag__l = brchs.length - (pag__n * pag__m);
                            pag__cont.empty().show();
                            pag__p = [];
                            if(pag__l > 0){pag__n++}
                            var pag__c = 0;
                            for(var p = 0; p < pag__n; p++){pag__p.push({from: pag__c, to: pag__c + pag__m, pos: p}); pag__c += pag__m}
                            if(pag__s != 0){ pag__cont.append(`<a class="item" data-position="prev"><i class="left chevron icon"></i></a>`)}
                            if(pag__p.length > 1){
                                for(var p = 0; p < pag__p.length; p++){
                                    pag__cont.append(`<a class="item" data-from="${pag__p[p].from}" data-to="${pag__p[p].to}" data-position="${pag__p[p].pos}">${pag__p[p].pos + 1}</a>`)
                                }
                            } else { pag__cont.hide() }
                            if(pag__p.length > 1 && pag__s != pag__p.length - 1){pag__cont.append(`<a class="icon item" data-position="next"><i class="right chevron icon"></i></a>`)}
                            pag__cont.find("a").click(function(){
                                var p = $(this).attr("data-position");
                                if(p == "next"){pag__s++} else if(p == "prev"){pag__s--;} else {pag__s = p;}
                                createpags(brchs, true);
                                brchs.sort(compare);
                                getRestaurantList(brchs.sort(compare).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)), usa, 1);
                            });
                            pag__cont.find("a[data-position="+pag__s+"]").addClass("active").siblings().removeClass("active");
                        } else { pag__p = []; pag__cont.empty().hide(); }
                    } else {
                        if(pgs > 0) {
                            var s__pg = spg;
                            pag__cont.empty().show();
                            if(s__pg != 1){ pag__cont.append(`<a class="item" data-position="prev"><i class="left chevron icon"></i></a>`)}
                            if(pgs > 1){
                                for(var p = 0; p < papgs; p++){
                                    pag__cont.append(`<a class="item" data-position="${p + 1}">${p + 1}</a>`)
                                }
                            } else { pag__cont.hide() }
                            if(pgs > 1 && s__pg != pgs - 1){pag__cont.append(`<a class="icon item" data-position="next"><i class="right chevron icon"></i></a>`)}
                            pag__cont.find("a").click(function(){
                                var p = $(this).attr("data-position");
                                if(p == "next"){s__pg++} else if(p == "prev"){s__pg--;} else {s__pg = p;}
                                searchfilterbranches(s__pg);
                            });
                            pag__cont.find("a[data-position="+s__pg+"]").addClass("active").siblings().removeClass("active");
                        } else { pag__cont.empty().hide(); }
                    }
                }

                function filterbranches(brs, fb){

                    if(fb.length > 0){

                        var brs__avail = []; var ccs__avail = [];
                        var brs__dist = []; var ccs__dist = [];
                        var brs__chairt = []; var ccs__chairt = [];
                        var brs__star = []; var ccs__star = [];
                        var brs__reviews = []; var ccs__reviews = [];
                        var brs__cuisines = []; var css__cuisines = [];
                        var brs__services = []; var css__services = [];
                        var brs__specials = []; var css__specials = [];
                        var brs__types = []; var css__types = [];

                        for(var i = 0; i < fb.length; i++){
                            var f = fb[i];
                            if(f.gval == "avail"){
                                ccs__avail.push(f);
                                var bf = brs.filter(function(b){
                                    var s = statusWorkTime(b.restaurant.opening, b.restaurant.closing);
                                    if(f.val == "false"){return b.isAvailable == false
                                    } else {return s.st == f.val && b.isAvailable == true}
                                }).forEach(function(b){if(brs__avail.includes(b) == false){brs__avail.push(b)}})
                            } else if(f.gval == "dist"){
                                ccs__dist.push(f);
                                var bf = brs.filter(function(b){return b.dist <= parseInt(f.val)}).forEach(function(b){if(brs__dist.includes(b) == false){brs__dist.push(b)}})
                            } else if(f.gval == "chairt" || f.gval == "tabloc"){
                                ccs__chairt.push(f);
                                var bf = brs.filter(function(b){return b.tables[f.val] > 0}).forEach(function(b){if(brs__chairt.includes(b) == false){brs__chairt.push(b)}})
                            } else if(f.gval == "star"){
                                ccs__star.push(f);
                                var bf = brs.filter(function(b){var ff = f.val.split(","); return b.reviews.average > parseFloat(ff[0]) && b.reviews.average <= parseFloat(ff[1])}).forEach(function(b){if(brs__star.includes(b) == false){brs__star.push(b)}})
                            } else if(f.gval == "reviews"){
                                ccs__reviews.push(f);
                                var bf = brs.filter(function(b){var ff = f.val.split(",");return b.reviews.count > parseInt(ff[0]) && b.reviews.count <= parseInt(ff[1])}).forEach(function(b){if(brs__reviews.includes(b) == false){brs__reviews.push(b)}})
                            } else if(f.gval == "cuis") {
                                css__cuisines.push(f);
                                var bf = brs.filter(function(b){return b.categories.categories.filter(function(ct) { return ct.id == f.val }).length > 0 }).forEach(function(b){if(brs__cuisines.includes(b) == false){brs__cuisines.push(b)}})
                            } else if(f.gval == "serv") {
                                css__services.push(f);
                                var bf = brs.filter(function(b){return b.services.filter(function(s) {return s.id == f.val }).length > 0}).forEach(function(b){if(brs__services.includes(b) == false){brs__services.push(b)}})
                            } else if(f.gval == "spec") {
                                css__specials.push(f);
                                var bf = brs.filter(function(b){return b.specials.filter(function(s) {return s.id == f.val }).length > 0}).forEach(function(b){if(brs__specials.includes(b) == false){brs__specials.push(b)}})
                            } else if (f.gval == "typ") {
                                css__types.push(f);
                                var bf = brs.filter(function(b){return b.type.id == f.val}).forEach(function(b){ if(brs__types.includes(b) == false){brs__types.push(b)}})
                            }
                        }
                        var brs__conc = {
                            "avail":{"brs": brs__avail, "ccs": ccs__avail},
                            "dist":{"brs": brs__dist, "ccs": ccs__dist},
                            "chairt":{"brs": brs__chairt, "ccs": ccs__chairt},
                            "star":{"brs": brs__star, "ccs": ccs__star},
                            "reviews":{"brs": brs__reviews, "ccs": ccs__reviews},
                            "cuis":{"brs": brs__cuisines, "ccs": css__cuisines},
                            "serv":{"brs": brs__services, "ccs": css__services},
                            "spec":{"brs": brs__specials, "ccs": css__specials},
                            "typ":{"brs": brs__types, "ccs": css__types}
                        }
                        var brs__all = [];
                        Object.keys(brs__conc).forEach(function(l){
                            var v = brs__conc[l];
                            v.brs.forEach(function(b){
                                var t = [];
                                Object.keys(brs__conc).forEach(function(k){
                                    if(l != k){if(brs__conc[k].brs.includes(b) == true){if(brs__conc[k].ccs.length > 0){t.push(true)} else { t.push(false) }
                                    } else {if(brs__conc[k].ccs.length <= 0){t.push(true)} else { t.push(false) }}}
                                });
                                if(t.every(function(v){ return v === true }) == true){if(brs__all.includes(b) == false){ brs__all.push(b)}}
                            });
                        });
                        return brs__all.sort(compare);
                    } else {return brs.sort(compare);}
                }

                function branchesmaps(br, usloc, click){

                    var map = new google.maps.Map(document.getElementById("ting-restaurants-map"), {
                        zoom: 16,
                        center: usloc
                    });

                    map.setCenter(usloc);

                    for(var i = 0; i < br.length; i++){

                        var branch = br[i]
                        var icon = {
                            url: branch.restaurant.pin,
                            size: new google.maps.Size(71, 71),
                            origin: new google.maps.Point(0, 0),
                            anchor: new google.maps.Point(30, 64),
                            scaledSize: new google.maps.Size(60, 60)
                        };

                        var contentInfo = `
                                        <div class="ting-restaurant-map-info">
                                            <div class="image">
                                                <img src="${branch.restaurant.logo}" />
                                            </div>
                                            <div class="about">
                                                <h2><a href="${branch.urls.relative}" target="_blank">${branch.restaurant.name}</a></h2>
                                                <p class="branch">${branch.name} Branch</p>
                                                <p><i class="lnr lnr-map-marker"></i>${branch.address}</p>
                                                <hr/>
                                            </div>
                                            <div class="resto-info">
                                                <p><i class="lnr lnr-bullhorn"></i>${branch.restaurant.motto}</p>
                                                <p><i class="lnr lnr-envelope"></i>${branch.email}</p>
                                                <p><i class="lnr lnr-phone-handset"></i>${branch.phone}</p>
                                                <p><i class="lnr lnr-clock"></i>${branch.restaurant.opening} - ${branch.restaurant.closing}</p>
                                            </div>
                                        </div>
                                    `;

                        var infowindow = new google.maps.InfoWindow({
                            content: contentInfo
                        });

                        var marker = new google.maps.Marker({
                            position: {lat: parseFloat(branch.latitude), lng: parseFloat(branch.longitude)},
                            map: map,
                            title: branch.restaurant.name + ",  " + branch.name,
                            zIndex: branch.id,
                            icon: icon
                        });

                        google.maps.event.addListener(marker, "click", (function(marker, contentInfo, infowindow){ 
                            return function() {
                                infowindow.setContent(contentInfo);
                                infowindow.open(map, marker);
                            };
                        })(marker, contentInfo, infowindow));
                        if(click == true){
                            if(usloc.lat == parseFloat(branch.latitude) && usloc.lng == parseFloat(branch.longitude)){
                                google.maps.event.trigger(marker, "click");
                            }
                        } 
                    }
                }

                function newBranches(branches, usa, f=true){
                    if(branches.length > 0){
                        branches.forEach(function(b){
                            if(usa.lat != 0 && usa.lat !== undefined && usa.lng != 0 && usa.lng !== undefined){
                                var _ds = new google.maps.LatLng(usa.lat, usa.lng)
                                var _de = new google.maps.LatLng(parseFloat(b.latitude), parseFloat(b.longitude))
                                b.dist = calculateDistance(_ds, _de)
                            } else { b.dist = 0.00 }
                        });
                    }
                    return f == true ? filterbranches(branches, fbs) : branches;
                }
                   
                function getRestaurantList(res, _ds, t){
                    if(res.length > 0){
                        res = res.sort(compare);
                        var ctn = $(`<div class="ui items"></div>`).empty();
                        for(var i = 0; i < res.length; i++){
                            var br = res[i];
                            var s = statusWorkTime(br.restaurant.opening, br.restaurant.closing)
                            var tc = $("<div class='item ting-resto-item'></div>");
                            tc.attr("id", "ting-resto-item-" + br.id);
                            tc.attr("data-position", i);
                            tc.attr("data-top-url", decodeURIparams(window.__TING__URL_Top_Five, {"restaurant": br.restaurant.id, "branch": br.id}));
                            tc.css("cursor", "pointer");
                            var ti = `  
                                    <div class="ui image">
                                        <a class="header" href="${br.urls.relative}" target="_blank">
                                            <img src="${br.restaurant.logo}" style="width:225px;">
                                        </a>
                                    </div>
                                    <div class="content">
                                        <a class="header" href="${br.urls.relative}" style="font-size:19px; font-weight:500;">${br.restaurant.name}, ${br.name}</a>
                                        <div class="meta" style="margin-top:5px;">
                                            <div class="ui disabled-rating star rating" data-rating="${br.reviews.average}" data-max-rating="5" style="margin-bottom:10px;"></div>
                                            <p class="ting-resto-item-address" data-position="${i}" data-branch-id="${br.id}"><i icon class="icon map marker alternate"></i> ${br.address}</p>
                                        </div>
                                        
                                        <div class="description">
                                            <div class="ui small labeled icon button top left pointing dropdown bt-popup ting-tab-btn" data-tab='{"id": "${br.id}", "type": "cat", "pos": ${i}}' data-branch-id="${br.id}" data-tooltip="Categories" data-position="top left">
                                                <i class="boxes link icon"></i> ${br.restaurant.foodCategories.count}
                                                <div class="menu fluid" style="width: auto !important;">
                                                    <div class="header">Categories</div>
                                                    ${br.restaurant.foodCategories.categories != null 
                                                        ? `${br.restaurant.foodCategories.categories.map(function(c){
                                                                return `<div class="item" style="width: auto !important;" data-value="${c.id}">
                                                                            <img class="ui mini avatar image" style="width: 30px; height: 30px;" src="${c.image}">
                                                                            <span class="text">${c.name}</span>
                                                                        </div>`;
                                                            }).join('')} 
                                                        ` : ``}
                                                </div>
                                            </div>
                                            <div class="ui small labeled icon button top left pointing dropdown bt-popup ting-tab-btn" data-tab='{"id": "${br.id}", "type": "food", "pos": ${i}}' data-branch-id="${br.id}" data-tooltip="Foods" data-position="top left">
                                                <i class="utensils spoon icon"></i> ${numerilize(br.menus.type.foods.count, br.menus.type.foods.count, 0)}
                                                <div class="menu fluid">
                                                    <div class="header">Foods</div>
                                                    ${br.menus.menus != null 
                                                        ? `${br.menus.menus.filter(function(m){return m.type.id == 1}).map(function(m){
                                                                return `<div class="item" data-value="${m.menu.id}">
                                                                            <img class="ui mini avatar image" style="width: 30px; height: 30px;" src="${m.menu.images.images[0].image}">
                                                                            <span class="text">${m.menu.name}</span>
                                                                            <span class="description">${m.menu.currency} ${numerilize(m.menu.price, m.menu.price, 0)}</span>
                                                                        </div>`;
                                                            }).join('')}
                                                        ` : ``}
                                                </div>
                                            </div>
                                            <div class="ui small labeled icon button top left pointing dropdown bt-popup ting-tab-btn" data-tab='{"id": "${br.id}", "type": "drink", "pos": ${i}}' data-branch-id="${br.id}" data-tooltip="Drinks" data-position="top left">
                                                <i class="glass martini icon"></i> ${numerilize(br.menus.type.drinks, br.menus.type.drinks, 0)}
                                                <div class="menu fluid">
                                                    <div class="header">Drinks</div>
                                                    ${br.menus.menus != null 
                                                        ? `${br.menus.menus.filter(function(m){return m.type.id == 2}).map(function(m){
                                                                return `<div class="item" data-value="${m.menu.id}">
                                                                            <img class="ui mini avatar image" style="width: 30px; height: 30px;" src="${m.menu.images.images[0].image}">
                                                                            <span class="text">${m.menu.name}</span>
                                                                            <span class="description">${m.menu.currency} ${numerilize(m.menu.price, m.menu.price, 0)}</span>
                                                                        </div>`;
                                                            }).join('')}
                                                        ` : ``}
                                                </div>
                                            </div>
                                            <div class="ui small labeled icon button top left pointing dropdown bt-popup ting-tab-btn" data-tab='{"id": "${br.id}", "type": "dish", "pos": ${i}}' data-branch-id="${br.id}" data-tooltip="Dishes" data-position="top left">
                                                <i class="utensils icon"></i> ${numerilize(br.menus.type.dishes, br.menus.type.dishes, 0)}
                                                <div class="menu fluid">
                                                    <div class="header">Dishes</div>
                                                    ${br.menus.menus != null 
                                                        ? `${br.menus.menus.filter(function(m){return m.type.id == 3}).map(function(m){
                                                                return `<div class="item" data-value="${m.menu.id}">
                                                                            <img class="ui mini avatar image" style="width: 30px; height: 30px;" src="${m.menu.images.images[0].image}">
                                                                            <span class="text">${m.menu.name}</span>
                                                                            <span class="description">${m.menu.currency} ${numerilize(m.menu.price, m.menu.price, 0)}</span>
                                                                        </div>`;
                                                            }).join('')}
                                                        ` : ``}
                                                </div>
                                            </div>
                                            <div class="ting-menus-list-item" id="ting-menus-list-item-${br.id}">
                                                ${br.restaurant.foodCategories.count > 0 ? br.restaurant.foodCategories.categories.sort(function(a, b){
                                                    if(Date.parse(a.createdAt) > Date.parse(b.createdAt)){return -1}
                                                    if(Date.parse(a.createdAt) < Date.parse(b.createdAt)){return 1}
                                                    return 0;
                                                }).slice(0, 4).map(function(c){
                                                    return `<div class="ting-menu-image-list lst-popup-${br.id}-${c.id}">
                                                                <a href="${decodeURIparams(window.__TING__URL_Menus_Category, {"branch": br.id, "category": c.id, "slug": randomString(16)})}" class="ting-menu-url" target="_blank">
                                                                    <img src="${c.image}" />
                                                                </a>
                                                            </div>
                                                            <div class="ui flowing popup basic transition hidden ting-menu-popup-${br.id}-${c.id}" style="top:-20px !important;">
                                                                <div class="header">${c.name}</div>
                                                                <div class="description">${c.description}</div>
                                                            </div><script type="text/javascript">$(".lst-popup-${br.id}-${c.id}").popup({popup : ".ting-menu-popup-${br.id}-${c.id}", on : "hover", boundery: "body"});</script>`;
                                                }).join("") : `<div class="ui red message">No Category To Show</div>`}
                                                    
                                            </div>
                                        </div> 
                                        
                                        ${br.categories.count > 0 ? `<p><i icon class="icon utensils" style="color: #999999;"></i> ${br.categories.categories.shuffle().map(function(c){ return c.name }).join(", ")}</p>` : ``}
                                        ${br.restaurant.foodCategories.count > 0 ? `<p><i icon class="icon boxes" style="color: #999999;"></i> ${br.restaurant.foodCategories.categories.shuffle().map(function(c){ return c.name }).join(", ")}</p>` : ``}

                                        <div class="extra">
                                            <div class="ui label ting-resto-item-map-direction" data-url="${decodeURIparams(window.__TING__URL_Load_Branch_Directions, {"restaurant": br.restaurant.id, "branch": br.id})}" data-position="${i}" data-branch-id="${br.id}"><i class="icon map marker alternate"></i> ${br.dist} Km</div>
                                            <span id="ting-resto-open-time-${br.id}"><div class="ui ${br.isAvailable == true ? s.clr : "red"} label"><i class="clock outline icon"></i> ${br.isAvailable == true ? s.msg : "Not Available"}</div></span>
                                            <div class="ui label" style="cursor:pointer;"><i class="heart outline icon"></i>${numerilize(br.likes.count, null, 0)}</div>
                                            <div class="ui label" id="ting-rate-btn-${br.id}" style="cursor:pointer;"><i class="star outline icon"></i>${numerilize(br.reviews.count, null, 0)}</div>
                                            <div class="ui label" id="ting-specials-btn-${br.id}" style="cursor:pointer;"><i class="plus icon"></i>${br.specials.length}</div>
                                            <div class="ui label" id="ting-cuisines-btn-${br.id}" style="cursor:pointer;"><i class="utensils icon"></i>${br.categories.count}</div>
                                        </div>
                                        <script>
                                            setInterval(function(){
                                                var time = statusWorkTime("${br.restaurant.opening}", "${br.restaurant.closing}")
                                                $("#ting-resto-open-time-${br.id}").html('<div class="ui ${br.isAvailable == true ? " ' + time.clr + ' " : "red"} label"><i class="clock outline icon"></i> ${br.isAvailable == true ? " ' + time.msg + ' " : "Not Available"}</div>')
                                            }, 30000)
                                        </script>
                                        <div class="ting-like-restaurant">
                                            <button class="ting-like-restaurant ting-btn-animate ${likesresto(br) == true ? 'liked' : ''}" id="ting-like-restaurant-${br.id}" data-like='{"resto":"${br.restaurant.id}", "branch": "${br.id}", "tkn":"${br.restaurant.token}", "id":"${br.id}", "typ":"link"}'>${likerestobtn(br)}</button>
                                        </div>
                                        <div class="ui flowing popup top left transition hidden" id="ting-rate-popup-${br.id}">
                                            <div class="header">Rating</div>
                                            <div class="content" style="width:300px;">
                                                <div class="ui huge star rating disabled-rating" data-rating="${br.reviews.average}" data-max-rating="5"></div>
                                                <div class="ui grid">
                                                    <div class="row" style="padding:0 !important;">
                                                        <div class="four wide column ting-rate-average">
                                                            <h1>${br.reviews.average}</h1>
                                                            <p>Out Of 5</p>
                                                        </div>
                                                        <div class="twelve wide column" style="padding: 0 !important;">
                                                            <div class="ui grid">
                                                                <div class="row" style="padding-bottom:0 !important;">
                                                                    <div class="eight wide column ting-rate-percent">
                                                                        <div class="ting-star"><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i></div>
                                                                        <div class="ting-star"><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i></div>
                                                                        <div class="ting-star"><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i></div>
                                                                        <div class="ting-star"><i class="star icon"></i><i class="star icon"></i></div>
                                                                        <div class="ting-star"><i class="star icon"></i></div>
                                                                    </div>
                                                                    <div class="eight wide column ting-rate-wrapper">
                                                                        <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${br.reviews.percents[4]}%"></div></div>
                                                                        <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${br.reviews.percents[3]}%"></div></div>
                                                                        <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${br.reviews.percents[2]}%"></div></div>
                                                                        <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${br.reviews.percents[1]}%"></div></div>
                                                                        <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${br.reviews.percents[0]}%"></div></div>
                                                                        <div class="ting-reviews-count"><p>${numerilize(br.reviews.count, br.restaurant.id, 0)} reviews</p></div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="ui flowing popup top left transition hidden" id="ting-specials-popup-${br.id}">
                                            <div class="header">Specials</div>
                                            <hr/>
                                            <div class="content" style="min-width:130px;">
                                                ${br.specials.length > 0 
                                                    ? `${br.specials.map(function(s){
                                                        return `<p><i class="icon ${s.icon}"></i> ${s.name}</p>`
                                                    }).join("")}` 
                                                    : `<div class="ui red message">No Specials Available</div>`}
                                            </div>
                                        </div>
                                        <div class="ui flowing popup right center transition hidden" id="ting-cuisines-popup-${br.id}">
                                            <div class="header">Cuisines</div>
                                            <hr/>
                                            <div class="ui items content" style="min-width:170px;">
                                                ${br.categories.count > 0 
                                                    ? `${br.categories.categories.map(function(c){
                                                        return `<div style="cursor: pointer;" class="item">
                                                                    <img class="ui avatar image" src="${c.image}" style="border-radius:2px;">
                                                                    <div class="content">
                                                                        <p class="header" href="${decodeURIparams(window.__TING__URL_Menus_Cuisine, {"branch": br.id, "cuisine": c.id, "slug": randomString(16)})}" style="font-weight: normal; font-size: 14px; margin-top:5px;">${c.name}</p>
                                                                    </div>
                                                                </div>`
                                                    }).join("")}` 
                                                : `<div class="ui red message">No Cuisine Available</div>`}
                                            </div>
                                        </div>
                                        <script type="text/javascript">
                                            $("#ting-rate-btn-${br.id}").popup({popup : "#ting-rate-popup-${br.id}", on : "click"});
                                            $("#ting-specials-btn-${br.id}").popup({popup : "#ting-specials-popup-${br.id}", on : "click"});
                                            $("#ting-cuisines-btn-${br.id}").popup({popup : "#ting-cuisines-popup-${br.id}", on : "click"});
                                            $("#ting-like-restaurant-${br.id}").likeRestaurant();
                                        </script>
                                    </div>
                                `;

                            var tb = ``;
                            tc.html(ti);
                            var mc = $(`<div class="five wide column" id="ting-menus-sticky" style="padding: 0;"></div>`);
                            var h = `<h4 style="text-transform:uppercase; font-weight:100;">Popular Menus</h4>`
                            mc.append(h);
                            var mcnt = $(`<div class="ui divided items"></div>`);
                            tc.click(function(e){
                                e.preventDefault();
                                mcnt.html(loader);
                                var i = $(this).attr("data-position");
                                var b = res[i];
                                var m = b.menus.menus;
                                var url = $(this).attr("data-top-url");

                                $.ajax({
                                    type: "GET",
                                    url: url,
                                    data: {},
                                    success: function(r){mcnt.empty().html(r);},
                                    error: function(_, t, e){mcnt.html(`<div class="ui red message">${e}</div>`);
                                        setTimeout(function(){
                                            mcnt.empty();
                                            var max = b.menus.count > 5 ? 5 : b.menus.count
                                            if(b.menus.count > 0){
                                                m.sort(function(a, b){
                                                    if ( a.menu.reviews.count < b.menu.reviews.count ){ return -1;}
                                                    if ( a.menu.reviews.count > b.menu.reviews.count ){ return 1;}
                                                    return 0;
                                                });
                                                var mm = m.slice(0, 5);
                                                for(var j = 0; j < mm.length; j++){
                                                    var bm = mm[j].menu;
                                                    var bmc = `
                                                            <div class="item">
                                                                <div class="ui tiny image">
                                                                    <img src="${bm.images.images[0].image}">
                                                                </div>
                                                                <div class="content" style="padding-left:1em;">
                                                                    <a class="header" style="font-size:15px; font-weight:500;">${bm.name}</a>
                                                                    <div class="meta" style="margin-top:5px;">
                                                                        <span class="cinema"></span>
                                                                    </div>
                                                                    <div class="description">
                                                                        <p></p>
                                                                    </div>
                                                                    <div class="extra">
                                                                        <div class="ui tiny label"><i class="icon map marker alternate"></i></div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        `;
                                                    mcnt.append(bmc);
                                                }
                                            } else { mcnt.html(`<div class="ui red message">No Menu To Show</div>`); }
                                        }, 100);
                                    }
                                });
                                mc.append(mcnt);
                            });
                            tc.find(".ting-tab-btn").click(function(e){
                                e.preventDefault();
                                if($(this).attr("data-tab") !== null && $(this).attr("data-tab") !== undefined){
                                    var dtt = JSON.parse($(this).attr("data-tab"));
                                    var cdtt = ctn.find("#ting-menus-list-item-" + dtt.id).empty();
                                    var brt = res[dtt.pos];
                                    var loadurl =  decodeURIparams(window.__TING__URL_Load_Menu_Rand, {"branch": brt.id})  
                                    
                                    var sploader = `<div style="width: 100%; height: 55px; text-align: center;">
                                                        <img src="${window.__TING__URL_Loader_Image}" style="width: 20px; height: 20px; margin-top: 17px;"/>
                                                    </div>`;

                                    cdtt.html(sploader);

                                    $.ajax({
                                        type:"GET", url: loadurl, data: {"type": dtt.type},
                                        success: function(r){cdtt.html(r)},
                                        error: function(_, t, e){cdtt.html(`<div class="ui red message">${e}</div>`)}
                                    });

                                    if(false) {
                                        if(dtt.type == "cat"){
                                            if(brt.restaurant.foodCategories.count > 0){
                                                var cs = brt.restaurant.foodCategories.categories.sort(function(a, b){
                                                    if(Date.parse(a.createdAt) > Date.parse(b.createdAt)){return -1}
                                                    if(Date.parse(a.createdAt) < Date.parse(b.createdAt)){return 1}
                                                    return 0;
                                                }).slice(0, 4);
                                                for(var i = 0; i < cs.length; i++){
                                                    cdtt.append(`<div class="ting-menu-image-list lst-popup-${brt.id}-${cs[i].id}">
                                                                    <a href="${decodeURIparams(window.__TING__URL_Menus_Category, {"branch": brt.id, "category": cs[i].id, "slug": randomString(16)})}" class="ting-menu-url-${brt.id}-c" target="_blank">
                                                                        <img src="${cs[i].image}" />
                                                                    </a>
                                                                </div>
                                                                <div class="ui flowing popup basic transition hidden ting-menu-popup-${brt.id}-${cs[i].id}" style="top:-20px !important;">
                                                                    <div class="header">${cs[i].name}</div>
                                                                    <div class="description">${cs[i].description}</div>
                                                                </div><script type="text/javascript">$(".lst-popup-${brt.id}-${cs[i].id}").popup({popup : ".ting-menu-popup-${brt.id}-${cs[i].id}", on : "hover", boundery: "body"});</script>
                                                            `);
                                                }
                                                cdtt.append(`<script type="text/javascript"> $(".ting-menu-url-${brt.id}-c").click(function(){window.open($(this).attr("href"), "_blank")}); </script>`)
                                            } else {cdtt.html(`<div class="ui red message">No Category To Show</div>`)}
                                        } else if (dtt.type == "food"){
                                            var fds = brt.menus.menus.filter(function(f){return f.type.id == 1}).sort(function(a, b){
                                                if(a.menu.likes.count > b.menu.likes.count){return 1}
                                                if(a.menu.likes.count < b.menu.likes.count){return -1}
                                                return 0
                                            }).slice(0, 4);
                                            if(fds.length > 0){
                                                for(var i = 0; i < fds.length; i++){
                                                    cdtt.append(`<div class="ting-menu-image-list lst-popup-${brt.id}-${fds[i].menu.id}">
                                                                    <a href="${fds[i].menu.url}" target="_blank" class="ting-menu-url-${brt.id}-f"><img src="${fds[i].menu.images.images[Math.floor(Math.random() * (fds[i].menu.images.count - 1))].image}" /></a>
                                                                </div>
                                                                <div class="ui flowing popup basic transition hidden ting-menu-popup-${brt.id}-${fds[i].menu.id}">
                                                                    <div class="header">${fds[i].menu.name}</div>
                                                                    <div class="ui star rating disabled-rating" data-rating="${fds[i].menu.reviews.average}" data-max-rating="5" style="margin-top:5px;"></div>
                                                                    <div class="description">${fds[i].menu.description}</div>
                                                                    <p class="ui ${fds[i].menu.isAvailable == true ? `green` : `red`}" style="color: ${fds[i].menu.isAvailable == true ? `green` : `red`}">${fds[i].menu.isAvailable == true ? `<i class="icon check"></i> Available` : `<i class="icon times"></i> Not Available`}</p>
                                                                    <div class="extra">
                                                                        <div class="ui label"><i class="icon boxes"></i> ${fds[i].menu.category.name}</div>
                                                                        <div class="ui label"><i class="icon utensils spoon"></i> ${fds[i].menu.foodType}</div>
                                                                        <div class="ui label"><i class="icon tag"></i> ${fds[i].menu.currency} ${numerilize(fds[i].menu.price, fds[i].menu.price, 0)} ${fds[i].menu.isCountable == true ? ` (${fds[i].menu.quantity} pieces)` : ``}</div>
                                                                    </div>
                                                                </div><script type="text/javascript">$(".lst-popup-${brt.id}-${fds[i].menu.id}").popup({popup : ".ting-menu-popup-${brt.id}-${fds[i].menu.id}", on : "hover"});</script>
                                                            `);
                                                }
                                                cdtt.append(`<script type="text/javascript">
                                                                $(".disabled-rating").rating("disable"); 
                                                                $(".ting-menu-url-${brt.id}-f").click(function(){window.open($(this).attr("href"), "_blank")})
                                                            </script>
                                                        `)
                                            } else {cdtt.html(`<div class="ui red message">No Food To Show</div>`)}
                                        } else if (dtt.type == "drink"){
                                            var fds = brt.menus.menus.filter(function(f){return f.type.id == 2}).sort(function(a, b){
                                                if(a.menu.likes.count > b.menu.likes.count){return 1}
                                                if(a.menu.likes.count < b.menu.likes.count){return -1}
                                                return 0
                                            }).slice(0, 4);
                                            if(fds.length > 0){
                                                for(var i = 0; i < fds.length; i++){
                                                    cdtt.append(`<div class="ting-menu-image-list lst-popup-${brt.id}-${fds[i].menu.id}">
                                                                    <a href="${fds[i].menu.url}" target="_blank" class="ting-menu-url-${brt.id}-dr"><img src="${fds[i].menu.images.images[Math.floor(Math.random() * (fds[i].menu.images.count - 1))].image}" /></a>
                                                                </div>
                                                                <div class="ui flowing popup basic transition hidden ting-menu-popup-${brt.id}-${fds[i].menu.id}">
                                                                    <div class="header">${fds[i].menu.name}</div>
                                                                    <div class="ui star rating disabled-rating" data-rating="${fds[i].menu.reviews.average}" data-max-rating="5" style="margin-top:5px;"></div>
                                                                    <div class="description">${fds[i].menu.description}</div>
                                                                    <p class="ui ${fds[i].menu.isAvailable == true ? `green` : `red`}" style="color: ${fds[i].menu.isAvailable == true ? `green` : `red`}">${fds[i].menu.isAvailable == true ? `<i class="icon check"></i> Available` : `<i class="icon times"></i> Not Available`}</p>
                                                                    <div class="extra">
                                                                        <div class="ui label"><i class="icon martini glass"></i> ${fds[i].menu.drinkType}</div>
                                                                        <div class="ui label"><i class="icon tag"></i> ${fds[i].menu.currency} ${numerilize(fds[i].menu.price, fds[i].menu.price, 0)} ${fds[i].menu.isCountable == true ? `(${fds[i].menu.quantity} pieces)` : ``}</div>
                                                                    </div>
                                                                </div><script type="text/javascript">$(".lst-popup-${brt.id}-${fds[i].menu.id}").popup({popup : ".ting-menu-popup-${brt.id}-${fds[i].menu.id}", on : "hover", boundery: "body"});</script>
                                                            `);
                                                }
                                                cdtt.append(`<script type="text/javascript">
                                                                $(".disabled-rating").rating("disable");
                                                                $(".ting-menu-url-${brt.id}-dr").click(function(){window.open($(this).attr("href"), "_blank")})
                                                            </script>
                                                        `)
                                            } else {cdtt.html(`<div class="ui red message">No Drink To Show</div>`)}
                                        } else if (dtt.type == "dish"){
                                            var fds = brt.menus.menus.filter(function(f){return f.type.id == 3}).sort(function(a, b){
                                                if(a.menu.likes.count > b.menu.likes.count){return 1}
                                                if(a.menu.likes.count < b.menu.likes.count){return -1}
                                                return 0
                                            }).slice(0, 4);
                                            if(fds.length > 0){
                                                for(var i = 0; i < fds.length; i++){
                                                    cdtt.append(`<div class="ting-menu-image-list lst-popup-${brt.id}-${fds[i].menu.id}">
                                                                    <a href="${fds[i].menu.url}" target="_blank" class="ting-menu-url-${brt.id}-ds"><img src="${fds[i].menu.images.images[Math.floor(Math.random() * (fds[i].menu.images.count - 1))].image}" /></a>
                                                                </div>
                                                                <div class="ui flowing popup basic transition hidden ting-menu-popup-${brt.id}-${fds[i].menu.id}">
                                                                    <div class="header">${fds[i].menu.name}</div>
                                                                    <div class="ui star rating disabled-rating" data-rating="${fds[i].menu.reviews.average}" data-max-rating="5" style="margin-top:5px;"></div>
                                                                    <div class="description">${fds[i].menu.description}</div>
                                                                    <p class="ui ${fds[i].menu.isAvailable == true ? `green` : `red`}" style="color: ${fds[i].menu.isAvailable == true ? `green` : `red`}">${fds[i].menu.isAvailable == true ? `<i class="icon check"></i> Available` : `<i class="icon times"></i> Not Available`}</p>
                                                                    <div class="extra">
                                                                        <div class="ui label"><i class="icon boxes"></i> ${fds[i].menu.category.name}</div>
                                                                        <div class="ui label"><i class="icon clock"></i> ${fds[i].menu.dishTime}</div>
                                                                        <div class="ui label"><i class="icon tag"></i> ${fds[i].menu.currency} ${numerilize(fds[i].menu.price, fds[i].menu.price, 0)} ${fds[i].menu.isCountable == true ? `(${fds[i].menu.quantity} pieces)` : ``}</div>
                                                                    </div>
                                                                </div><script type="text/javascript">$(".lst-popup-${brt.id}-${fds[i].menu.id}").popup({popup : ".ting-menu-popup-${brt.id}-${fds[i].menu.id}", on : "hover", boundery: "body"});</script>
                                                            `);
                                                }
                                                cdtt.append(`<script type="text/javascript">
                                                                $(".disabled-rating").rating("disable"); 
                                                                $(".ting-menu-url-${brt.id}-ds").click(function(){window.open($(this).attr("href"), "_blank")})
                                                            </script>
                                                        `)
                                            } else {cdtt.html(`<div class="ui red message">No Dish To Show</div>`)}
                                        }
                                    }
                                } 
                            });
                            tc.find(".ting-resto-item-address").click(function(e){
                                e.preventDefault();var p = $(this).attr("data-position");
                                var b = res[p];var s = {lat: parseFloat(b.latitude), lng: parseFloat(b.longitude)}
                                branchesmaps(res, s, true);window.scrollTo({ top: 0, behavior: 'smooth' });
                            });
                            tc.find(".ting-resto-item-map-direction").click(function(e){
                                e.preventDefault();
                                var m = $("#ting-resto-branch-direction").modal("show");
                                m.find(".content").html(loader);
                                var url = $(this).attr("data-url");
                                $.ajax({
                                    type:"GET", url: url, data: {"lat": lat, "long": long, "addr": addr, "count": cntr, "town": twn},
                                    success: function(r){m.find(".content").html(r)},
                                    error: function(_, t, e){m.find(".content").html(`<div class="ui red message">${e}</div>`)}
                                });
                            });
                            ctn.append(tc);
                        }
                        ctn.append(`
                            <script type="text/javascript">
                                $(".bt-popup").popup();
                                $(".disabled-rating").rating("disable"); 
                                $(".header").click(function(){
                                    if($(this).attr("href") != null && $(this).attr("href") != undefined && $(this).attr("href") != ""){
                                        $('<a href="' + $(this).attr("href") + '" target="_blank"></a>')[0].click();
                                    }
                                });
                                $(".ting-menu-url").click(function(){window.open($(this).attr("href"), "_blank")})
                            </script>
                        `);
                        md.html(ctn);
                    } else {md.html(`<div class="ting-empty-data"><i class="icon utensils"></i><p>No Restaurant To Show</p></div>`)}
                }
            }
        } else if(state.type == "restaurant"){

            var branch = window.__TING__Restaurant
            var usa = {lat: lat, lng: long}

            if(usa.lat != 0 && usa.lat !== undefined && usa.lng != 0 && usa.lng !== undefined){
                var _ds = new google.maps.LatLng(usa.lat, usa.lng)
                var _de = new google.maps.LatLng(parseFloat(branch.latitude), parseFloat(branch.longitude))
                branch.dist = calculateDistance(_ds, _de)
            } else {branch.dist = 0.00 }

            var bst = statusWorkTime(branch.restaurant.opening, branch.restaurant.closing)

            var rb = $("#ting-restaurant-about");
            var rb__ui = $(`<div class="ui grid"></div>`);
            var rb__r = $(`<div class="row" style="padding:0 !important"></div>`);

            var rb__ct = $(`<div class="ten wide column"></div>`);
            var rb__cd = $(`<div class="six wide column" style="padding: 0 !important"></div>`);

            var rb__ct__in = `<span id="ting-resto-open-time-${branch.id}"><div class="ui ${branch.isAvailable == true ? bst.clr : "red"} label" style="width: 100%"><i class="clock outline icon"></i> ${branch.isAvailable == true ? bst.msg : "Not Available"}</div></span>
                <script>
                    setInterval(function(){
                        var time = statusWorkTime("${branch.restaurant.opening}", "${branch.restaurant.closing}")
                        $("#ting-resto-open-time-${branch.id}").html('<div class="ui ${branch.isAvailable == true ? " ' + time.clr + ' " : "red"} label"><i class="clock outline icon"></i> ${branch.isAvailable == true ? " ' + time.msg + ' " : "Not Available"}</div>')
                    }, 30000)
                </script>`;
            var rb__cd__in = `<div class="ui label ting-resto-item-map-direction" style="cursor:pointer; width: 100% !important;" data-url="${decodeURIparams(window.__TING__URL_Load_Branch_Directions, {"restaurant": branch.restaurant.id, "branch": branch.id})}" data-branch-id="${branch.id}"><i class="icon map marker alternate"></i> ${branch.dist} Km</div>`

            rb__ct.html(rb__ct__in);
            rb__cd.html(rb__cd__in);
            rb__ui.html(rb__r.append(rb__ct).append(rb__cd));

            rb__r.find(".ting-resto-item-map-direction").click(function(e){
                e.preventDefault();
                var m = $("#ting-resto-branch-direction").modal("show");
                m.find(".content").html(loader);
                var url = $(this).attr("data-url");
                $.ajax({
                    type:"GET", url: url, data: {"lat": lat, "long": long, "addr": addr, "count": cntr, "town": twn},
                    success: function(r){m.find(".content").html(r)},
                    error: function(_, t, e){m.find(".content").html(`<div class="ui red message">${e}</div>`)}
                });
            });

            rb.append(rb__ui).append(`<hr/>`);
            rb.append(`
                <div class="header" id="ting-open-specials-popup" style="font-size:16px; font-weight:500; text-transform:uppercase; cursor: pointer;">Specials <span style="position:absolute; right: 0;"><i class="icon chevron right"></i></span></div>
                <div class="ui flowing popup right center transition hidden" id="ting-specials-popup">
                    <div class="header">Specials</div>
                    <hr/>
                    <div class="content" style="min-width:130px;">
                        ${branch.specials.length > 0 
                            ? `${branch.specials.map(function(s){
                                return `<p><i class="icon ${s.icon}"></i> ${s.name}</p>`
                            }).join("")}` 
                        : `<div class="ui red message">No Specials Available</div>`}
                    </div>
                </div>
                <hr/>
                <div class="header" id="ting-open-services-popup" style="font-size:16px; font-weight:500; text-transform:uppercase; cursor: pointer;">Services <span style="position:absolute; right: 0;"><i class="icon chevron right"></i></span></div>
                <div class="ui flowing popup right center transition hidden" id="ting-services-popup">
                    <div class="header">Services</div>
                    <hr/>
                    <div class="content" style="min-width:130px;">
                        ${branch.services.length > 0 
                            ? `${branch.services.map(function(s){
                                return `<p><i class="icon ${s.icon}"></i> ${s.name}</p>`
                            }).join("")}` 
                        : `<div class="ui red message">No Services Available</div>`}
                    </div>
                </div>
                <hr/>
                <div class="header" id="ting-open-cuisines-popup" style="font-size:16px; font-weight:500; text-transform:uppercase; cursor: pointer;">Cuisines <span style="position:absolute; right: 0;"><i class="icon chevron right"></i></span></div>
                <div class="ui flowing popup right center transition hidden" id="ting-cuisines-popup">
                    <div class="header">Cuisines</div>
                    <hr/>
                    <div class="ui items content" style="min-width:130px;">
                        ${branch.categories.count > 0 
                            ? `${branch.categories.categories.map(function(c){
                                return `<div style="cursor: pointer;" class="item ting-item-link" data-href="${decodeURIparams(window.__TING__URL_Menus_Cuisine, {"branch": branch.id, "cuisine": c.id, "slug": randomString(16)})}">
                                            <img class="ui avatar image" src="${c.image}" style="border-radius:2px;">
                                            <div class="content">
                                                <p class="header" style="font-weight: normal; font-size: 14px; margin-top:5px;">${c.name}</p>
                                            </div>
                                        </div>`
                            }).join("")}` 
                        : `<div class="ui red message">No Cuisine Available</div>`}
                    </div>
                </div>
                <hr/>
                <div class="header" id="ting-open-categories-popup" style="font-size:16px; font-weight:500; text-transform:uppercase; cursor: pointer;">Categories <span style="position:absolute; right: 0;"><i class="icon chevron right"></i></span></div>
                <div class="ui flowing popup right center transition hidden" id="ting-categories-popup">
                    <div class="header">Categories</div>
                    <hr/>
                    <div class="ui items content" style="min-width:130px;">
                        ${branch.restaurant.foodCategories.count > 0 
                            ? `${branch.restaurant.foodCategories.categories.map(function(c){
                                return `<div style="cursor: pointer;" class="item ting-item-link" data-href="${decodeURIparams(window.__TING__URL_Menus_Category, {"branch": branch.id, "category": c.id, "slug": randomString(16)})}">    
                                            <img class="ui avatar image" src="${c.image}" style="border-radius:2px;">
                                            <div class="content">
                                                <p class="header" style="font-weight: normal; font-size: 14px; margin-top:5px;">${c.name}</p>
                                            </div>
                                        </div>`
                            }).join("")}` 
                        : `<div class="ui red message">No Category Available</div>`}
                    </div>
                </div>
                <hr/>
                <script type="text/javascript">
                    $("#ting-open-specials-popup").popup({popup : "#ting-specials-popup", on : "click"});
                    $("#ting-open-services-popup").popup({popup : "#ting-services-popup", on : "click"});
                    $("#ting-open-cuisines-popup").popup({popup : "#ting-cuisines-popup", on : "click"});
                    $("#ting-open-categories-popup").popup({popup : "#ting-categories-popup", on : "click"});
                    $(".ting-item-link").click(function() { if($(this).attr("data-href") != null) { window.location = $(this).attr("data-href") }})
                </script>`);
            if(branch.restaurant.purposeId == 2){ rb.append(`<button class="ui primary fluid button" style="text-transform:uppercase;" ${branch.isAvailable == false ? `disabled` : ``}  id="ting-open-make-reservation">Make a Reservation</button>`)}

            var rb__pi = $(".ting-session-profile-image");
            rb__pi.append(`<button class="ting-btn-animate ting-like-restaurant-branch ${likesresto(branch) == true ? 'liked' : ''}" id="ting-like-restaurant-branch-${branch.id}" style="margin-top:8px; margin-right:6px;" data-like='{"resto":"${branch.restaurant.id}", "tkn":"${branch.restaurant.token}", "branch": "${branch.id}", "id":"${branch.id}", "typ":"link"}'>${likerestobtn(branch)}</button>
                           <script type="text/javascript">$(".ting-like-restaurant-branch").likeRestaurant();</script>`);
            
            var bctn = $("#ting-menus-list");
            var tmc = $("#ting-menus-container");
            var octn = $("#ting-other-menus-list");

            var pag__p = [];
            var pag__s = 0;
            var pag__m = 15;
            var pag__cont = $(`<div class="ui right floated pagination menu"></div>`);
            tmc.append(pag__cont);

            rb.find("#ting-open-make-reservation").click(function(e){
                e.preventDefault();
                var auth = window.__TING__Session;
                if(typeof auth == 'object' && auth.id !== null && auth.token !== undefined){
                    $("#ting-make-reservation-modal").modal({
                        onShow: function(){
                            var today = new Date();
                            $("#ting-datepicker-book-date").calendar({
                                type: 'date',
                                minDate: new Date(today.getFullYear(), today.getMonth(), today.getDate() + parseInt(branch.restaurant.config.daysBeforeReservation)),
                                monthFirst: false,
                                formatter: {
                                    date: function (date, settings) {
                                        if (!date) return '';
                                        var day = date.getDate();
                                        var month = date.getMonth() + 1;
                                        var year = date.getFullYear();
                                        return year + '-' + month + '-' + day;
                                    }
                                }
                            });
                            $("#ting-datepicker-book-time").calendar({
                                type: 'time',
                                formatter: {
                                    date: function(date, settings){
                                        if(!date) return '';
                                        var hours = date.getHours();
                                        var mins = date.getMinutes();
                                        return hours + ":" + mins;
                                    }
                                }
                            });
                        }
                    }).modal("show");
                } else {$("#ting-user-login").click(); showErrorMessage(randomString(10), "Login Required !!!");}
            });

            $("#ting-make-reservation-modal-form").submit(function(e){
                e.preventDefault();
                var method = $(this).attr("method");
                var url = $(this).attr("action");
                var form = new FormData($(this)[0]);
                var outter_progress =  $(this).find(".ting-loader");
                var button = $(this).find("button[type=submit]");
                form.append("link", window.location.href);
                form.append("os", window.navigator.appVersion);

                $.ajax({
                    xhr: function () {
                        var xhr = new window.XMLHttpRequest();
                        button.attr("disabled", "disabled");
                        if(outter_progress != null) outter_progress.show();
                        return xhr;
                    },
                    type: method,
                    url: url,
                    data: form,
                    processData: false,
                    contentType: false,
                    success: function(r){
                        if(r.type == "success"){
                            showSuccessMessage(r.type, r.message);
                            $("#ting-make-reservation-modal").modal("hide");
                        } else { showErrorMessage(r.type, r.message);}
                        button.removeAttr("disabled");
                        if(outter_progress != null) outter_progress.hide();
                    },
                    error: function(_, t, e){showErrorMessage(randomString(8), e); button.removeAttr("disabled");if(outter_progress != null){outter_progress.hide()}}
                });
            });

            if(state.name == "promos"){
                var promos = branch.promotions.promotions;
                var tpromos = promos.filter(function(p){return p.isOnToday == true && p.isOn == true});
                var opromos = promos.filter(function(p){return p.isOnToday == false && p.isOn == true});
                getpromotionslist(tpromos, 0);
                getpromotionslist(opromos, 1);
                tmc.find(".pagination").hide();
            } else if (state.name == "foods"){
                var foods = branch.menus.menus.filter(function(m){ return m.type.id == 1 });
                creatempags(foods, true);
                if(foods.length > 0){ getmenuslist(foods.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)));} 
                else { getmenuslist(foods.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}));}
            
                var mf__fd = $("#ting-food-groups");

                mf__fd.change(function(e){
                    var v = $(this).val(); pag__s = 0;
                    if (v == 0 ){ 
                        creatempags(foods, true);
                        if(foods.length > 0){getmenuslist(foods.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)));} 
                        else {getmenuslist(foods.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}));}
                    } else {
                        var nfds = foods.filter(function(m) { return m.menu.foodTypeId == v });
                        creatempags(nfds, true); 
                        if(nfds.length > 0){getmenuslist(nfds.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)));} 
                        else { getmenuslist(nfds.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}));}
                    }
                });
            } else if (state.name == "drinks"){
                var drinks = branch.menus.menus.filter(function(m){ return m.type.id == 2 });
                creatempags(drinks, true);
                if(drinks.length > 0){ getmenuslist(drinks.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)));} 
                else { getmenuslist(drinks.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}));}
            
                var mf__fd = $("#ting-food-groups");

                mf__fd.change(function(e){
                    var v = $(this).val(); pag__s = 0;
                    if (v == 0 ){ 
                        creatempags(drinks, true);
                        if(drinks.length > 0){getmenuslist(drinks.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)));} 
                        else {getmenuslist(drinks.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}));}
                    } else {
                        var nfds = drinks.filter(function(m) { return m.menu.drinkTypeId == v });
                        creatempags(nfds, true); 
                        if(nfds.length > 0){getmenuslist(nfds.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)));} 
                        else { getmenuslist(nfds.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}));}
                    }
                });
            } else if (state.name == "dishes"){
                var dishes = branch.menus.menus.filter(function(m){ return m.type.id == 3 });
                creatempags(dishes, true);
                if(dishes.length > 0){ getmenuslist(dishes.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)));} 
                else { getmenuslist(dishes.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}));}
            
                var mf__fd = $("#ting-food-groups");

                mf__fd.change(function(e){
                    var v = $(this).val(); pag__s = 0;
                    if (v == 0 ){ 
                        creatempags(dishes, true);
                        if(dishes.length > 0){getmenuslist(dishes.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)));} 
                        else {getmenuslist(dishes.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}));}
                    } else {
                        var nfds = dishes.filter(function(m) { return m.menu.dishTimeId == v });
                        creatempags(nfds, true); 
                        if(nfds.length > 0){getmenuslist(nfds.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}).slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)));} 
                        else { getmenuslist(nfds.sort(function(a, b){ if ( a.menu.price < b.menu.price ){ return -1;} if ( a.menu.price > b.menu.price ){ return 1;} return 0;}));}
                    }
                });
            } else if (state.name == "reviews"){
                var rcnt = $("#ting-restaurant-reviews");
                rcnt.html(`
                    <div class="ui grid">
                        <div class="row" style="padding:0 !important;">
                            <div class="four wide column ting-rate-average">
                                <h1 style="font-weight:500; margin-top:0 !important; font-size:50px !important;">${branch.reviews.average}</h1>
                                <p>Out Of 5</p>
                                <div class="ui disabled-rating huge star rating" data-rating="${branch.reviews.average}" data-max-rating="5"></div>
                            </div>
                            <div class="twelve wide column" style="padding: 0 !important;">
                                <div class="ui grid">
                                    <div class="row" style="padding-bottom:0 !important;">
                                        <div class="eight wide column ting-rate-percent">
                                            <div class="ting-star"><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i></div>
                                            <div class="ting-star"><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i></div>
                                            <div class="ting-star"><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i></div>
                                            <div class="ting-star"><i class="star icon"></i><i class="star icon"></i></div>
                                            <div class="ting-star"><i class="star icon"></i></div>
                                        </div>
                                        <div class="eight wide column ting-rate-wrapper">
                                            <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${branch.reviews.percents[4]}%"></div></div>
                                            <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${branch.reviews.percents[3]}%"></div></div>
                                            <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${branch.reviews.percents[2]}%"></div></div>
                                            <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${branch.reviews.percents[1]}%"></div></div>
                                            <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${branch.reviews.percents[0]}%"></div></div>
                                            <div class="ting-reviews-count"><p>${numerilize(branch.reviews.count, branch.id, 0)} reviews</p></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <script type="text/javascript">$(".disabled-rating").rating("disable"); $(".pagination").hide();</script>
                `);

                $.ajax({
                    type:"GET", url: branch.urls.loadReviews, data:{},
                    success: function(r){bctn.html(r)},
                    error: function(_, t, e){bctn.html(`<div class="ui red message">${e}</div>`)}
                });

                $("#ting-open-resto-review-modal").click(function(e){
                    e.preventDefault();
                    var auth = window.__TING__Session;
                    if(typeof auth == 'object' && auth.id !== undefined && auth.token !== undefined){
                        $("#ting-resto-review-modal").modal({
                            onShow: function(e){
                                $.ajax({
                                    type: "GET",
                                    url: branch.urls.addReview,
                                    data: {},
                                    success: function(r){
                                        var resp = JSON.parse(r);
                                        if(resp.type == true){
                                            $("#ting-resto-review-rate").rating("set rating", resp.data.review);
                                            $("#ting-resto-review-comment").val(resp.data.comment);
                                        }
                                    },
                                    error: function(_, t, e){showErrorMessage(randomString(8), e)}
                                });
                            }
                        }).modal("show");
                    } else {$("#ting-user-login").click(); showErrorMessage(randomString(10), "Login Required !!!");}
                });

                $("#ting-resto-review-rate").rating({onRate: function(value){$(this).attr("data-value", value);}}).rating();

                $("#ting-resto-review-form").submit(function(e){
                    e.preventDefault();
                    var method = $(this).attr("method");
                    var url = branch.urls.addReview;
                    var form = new FormData($(this)[0]);
                    var outter_progress =  $(this).find(".ting-loader");
                    var button = $(this).find("button[type=submit]");
                    var rate = $("#ting-resto-review-rate").rating("get rating");
                    form.append("review", rate);

                    $.ajax({
                        xhr: function () {
                            var xhr = new window.XMLHttpRequest();
                            button.attr("disabled", "disabled");
                            if(outter_progress != null) outter_progress.show();
                            return xhr;
                        },
                        type: method,
                        url: url,
                        data: form,
                        processData: false,
                        contentType: false,
                        success: function(r){
                            if(r.type == "success"){
                                showSuccessMessage(r.type, r.message);
                                $.ajax({
                                    type:"GET", url: branch.urls.loadReviews,
                                    success: function(r){bctn.html(r);},
                                    error: function(_, t, e){bctn.html(`<div class="ui red message">${e}</div>`)}
                                });
                            } else { showErrorMessage(r.type, r.message);}
                            $("#ting-resto-review-modal").modal("hide");
                            button.removeAttr("disabled");
                            if(outter_progress != null) outter_progress.hide();
                        },
                        error: function(_, t, e){showErrorMessage(randomString(8), e); button.removeAttr("disabled");if(outter_progress != null){outter_progress.hide()}}
                    });
                });
            } else if (state.name == "likes"){
                $.ajax({
                    type:"GET", url: branch.urls.loadLikes, data:{},
                    success: function(r){bctn.html(r)},
                    error: function(_, t, e){bctn.html(`<div class="ui red message">${e}</div>`)}
                });
                $(".pagination").hide();
            }

            function getpromotionslist(promos, t){
                if (promos.length > 0){

                    promos = promos.sort(function(a, b){
                        if ( Date.parse(a.updatedAt) < Date.parse(b.updatedAt) ){ return -1;}
                        if ( Date.parse(a.updatedAt) > Date.parse(b.updatedAt) ){ return 1;}
                        return 0;
                    });

                    var ctn = $(`<div class="ui items"></div>`).empty();

                    for (var i = 0; i < promos.length; i++){
                        var p = promos[i];
                        var tc = $("<div class='item ting-resto-item'></div>");
                        tc.attr("id", "ting-menu-item-" + p.id);
                        tc.attr("data-position", i);
                        tc.css("cursor", "pointer");
                        var ti = `  
                                <div class="ui medium image">
                                    <a href="${p.urls.relative}" target="_blank">
                                        <img src="${p.posterImage}">
                                    </a>
                                </div>
                                <div class="ui content">
                                    <a class="header" href="${p.urls.relative}" target="_blank" style="font-size:19px; font-weight:500;">${p.occasionEvent}</a>
                                    <div class="ting-like-restaurant">
                                        <button class="ting-like-restaurant ting-btn-animate ${interesetpromo(p.interests) == true ? 'liked' : ''}" id="ting-interest-promo-${p.id}" data-like='{"resto":"${branch.restaurant.id}", "tkn":"${branch.restaurant.token}", "id":"${p.id}", "promo": "${p.id}", "typ":"link", "url":"${p.urls.interest}"}'>${interesetpromoic(p.interests)}</button>
                                    </div>
                                    <div class="extra">
                                        <div class="ui label">
                                            <i class="icon star"></i>
                                            Promotion On ${p.promotionItem.type.name}
                                        </div>
                                        ${p.promotionItem.type.id == '05' 
                                            ? `<div class="ui image label">
                                                    <img src="${p.promotionItem.category.image}" />
                                                    Promotion On ${p.promotionItem.category.name}
                                                </div>` 
                                            : ``}
                                        ${p.promotionItem.type.id == '04' 
                                            ? `<div class="ui image label" onclick="window.open('${p.promotionItem.menu.url}', '_blank')">
                                                    <img src="${p.promotionItem.menu.menu.images.images[0].image}" />
                                                    Promotion On ${p.promotionItem.menu.menu.name}
                                                </div>` 
                                            : ``}
                                    </div>
                                    <div class="meta" style="padding:0;">
                                        ${p.promotionItem.type.id == `00` 
                                            ? `
                                                <div class="ting-menus-list-item">
                                                    ${branch.menus.count > 0 ? branch.menus.menus.sort(function(a, b){
                                                        if ( a.menu.reviews.count < b.menu.reviews.count ){ return -1;}
                                                        if ( a.menu.reviews.count > b.menu.reviews.count ){ return 1;}
                                                        return 0;
                                                    }).slice(0, 4).sort(function(){return Math.random() - 0.5}).map(function(m){
                                                        return `${_getmenu(m)}`;
                                                    }).join("") : `<div class="ui red message">No Menu To Show</div>`}
                                                </div>
                                            ` 
                                            : ``}
                                        ${p.promotionItem.type.id == `01` 
                                            ? `
                                                <div class="ting-menus-list-item">
                                                    ${branch.menus.menus.filter(function(m){return m.type.id == 1}).length > 0 ? branch.menus.menus.filter(function(m){return m.type.id == 1}).sort(function(a, b){
                                                        if ( a.menu.reviews.count < b.menu.reviews.count ){ return -1;}
                                                        if ( a.menu.reviews.count > b.menu.reviews.count ){ return 1;}
                                                        return 0;
                                                    }).slice(0, 4).sort(function(){return Math.random() - 0.5}).map(function(m){
                                                        return `${_getmenu(m)}`;
                                                    }).join("") : `<div class="ui red message">No Menu To Show</div>`}
                                                </div>
                                            ` 
                                            : ``}
                                        ${p.promotionItem.type.id == `02` 
                                            ? `
                                                <div class="ting-menus-list-item">
                                                    ${branch.menus.menus.filter(function(m){return m.type.id == 2}).length > 0 ? branch.menus.menus.filter(function(m){return m.type.id == 2}).sort(function(a, b){
                                                        if ( a.menu.reviews.count < b.menu.reviews.count ){ return -1;}
                                                        if ( a.menu.reviews.count > b.menu.reviews.count ){ return 1;}
                                                        return 0;
                                                    }).slice(0, 4).sort(function(){return Math.random() - 0.5}).map(function(m){
                                                        return `${_getmenu(m)}`;
                                                    }).join("") : `<div class="ui red message">No Menu To Show</div>`}
                                                </div>
                                            ` 
                                            : ``}
                                        ${p.promotionItem.type.id == `03` 
                                            ? `
                                                <div class="ting-menus-list-item">
                                                    ${branch.menus.menus.filter(function(m){return m.type.id == 3}).length > 0 ? branch.menus.menus.filter(function(m){return m.type.id == 3}).sort(function(a, b){
                                                        if ( a.menu.reviews.count < b.menu.reviews.count ){ return -1;}
                                                        if ( a.menu.reviews.count > b.menu.reviews.count ){ return 1;}
                                                        return 0;
                                                    }).slice(0, 4).sort(function(){return Math.random() - 0.5}).map(function(m){
                                                        return `${_getmenu(m)}`;
                                                    }).join("") : `<div class="ui red message">No Menu To Show</div>`}
                                                </div>
                                            ` 
                                            : ``}
                                        ${p.promotionItem.type.id == `04` 
                                            ? `
                                                <div class="ting-menus-list-item ting-menu-url lst-popup-${p.id}-${p.promotionItem.menu.id}" href="${p.promotionItem.menu.url}" id="ting-menus-list-item-${p.id}-${p.promotionItem.menu.id}">
                                                    ${p.promotionItem.menu.menu.images.count > 0 ? p.promotionItem.menu.menu.images.images.sort(function(){
                                                        return Math.random() - 0.5
                                                    }).slice(0, 4).map(function(m){
                                                        return `<div class="ting-menu-image-list">
                                                                    <img src="${m.image}" />
                                                                </div>`;
                                                    }).join("") : `<div class="ui red message">No Images To Show</div>`}
                                                </div>
                                                <div class="ui flowing popup basic transition hidden ting-menu-popup-${p.id}-${p.promotionItem.menu.id}">
                                                    <div class="header">${p.promotionItem.menu.menu.name}</div>
                                                    <div class="ui star rating disabled-rating" data-rating="${p.promotionItem.menu.menu.reviews.average}" data-max-rating="5" style="margin-top:5px;"></div>
                                                    <div class="description">${p.promotionItem.menu.menu.description}</div>
                                                    <p class="ui ${p.promotionItem.menu.menu.isAvailable == true ? `green` : `red`}" style="color: ${p.promotionItem.menu.menu.isAvailable == true ? `green` : `red`}">${p.promotionItem.menu.menu.isAvailable == true ? `<i class="icon check"></i> Available` : `<i class="icon times"></i> Not Available`}</p>
                                                    <div class="extra">
                                                        ${p.promotionItem.menu.menu.category !== undefined ? `<div class="ui label"><i class="icon boxes"></i> ${p.promotionItem.menu.menu.category.name}</div>` : ``}
                                                        ${p.promotionItem.menu.type.id == 1 ? `<div class="ui label"><i class="icon utensils spoon"></i> ${p.promotionItem.menu.menu.foodType}</div>` : ``}
                                                        ${p.promotionItem.menu.type.id == 2 ? `<div class="ui label"><i class="icon glass martini"></i> ${p.promotionItem.menu.menu.drinkType}</div>` : ``}
                                                        ${p.promotionItem.menu.type.id == 3 ? `<div class="ui label"><i class="icon clock"></i> ${p.promotionItem.menu.menu.dishTime}</div>` : ``}
                                                        <div class="ui label"><i class="icon tag"></i> ${p.promotionItem.menu.menu.currency} ${numerilize(p.promotionItem.menu.menu.price, p.promotionItem.menu.menu.price, 0)} ${p.promotionItem.menu.menu.isCountable == true ? ` (${p.promotionItem.menu.menu.quantity} pieces)` : ``}</div>
                                                    </div>
                                                </div><script type="text/javascript">$(".lst-popup-${p.id}-${p.promotionItem.menu.id}").popup({popup : ".ting-menu-popup-${p.id}-${p.promotionItem.menu.id}", on : "hover"});
                                                    $(".disabled-rating").rating("disable");
                                                    $(".ting-menu-url").click(function(){window.open($(this).attr("href"), "_blank")})
                                                </script>
                                            ` 
                                            : ``}
                                        ${p.promotionItem.type.id == `05` 
                                            ? `
                                                <div class="ting-menus-list-item">
                                                    ${branch.menus.menus.filter(function(m){return m.type.id != 2}).filter(function(m){return m.menu.category.id == p.promotionItem.category.id}).length > 0 
                                                    ? branch.menus.menus.filter(function(m){return m.type.id != 2}).filter(function(m){return m.menu.category.id == p.promotionItem.category.id}).sort(function(a, b){
                                                        if ( a.menu.reviews.count < b.menu.reviews.count ){ return -1;}
                                                        if ( a.menu.reviews.count > b.menu.reviews.count ){ return 1;}
                                                        return 0;
                                                    }).slice(0, 4).sort(function(){return Math.random() - 0.5}).map(function(m){
                                                        return `${_getmenu(m)}`;
                                                    }).join("") : `<div class="ui red message">No Menu To Show</div>`}
                                                </div>
                                            ` 
                                            : ``}
                                    </div>
                                    <div class="description">
                                        <p><i class="icon calendar alternate outline"></i> ${p.period}</p>
                                        ${p.reduction.hasReduction == true ? `<p><i class="icon minus square outline"></i> Order this menu and get a ${p.reduction.amount} ${p.reduction.reductionType} reduction</p>` : ``}
                                        ${p.supplement.hasSupplement == true ? 
                                            `<p>
                                                <i class="icon plus square outline"></i>
                                                Order ${p.supplement.minQuantity} pieces or packs of this menu and get ${p.supplement.quantity}
                                                ${p.supplement.isSame == true ?
                                                    ` more for free` 
                                                    : ` free <a href="${p.supplement.supplement.url}" target="_blank">${p.supplement.supplement.menu.name}</a> `}
                                                        </p>` 
                                            : ``}
                                    </div>
                                    <div class="extra">
                                        <div class="ui label"><i class="icon clock"></i>${makeMoment(p.updatedAt)}</div>
                                        <div class="ui label"><i class="icon star"></i>${p.interests.count}</div>
                                    </div>
                                </div>
                                <script type="text/javascript">$("#ting-interest-promo-${p.id}").interestPromotion();</script>
                            `;

                        function _getmenu(m){
                            return `<div class="ting-menu-image-list ting-menu-url lst-popup-${p.id}-${m.id}" href="${m.url}" id="ting-menus-list-item-${p.id}-${m.id}">
                                    <img src="${m.menu.images.images[Math.floor(Math.random() * (m.menu.images.count - 1))].image}" />
                                </div>
                                <div class="ui flowing popup basic transition hidden ting-menu-popup-${p.id}-${m.id}">
                                    <div class="header">${m.menu.name}</div>
                                    <div class="ui star rating disabled-rating" data-rating="${m.menu.reviews.average}" data-max-rating="5" style="margin-top:5px;"></div>
                                    <div class="description">${m.menu.description}</div>
                                    <p class="ui ${m.menu.isAvailable == true ? `green` : `red`}" style="color: ${m.menu.isAvailable == true ? `green` : `red`}">${m.menu.isAvailable == true ? `<i class="icon check"></i> Available` : `<i class="icon times"></i> Not Available`}</p>
                                    <div class="extra">
                                        ${m.menu.category !== undefined ? `<div class="ui label"><i class="icon boxes"></i> ${m.menu.category.name}</div>` : ``}
                                        ${m.type.id == 1 ? `<div class="ui label"><i class="icon utensils spoon"></i> ${m.menu.foodType}</div>` : ``}
                                        ${m.type.id == 2 ? `<div class="ui label"><i class="icon glass martini"></i> ${m.menu.drinkType}</div>` : ``}
                                        ${m.type.id == 3 ? `<div class="ui label"><i class="icon clock"></i> ${m.menu.dishTime}</div>` : ``}
                                    <div class="ui label"><i class="icon tag"></i> ${m.menu.currency} ${numerilize(m.menu.price, m.menu.price, 0)} ${m.menu.isCountable == true ? ` (${m.menu.quantity} pieces)` : ``}</div>
                                </div>
                                </div><script type="text/javascript">$(".lst-popup-${p.id}-${m.id}").popup({popup : ".ting-menu-popup-${p.id}-${m.id}", on : "hover"});
                                    $(".disabled-rating").rating("disable");
                                    $(".ting-menu-url").click(function(){window.open($(this).attr("href"), "_blank")})
                                </script>
                            `;
                        }

                        tc.html(ti);
                        ctn.append(tc);
                    }
                    if(t == 0){bctn.html(ctn);} else {octn.html(ctn);}
                } else { if(t == 0){bctn.html(`<div class="ting-empty-data"><i class="icon star"></i><p>No Promotion To Show</p></div>`)} else {octn.html(`<div class="ting-empty-data"><i class="icon star"></i><p>No Promotion To Show</p></div>`)}}
            }

            function getmenuslist(menus){

                if (menus.length > 0){
                    
                    menus = menus.sort(function(a, b){
                        if ( a.menu.price < b.menu.price ){ return -1;}
                        if ( a.menu.price > b.menu.price ){ return 1;}
                        return 0;
                    });

                    var ctn = $(`<div class="ui items"></div>`).empty();

                    for(var i = 0; i < menus.length; i++){
                        var m = menus[i].menu;
                        var tc = $("<div class='item ting-resto-item'></div>");
                        tc.attr("id", "ting-menu-item-" + m.id);
                        tc.attr("data-position", i);
                        tc.css("cursor", "pointer");
                        var ti = `  
                                <div class="ui medium image">
                                    <a href="${m.url}" target="_blank">
                                        <img src="${m.images.images[Math.floor(Math.random() * (m.images.count - 1))].image}">
                                    </a>
                                </div>
                                <div class="ui content">
                                    <a class="header" href="${m.url}" target="_blank" style="font-size:19px; font-weight:500;">${m.name}</a>
                                    <div class="meta" style="margin-top:5px;">
                                        <div class="ui disabled-rating star rating" data-rating="${m.reviews.average}" data-max-rating="5" style="margin-bottom:10px;"></div>
                                        <p><i icon class="icon align left"></i> ${m.description}</p>
                                        <div class="ting-price-promo" style="height:46px;">
                                            <div class="ting-menu-promo" id="ting-menu-promo-${menus[i].id}">
                                                <div style="width: 100%; height: 55px; text-align: center;">
                                                    <img src="${window.__TING__URL_Loader_Image}" style="width: 20px; height: 20px; margin-top: 17px;"/>
                                                </div>
                                            </div>
                                            <div class="ting-menu-price" ${m.isCountable == false ? `style="margin-top:13px;"` : ``}>
                                                ${m.isCountable == true ? `<p>${m.quantity} pieces / packs</p>` : ``}
                                                <p>${m.price != m.lastPrice ? `<span style="font-size:14px; text-decoration: line-through;">${m.currency}${numerilize(m.lastPrice, m.lastPrice, 0)}</span>` : ``}<span style="font-weight:500; font-size: 20px;">${m.currency} ${numerilize(m.price, m.price, 0)}</span></p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="description">
                                        <div class="ting-menus-list-item" id="ting-menus-list-item-${menus[i].id}">
                                            ${m.images.count > 0 ? m.images.images.map(function(m){
                                                return `<div class="ting-menu-image-list">
                                                            <img src="${m.image}" />
                                                        </div>`;
                                            }).join("") : `<div class="ui red message">No Images To Show</div>`}
                                        </div>
                                    </div>
                                    ${menus[i].type.id !== 2 ? `
                                        <div class="extra">
                                            <div class="ui label"><i class="icon boxes"></i> ${m.category.name}</div>
                                            <div class="ui image label"><img src="${m.cuisine.image}" /> ${m.cuisine.name}</div>
                                        </div>
                                    ` : ``}
                                    <div class="extra">
                                        ${menus[i].type.id == 1 ? `<div class="ui label"><i class="icon utensils spoon"></i> ${m.foodType}</div>` : ``}
                                        ${menus[i].type.id == 2 ? `<div class="ui label"><i class="icon glass martini"></i> ${m.drinkType}</div>` : ``}
                                        ${menus[i].type.id == 3 ? `<div class="ui label"><i class="icon clock"></i> ${m.dishTime}</div>` : ``}
                                        <div class="ui ${m.isAvailable == true ? "green" : "red"} label"><i class="${m.isAvailable == true ? "check" : "times"} icon"></i> ${m.isAvailable == true ? "Available" : "Not Available"}</div>
                                        <div class="ui label" style="cursor:pointer;"><i class="heart outline icon"></i>${numerilize(m.likes.count, null, 0)}</div>
                                        <div class="ui label ting-rate-btn-${menus[i].id}" style="cursor:pointer;"><i class="star outline icon"></i>${numerilize(m.reviews.count, null, 0)}</div>
                                    </div>
                                    <div class="ting-like-restaurant">
                                        <button class="ting-like-restaurant ting-btn-animate ${likesmenu(m) == true ? 'liked' : ''}" id="ting-like-menu-${menus[i].id}" data-like='{"menu":"${menus[i].id}", "pk":"${m.id}", "type": "${menus[i].type.id}", "typ":"link"}'>${likemenubtn(m)}</button>
                                    </div>
                                    <div class="ui flowing popup top left transition hidden ting-rate-popup-${menus[i].id}">
                                        <div class="header">Rating</div>
                                        <div class="content" style="width:300px;">
                                            <div class="ui huge star rating disabled-rating" data-rating="${m.reviews.average}" data-max-rating="5"></div>
                                            <div class="ui grid">
                                                <div class="row" style="padding:0 !important;">
                                                    <div class="four wide column ting-rate-average">
                                                        <h1 style="font-weight:500; margin-top:0 !important;">${m.reviews.average}</h1>
                                                        <p>Out Of 5</p>
                                                    </div>
                                                    <div class="twelve wide column" style="padding: 0 !important;">
                                                        <div class="ui grid">
                                                            <div class="row" style="padding-bottom:0 !important;">
                                                                <div class="eight wide column ting-rate-percent">
                                                                    <div class="ting-star"><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i></div>
                                                                    <div class="ting-star"><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i></div>
                                                                    <div class="ting-star"><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i></div>
                                                                    <div class="ting-star"><i class="star icon"></i><i class="star icon"></i></div>
                                                                    <div class="ting-star"><i class="star icon"></i></div>
                                                                </div>
                                                                <div class="eight wide column ting-rate-wrapper">
                                                                    <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${m.reviews.percents[4]}%"></div></div>
                                                                    <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${m.reviews.percents[3]}%"></div></div>
                                                                    <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${m.reviews.percents[2]}%"></div></div>
                                                                    <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${m.reviews.percents[1]}%"></div></div>
                                                                    <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${m.reviews.percents[0]}%"></div></div>
                                                                    <div class="ting-reviews-count"><p>${numerilize(m.reviews.count, m.id, 0)} reviews</p></div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <script type="text/javascript">
                                        $(".disabled-rating").rating("disable"); $("#ting-like-menu-${menus[i].id}").likeMenu();
                                        $(".ting-rate-btn-${menus[i].id}").popup({popup : ".ting-rate-popup-${menus[i].id}", on : "click"});
                                    </script>
                                </div>
                            `;
                        tc.html(ti);
                        ctn.append(tc);
                    }
                    bctn.html(ctn);
                    setTimeout(function(){
                        menus.forEach(function(menu) {
                            var mtpros = decodeURIparams(window.__TING__URL__Menu__Today__Promotion, {"menu": menu.id})
                            $.ajax({
                                type:"GET", url: mtpros, data:{},
                                success: function(r){bctn.find("#ting-menu-promo-" + menu.id).html(r)},
                                error: function(_, t, e){bctn.find("#ting-menu-promo-" + menu.id).html(`<div class="ui red message">${e}</div>`)}
                            })
                        })
                    }, 2000)
                } else { bctn.html(`<div class="ting-empty-data"><i class="icon utensils"></i><p>No Menu ${capitalize(state.name)} To Show</p></div>`) }
            }

            function creatempags(mns, ev){
                if(mns.length > 0){
                    var pag__n = Math.floor(mns.length / pag__m);
                    var pag__l = mns.length - (pag__n * pag__m);
                    pag__cont.empty().show();
                    pag__p = [];
                    if(pag__l > 0){pag__n++}
                    var pag__c = 0;
                    for(var p = 0; p < pag__n; p++){pag__p.push({from: pag__c, to: pag__c + pag__m, pos: p}); pag__c += pag__m}
                    if(pag__s != 0){ pag__cont.append(`<a class="item" data-position="prev"><i class="left chevron icon"></i></a>`)}
                    if(pag__p.length > 1){
                        for(var p = 0; p < pag__p.length; p++){
                            pag__cont.append(`<a class="item" data-from="${pag__p[p].from}" data-to="${pag__p[p].to}" data-position="${pag__p[p].pos}">${pag__p[p].pos + 1}</a>`)
                        }
                    } else { pag__cont.hide() }
                    if(pag__p.length > 1 && pag__s != pag__p.length - 1){pag__cont.append(`<a class="icon item" data-position="next"><i class="right chevron icon"></i></a>`)}
                    pag__cont.find("a").click(function(){
                        var p = $(this).attr("data-position");
                        if(p == "next"){pag__s++} else if(p == "prev"){pag__s--;} else {pag__s = p;}
                        creatempags(mns, true);
                        getmenuslist(mns.slice(parseInt(pag__p[pag__s].from), parseInt(pag__p[pag__s].to)));
                    });
                    pag__cont.find("a[data-position="+pag__s+"]").addClass("active").siblings().removeClass("active");
                } else { pag__p = []; pag__cont.empty().hide(); }
            }
        } else if (state.type == "menu"){

            var menu = window.__TING__Menu;
            var m = menu.menu;
            var mcnt = $("#ting-menu-container");
            var macnt = $(`<div></div>`);

            var usa = {lat: lat, lng: long}

            if(usa.lat != 0 && usa.lat !== undefined && usa.lng != 0 && usa.lng !== undefined){
                var _ds = new google.maps.LatLng(usa.lat, usa.lng)
                var _de = new google.maps.LatLng(parseFloat(m.branch.latitude), parseFloat(m.branch.longitude))
                m.branch.dist = calculateDistance(_ds, _de)
            } else {m.branch.dist = 0.00 }

            var bst = statusWorkTime(m.restaurant.opening, m.restaurant.closing)

            var bg__grid = $(`<div class="ui grid"></div>`);
            var bg__row = $(`<div class="row" style="padding:0;"></div>`);

            var img__cnt = $(`<div class="col-lg-6"></div>`);
            var desc__cnt = $(`<div class="col-lg-6"></div>`);

            var img__grid = $(`<div class="ui grid"></div>`);
            var img__row = $(`<div class="row" style="padding-top:0;"></div>`);

            var img__lst = $(`<div class="two wide column" style="padding-right:0"></div>`);
            var img__bg = $(`<div class="fourteen wide column" style="padding-right:0;"></div>`);

            var img__lst__itms = $(`<div class="ui items ting-menu-image-big-list"></div>`);

            var m__imgs = menu.menu.images;
            var rand__img__p = Math.floor(Math.random() * (m__imgs.count - 1));

            for(var i = 0; i < m__imgs.count; i++){
                img__lst__itms.append(`<div class="item"><img src="${m__imgs.images[i].image}" class="ui image fluid ${i == rand__img__p ? `active` : ``}"/></div>`)
            }

            img__bg.append(`<div class="ting-menu-image-big ui image fluid"><img id="ting-menu-image-big" src="${m__imgs.images[rand__img__p].image}"/></div>`);

            img__lst__itms.find("img").click(function(){
                var src = $(this).attr("src");
                $(this).addClass("active").parent().siblings().find("img").removeClass("active");
                $("#ting-menu-image-big").attr("src", src);
            });

            desc__cnt.append(`
                    <div class="ui ting-menu-description">
                        <div class="header"><h3>${m.name}</h3></div>
                        <div class="ui disabled-rating star large rating" style="margin-top:5px;" data-rating="${m.reviews.average}" data-max-rating="5" style="margin-bottom:10px;"></div>
                        <p style="margin-top:5px;"><i icon class="icon align left"></i> ${m.description}</p>
                        ${menu.type.id != 2 ? `
                            <div class="extra" style="margin-bottom:10px;">
                                <div class="ui image label"><img src="${m.category.image}">${m.category.name}</div>
                                <div class="ui image label"><img src="${m.cuisine.image}">${m.cuisine.name}</div>
                            </div>
                        ` : ``}
                        <div class="extra">
                            ${menu.type.id == 1 ? `<div class="ui label"><i class="utensils spoon icon"></i> ${menu.type.name}</div> <div class="ui label"><i class="icon boxes"></i> ${m.foodType}</div>` : ``}
                            ${menu.type.id == 2 ? `<div class="ui label"><i class="icon martini glass"></i> ${menu.type.name}</div> <div class="ui label"><i class="icon boxes"></i> ${m.drinkType}</div>` : ``}
                            ${menu.type.id == 3 ? `<div class="ui label"><i class="icon utensils"></i> ${menu.type.name}</div> <div class="ui label"><i class="icon clock alternate"></i> ${m.dishTime}</div>` : ``}
                            <div class="ui ${m.isAvailable == true ? "green" : "red"} label"><i class="${m.isAvailable == true ? "check" : "times"} icon"></i> ${m.isAvailable == true ? "Available" : "Not Available"}</div>
                            <div class="ui label" style="cursor:pointer;"><i class="heart outline icon"></i>${numerilize(m.likes.count, null, 0)}</div>
                        </div>
                    </div>
                    <div class="ting-menu-desc-ingredients">
                        <h6 style="font-size:15px;">Ingredients</h6>
                        <hr/>
                        ${m.ingredients}
                    </div>
                    <div class="ting-menu-promos">
                        <div class="ui items">
                            ${menu.type.id == 3 
                                ? `${m.foods.count > 0 
                                    ? `${m.foods.foods.map(function(f){
                                        return `
                                            <div class="item ting-resto-item ting-menu-url" href="${f.food.url}"  style="padding:1rem !important; cursor: pointer;">
                                                <div class="ui small image">
                                                    <div class="ui yellow ribbon label">
                                                        <i class="utensils spoon icon"></i> Food
                                                    </div>
                                                    <img src="${f.food.images.images[Math.floor(Math.random() * (f.food.images.count - 1))].image}" />
                                                </div>
                                                <div class="ui content">
                                                    <a class="header" style="color:#666; font-weight:400;">${f.food.name}</a>
                                                    <div class="description" style="margin-top:0;">
                                                        <div class="ui star rating disabled-rating" data-rating="${f.food.reviews.average}" data-max-rating="5" style="margin-top:5px;"></div>
                                                    </div>
                                                    <div class="description">
                                                        <p><i class="icon align left"></i> ${f.food.description}</p>
                                                        ${f.isCountable == true ? `<p><b>Quantity : </b> ${f.quantity} pieces / packs</p>` : ``}
                                                    </div>
                                                    <div class="extra">
                                                        <div class="ui label"><i class="icon boxes"></i> ${f.food.category.name}</div>
                                                        <div class="ui label"><i class="icon utensils spoon"></i> ${f.food.foodType}</div>
                                                        <div class="ui label"><i class="icon tag"></i> ${f.food.currency} ${numerilize(f.food.price, f.food.price, 0)} ${f.food.isCountable == true ? ` (${f.food.quantity} pieces)` : ``}</div>
                                                        <div class="ui ${f.food.isAvailable == true ? `green` : `red`} label" style="color: ${f.food.isAvailable == true ? `green` : `red`}">${f.food.isAvailable == true ? `<i class="icon check"></i> Available` : `<i class="icon times"></i> Not Available`}</div>
                                                    </div>
                                                </div>
                                            </div>
                                        `;
                                    }).join("")}` 
                                    : ``}` 
                                : ``}
                            ${menu.type.id == 3 
                                ? `${m.hasDrink == true 
                                    ? `
                                        <div class="item ting-resto-item ting-menu-url" href="${m.drink.url}"  style="padding:1rem !important; cursor: pointer;">
                                                <div class="ui small image">
                                                    <div class="ui yellow ribbon label">
                                                        <i class="glass martini icon"></i> Food
                                                    </div>
                                                    <img src="${m.drink.images.images[Math.floor(Math.random() * (m.drink.images.count - 1))].image}" />
                                                </div>
                                                <div class="ui content">
                                                    <a class="header" style="color:#666; font-weight:400;">${m.drink.name}</a>
                                                    <div class="description" style="margin-top:0;">
                                                        <div class="ui star rating disabled-rating" data-rating="${m.drink.reviews.average}" data-max-rating="5" style="margin-top:5px;"></div>
                                                    </div>
                                                    <div class="description">
                                                        <p><i class="icon align left"></i> ${m.drink.description}</p>
                                                    </div>
                                                    <div class="extra">
                                                        <div class="ui label"><i class="icon martini glass"></i> ${m.drink.drinkType}</div>
                                                        <div class="ui label"><i class="icon tag"></i> ${m.drink.currency} ${numerilize(m.drink.price, m.drink.price, 0)} ${m.drink.isCountable == true ? ` (${m.drink.quantity} pieces)` : ``}</div>
                                                        <div class="ui ${m.drink.isAvailable == true ? `green` : `red`} label" style="color: ${m.drink.isAvailable == true ? `green` : `red`}">${m.drink.isAvailable == true ? `<i class="icon check"></i> Available` : `<i class="icon times"></i> Not Available`}</div>
                                                    </div>
                                                </div>
                                            </div>
                                    ` 
                                    : ``}` 
                                : ``}
                            ${m.promotions.promotions.filter(function(p){return p.isOn == true && p.isOnToday == true}).length > 0 
                                ? `
                                ${m.promotions.promotions.filter(function(p){return p.isOn == true && p.isOnToday == true}).map(function(p){
                                    return `
                                    <div class="item ting-resto-item" style="padding:1rem !important;">
                                        <div class="ui small image">
                                            <div class="ui yellow ribbon label">
                                                <i class="star icon"></i> Promotion
                                            </div>
                                            <img src="${p.posterImage}" />
                                        </div>
                                        <div class="ui content">
                                            <a href="#" class="header" style="color:#666; font-weight:400;">${p.occasionEvent}</a>
                                            <div class="description">
                                                <p><i class="icon calendar alternate outline"></i> ${p.period}</p>
                                                ${p.reduction.hasReduction == true ? `<p><i class="icon minus square outline"></i> Order this menu and get a ${p.reduction.amount} ${p.reduction.reductionType} reduction</p>` : ``}
                                                ${p.supplement.hasSupplement == true ? 
                                                    `<p>
                                                        <i class="icon plus square outline"></i>
                                                        Order ${p.supplement.minQuantity} pieces or packs of this menu and get ${p.supplement.quantity}
                                                        ${p.supplement.isSame == true ?
                                                            ` more for free` 
                                                            : ` free ${p.supplement.supplement.menu.name} `}
                                                    </p>` 
                                                    : ``}
                                            </div>
                                        </div>
                                    </div>`;
                                }).join("")}
                            </div>
                            ` 
                            : `<div class="ui red message">No Promotion For This Menu</div>`}
                        </div>
                        <script type="text/javascript">
                            $(".disabled-rating").rating("disable");
                            $(".ting-menu-url").click(function(){window.open($(this).attr("href"))})
                        </script>
                    </div>
                    <hr/>
                    <div class="ting-meny-price">
                        ${menu.type.id == 1 ? `${m.isCountable == true ? `<p style="margin-bottom:5px;">${m.quantity} pieces / packs</p>` : ``}`:``}
                        ${menu.type.id == 2 ? `${m.isCountable == true ? `<p style="margin-bottom:5px;">${m.quantity} cups / bottles</p>` : ``}`:``}
                        ${menu.type.id == 3 ? `${m.isCountable == true ? `<p style="margin-bottom:5px;">${m.quantity} plates / packs</p>` : ``}`:``}
                        <p><span style="font-weight:500; font-size: 28px;">${m.currency} ${numerilize(m.price, m.price, 0)}</span>${m.price != m.lastPrice ? `<br/><span style="font-size:14px; text-decoration: line-through;">${m.currency}${numerilize(m.lastPrice, m.lastPrice, 0)}</span>` : ``}</p>
                        <div class="ting-like-restaurant">
                            <button class="ting-like-restaurant ting-btn-animate ${likesmenu(m) == true ? 'liked' : ''}" id="ting-like-menu-${menu.id}" data-like='{"menu":"${menu.id}", "pk":"${m.id}", "type": "${menu.type.id}", "typ":"link"}'>${likemenubtn(m)}</button>
                        </div>
                    </div>
                    <hr/>
                    <div class="extra">
                        <div class="ui image label" style="font-size:17px;">
                            <img src="${m.restaurant.logo}" />
                            <span class="text" style="cursor:pointer;" onclick="window.location = '${m.branch.urls.relative}'" >${m.restaurant.name}, ${m.branch.name}</span>
                        </div>
                        <span id="ting-resto-open-time-${m.branch.id}"><div class="ui ${m.branch.isAvailable == true ? bst.clr : "red"} label" style="padding-top: 0.85rem; padding-bottom:0.85rem;"><i class="clock outline icon"></i> ${m.branch.isAvailable == true ? bst.msg : "Not Available"}</div></span>
                        <div class="ui label ting-resto-item-map-direction" style="cursor:pointer; padding-top: 0.85rem; padding-bottom:0.85rem;" data-url="${decodeURIparams(window.__TING__URL_Load_Branch_Directions, {"restaurant": m.restaurant.id, "branch": m.branch.id})}" data-branch-id="${m.branch.id}"><i class="icon map marker alternate"></i> ${m.branch.dist} Km</div>
                    </div>
                    <script type="text/javascript">
                        $(".disabled-rating").rating("disable");$("#ting-like-menu-${menu.id}").likeMenu();
                        setInterval(function(){
                            var time = statusWorkTime("${m.restaurant.opening}", "${m.restaurant.closing}")
                            $("#ting-resto-open-time-${m.branch.id}").html('<div class="ui ${m.branch.isAvailable == true ? " ' + time.clr + ' " : "red"} label"><i class="clock outline icon"></i> ${m.branch.isAvailable == true ? " ' + time.msg + ' " : "Not Available"}</div>')
                        }, 30000)
                    </script>
                `);

            desc__cnt.find(".ting-resto-item-map-direction").click(function(e){
                e.preventDefault();
                var m = $("#ting-resto-branch-direction").modal("show");
                m.find(".content").html(loader);
                var url = $(this).attr("data-url");
                $.ajax({
                    type:"GET", url: url, data: {"lat": lat, "long": long, "addr": addr, "count": cntr, "town": twn},
                    success: function(r){m.find(".content").html(r)},
                    error: function(_, t, e){m.find(".content").html(`<div class="ui red message">${e}</div>`)}
                });
            });

            img__lst.html(img__lst__itms);
            img__row.append(img__lst).append(img__bg);
            img__grid.html(img__row);
            img__cnt.html(img__grid);

            bg__row.append(img__cnt).append(desc__cnt);
            bg__grid.html(bg__row);
            macnt.append(bg__grid).append(`<hr/>`);

            var br__grid = $(`<div class="ui divided grid"></div>`);
            var br__row = $(`<div class="row" style="padding:0;"></div>`);

            var br__reviews = $(`<div class="col-lg-8"></div>`);
            var br__omenu = $(`<div class="col-lg-4" style="padding-right:0;"></div>`);

            br__reviews.append(`
                    <div class="ui grid">
                        <div class="row" style="padding:0">
                            <div class="eleven wide column"><h3 style="font-weight: 100; text-transform:uppercase">Menu's Reviews</h3></div>
                            <div class="five wide column" style="padding:0; margin-left:-3px;"><button class="ui icon labeled primary button fluid" id="ting-open-menu-review-modal"><i class="icon pencil"></i>Write a Review</div></div>
                        </div>
                    </div>
                    <div class="content">
                        <div class="ui grid">
                            <div class="row" style="padding:0 !important;">
                                <div class="four wide column ting-rate-average">
                                    <h1 style="font-weight:500; margin-top:0 !important; font-size:50px !important;">${m.reviews.average}</h1>
                                    <p>Out Of 5</p>
                                    <div class="ui disabled-rating huge star rating" data-rating="${m.reviews.average}" data-max-rating="5"></div>
                                </div>
                                <div class="twelve wide column" style="padding: 0 !important;">
                                    <div class="ui grid">
                                        <div class="row" style="padding-bottom:0 !important;">
                                            <div class="eight wide column ting-rate-percent">
                                                <div class="ting-star"><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i></div>
                                                <div class="ting-star"><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i></div>
                                                <div class="ting-star"><i class="star icon"></i><i class="star icon"></i><i class="star icon"></i></div>
                                                <div class="ting-star"><i class="star icon"></i><i class="star icon"></i></div>
                                                <div class="ting-star"><i class="star icon"></i></div>
                                            </div>
                                            <div class="eight wide column ting-rate-wrapper">
                                                <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${m.reviews.percents[4]}%"></div></div>
                                                <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${m.reviews.percents[3]}%"></div></div>
                                                <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${m.reviews.percents[2]}%"></div></div>
                                                <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${m.reviews.percents[1]}%"></div></div>
                                                <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${m.reviews.percents[0]}%"></div></div>
                                                <div class="ting-reviews-count"><p>${numerilize(m.reviews.count, m.id, 0)} reviews</p></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <hr/>
                    <div class="content" id="ting-menu-reviews">${loader}</div>
                `);

            br__reviews.ready(function(){
                var c = br__reviews.find("#ting-menu-reviews");
                $.ajax({
                    type:"GET", url: menu.urls.loadReviews,
                    success: function(r){c.html(r);},
                    error: function(_, t, e){c.html(`<div class="ui red message">${e}</div>`)}
                });
                br__reviews.find("#ting-open-menu-review-modal").click(function(e){
                    e.preventDefault();
                    var auth = window.__TING__Session;
                    if(typeof auth == 'object' && auth.id !== undefined && auth.token !== undefined){
                        $("#ting-menu-review-modal").modal({
                            onShow: function(e){
                                $.ajax({
                                    type: "GET",
                                    url: menu.urls.addReview,
                                    data: {},
                                    success: function(r){
                                        var resp = JSON.parse(r);
                                        if(resp.type == true){
                                            $("#ting-menu-review-rate").rating("set rating", resp.data.review);
                                            $("#ting-menu-review-comment").val(resp.data.comment);
                                        }
                                    },
                                    error: function(_, t, e){showErrorMessage(randomString(8), e)}
                                });
                            }
                        }).modal("show");
                    } else {$("#ting-user-login").click(); showErrorMessage(randomString(10), "Login Required !!!");}
                });
            });

            $("#ting-menu-review-rate").rating({onRate: function(value){$(this).attr("data-value", value);}}).rating();

            $("#ting-menu-review-form").submit(function(e){
                e.preventDefault();
                var method = $(this).attr("method");
                var url = menu.urls.addReview;
                var form = new FormData($(this)[0]);
                var outter_progress =  $(this).find(".ting-loader");
                var button = $(this).find("button[type=submit]");
                var rate = $("#ting-menu-review-rate").rating("get rating");
                form.append("review", rate);

                $.ajax({
                    xhr: function () {
                        var xhr = new window.XMLHttpRequest();
                        button.attr("disabled", "disabled");
                        if(outter_progress != null) outter_progress.show();
                        return xhr;
                    },
                    type: method,
                    url: url,
                    data: form,
                    processData: false,
                    contentType: false,
                    success: function(r){
                        if(r.type == "success"){
                            showSuccessMessage(r.type, r.message);
                            var c = br__reviews.find("#ting-menu-reviews");
                            $.ajax({
                                type:"GET", url: menu.urls.loadReviews,
                                success: function(r){c.html(r);},
                                error: function(_, t, e){c.html(`<div class="ui red message">${e}</div>`)}
                            });
                        } else { showErrorMessage(r.type, r.message);}
                        $("#ting-menu-review-modal").modal("hide");
                        button.removeAttr("disabled");
                        if(outter_progress != null) outter_progress.hide();
                    },
                    error: function(_, t, e){showErrorMessage(randomString(8), e); button.removeAttr("disabled");if(outter_progress != null){outter_progress.hide()}}
                });
            });

            br__omenu.append(`<h2 style="font-weight:100; text-transform:uppercase">Others</h2>`)
            var br__omenu__items = $(`<div class="ui items"></div>`);

            var oms = menu.menu.branch.menus.menus.filter(function(_m){
                if (_m.type.id != 2 && m.category != undefined) {return _m.menu.category.id == menu.menu.category.id && _m.type.id == menu.type.id && _m.id != menu.id}
                else {return _m.type.id == menu.type.id && _m.id != menu.id && _m.menu.drinkType == m.drinkType}
            }).sort(function(){return Math.random() - 0.5}).slice(0, 4);

            if (oms.length > 0){
                for (var i = 0; i < oms.length; i++){
                    var _m = oms[i].menu;
                    var r = Math.floor(Math.random() * (_m.images.count - 1));
                    br__omenu__items.append(`
                        <div class="ting-menu-other">
                            <div class="item">
                                <div class="ui fluid image"><a href="${oms[i].url}"><img src="${_m.images.images[r].image}"/></a></div>
                            </div>
                            <div class="content" style="margin-top:5px;">
                                <a class="header" style="font-weight:500; font-size:17px; color: #666;" href="${oms[i].url}">${_m.name}</a>
                                <div class="description">
                                    <div class="ui disabled-rating star rating" data-rating="${_m.reviews.average}" data-max-rating="5"></div>
                                    <p><i icon class="icon align left"></i> ${_m.description}</p>
                                    ${oms[i].type.id == 1 ? `<div class="ui label" style="margin-bottom:8px;"><i class="utensils spoon icon"></i> ${oms[i].type.name}</div> <div class="ui label"><i class="icon boxes"></i> ${_m.foodType}</div>` : ``}
                                    ${oms[i].type.id == 2 ? `<div class="ui label" style="margin-bottom:8px;"><i class="icon martini glass"></i> ${oms[i].type.name}</div> <div class="ui label"><i class="icon boxes"></i> ${_m.drinkType}</div>` : ``}
                                    ${oms[i].type.id == 3 ? `<div class="ui label" style="margin-bottom:8px;"><i class="icon utensils"></i> ${oms[i].type.name}</div> <div class="ui label"><i class="icon clock alternate"></i> ${_m.dishTime}</div>` : ``}
                                    <div class="ui icon label" style="margin-bottom:8px;"><i class="icon tag"></i> ${_m.currency} ${numerilize(_m.price, _m.price, 0)}</div>
                                </div>
                            </div>
                            <hr/>
                        </div>
                    `)
                }
            } else {br__omenu__items.html(`<div class="ui red message">No Menu of The Same Category</div>`);}

            br__omenu.append(br__omenu__items);
            br__row.append(br__reviews).append(br__omenu);
            br__grid.html(br__row);
            macnt.append(br__grid);
            mcnt.html(macnt);
        } else if(state.type == "promotion"){

            if(state.name == "about"){
                var promo = window.__TING__Promotion;
                var mcnt = $("#ting-menu-container");
                var macnt = $(`<div></div>`);

                var usa = {lat: lat, lng: long}

                if(usa.lat != 0 && usa.lat !== undefined && usa.lng != 0 && usa.lng !== undefined){
                    var _ds = new google.maps.LatLng(usa.lat, usa.lng)
                    var _de = new google.maps.LatLng(parseFloat(promo.branch.latitude), parseFloat(promo.branch.longitude))
                    promo.branch.dist = calculateDistance(_ds, _de)
                } else { promo.branch.dist = 0.00 }

                var branch = promo.branch;

                var bst = statusWorkTime(promo.restaurant.opening, promo.restaurant.closing)

                var bg__grid = $(`<div class="ui grid"></div>`);
                var bg__row = $(`<div class="row" style="padding:0;"></div>`);

                var img__cnt = $(`<div class="container" style="padding-left:0; padding-right:0; margin-bottom:1rem;"></div>`);
                var desc__cnt = $(`<div class="col-lg-8"></div>`);
                var oth__promo = $(`<div class="col-lg-4" style="padding-right:0;"></div>`);

                var img__grid = $(`<div class="ui grid"></div>`);
                var img__row = $(`<div class="row" style="padding-top:0;"></div>`);

                var img__bg = $(`<div class="sixteen wide column" style="padding-right:0;"></div>`);

                img__bg.append(`<div class="ting-menu-image-big ui image fluid"><img id="ting-menu-image-big" src="${promo.posterImage}"/></div>`);

                desc__cnt.append(`
                        <div class="ui ting-menu-description">
                            <div class="header"><h3>${promo.occasionEvent}</h3></div>
                            <div class="ting-like-restaurant">
                                <button class="ting-like-restaurant ting-btn-animate ${interesetpromo(promo.interests) == true ? 'liked' : ''}" id="ting-interest-promo" data-like='{"resto":"${promo.restaurant.id}", "tkn":"${promo.restaurant.token}", "id":"${promo.id}", "promo": "${promo.id}", "typ":"link", "url":"${promo.urls.interest}"}'>${interesetpromoic(promo.interests)}</button>
                            </div>
                            <div class="extra" style="margin-top:1rem;">
                                <div class="ui label">
                                    <i class="icon star"></i>
                                    Promotion On ${promo.promotionItem.type.name}
                                </div>
                                ${promo.promotionItem.type.id == '05' 
                                    ? `<div class="ui image label">
                                            <img src="${promo.promotionItem.category.image}" />
                                            Promotion On ${promo.promotionItem.category.name}
                                        </div>` 
                                    : ``}
                                ${promo.promotionItem.type.id == '04' 
                                    ? `<div class="ui image label" onclick="window.open('${promo.promotionItem.menu.url}', '_blank')">
                                            <img src="${promo.promotionItem.menu.menu.images.images[0].image}" />
                                            Promotion On ${promo.promotionItem.menu.menu.name}
                                        </div>` 
                                    : ``}
                                <div class="ui ${promo.isOn == true && promo.isOnToday == true ? `green` : `red`} label" style="color: ${promo.isOn == true && promo.isOnToday == true ? `green` : `red`}">${promo.isOn == true && promo.isOnToday == true ? `<i class="icon check"></i> Is On Today` : `<i class="icon times"></i> Is Off Today`}</div>
                            </div>
                        </div>
                        <div class="ting-menu-desc-ingredients">
                            ${promo.description}
                        </div>
                        <div class="extra">
                            <div class="ui label"><i class="icon clock"></i>${makeMoment(promo.updatedAt)}</div>
                            <div class="ui label"><i class="icon star"></i>${promo.interests.count}</div>
                        </div>
                        <hr/>
                        <div class="description">
                            <p style="font-size:16px; margin-bottom:5px; "><i class="icon calendar alternate outline"></i> ${promo.period}</p>
                            ${promo.reduction.hasReduction == true ? `<p style="font-size:16px; margin-bottom:5px;"><i class="icon minus square outline"></i> Order this menu and get a ${promo.reduction.amount} ${promo.reduction.reductionType} reduction</p>` : ``}
                            ${promo.supplement.hasSupplement == true ? 
                                `<p style="font-size:16px; margin-bottom:5px;">
                                    <i class="icon plus square outline"></i>
                                    Order ${promo.supplement.minQuantity} pieces or packs of this menu and get ${promo.supplement.quantity}
                                    ${promo.supplement.isSame == true ?
                                        ` more for free` 
                                        : ` free <a href="${promo.supplement.supplement.url}" target="_blank">${promo.supplement.supplement.menu.name}</a> `}
                                            </p>` 
                                : ``}
                        </div>
                        <hr/>
                        <div class="ting-menu-promos">
                            <h5>Promoted Menus</h5>
                            <hr/>
                            ${promo.promotionItem.type.id == `00` 
                                ? `
                                    <div class="ui items">
                                        ${branch.menus.count > 0 ? branch.menus.menus.sort(function(a, b){
                                            if ( a.menu.reviews.count < b.menu.reviews.count ){ return -1;}
                                            if ( a.menu.reviews.count > b.menu.reviews.count ){ return 1;}
                                            return 0;
                                        }).slice(0, 4).sort(function(){return Math.random() - 0.5}).map(function(m){
                                            return `${_getmenu(m)}`;
                                        }).join("") : `<div class="ui red message">No Menu To Show</div>`}
                                    </div>
                                ` 
                                : ``}
                            ${promo.promotionItem.type.id == `01` 
                                ? `
                                    <div class="ui items">
                                        ${branch.menus.menus.filter(function(m){return m.type.id == 1}).length > 0 ? branch.menus.menus.filter(function(m){return m.type.id == 1}).sort(function(a, b){
                                            if ( a.menu.reviews.count < b.menu.reviews.count ){ return -1;}
                                            if ( a.menu.reviews.count > b.menu.reviews.count ){ return 1;}
                                            return 0;
                                        }).slice(0, 4).sort(function(){return Math.random() - 0.5}).map(function(m){
                                            return `${_getmenu(m)}`;
                                        }).join("") : `<div class="ui red message">No Menu To Show</div>`}
                                    </div>
                                ` 
                                : ``}
                            ${promo.promotionItem.type.id == `02` 
                                ? `
                                    <div class="ui items">
                                        ${branch.menus.menus.filter(function(m){return m.type.id == 2}).length > 0 ? branch.menus.menus.filter(function(m){return m.type.id == 2}).sort(function(a, b){
                                            if ( a.menu.reviews.count < b.menu.reviews.count ){ return -1;}
                                            if ( a.menu.reviews.count > b.menu.reviews.count ){ return 1;}
                                            return 0;
                                        }).slice(0, 4).sort(function(){return Math.random() - 0.5}).map(function(m){
                                            return `${_getmenu(m)}`;
                                        }).join("") : `<div class="ui red message">No Menu To Show</div>`}
                                    </div>
                                ` 
                                : ``}
                            ${promo.promotionItem.type.id == `03` 
                                ? `
                                    <div class="ui items">
                                        ${branch.menus.menus.filter(function(m){return m.type.id == 3}).length > 0 ? branch.menus.menus.filter(function(m){return m.type.id == 3}).sort(function(a, b){
                                            if ( a.menu.reviews.count < b.menu.reviews.count ){ return -1;}
                                            if ( a.menu.reviews.count > b.menu.reviews.count ){ return 1;}
                                            return 0;
                                        }).slice(0, 4).sort(function(){return Math.random() - 0.5}).map(function(m){
                                            return `${_getmenu(m)}`;
                                        }).join("") : `<div class="ui red message">No Menu To Show</div>`}
                                    </div>
                                ` 
                                : ``}
                            ${promo.promotionItem.type.id == `04` 
                                ? `<div class="ui items">${_getmenu(promo.promotionItem.menu)}</div>` 
                                : ``}
                            ${promo.promotionItem.type.id == `05` 
                                ? `
                                    <div class="ui items">
                                        ${branch.menus.menus.filter(function(m){return m.type.id != 2}).filter(function(m){return m.menu.category.id == promo.promotionItem.category.id}).length > 0 
                                            ? branch.menus.menus.filter(function(m){return m.type.id != 2}).filter(function(m){return m.menu.category.id == promo.promotionItem.category.id}).sort(function(a, b){
                                                if ( a.menu.reviews.count < b.menu.reviews.count ){ return -1;}
                                                if ( a.menu.reviews.count > b.menu.reviews.count ){ return 1;}
                                                return 0;
                                            }).slice(0, 4).sort(function(){return Math.random() - 0.5}).map(function(m){
                                                return `${_getmenu(m)}`;
                                            }).join("") : `<div class="ui red message">No Menu To Show</div>`}
                                    </div>
                                ` 
                                : ``}
                            <script type="text/javascript">$(".disabled-rating").rating("disable");</script>
                        </div>
                        <hr/>
                        <div class="extra" style="margin-bottom:1rem;">
                            <div class="ui image label" style="font-size:17px;">
                                <img src="${promo.restaurant.logo}" />
                                <span class="text" style="cursor:pointer;" onclick="window.location = '${promo.branch.urls.relative}'" >${promo.restaurant.name}, ${promo.branch.name}</span>
                            </div>
                            <span id="ting-resto-open-time-${promo.branch.id}"><div class="ui ${promo.branch.isAvailable == true ? bst.clr : "red"} label" style="padding-top: 0.85rem; padding-bottom:0.85rem;"><i class="clock outline icon"></i> ${promo.branch.isAvailable == true ? bst.msg : "Not Available"}</div></span>
                            <div class="ui label ting-resto-item-map-direction" style="cursor:pointer; padding-top: 0.85rem; padding-bottom:0.85rem;" data-url="${decodeURIparams(window.__TING__URL_Load_Branch_Directions, {"restaurant": promo.restaurant.id, "branch": promo.branch.id})}" data-branch-id="${promo.branch.id}"><i class="icon map marker alternate"></i> ${promo.branch.dist} Km</div>
                        </div>
                        <hr/>
                        <script type="text/javascript">
                            $("#ting-interest-promo").interestPromotion();
                            setInterval(function(){
                                var time = statusWorkTime("${promo.restaurant.opening}", "${promo.restaurant.closing}")
                                $("#ting-resto-open-time-${promo.branch.id}").html('<div class="ui ${promo.branch.isAvailable == true ? " ' + time.clr + ' " : "red"} label"><i class="clock outline icon"></i> ${promo.branch.isAvailable == true ? " ' + time.msg + ' " : "Not Available"}</div>')
                            }, 30000)
                        </script>
                    `);

                function _getmenu(m){
                    return `
                        <div class="item ting-resto-item ting-menu-url" href="${m.url}"  style="padding:1rem !important;">
                            <div class="ui small image">
                                <img src="${m.menu.images.images[Math.floor(Math.random() * (m.menu.images.count - 1))].image}" />
                            </div>
                            <div class="ui content">
                                <a href="${m.url}" class="header" style="color:#666; font-weight:400;">${m.menu.name}</a>
                                <div class="description" style="margin-top:0;">
                                    <div class="ui star rating disabled-rating" data-rating="${m.menu.reviews.average}" data-max-rating="5" style="margin-top:5px;"></div>
                                </div>
                                <div class="description">
                                    <p><i class="icon align left"></i> ${m.menu.description}</p>
                                </div>
                                <div class="extra">
                                    ${m.menu.category !== undefined ? `<div class="ui label"><i class="icon boxes"></i> ${m.menu.category.name}</div>` : ``}
                                    ${m.type.id == 1 ? `<div class="ui label"><i class="icon utensils spoon"></i> ${m.menu.foodType}</div>` : ``}
                                    ${m.type.id == 2 ? `<div class="ui label"><i class="icon glass martini"></i> ${m.menu.drinkType}</div>` : ``}
                                    ${m.type.id == 3 ? `<div class="ui label"><i class="icon clock"></i> ${m.menu.dishTime}</div>` : ``}
                                    <div class="ui label"><i class="icon tag"></i> ${m.menu.currency} ${numerilize(m.menu.price, m.menu.price, 0)} ${m.menu.isCountable == true ? ` (${m.menu.quantity} pieces)` : ``}</div>
                                    <div class="ui ${m.menu.isAvailable == true ? `green` : `red`} label" style="color: ${m.menu.isAvailable == true ? `green` : `red`}">${m.menu.isAvailable == true ? `<i class="icon check"></i> Available` : `<i class="icon times"></i> Not Available`}</div>
                                </div>
                            </div>
                        </div>
                    `;
                }

                desc__cnt.find(".ting-resto-item-map-direction").click(function(e){
                    e.preventDefault();
                    var m = $("#ting-resto-branch-direction").modal("show");
                    m.find(".content").html(loader);
                    var url = $(this).attr("data-url");
                    $.ajax({
                        type:"GET", url: url, data: {"lat": lat, "long": long, "addr": addr, "count": cntr, "town": twn},
                        success: function(r){m.find(".content").html(r)},
                        error: function(_, t, e){m.find(".content").html(`<div class="ui red message">${e}</div>`)}
                    });
                });

                img__row.append(img__bg);
                img__grid.html(img__row);
                img__cnt.html(img__grid);

                oth__promo.append(`<h2 style="font-weight:100; text-transform:uppercase">Others</h2>`)
                var br__omenu__items = $(`<div class="ui items"></div>`);

                var oms = branch.promotions.promotions.filter(function(p){return p.id != promo.id}).sort(function(){return Math.random() - 0.5}).slice(0, 4);

                if (oms.length > 0){
                    for (var i = 0; i < oms.length; i++){
                        var p = oms[i];
                        br__omenu__items.append(`
                            <div class="ting-menu-other">
                                <div class="item">
                                    <div class="ui fluid image"><a href="${p.urls.relative}"><img src="${p.posterImage}"/></a></div>
                                </div>
                                <div class="content" style="margin-top:5px;">
                                    <a class="header" style="font-weight:500; font-size:17px; color: #666;" href="${p.urls.relative}">${p.occasionEvent}</a>
                                    <div class="extra" style="margin-bottom:8px;">
                                        <div class="ui label">
                                            <i class="icon star"></i>
                                            Promotion On ${p.promotionItem.type.name}
                                        </div>
                                    </div>
                                    <div class="description">
                                        <p style="margin-bottom:5px;"><i class="icon calendar alternate outline"></i> ${p.period}</p>
                                        ${p.reduction.hasReduction == true ? `<p><i class="icon minus square outline"></i> Order this menu and get a ${p.reduction.amount} ${p.reduction.reductionType} reduction</p>` : ``}
                                        ${p.supplement.hasSupplement == true ? 
                                            `<p>
                                                <i class="icon plus square outline"></i>
                                                Order ${p.supplement.minQuantity} pieces or packs of this menu and get ${p.supplement.quantity}
                                                ${p.supplement.isSame == true ?
                                                    ` more for free` 
                                                    : ` free <a href="${p.supplement.supplement.url}" target="_blank">${p.supplement.supplement.menu.name}</a> `}
                                                        </p>` 
                                            : ``}
                                    </div>
                                    <div class="extra" style="margin-top:1rem;">
                                        ${p.promotionItem.type.id == '05' 
                                            ? `<div class="ui image label" style="margin-bottom:8px;">
                                                    <img src="${p.promotionItem.category.image}" />
                                                    Promotion On ${p.promotionItem.category.name}
                                                </div>` 
                                            : ``}
                                        ${p.promotionItem.type.id == '04' 
                                            ? `<div class="ui image label" style="margin-bottom:8px;" onclick="window.open('${p.promotionItem.menu.url}', '_blank')">
                                                    <img src="${p.promotionItem.menu.menu.images.images[0].image}" />
                                                    Promotion On ${p.promotionItem.menu.menu.name}
                                                </div>` 
                                            : ``}
                                        <div class="ui ${p.isOn == true && p.isOnToday == true ? `green` : `red`} label" style="color: ${p.isOn == true && p.isOnToday == true ? `green` : `red`}">${p.isOn == true && p.isOnToday == true ? `<i class="icon check"></i> Is On Today` : `<i class="icon times"></i> Is Off Today`}</div>
                                    </div>
                                </div>
                                <hr/>
                            </div>
                        `)
                    }
                } else {br__omenu__items.html(`<div class="ui red message">No Other Promotions</div>`);}

                oth__promo.append(br__omenu__items);
                bg__row.append(desc__cnt).append(oth__promo);
                bg__grid.html(bg__row);
                macnt.append(img__cnt).append(bg__grid);
                mcnt.html(macnt);
            }
        } else if(state.type == "user"){
            var usr = window.__TING__User;
            var mcnt = $("#ting-menu-container");
            var lcnt = $("#ting-menus-list");
            if(state.name == "restaurants"){
                $.ajax({
                    type:"GET", url: usr.urls.loadRestaurants, data:{},
                    success: function(r){lcnt.html(r)},
                    error: function(_, t, e){lcnt.html(`<div class="ui red message">${e}</div>`)}
                });
            } else if (state.name == "bookings"){
                $.ajax({
                    type:"GET", url: usr.urls.loadReservations, data:{},
                    success: function(r){lcnt.html(r)},
                    error: function(_, t, e){lcnt.html(`<div class="ui red message">${e}</div>`)}
                });
            }
        }
    }
}

function likesresto(r){
    if (typeof window.__TING__Session === 'object'){
        return r.likes.likes.includes(window.__TING__Session.id)
    } else {return false}
}

function likesmenu(r){
    if (typeof window.__TING__Session === 'object'){
        return r.likes.likes.includes(window.__TING__Session.id)
    } else {return false}
}

function interesetpromo(int){
    if (typeof window.__TING__Session === 'object'){
        return int.interests.includes(window.__TING__Session.id)
    } else {return false}
}

function likerestobtn(r){ return likesresto(r) == true ? likedresto : unlikedresto }

function likemenubtn(r){ return likesmenu(r) == true ? likedresto : unlikedresto }

function interesetpromoic(int){ return interesetpromo(int) == true ? interestedpromo : uninterestedpromo }

var likedresto = `<svg height="30px" style="enable-background:new 0 0 30 30;" version="1.1" viewBox="0 0 30 30" width="30px" xml:space="preserve" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><path d="M11.608,20.776c-22.647-12.354-6.268-27.713,0-17.369  C17.877-6.937,34.257,8.422,11.608,20.776z" style="fill-rule:evenodd;clip-rule:evenodd;fill:#b56fe8;"/><g/><g/><g/><g/><g/><g/><g/><g/><g/><g/><g/><g/><g/><g/><g/></svg>`;

var unlikedresto = `<i class="lnr lnr-heart"></i>`;

var interestedpromo = `<i class="icon star" style="color:#b56fe8;"></i>`;

var uninterestedpromo = `<i class="icon star outline"></i>`;

var loader = `<div class="ui right ting-loader" style="margin: auto; text-align: center; padding: 40px 0;">
                <img src="/tingstatics/imgs/loading.gif">
            </div>`;

function loadfn(id){
    $("div.rating, .rating, .ui.rating").rating("disable");
    $(".ting-rate-btn-" + id).popup({
        popup : ".ting-rate-popup-" + id,
        on : "click"
    }).popup("toggle");
}

function capitalize(text){
    return text.replace(text.charAt(0), text.charAt(0).toUpperCase())
}

function randomString(length) {
    var chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    var result = '';
    for (var i = length; i > 0; --i) result += chars[Math.floor(Math.random() * chars.length)];
    return result;
}

function isObjEmpty(obj){
    return Object.keys(obj).length === 0 && obj.constructor === Object
}

function compare( a, b ) {
    if ( a.dist < b.dist ) { return -1; }
    if ( a.dist > b.dist ) { return 1; }
    return 0;
}

function statusWorkTime(o, c){
    var today = new Date()
    var td = today.getFullYear() + "-" + (today.getMonth() + 1) + "-" + today.getDate()
    var now = Date.parse(td + " " + today.getHours() + ":" + today.getMinutes())

    var ot = Date.parse(td + " " + o)
    var ct = Date.parse(td + " " + c)

    if (ot >= now) {
        if (((ot - now) / (1000 * 60)) < 119){
            var r = (ot - now) / (1000 * 60) >= 60 ? Math.round(((ot - now) / (1000 * 60) - 1) / 60) + " hr" : Math.round((ot - now) / (1000 * 60) + 1) + " min"
            return {"clr": "orange", "msg": "Opening in " + r, "st": "closed"}} 
        else { return {"clr": "red", "msg": "Closed", "st": "closed"} }
    } else if (now > ot) {
        if(now > ct){ return {"clr": "red", "msg": "Closed", "st": "closed"}}
        else {
            if(((ct - now) / (1000 * 60)) < 119){
                var r = (ct - now) / (1000 * 60) >= 60 ? Math.round(((ct - now) / (1000 * 60) - 1) / 60) + " hr" : Math.round((ct - now) / (1000 * 60) + 1) + " min"
                return {"clr": "orange", "msg": "Closing in " + r, "st": "opened"} } 
            else { return {"clr": "green", "msg": "Opened", "st": "opened"} } }
    }
}

function singleImagePreview(input, img) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            var ext = $(input).val().split('.').pop().toLowerCase();
            var extVid = $(input).val().split('.').pop();
            if($.inArray(ext, ['gif','png','jpg','jpeg']) > 0) {
                $("#" + img).attr('src', e.target.result).show();
            } else { showErrorMessage("img", "Please, Insert Only Image");}
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function multipleImagesPreview(input, placeToInsertImagePreview) {
    placeToInsertImagePreview.empty();
    if (input.files) {
        var filesAmount = input.files.length;
        var images = new Array();
        for (i = 0; i < filesAmount; i++) {
            var reader = new FileReader();
            reader.onload = function(event) {
                var image = $($.parseHTML('<img>')).attr('src', event.target.result).appendTo(placeToInsertImagePreview);
                images.push(image[0].clientHeight)
            }
            reader.readAsDataURL(input.files[i]);
        }
        var max = Math.max.apply(null, images)
    }
}

function getCookie(key) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, key.length + 1) === (key + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(key.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function setCookie(key, value, expiry) {
    var expires = new Date();
    expires.setTime(expires.getTime() + (expiry * 24 * 60 * 60 * 1000));
    document.cookie = key + '=' + value + ';expires=' + expires.toUTCString();
}

function eraseCookie(key) {
    var keyValue = getCookie(key);
    setCookie(key, keyValue, '-1');
}

function makeMoment(time){
    var utc_timestamp = (Date.parse(time)) - (new Date().getTimezoneOffset() * 60 * 1000);
    var hours_check = new Date(utc_timestamp).getHours();

    var post_time = utc_timestamp / 1000;
    var timee =  utc_timestamp;
    var current_time = Math.floor(jQuery.now() / 1000);

    real_time = (current_time - post_time);
    if (real_time < 60) {
        return 'Just Now';
    } else if (real_time >= 60 && real_time < 3600) {
        time_be = moment(timee).fromNow();
        return time_be;
    } else if (real_time >= 3600 && real_time < 86400) {
        time_be = moment(timee).fromNow();
        return time_be;
    } else if (real_time >= 86400 && real_time < 604800) {
        time_b = Math.floor(real_time / (60 * 60 * 24));
        time_be = moment(timee).calendar();
        return time_be;
    } else if (real_time >= 604800 && real_time < 31104000 ) {
        time_be = moment(timee).format('MMMM Do [at] h:mm a');
        return time_be;
    } else {
        time_be = moment(timee).format('DD MMM YYYY [at] h:mm a');
        return time_be;
    }
}

jQuery.fn.setFroalaEditor = function(){
    var placeholder = $(this).attr("placeholder");
    $(this).froalaEditor(
        {
            placeholderText: placeholder,
            charCounterCount: false,
            toolbarButtons: ['bold', 'italic', 'underline', 'strikeThrough', 'color', 'fontSize', 'align', 'formatOL', 'formatUL', 'undo', 'redo']
        }
    );
}

jQuery.fn.submitFormAjax = function(){

    $(this).submit(function(e){
        e.preventDefault();
        if (window.event && window.event.keyCode == 13) e.preventDefault();

        let data = new FormData($(this)[0]);
        let action = $(this).attr("action");
        let method = $(this).attr("method");
        let button = $(this).find("button[type=submit]");
        let loader = $(this).find(".ting-loader");
        let form = $(this).find(".form");
        let progress = $(this).find(".ting-progress-form");
        let parent = $(this).find(".modal");
        let outter_progress =  parent.find(".ting-loader");
        let multiple = $(this).attr("ting-multiple-select");
        let callback = $(this).attr("ting-form-callback");
        
        $.ajax({
            xhr: function () {
                var xhr = new window.XMLHttpRequest();
                button.attr("disabled", "disabled");
                if(loader != null) loader.show();
                if(form != null) form.addClass("loading");
                if(progress != null) progress.show();
                if(outter_progress != null) outter_progress.show();
                xhr.addEventListener("progress", function (e) {
                    if (e.lengthComputable) {
                        var percent = Math.round((e.loaded / e.total) * 100);
                        progress.attr("data-value", percent).progress({percent: percent});
                    }
                });
                return xhr;
            },
            beforeSend: function( xhr ) {
                if(multiple != null && multiple != ""){
                    if($("#" + multiple).val() != null){
                        var periods = $("#" + multiple).dropdown("get values").join(",")
                        data.append("promotion_period", periods)
                    }
                }
                data.append("link", window.location.href)
                data.append("lat", $("#ting-lat").val());
                data.append("long", $("#ting-long").val());
                data.append("addr", $("#ting-addr").val());
                data.append("count", $("#ting-country").val());
                data.append("city", $("#ting-town").val());
                data.append("ip", $("#ting-ip").val());
                data.append("tz", $("#ting-tz").val());
                data.append("curr", $("#ting-currency").val());
                data.append("os", window.navigator.appVersion);
            },
            type: method,
            url: action,
            data: data,
            processData: false,
            contentType: false,
            success: function(response){
                if(response.type == "success" || response.type == "info"){
                    showSuccessMessage(response.type, response.message);
                    if(loader != null) loader.hide();
                    button.removeAttr("disabled");
                    if(form != null) form.removeClass("loading");
                    if(progress != null) progress.hide();
                    if(outter_progress != null) outter_progress.hide();
                    if(callback != "" && callback != null){ 
                        $(".ting-load-" + callback).modal('show');
                    } else { if(response.redirect != null) window.location = response.redirect; }
                } else {
                    button.removeAttr("disabled");
                    if(loader != null) loader.hide();
                    if(form != null) form.removeClass("loading");
                    if(progress != null) progress.hide();
                    if(outter_progress != null) outter_progress.hide()
                    showErrorMessage(response.type, response.message);
                    if(response.msgs.length > 0){
                        response.msgs.forEach(msg => {
                            var title = capitalize(msg[0])
                            msg[1].forEach(err => {
                                showErrorMessage(randomString(10), `<b>${title} : </b> ${err}`);
                            });
                        });
                    }
                }
            },
            error: function(_, t, e){
                button.removeAttr("disabled");
                if(loader != null) loader.hide();
                if(form != null) form.removeClass("loading");
                if(progress != null) progress.hide();
                if(outter_progress != null) outter_progress.hide()
                showErrorMessage(t, e);
            }
        });
    });
}

function resetImage(){
    $("#ting-image-overlay").css('opacity', '0');
    $("#ting-image-icon").show();
    $("#ting-image-load").hide();
}

jQuery.fn.submitProfileImage = function(){
    $(this).submit(function(e){
        e.preventDefault();
        var action = $(this).attr("action");
        var data = new FormData($(this)[0]);
        var image = $(this).attr("data-image");
        jQuery.ajax({
            type:'POST',
            data: data,
            url: action,
            processData: false,
            contentType: false,
            success: function(response){
                if(response.type == "success"){
                    showSuccessMessage(response.type, response.message);
                } else {
                    showErrorMessage(response.type, response.message);
                    if(response.msgs.length > 0){
                        response.msgs.forEach(msg => {
                            var title = capitalize(msg[0])
                            msg[1].forEach(err => {
                                showErrorMessage(randomString(10), `<b>${title} : </b> ${err}`);
                            });
                        });
                    }
                }
                resetImage();
            },
            error: function(_, t, e){
                showErrorMessage(t, e);
                resetImage();
                $("#ting-profile-image").attr("src", image);
            }
        });
    });
}

function updateProfileImage(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            var ext = $(input).val().split('.').pop().toLowerCase();
            if ($.inArray(ext, ['gif', 'jpg', 'png', 'jpeg']) > 0) {
                $("#ting-profile-image").attr("src", e.target.result);
                $("#ting-image-overlay").css('opacity', '1');
                $("#ting-image-icon").hide();
                $("#ting-image-load").show();
                $("#ting-session-profile-image-update").submit();
            } else {showErrorMessage("image", "Only jpg, png and jpeg images allowed !!!");}
        };
        reader.readAsDataURL(input.files[0]);
    }
}

jQuery.fn.openModal = function(){
    $(this).click(function(e){
        e.preventDefault();
        var url = $(this).attr("ting-data-url");
        var type = $(this).attr("ting-modal-type");
        var form_id = $(this).attr("ting-modal-form");
        var hide_content = $(this).attr("ting-hide-content");
        var data = $(this).attr("ting-modal-data");
        var modal_callback = $(this).attr("ting-modal-callback");

        if(url != null && url != ""){
            if(type == "ajax" || type == "ajax-form"){
                
                $("[data-modal=" + $(this).attr("ting-modal-target") + "]").modal({
                    allowMultiple: false,
                    onVisible: function(callback){
                        callback = $.isFunction(callback) ? callback : function () { };
                        var content = $(this).find('.content');
                        parent_modal = $(this);
                        $.ajax({
                            type: 'GET',
                            url: url,
                            success: function(response){
                                if(typeof response === 'object' && response != null){
                                    if(response.type == 'error'){
                                        content.find(".ting-loader").hide();
                                        content.find(".ting-data-content").html('<div class="ui red message"><b>Error '+ response.status +' : </b>' + response.message + '</div>');
                                        showErrorMessage(response.type, response.message);
                                    }
                                } else {
                                    content.find(".ting-loader").hide();                  
                                    content.find(".ting-data-content").html(response);
                                }
                            },
                            error: function(_, t, e){
                                content.find(".ting-loader").hide();
                                content.find(".ting-data-content").html('<div class="ui red message">' + e + '</div>');
                                showErrorMessage(t, e);
                            }
                        });
                    },
                    onHidden: function(callback){
                        callback = $.isFunction(callback) ? callback : function () { };
                        var content = $(this).find('.content');
                        content.find(".ting-loader").show();
                        content.find(".ting-data-content").html('<div></div>');
                    },
                    onApprove(){
                        if(form_id != null && form_id != ""){
                            var form = $(this).find("#" + form_id);
                            if(form != null){form.submit();
                            } else {showErrorMessage(randomString(12), "There Is No Form To Submit !!!")}
                        } else {showErrorMessage(randomString(12), "Form ID Not Specified !!!")}
                        return false;
                    },
                    onShow: function(){
                        var today = new Date();
                        $("#ting-datepicker-start-date-else, #ting-datepicker-end-date-else, #ting-datepicker-book-date").calendar({
                            type: 'date',
                            minDate: new Date(today.getFullYear(), today.getMonth(), today.getDate()),
                            monthFirst: false,
                            formatter: {
                                date: function (date, settings) {
                                    if (!date) return '';
                                    var day = date.getDate();
                                    var month = date.getMonth() + 1;
                                    var year = date.getFullYear();
                                    return year + '-' + month + '-' + day;
                                }
                            }
                        });
                        $("#ting-datepicker-book-time").calendar({type: 'time'})
                    },
                    onDeny: function() { if(modal_callback != "" && modal_callback != null){ $(".ting-load-" + modal_callback).modal('show');} }
                }).modal("show");

            } else if (type == "form") {

                $("[data-modal=" + $(this).attr("ting-modal-target") + "]").modal({
                    closable: false,
                    allowMultiple: false,
                    onVisible: function(callback){
                        callback = $.isFunction(callback) ? callback : function () { };
                    },
                    onHidden: function(callback){
                        callback = $.isFunction(callback) ? callback : function () { };
                    },
                    onApprove(){
                        if(form_id != null && form_id != ""){
                            var form = $(this).find("#" + form_id);
                            if(form != null){form.submit();
                            } else {showErrorMessage(randomString(12), "There Is No Form To Submit !!!")}
                        } else {showErrorMessage(randomString(12), "Form ID Not Specified !!!")}
                        return false;
                    },
                    onShow: function(){},
                    onDeny: function(){ if(modal_callback != "" && modal_callback != null){ $(".ting-load-" + modal_callback).modal('show');} }
                }).modal("show");

            } else if (type == "confirm"){

                $("[data-modal=" + $(this).attr("ting-modal-target") + "]").modal({
                    closable: false,
                    allowMultiple: false,
                    onApprove: function(){
                        var modal = $(this);
                        modal.find(".positive.button").addClass("disabled");
                        $.ajax({
                            type: 'GET',
                            url: url,
                            success: function(response){
                                if(response.type == "success"){
                                    showSuccessMessage(response.type, response.message);
                                    if(hide_content != "" && hide_content != null) modal.siblings().find("#" + hide_content).hide();
                                    if(modal_callback != "" && modal_callback != null){
                                        $(".ting-load-" + modal_callback).modal('show');
                                    } else { if(response.redirect != null) window.location = response.redirect; }
                                } else { showErrorMessage(response.type, response.message); }
                                modal.find(".positive.button").addClass("disabled");
                            },
                            error: function(_, t, e){ showErrorMessage(t, e); modal.find(".positive.button").addClass("disabled");}
                        });
                        return false;
                    },
                    onDeny: function(){ 
                        if(modal_callback != "" && modal_callback != null){ $(".ting-load-" + modal_callback).modal('show');}
                        showInfoMessage(randomString(16), "Operation Cancelled !!!");
                    }
                }).modal("show");
            } else if(type == "confirm-ajax"){
                if(data != null && data != ""){
                    var object = JSON.parse(data);
                    iziToast.question({
                        timeout: 10000,
                        close: false,
                        overlay: true,
                        toastOnce: true,
                        id: randomString(16),
                        zindex: 999,
                        title: object.title.toUpperCase(),
                        message: object.message,
                        position: 'center',
                        buttons: [
                            ['<button><b>YES</b></button>', function (instance, toast) {
                                instance.hide({ transitionOut: 'fadeOut' }, toast, 'button');
                                var modal = $(this);
                                $.ajax({
                                    type: 'GET',
                                    url: url,
                                    success: function(response){
                                        if(response.type == "success"){
                                            showSuccessMessage(response.type, response.message);
                                            if(hide_content != "" && hide_content != null) modal.siblings().find("#" + hide_content).hide();
                                            if(response.redirect != null) window.location = response.redirect;
                                        } else {showErrorMessage(response.type, response.message);}
                                    },
                                    error: function(_, t, e){showErrorMessage(t, e);}
                                });
                            }, true],
                            ['<button>NO</button>', function (instance, toast) {
                                instance.hide({ transitionOut: 'fadeOut' }, toast, 'button');
                                showInfoMessage(randomString(16), "Operation Cancelled !!!");
                            }],
                        ],
                        onClosing: function(instance, toast, closedBy){},
                        onClosed: function(instance, toast, closedBy){
                            showInfoMessage(randomString(16), "Operation Cancelled !!!");
                        }
                    });
                } else {showErrorMessage(randomString(16), "No Data To Show !!!")}
            }
        } else { 
            $("[data-modal=" + $(this).attr("id") + "]").modal({
                allowMultiple: false,
                onShow: function(){
                    var today = new Date();
                    $("#ting-datepicker-start-date, #ting-datepicker-end-date").calendar({
                        type: 'date',
                        minDate: new Date(today.getFullYear(), today.getMonth(), today.getDate()),
                        monthFirst: false,
                        formatter: {
                            date: function (date, settings) {
                                if (!date) return '';
                                var day = date.getDate();
                                var month = date.getMonth() + 1;
                                var year = date.getFullYear();
                                return year + '-' + month + '-' + day;
                            }
                        }
                    });
                },
                onDeny: function() { if(modal_callback != "" && modal_callback != null){ $(".ting-load-" + modal_callback).modal('show');} }
            }).modal("show");
        }
    });
}

jQuery.fn.searchLocationByAddress = function(lat, long, addr, addr_else, place, reg, rd, cont, clickable, img){

    $(this).keyup(function (e) {
        
        var key = e.charCode || e.keyCode || 0;
        
        if (key == 13) {
            
            e.preventDefault();
            var address = $(this).val();
            var geocoder = new google.maps.Geocoder();
            
            geocoder.geocode({
                'address': address
            }, function (results, status) {
                
                if (status == google.maps.GeocoderStatus.OK) {
                    
                    var from_lat = results[0].geometry.location.lat();
                    var from_long = results[0].geometry.location.lng();

                    var country = getaddresstype(results[0].address_components, "country")
                    var town_1 = getaddresstype(results[0].address_components, "administrative_area_level_2")
                    var town_2 = getaddresstype(results[0].address_components, "locality")
                    var region_1 = getaddresstype(results[0].address_components, "sublocality_level_1")
                    var region_2 = getaddresstype(results[0].address_components, "sublocality_level_2")
                    var road = getaddresstype(results[0].address_components, "route")
                    var region = region_2 !== undefined && region_2 !== null && region_2 != "Unknown" ? region_2 : region_1
                    var town = town_1 !== undefined && town_1 !== null && town_1 != "Unknown" ? town_1 : town_2

                    $("#" + lat).val(from_lat);
                    $("#" + long).val(from_long);
                    $("#" + addr).val(results[0].formatted_address);
                    $("#" + place).val(results[0].place_id);
                    $("#" + reg).val(region)
                    $("#" + rd).val(road)
                }
            });
            
            setTimeout(function () {
                initializeRestaurantMap(lat, long, addr, addr_else, place, reg, rd, cont, clickable, img);
            }, 1000);
        }
    });
}

jQuery.fn.likeRestaurant = function(){
    $(this).click(function(e){
        e.preventDefault();
        var data = JSON.parse($(this).attr("data-like"));
        var csrftoken = getCookie("csrftoken") != null ? getCookie("csrftoken") : window.__TING__Token;
        var url = decodeURIparams(window.__TING__URL_Like, {"restaurant":data.resto, "branch": data.branch});
        var auth = window.__TING__Session;
        var f = new FormData();
        f.append("csrfmiddlewaretoken", csrftoken);
        f.append("link", window.location.href);
        f.append("os", window.navigator.appVersion);
        f.append("restaurant", data.resto);
        f.append("user", auth.id || auth.token);

        if(typeof auth === 'object' && auth.id !== undefined && auth.token != undefined){
            var b = $(this);
            $.ajax({
                url: url,
                method: "POST",
                data:f,
                processData: false,
                contentType: false,
                success: function(response){
                    if(response.type == "success"){
                        if(b.hasClass("liked")){ b.removeClass("liked").empty().html(unlikedresto);} 
                        else { b.addClass("liked").addClass("ting-btn-animate").empty().html(likedresto);}
                    } else { showErrorMessage(response.type, response.message);}
                }, error: function(_, t, e){ showErrorMessage(t, e); }
            });
        } else { $("#ting-user-login").click(); showErrorMessage(randomString(10), "Login Required !!!");}
    });
}

jQuery.fn.likeMenu = function(){
    $(this).click(function(e){
        e.preventDefault();
        var data = JSON.parse($(this).attr("data-like"));
        var csrftoken = getCookie("csrftoken") != null ? getCookie("csrftoken") : window.__TING__Token;
        var url = decodeURIparams(window.__TING__URL_Like_Menu, {"menu":data.menu});
        var auth = window.__TING__Session;
        var f = new FormData();
        f.append("csrfmiddlewaretoken", csrftoken);
        f.append("link", window.location.href);
        f.append("os", window.navigator.appVersion);
        f.append("menu", data.menu);
        f.append("type", data.type);
        f.append("pk", data.pk);
        f.append("user", auth.id || auth.token);

        if(typeof auth === 'object' && auth.id !== undefined && auth.token != undefined){
            var b = $(this);
            $.ajax({
                url: url,
                method: "POST",
                data:f,
                processData: false,
                contentType: false,
                success: function(response){
                    if(response.type == "success"){
                        if(b.hasClass("liked")){ b.removeClass("liked").empty().html(unlikedresto);} 
                        else { b.addClass("liked").addClass("ting-btn-animate").empty().html(likedresto);}
                    } else { showErrorMessage(response.type, response.message);}
                }, error: function(_, t, e){ showErrorMessage(t, e); }
            });
        } else { $("#ting-user-login").click(); showErrorMessage(randomString(10), "Login Required !!!");}
    });
}

jQuery.fn.interestPromotion = function(){
    $(this).click(function(e){
        e.preventDefault();
        var data = JSON.parse($(this).attr("data-like"));
        var csrftoken = getCookie("csrftoken") != null ? getCookie("csrftoken") : window.__TING__Token;
        var url = data.url;
        var auth = window.__TING__Session;
        var f = new FormData();
        f.append("csrfmiddlewaretoken", csrftoken);
        f.append("link", window.location.href);
        f.append("os", window.navigator.appVersion);
        f.append("promo", data.promo || data.id);
        f.append("type", data.type);
        f.append("pk", data.id);
        f.append("user", auth.id || auth.token);

        if(typeof auth === 'object' && auth.id !== undefined && auth.token != undefined){
            var b = $(this);
            $.ajax({
                url: url,
                method: "POST",
                data:f,
                processData: false,
                contentType: false,
                success: function(response){
                    if(response.type == "success"){
                        if(b.hasClass("liked")){ b.removeClass("liked").empty().html(uninterestedpromo);} 
                        else { b.addClass("liked").addClass("ting-btn-animate").empty().html(interestedpromo);}
                    } else { showErrorMessage(response.type, response.message);}
                }, error: function(_, t, e){ showErrorMessage(t, e); }
            });
        } else { $("#ting-user-login").click(); showErrorMessage(randomString(10), "Login Required !!!");}
    });
}

jQuery.fn.navigateCuisines = function() {

    var container = $(this);
    var items = parseInt($(this).attr("data-items-count"));
    var prev = $(this).parent().find("#ting-cuisine-prev");
    var next = $(this).parent().find("#ting-cuisine-next");

    var maxCount = items - 4;

    var width = $(this).width();
    var innerWidth = 0

    container.find("li").each(function(){
        innerWidth += $(this).width() + 4;
    });

    var slideWidth = innerWidth - width;
    var slideMesure = (slideWidth / maxCount) + 15 + 6 + (15 / maxCount) + (2 / maxCount);

    var counter = 0;
    var duration = 300;

    next.click(function(e){
        e.preventDefault();
        if (maxCount > counter) {
            container.animate({
                scrollLeft: '+=' + slideMesure + 'px'
            }, duration);
            counter++;
        }
        if(counter > 0) { prev.show(); }
        if(maxCount == counter) { next.hide() }
    });

    prev.click(function(e){
        e.preventDefault();
        if (counter > 0) {
            container.animate({
                scrollLeft: '-=' + slideMesure + 'px'
            }, duration);
            counter--;
        }
        if(counter <= 0) { prev.hide(); }
        if(maxCount > counter) { next.show() }
    });
}

jQuery.fn.tingLiveSeacrh = function(){

    let form = $(this);
    let url = $(this).attr("action");
    let input = form.find("input");
    let spinner = $("#ting-search-form-spinner");
    let results = $("#ting-search-result");
    let disallowed = [13, 38, 40];
    let index = -1;

    let country = $("#ting-country").val();
    let town = $("#ting-town").val();

    if(country == '' || country == null || country == undefined) {
        var session = window.__TING__Session;
        if(session != null && !isObjEmpty(session)) { country = session.country; town = session.town }
        else { country = 'Uganda'; town = 'Kampala'; }
    }

    input.keyup(function(e){
        spinner.show();
        results.show().focus();
        let query = $(this).val();
        let active = results.find(".active");
        let responses = results.find(".ting-search-data");
        let resultsHeight = results.height();
        if(e.keyCode === 13){
            e.preventDefault();
            if(active.length > 0){window.location = active.attr("data-url")} 
            else { window.location = url + "?q=" + query}
        }
        if(e.keyCode === 38){
            e.preventDefault();
            if(responses.length > 0){
                if(index <= 0) {index = responses.length; resultsHeight = results.height(); results.scrollTop(0)}
                if(index >= responses.length){results.scrollTop(results.height())}
                index--;
                if(index <= 0) {}
                $(responses[index]).addClass("active").siblings().removeClass("active");
                input.val($(responses[index]).attr("data-name"));
                if(index > 3 && index < responses.length - 3) { resultsHeight += 100; results.scrollTop(resultsHeight) }
                if(index < 3) { resultsHeight = results.height(); results.scrollTop(0) }
            }
        }
        if(e.keyCode === 40){
            e.preventDefault();
            if(responses.length > 0){
                index++;
                if(index == 0) {resultsHeight = results.height(); results.scrollTop(0)}
                $(responses[index]).addClass("active").siblings().removeClass("active");
                input.val($(responses[index]).attr("data-name"));
                if(index > 3) { resultsHeight -= 100; results.scrollTop(resultsHeight) }
                if(index >= responses.length - 1) {index = -1; results.scrollTop(results.height())}
            }  
        }
        if(query == "" || query == null) {spinner.hide(); results.hide()}
        if(!disallowed.includes(e.keyCode)){
            $.ajax({
                type: "GET",
                url: url,
                data: {query: query, town: town, country: country},
                success: function(response){
                    let data = response;
                    if(data.length > 0){
                        results.empty();
                        index = -1;
                        data.forEach((dt) => {
                            var dist = 0.0;
                            let lat = $("#ting-lat").val();
                            let lng = $("#ting-long").val();
                            if(lat != '' && lng != '' && lat != null && lng != null) {
                                var _ds = new google.maps.LatLng(parseFloat(lat), parseFloat(lng));
                                var _de = new google.maps.LatLng(parseFloat(dt.coords.lat), parseFloat(dt.coords.lng))
                                dist = calculateDistance(_ds, _de);
                            }
                            let template = $(resultSearchTemplate(dt, dist));
                            template.click(function(){
                                window.location = $(this).attr("data-url")
                            }); 
                            template.hover(function(){
                                let resps = results.find(".ting-search-data");
                                $(this).addClass("active").siblings().removeClass("active");
                                input.val($(this).attr("data-name"));
                                index = data.indexOf(dt) + 1;
                            });
                            results.append(template).focus();
                        });
                    } else { results.html('<p class="ting-error">NO RESULT FOUND</p>'); }
                },
                error: function(_, t, e){ showErrorMessage(t, e); }
            });
        }
    });
}

function resultSearchTemplate(data, dist){
    return `
            <div class="ting-search-data" data-url="${data.relative}" data-name="${data.name}">
                <div class="ting-search-data-image">
                    <img src="${data.image}">
                </div>
                <div class="ting-search-data-description">
                    <h4>${data.name}</h4>
                    <p class="ting-price"><i class="icon map marker alternate"></i> ${data.description}</p>
                    <p class="ting-location">${data.type == 1 ? `<i class="icon boxes"></i>` : `<i class="icon tag"></i>`} ${data.text}</p>
                    <p class="ting-date">${dist} km from your location</p>
                </div>
            </div>
        `;
}

var animateButton = function(e) {
    e.preventDefault;
    e.target.classList.remove("ting-btn-animate");
    e.target.classList.add("ting-btn-animate");
    setTimeout(function(){
        e.target.classList.remove("ting-btn-animate");
    },700);
};

var decodeURIparams =  function(url, params){
    if(typeof params === 'object' || params != null){
        var regExp = /\{([^{}]+)\}/;
        var m = url.match(regExp);
        for (var i = 0; i < Object.keys(params).length; i++){
            var k = Object.keys(params)[i];
            var v = params[k];
            if (v !== undefined && k !== null) { url = url.replace("{" + k + "}", v); }
        }
        if(url.includes("{") || url.includes("}")){
            for (var i = 0; i < m.length; i++) {
                var str = m[i];
                var k = str.substring(1, str.length - 1)
                if (k !== undefined && k != null && params[k] !== undefined && params[k] != null){url = url.replace(str, params[k])}
            }
        }
        return url;
    } else { return url }
};

var numerilize = function(n, t, d){
    if(typeof t === undefined || t == null){
        if(typeof n === 'number' || typeof n === 'string'){
            if(n > 1000000000000) return (n / 1000000000000).toFixed(d) + " Tn";
            else if(n > 1000000000) return (n / 1000000000).toFixed(d) + " Bn";
            else if(n > 1000000) return (n / 1000000).toFixed(d) + " M";
            else if(n > 1000) return (n / 1000).toFixed(d) + " K";
            return n;
        } else { return n; }
    } else {
        var num = !isFinite(+n) ? 0 : +n, 
            prec = !isFinite(+d) ? 0 : Math.abs(d),
            sep = ",",
            dec = ".",
            toFixedFix = function (num, prec) {
                var k = Math.pow(10, prec);
                return Math.round(num * k) / k;
            },
            s = (prec ? toFixedFix(num, prec) : Math.round(num)).toString().split('.');
        if (s[0].length > 3) {
            s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
        }
        if ((s[1] || '').length < prec) {
            s[1] = s[1] || '';
            s[1] += new Array(prec - s[1].length + 1).join('0');
        }
        return s.join(dec);
    }
}

String.prototype.htmlspecialchars = function() {
    var escapedString = this;
    var specialchars = [
        [ '&', '&amp;' ],
        [ '<', '&lt;' ],
        [ '>', '&gt;' ],
        [ '"', '&quot;' ]
    ];
    var len = specialchars.length;
    for (var x = 0; x < len; x++) {
        escapedString = escapedString.replace(
            new RegExp(specialchars[x][0], 'g'),
            specialchars[x][1]
        );
    }
    return escapedString;
};

Array.prototype.shuffle = function () {
    for (var i = this.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        [this[i], this[j]] = [this[j], this[i]];
    }
    return this;
}

Array.prototype.join2 = function(all, last) {
    var arr = this.slice();                   //make a copy so we don't mess with the original
    var lastItem = arr.splice(-1);            //strip out the last element
    arr = arr.length ? [arr.join(all)] : [];  //make an array with the non-last elements joined with our 'all' string, or make an empty array
    arr.push(lastItem);                       //add last item back so we should have ["some string with first stuff split by 'all'", last item]; or we'll just have [lastItem] if there was only one item, or we'll have [] if there was nothing in the original array
    return arr.join(last);                    //now we join the array with 'last'
}

function hideModal(container){ $(container).modal("hide");}

function showErrorMessage(id, message) {
    iziToast.error({
        id: id,
        timeout: 10000,
        title: 'Error',
        message: message,
        position: 'bottomLeft',
        transitionIn: 'bounceInLeft',
        close: false,
    });
}

function showSuccessMessage(id, message) {
    iziToast.success({
        id: id,
        timeout: 10000,
        title: 'Success',
        message: message,
        position: 'bottomLeft',
        transitionIn: 'bounceInLeft',
        close: false,
    });
}

function showInfoMessage(id, message) {
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

function getUserCurrentLocation(lt, lg, ad, tc, cc, ads, id, rg, rd) {

    if (!navigator.geolocation) {
        $.getJSON('https://ipapi.co/json/', function(data) {
            document.getElementById(lt).value = data.latitude;
            document.getElementById(lg).value = data.longitude;
            document.getElementById(ad).value = data.city + ", " + data.region + ", " + data.country_name;
            document.getElementById(tc).value = data.city;
            document.getElementById(cc).value = data.country_name;
            document.getElementById(id).value = data.ip
            document.getElementById(rg).value = data.region
            document.getElementById(rd).value = "Unknown"
            
            let inputElse = document.getElementById(ads);
            if(inputElse != null){ inputElse.value = data.city + ", " + data.region + ", " + data.country_name;}
        });
        return showErrorMessage('error_geolocation', 'Geolocation not supported by your browser');
    }
    navigator.geolocation.getCurrentPosition(function (position) {

        var geocoder = new google.maps.Geocoder();
        var location = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);

        geocoder.geocode({ 'latLng': location }, function (results, status) {

            if (status == google.maps.GeocoderStatus.OK) {

                var latitude = position.coords.latitude;
                var longitude = position.coords.longitude;
                var address = results[0].formatted_address;

                var country = getaddresstype(results[0].address_components, "country")
                var town_1 = getaddresstype(results[0].address_components, "administrative_area_level_2")
                var town_2 = getaddresstype(results[0].address_components, "locality")
                var region_1 = getaddresstype(results[0].address_components, "sublocality_level_1")
                var region_2 = getaddresstype(results[0].address_components, "sublocality_level_2")
                var road = getaddresstype(results[0].address_components, "route")
                var region = region_2 !== undefined && region_2 !== null && region_2 != "Unknown" ? region_2 : region_1
                var town = town_1 !== undefined && town_1 !== null && town_1 != "Unknown" ? town_1 : town_2

                document.getElementById(lt).value = latitude;
                document.getElementById(lg).value = longitude;
                document.getElementById(ad).value = address;
                document.getElementById(tc).value = town;
                document.getElementById(cc).value = country;
                document.getElementById(id).value = results[0].place_id
                document.getElementById(rg).value = region
                document.getElementById(rd).value = road

                let inputElse = document.getElementById(ads);
                if(inputElse != null){ inputElse.value = address;}
            }
        });
    }, function () { 

        $.getJSON('https://ipapi.co/json/', function(data) {
            document.getElementById(lt).value = data.latitude;
            document.getElementById(lg).value = data.longitude;
            document.getElementById(ad).value = data.city + ", " + data.region + ", " + data.country_name;
            document.getElementById(tc).value = data.city;
            document.getElementById(cc).value = data.country_name;
            document.getElementById(id).value = data.ip
            document.getElementById(rg).value = data.region
            document.getElementById(rd).value = "Unknown"

            let inputElse = document.getElementById(ads);
            if(inputElse != null){ inputElse.value = data.city + ", " + data.region + ", " + data.country_name;}
        });

    }, {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
    });
}

function initializeRestaurantMap(lat, long, addr, addr_else, place, reg, rd, cont, clickable, img) {

    var latitude = parseFloat($("#" + lat).val());
    var longitude = parseFloat($("#" + long).val());
    var address = $("#" + addr).val();
    var place_id = $("#" + place).val();

    var myLatLng = {
        lat: latitude,
        lng: longitude
    };

    map = new google.maps.Map(document.getElementById(cont), {
        zoom: 17,
        center: myLatLng,
        gestureHandling: 'cooperative',
        clickable: clickable
    });

    if(clickable == true){

        var marker;

        if(place_id == 'is-really-needed'){
            var service = new google.maps.places.PlacesService(map);
            service.getDetails({
                placeId: place_id
            }, function (result, status) {

                var marker = new google.maps.Marker({
                    map: map,
                    place: {
                        placeId: place_id,
                        location: result.geometry.location
                    }
                });
            });

        } else {

            var marker = new google.maps.Marker({
                position: myLatLng,
                map: map,
                title: address,
                animation: google.maps.Animation.DROP,
            });

            marker.addListener('click', toggleBounce);

            function toggleBounce() {
                if (marker.getAnimation() !== null) {
                    marker.setAnimation(null);
                } else { marker.setAnimation(google.maps.Animation.BOUNCE); }
            }
            markers.push(marker);
        }

    } else {
        var htmlMarker = new HTMLMarker(latitude, longitude, img);
        var marker = new google.maps.Marker({
            position: myLatLng,
            map: map,
            title: address,
            animation: google.maps.Animation.DROP,
        });

        marker.addListener('click', toggleBounce);

        function toggleBounce() {
            if (marker.getAnimation() !== null) {
                marker.setAnimation(null);
            } else { marker.setAnimation(google.maps.Animation.BOUNCE); }
        }
        markers.push(marker);
    }

    var geocoder = new google.maps.Geocoder();

    if (clickable == true){

        google.maps.event.addListener(map, 'click', function (event) {
            geocoder.geocode({
                'latLng': event.latLng
            }, function (results, status) {
                if (status == google.maps.GeocoderStatus.OK) {

                    if (results[0]) {

                        var n_address = results[0].formatted_address;
                        var n_latitude = results[0].geometry.location.lat();
                        var n_longitude = results[0].geometry.location.lng();

                        var country = getaddresstype(results[0].address_components, "country")
                        var town_1 = getaddresstype(results[0].address_components, "administrative_area_level_2")
                        var town_2 = getaddresstype(results[0].address_components, "locality")
                        var region_1 = getaddresstype(results[0].address_components, "sublocality_level_1")
                        var region_2 = getaddresstype(results[0].address_components, "sublocality_level_2")
                        var road = getaddresstype(results[0].address_components, "route")
                        var region = region_2 !== undefined && region_2 !== null && region_2 != "Unknown" ? region_2 : region_1
                        var town = town_1 !== undefined && town_1 !== null && town_1 != "Unknown" ? town_1 : town_2

                        var position = {
                            lat: n_latitude,
                            lng: n_longitude
                        }

                        $("#" + lat).val(n_latitude);
                        $("#" + long).val(n_longitude);
                        $("#" + addr).val(n_address);
                        $("#" + place).val(results[0].place_id);
                        $("#" + reg).val(region)
                        $("#" + rd).val(road)
                        
                        let inputElse = $("#" + addr_else);

                        if (inputElse != null) {
                            inputElse.val(n_address);
                        }

                        clearMarkers();

                        var marker = new google.maps.Marker({
                            position: position,
                            map: map,
                            title: n_address
                        });

                        markers.push(marker);
                    }
                } else {
                    showErrorMessage("init_map", status);
                }
            });
        });
    }
}

function setMapOnAll(map) {
    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(map);
    }
}

function clearMarkers() {
    setMapOnAll(null);
}

function deleteMarkers() {
    clearMarkers();
    markers = [];
}

function InitializePlaces(input) {
    var autocomplete = new google.maps.places.Autocomplete(document.getElementById(input));
    google.maps.event.addListener(autocomplete, 'place_changed', function () {
        autocomplete.getPlace();
    });
}

function calculateDistance(end, start){
    return (google.maps.geometry.spherical.computeDistanceBetween(end, start) / 1000).toFixed(2);
}

function mapsDirection(s, e, cs, m) {

    var directionsDisplay;
    var directionsService = new google.maps.DirectionsService();
    var map;

    directionsDisplay = new google.maps.DirectionsRenderer();
    directionsDisplay.setOptions({
        suppressMarkers: true,
        polylineOptions: {
            strokeColor: '#b56fe8',
            strokeOpacity: 0.7,
            strokeWeight: 5
        }
    });

    var myLatLng = {
        lat: parseFloat(s.latitude),
        lng: parseFloat(s.longitude)
    };

    map = new google.maps.Map(document.getElementById(cs.map), {
        zoom: 17,
        center: myLatLng,
        gestureHandling: 'cooperative'
    });

    var end = new google.maps.LatLng(parseFloat(e.latitude), parseFloat(e.longitude));
    var start = new google.maps.LatLng(parseFloat(s.latitude), parseFloat(s.longitude));

    $("#" + cs.distance).text(calculateDistance(end, start) + " km");
    $("#" + cs.from).text(s.location);$("#" + cs.to).text(e.branch);

    var service = new google.maps.DistanceMatrixService();
    var bounds = new google.maps.LatLngBounds();

    bounds.extend(start);
    bounds.extend(end);
    map.fitBounds(bounds);

    var is = {
        url: s.pin,
        size: new google.maps.Size(71, 71),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(30, 64),
        scaledSize: new google.maps.Size(60, 60)
    };

    var ie = {
        url: e.pin,
        size: new google.maps.Size(71, 71),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(30, 64),
        scaledSize: new google.maps.Size(60, 60)
    };

    new google.maps.Marker({
        position: {lat: parseFloat(s.latitude), lng: parseFloat(s.longitude)},
        map: map,
        title: s.address,
        icon: is
    });

    new google.maps.Marker({
        position: {lat: parseFloat(e.latitude), lng: parseFloat(e.longitude)},
        map: map,
        title: e.address,
        icon: ie
    });

    if(m == "d"){
        service.getDistanceMatrix({
            origins: [s.address],
            destinations: [e.address],
            travelMode: 'DRIVING',
            drivingOptions: {
                departureTime: new Date(Date.now()),
                trafficModel: 'optimistic'
            },
            unitSystem: google.maps.UnitSystem.METRIC,
            avoidHighways: true,
            avoidTolls: true,

        }, function (response) {
            var time_drive = response.rows[0].elements[0].duration.text;
            var time_with_traffic = response.rows[0].elements[0].duration_in_traffic.text;
            var distance = response.rows[0].elements[0].distance.text;
            $("#" + cs.time).text(time_drive);
            $("#" + cs.distance).text(distance);
        });

        var request = {
            origin: start,
            destination: end,
            travelMode: google.maps.TravelMode.DRIVING
        };

        directionsService.route(request, function (response, status) {
            if (status == google.maps.DirectionsStatus.OK) {
                directionsDisplay.setDirections(response);
                directionsDisplay.setMap(map);
            } else {showErrorMessage(randomString(8), status);}
        });
    } else if (m == "w"){

        service.getDistanceMatrix({
            origins: [s.address],
            destinations: [e.address],
            travelMode: 'WALKING',
            drivingOptions: {
                departureTime: new Date(Date.now()),
                trafficModel: 'optimistic'
            },
            unitSystem: google.maps.UnitSystem.METRIC,
            avoidHighways: true,
            avoidTolls: true,

        }, function (response) {
            var time_walk = response.rows[0].elements[0].duration.text;
            var distance = response.rows[0].elements[0].distance.text;
            $("#" + cs.time).text(time_walk);
            $("#" + cs.distance).text(distance);
        });

        var request = {
            origin: start,
            destination: end,
            travelMode: google.maps.TravelMode.WALKING
        };

        directionsService.route(request, function (response, status) {
            if (status == google.maps.DirectionsStatus.OK) {
                directionsDisplay.setDirections(response);
                directionsDisplay.setMap(map);
            } else {showErrorMessage(randomString(8), status);}
        });
    }
}

function HTMLMarker(lat, lng, img, map){
    this.lat = lat;
    this.lng = lng;
    this.img = img;
    this.pos = new google.maps.LatLng(lat, lng);
    this.setMap(map)
}
    
HTMLMarker.prototype = new google.maps.OverlayView();
HTMLMarker.prototype.onRemove = function(){}
    
HTMLMarker.prototype.onAdd = function(){
    this.div = document.createElement('div');
    this.div.className = "ting-maps-marker";
    this.div.style.position = "absolute"
    this.div.innerHTML = "<div class='ting-maps-marker-box'><img src='" + this.img + "' alt=''></div>";
    var panes = this.getPanes();
    panes.overlayImage.appendChild(this.div);
}
    
HTMLMarker.prototype.draw = function(){
    var overlayProjection = this.getProjection();
    var position = overlayProjection.fromLatLngToDivPixel(this.pos);
    var panes = this.getPanes();
    panes.overlayImage.style.left = position.x + 30 + 'px';
    panes.overlayImage.style.top = position.y + 52 + 'px';
}