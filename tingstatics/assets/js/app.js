/*  THIS JS SHEET BELONGS TO TING.COM
    Author: Ir Christian Scott -> Code Pipes Solutions
    Date : 23 April 2019
*/

let markers = [];

$(document).ready(function(){

    loadtingdotcom();

    $("#ting-open-add-restaurant-location").click(function (e) {
        
        e.preventDefault();
        
        getUserCurrentLocation("ting-restaurant-latitude", "ting-restaurant-longitude", "ting-search-location-input", "ting-restaurant-town", "ting-restaurant-country", "ting-search-location-input-else", "ting-restaurant-place-id");
        
        setTimeout(function () {
            initializeRestaurantMap("ting-restaurant-latitude", "ting-restaurant-longitude", "ting-search-location-input", "ting-search-location-input-else", "ting-restaurant-place-id", "ting-restaurant-map-container", true, "");
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
            initializeRestaurantMap("ting-lat", "ting-long", "ting-addr", "ting-user-address", "ting-place", "ting-user-map-container", true, "");
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

    $("#ting-map-form").submit(function(e){
        e.preventDefault();
    });

    $("#ting-search-location-input-else").searchLocationByAddress("ting-restaurant-latitude", "ting-restaurant-longitude", "ting-search-location-input", "ting-search-location-input-else", "ting-restaurant-place-id", "ting-restaurant-map-container", true, "")
    $("#ting-user-address").searchLocationByAddress("ting-lat", "ting-long", "ting-addr", "ting-user-address", "ting-place", "ting-user-map-container", true, "")

    $("select.dropdown, .dropdown").dropdown("hide");
    $("div.rating, .rating, .ui.rating").rating();

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
});

function loadtingdotcom(){

    //tingdotcom(0, 0, "", "", "")

    if (!navigator.geolocation) {
        $.getJSON('https://ipapi.co/json/', function(data) {
            tingdotcom(data.latitude, data.longitude, data.address, data.country_name, data.city)
        });
        return showErrorMessage('error_geolocation', 'Geolocation not supported by your browser');
    }
    navigator.geolocation.getCurrentPosition(function (position) {

        var geocoder = new google.maps.Geocoder();
        var location = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);

        geocoder.geocode({ 'latLng': location }, function (results, status) {

            if (status == google.maps.GeocoderStatus.OK) {
                var length = results[0].address_components.length
                tingdotcom(position.coords.latitude, position.coords.longitude, results[0].formatted_address, results[0].address_components[length - 1], results[0].address_components[length - 3])
            }
        });
    }, function () { 

        $.getJSON('https://ipapi.co/json/', function(data) {
            tingdotcom(data.latitude, data.longitude, data.address, data.country_name, data.city)
        });

    }, {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
    });
}

function tingdotcom(lat, long, addr, cntr, twn){

    var state = window.__TING__Link
    var session = window.__TING__Session
    var sloc = {}

    if(state == "global_restaurants"){

        var branches = window.__TING__Restaurants
        var usl = $("#ting-user-locations");
        usl.empty();
        usl.append(`<option value="0">Current Location</option>`);

        var usa = {lat: lat, lng: long}
        branches = newBranches(branches, usa)

        var c = $("#ting-restaurants-list");
        var g = $(`<div class="ui grid" style="position: relative;"></div>`);
        var r = $(`<div class="row" style="position: relative;"></div>`);
        var fc = $(`<div class="five wide column"></div>`);
        var rc = $(`<div class="eleven wide column" style="padding-right: 0;"></div>`);

        var hf = `<h4 style="text-transform:uppercase; font-weight:100;">Search Restaurant</h4><br/>`;
        fc.append(hf);
        var cd = $(`<select name="country" class="ui dropdown"></select>`);
        cd.append(`<option value="all">All</option>`);
        cd.append(`<option value="${cntr}">Current</option>`);
        var cntrs = window.__TING__Countries;
        for(var k = 0; k < cntrs.length; k++){cd.append(`<option value="${cntrs[k].country.toLowerCase()}">${cntrs[k].country}</option>`);}
            
        var f = $(`<form class="ui form" action="${window.__TING__URL_Filter_Restaurants}" method="GET"></form>`);
        f.append(`<div class="field">
                        <label>By Restaurant Name :</label>
                        <input type="text" name="resto" placeholder="Restaurant Name" autocomplete="off" />
                    </div>`);
        f.append(`<div class="field">
                    <label>By Branch Name :</label>
                        <input type="text" name="branch" placeholder="Branch Name" autocomplete="off" />
                    </div>`);
        var cdc = $(`<div class="field"></div>`);
        cdc.append(`<label>By Country</label>`);
        cdc.append(cd);
        f.append(cdc).append(`<script>$("select").dropdown()</script>`);
        f.append(`<button class="ui button primary fluid" type="submit">${"Search".toUpperCase()}</button>`);
            
        f.submit(function(e){
            e.preventDefault();
            var _dt = new FormData($(this)[0]);
            _dt.append("csrfmiddlewaretoken", window.__TING__Token);
            var _url = $(this).attr("action");
            var _meth = $(this).attr("method");
            $.ajax({
                type: "POST", url: _url,data: _dt,
                processData: false, contentType: false,
                success: function(r){window.__TING__Restaurants = r;
                    getRestaurantList(newBranches(r, sloc), sloc, 1);
                    branchesmaps(newBranches(r, sloc), sloc);
                }, error: function(_, t, e){showErrorMessage(t, e);}
            });
        });
            
        fc.append(f).append(`<hr/>`);
        var hff = `<h4 style="text-transform:uppercase; font-weight:100;">Filter By</h4>`;
            
        r.append(fc).append(rc);
        g.html(r); c.html(g);
        
        getRestaurantList(branches, usa, 1);
        branchesmaps(branches, usa);
        sloc = usa

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
            branches = newBranches(branches, usa);
            getRestaurantList(branches, usa, 1);
            branchesmaps(branches, usa);
        });


        function branchesmaps(br, usloc){

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
                                        <h2><a href="#">${branch.restaurant.name}</a></h2>
                                        <p class="branch">${branch.name} Branch</p>
                                        <p><i class="lnr lnr-map-marker"></i>${branch.address}</p>
                                        <hr/>
                                    </div>
                                    <div class="resto-info">
                                        <p><i class="lnr lnr-bullhorn"></i>${branch.restaurant.motto}</p>
                                        <p><i class="lnr lnr-envelope"></i>${branch.restaurant.config.email}</p>
                                        <p><i class="lnr lnr-phone-handset"></i>${branch.restaurant.config.phone}</p>
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
            }
        }
        

        function newBranches(branches, usa){
            if(branches.length > 0){
                branches.forEach(function(b){
                    // var _ds = new google.maps.LatLng(usa.lat, usa.lng)
                    // var _de = new google.maps.LatLng(parseFloat(b.latitude), parseFloat(b.longitude))
                    // b.dist = calculateDistance(_ds, _de)
                });
            }
            return branches
        }
           
        function getRestaurantList(res, _ds, t){

            if(res.length > 0){
                res.sort(compare)
                var ctn = $(`<div class="ui divided items"></div>`);
                for(var i = 0; i < res.length; i++){
                    var br = res[i]
                    var s = statusWorkTime(br.restaurant.opening, br.restaurant.closing)
                    var tc = $("<div class='item ting-resto-item'></div>");
                    tc.attr("id", "ting-resto-item-" + br.id);
                    tc.attr("data-position", i);
                    tc.attr("data-top-url", decodeURIparams(window.__TING__URL_Top_Five, {"restaurant": br.restaurant.id, "branch": br.id}));
                    tc.css("cursor", "pointer");
                    var ti = `  
                            <div class="ui tiny image">
                                <img src="${br.restaurant.logo}">
                            </div>
                            <div class="content">
                                <a class="header" style="font-size:17px; font-weight:500;">${br.restaurant.name}, ${br.name}</a>
                                <div class="meta" style="margin-top:5px;">
                                    <span class="cinema">${br.address}</span>
                                </div>
                                <div class="description">
                                    <p></p>
                                </div>
                                <div class="extra">
                                    <div class="ui label"><i class="icon map marker alternate"></i> ${br.dist} Km</div>
                                    <div class="ui ${br.isAvailable == true ? s.clr : "red"} label"><i class="clock outline icon"></i> ${br.isAvailable == true ? s.msg : "Not Available"}</div>
                                    <div class="ui label" style="cursor:pointer;"><i class="heart outline icon"></i>${numerilize(br.restaurant.likes.count, null, 0)}</div>
                                    <div class="ui label ting-rate-btn-${br.id}" style="cursor:pointer;"><i class="star outline icon"></i>${br.restaurant.reviews.average}</div>
                                </div>
                                <div class="ting-like-restaurant">
                                    <button class="ting-like-restaurant ting-btn-animate ${likesresto(br.restaurant) == true ? 'liked' : ''}" id="ting-like-restaurant-${br.id}" data-like='{"resto":"${br.restaurant.id}", "tkn":"${br.restaurant.token}", "id":"${br.id}", "typ":"link"}'>${likerestobtn(br.restaurant)}</button>
                                </div>
                                <div class="ui flowing popup top left transition hidden ting-rate-popup-${br.id}">
                                    <div class="header">Rating</div>
                                    <div class="content" style="width:300px;">
                                        <div class="ui huge star rating" data-rating="${br.restaurant.reviews.average}" data-max-rating="5"></div>
                                        <div class="ui grid">
                                            <div class="row" style="padding:0 !important;">
                                                <div class="four wide column ting-rate-average">
                                                    <h1>${br.restaurant.reviews.average}</h1>
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
                                                                <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${br.restaurant.reviews.percents[4]}%"></div></div>
                                                                <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${br.restaurant.reviews.percents[3]}%"></div></div>
                                                                <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${br.restaurant.reviews.percents[2]}%"></div></div>
                                                                <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${br.restaurant.reviews.percents[1]}%"></div></div>
                                                                <div class="ting-rate-container"><div class="ting-rate-fill" style="width:${br.restaurant.reviews.percents[0]}%"></div></div>
                                                                <div clsas="ting-reviews-count"><p>${numerilize(br.restaurant.reviews.count, br.restaurant.id, 0)} reviews</p></div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <script type="text/javascript">
                                    $("div.rating, .rating, .ui.rating").rating();
                                    $(".ting-rate-btn-${br.id}").popup({popup : ".ting-rate-popup-${br.id}", on : "click"});
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
                    ctn.append(tc);
                }
                rc.html(ctn);
            } 
            else {rc.html(`<div class="ui red message">No Restaurants To Show</div>`)}
        }

        function likesresto(r){
            if (typeof window.__TING__Session === 'object'){
                var l = r.likes.likes
                for(var i = 0; i < l.length; i++){if(l[i].id == window.__TING__Session.id){return true;}}
                return false
            } else {return false}
        }

        function likerestobtn(r){ return likesresto(r) == true ? likedresto : unlikedresto }
    }
}

var likedresto = `<svg height="30px" style="enable-background:new 0 0 30 30;" version="1.1" viewBox="0 0 30 30" width="30px" xml:space="preserve" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><path d="M11.608,20.776c-22.647-12.354-6.268-27.713,0-17.369  C17.877-6.937,34.257,8.422,11.608,20.776z" style="fill-rule:evenodd;clip-rule:evenodd;fill:#b56fe8;"/><g/><g/><g/><g/><g/><g/><g/><g/><g/><g/><g/><g/><g/><g/><g/></svg>`;

var unlikedresto = `<i class="lnr lnr-heart"></i>`;

var loader = `<div class="ui right ting-loader" style="margin: auto; text-align: center; padding: 40px 0;">
                <img src="/tingstatics/imgs/loading.gif">
            </div>`;

function loadfn(id){
    $("div.rating, .rating, .ui.rating").rating();
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
    if ( a.dist < b.dist ){ return -1;}
    if ( a.dist > b.dist ){ return 1;}
    return 0;
}

function statusWorkTime(o, c){
    var today = new Date()
    var td = today.getFullYear() + "-" + today.getMonth() + "-" + today.getDate()
    var now = Date.parse(td + " " + today.getHours() + ":" + today.getMinutes())

    var ot = Date.parse(td + " " + o)
    var ct = Date.parse(td + " " + c)

    if(ot >= now){
        if(((ot - now) / (1000 * 60)) < 120){
            var r = (ot - now) / (1000 * 60) > 60 ? Math.round((ot - now) / (1000 * 60 * 60)) + " hr" : Math.round((ot - now) / (1000 * 60)) + " min"
            return {"clr": "orange", "msg": "Opening in " + r}} 
        else {return {"clr": "red", "msg": "Closed"}}
    } else if (now > ot){
        if(now > ct){ return {"clr": "red", "msg": "Closed"}}
        else {
            if(((ct - now) / (1000 * 60)) < 120){
                var r = (ct - now) / (1000 * 60) > 60 ? Math.round((ct - now) / (1000 * 60 * 60)) + " hr" : Math.round((ct - now) / (1000 * 60)) + " min"
                return {"clr": "orange", "msg": "Closing in " + r}} 
            else {return {"clr": "green", "msg": "Opened"}}}
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
            }else{
                showErrorMessage("img", "Please, Insert Only Image");
            }
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

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
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
                    if(outter_progress != null) outter_progress.hide()
                    if(response.redirect != null) window.location = response.redirect;
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
            } else {
                showErrorMessage("image", "Only jpg, png and jpeg images allowed !!!");
            }
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

        if(url != null && url != ""){
            if(type == "ajax" || type == "ajax-form"){
                
                $("[data-modal=" + $(this).attr("ting-modal-target") + "]").modal({
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
                            if(form != null){
                                form.submit();
                            } else {
                                showErrorMessage(randomString(12), "There Is No Form To Submit !!!")
                            }
                        } else {
                            showErrorMessage(randomString(12), "Form ID Not Specified !!!")
                        }
                        return false;
                    },
                    onShow: function(){
                        var today = new Date();
                        $("#ting-datepicker-start-date-else, #ting-datepicker-end-date-else").calendar({
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
                    }
                }).modal("show");

            } else if (type == "confirm"){

                $("[data-modal=" + $(this).attr("ting-modal-target") + "]").modal({
                    onApprove: function(){
                        var modal = $(this);
                        $.ajax({
                            type: 'GET',
                            url: url,
                            success: function(response){
                                if(response.type == "success"){
                                    showSuccessMessage(response.type, response.message);
                                    if(hide_content != "" && hide_content != null) modal.siblings().find("#" + hide_content).hide();
                                    if(response.redirect != null) window.location = response.redirect;
                                } else {
                                    showErrorMessage(response.type, response.message);
                                }
                            },
                            error: function(_, t, e){
                                showErrorMessage(t, e);
                            }
                        });
                    },
                    onDeny: function(){
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
                                        } else {
                                            showErrorMessage(response.type, response.message);
                                        }
                                    },
                                    error: function(_, t, e){
                                        showErrorMessage(t, e);
                                    }
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
                } else {
                    showErrorMessage(randomString(16), "No Data To Show !!!")
                }
            }
        } else { 
            $("[data-modal=" + $(this).attr("id") + "]").modal({
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
                }
            }).modal("show");
        }
    });
}

jQuery.fn.searchLocationByAddress = function(lat, long, addr, addr_else, place, cont, clickable, img){

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

                    $("#" + lat).val(from_lat);
                    $("#" + long).val(from_long);
                    $("#" + addr).val(results[0].formatted_address);
                    $("#" + place).val(results[0].place_id);
                }
            });
            
            setTimeout(function () {
                initializeRestaurantMap(lat, long, addr, addr_else, place, cont, clickable, img);
            }, 1000);
        }
    });
}

jQuery.fn.likeRestaurant = function(){
    $(this).click(function(e){
        e.preventDefault();
        var data = JSON.parse($(this).attr("data-like"));
        var csrftoken = getCookie("csrftoken") != null ? getCookie("csrftoken") : window.__TING__Token;
        var url = decodeURIparams(window.__TING__URL_Like, {"restaurant":data.resto})
        var auth = window.__TING__Session
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
                        if(b.hasClass("liked")){ b.removeClass("liked").html(unlikedresto);} 
                        else { b.addClass("liked").addClass("ting-btn-animate").html(likedresto);}
                    } else { showErrorMessage(response.type, response.message);}
                }, error: function(_, t, e){ showErrorMessage(t, e); }
            });
        } else { $("#ting-user-login").click(); showErrorMessage(randomString(10), "Login Required !!!");}
    });
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
    } else {return url}
};

var numerilize = function(n, t, d){
    if(typeof t === undefined || t == null){
        if(typeof n === 'number'){
            if(n > 1000000000000) return (n / 1000000000000).toFixed(2) + " Tn";
            else if(n > 1000000000) return (n / 1000000000).toFixed(2) + " Bn";
            else if(n > 1000000) return (n / 1000000).toFixed(2) + " M";
            else if(n > 1000) return (n / 1000).toFixed(2) + " K";
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

function getUserCurrentLocation(lt, lg, ad, tc, cc, ads, id) {

    if (!navigator.geolocation) {
        $.getJSON('https://ipapi.co/json/', function(data) {
            document.getElementById(lt).value = data.latitude;
            document.getElementById(lg).value = data.longitude;
            document.getElementById(ad).value = data.city + ", " + data.region + ", " + data.country;
            document.getElementById(tc).value = data.city;
            document.getElementById(cc).value = data.country_name;
            document.getElementById(id).value = data.ip
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

                var length = results[0].address_components.length
                var country = results[0].address_components[length - 1]
                var town = results[0].address_components[length - 3]

                document.getElementById(lt).value = latitude;
                document.getElementById(lg).value = longitude;
                document.getElementById(ad).value = address;
                document.getElementById(tc).value = town.long_name;
                document.getElementById(cc).value = country.long_name;
                document.getElementById(id).value = results[0].place_id

                let inputElse = document.getElementById(ads);

                if(inputElse != null){
                    inputElse.value = address;
                }

            }
        });
    }, function () { 

        $.getJSON('https://ipapi.co/json/', function(data) {
            document.getElementById(lt).value = data.latitude;
            document.getElementById(lg).value = data.longitude;
            document.getElementById(ad).value = data.city + ", " + data.region + ", " + data.country;
            document.getElementById(tc).value = data.city;
            document.getElementById(cc).value = data.country_name;
            document.getElementById(id).value = data.ip
        });

    }, {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
    });
}

function initializeRestaurantMap(lat, long, addr, addr_else, place, cont, clickable, img) {

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

        } else{
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
                } else {
                    marker.setAnimation(google.maps.Animation.BOUNCE);
                }
            }
            markers.push(marker);
        }

    } else {
        var htmlMarker = new HTMLMarker(latitude, longitude, img);
        htmlMarker.setMap(map);
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

                        var position = {
                            lat: n_latitude,
                            lng: n_longitude
                        }

                        $("#" + lat).val(n_latitude);
                        $("#" + long).val(n_longitude);
                        $("#" + addr).val(n_address);
                        $("#" + place).val(results[0].place_id);
                        
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

function HTMLMarker(lat, lng, img, map){
    this.lat = lat;
    this.lng = lng;
    this.img = img;
    this.pos = new google.maps.LatLng(lat,lng);
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