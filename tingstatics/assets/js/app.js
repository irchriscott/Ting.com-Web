/*  THIS JS SHEET BELONGS TO TING.COM
    Author: Ir Christian Scott -> Code Pipes Solutions
    Date : 23 April 2019
*/

let markers = [];

$(document).ready(function(){

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

    $("#ting-map-form").submit(function(e){
        e.preventDefault();
    });

    $("#ting-search-location-input-else").searchLocationByAddress("ting-restaurant-latitude", "ting-restaurant-longitude", "ting-search-location-input", "ting-search-location-input-else", "ting-restaurant-place-id", "ting-restaurant-map-container")

    $("select.dropdown, .dropdown").dropdown('hide');

    $("#ting-new-restaurant-form").submitFormAjax();
    $("#ting-new-category-form").submitFormAjax();
    $("#ting-new-package-form").submitFormAjax();
    $("#ting-admin-login-form").submitFormAjax();
    $("#ting-activate-licence-key").submitFormAjax();
    $("#ting-admin-edit-restaurant-form").submitFormAjax();
    $("#ting-admin-config-restaurant-form").submitFormAjax();
    $("#ting-admin-edit-profile-form").submitFormAjax();
    $("#ting-admin-change-password-form").submitFormAjax();
    $("#ting-add-administrator-profile-form").submitFormAjax();
    $("#ting-add-category-form").submitFormAjax();
    $("#ting-add-menu-food-form").submitFormAjax();
    $("#ting-admin-reset-password").submitFormAjax();
    $("#ting-add-menu-drink-form").submitFormAjax();
    $("#ting-add-menu-dish-form").submitFormAjax();
    $("#ting-add-branch-form").submitFormAjax();
    $("#ting-add-table-form").submitFormAjax();

    let today = new Date();

    // $("#").calendar({
    //     minDate: new Date(today.getFullYear(), today.getMonth(), today.getDate() - 5)
    // });

    var window_width = $(window).width(),
        window_height = window.innerHeight,
        header_height = $(".default-header").height(),
        header_height_static = $(".site-header.static").outerHeight(),
        fitscreen = window_height - header_height;

    $(".fullscreen").css("height", window_height);
    $(".fitscreen").css("height", fitscreen);

    $(".default-header").sticky({
        topSpacing: 0
    });

    $("#ting-session-profile-image-update").submitProfileImage();

    $("#ting-open-profile-img-input").click(function(e){
        e.preventDefault();
        $("#ting-profile-img-input").click();
    });

    $("#ting-profile-img-input").change(function(){
        updateProfileImage(this);
    });

    $("#ting-single-image-input").change(function(e){
        singleImagePreview(this, "ting-single-image-preview");
    });

    $("#ting-multiple-image-input").change(function(e){
        multipleImagesPreview(this, $(".ting-item-images-preview"));
    });

    $(".ting-textarea-froala-editor").setFroalaEditor();
});

function capitalize(text){
    return text.replace(text.charAt(0), text.charAt(0).toUpperCase())
}

function randomString(length) {
    var chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    var result = '';
    for (var i = length; i > 0; --i) result += chars[Math.floor(Math.random() * chars.length)];
    return result;
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
        } else { $("[data-modal=" + $(this).attr("id") + "]").modal("show") }
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

function hideModal(container){
    $(container).modal('hide');
}

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

            } else {
                showErrorMessage("locate_user", status);
            }
        });
    }, function () { showErrorMessage("locate_user", 'Unable To Fetch Location !!!') });
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

function HTMLMarker(lat, lng, img){
    this.lat = lat;
    this.lng = lng;
    this.img = img;
    this.pos = new google.maps.LatLng(lat,lng);
}
    
HTMLMarker.prototype = new google.maps.OverlayView();
HTMLMarker.prototype.onRemove = function(){}
    
HTMLMarker.prototype.onAdd = function(){
    div = document.createElement('div');
    div.className = "ting-maps-marker";
    div.innerHTML = "<div class='ting-maps-marker-box'><img src='" + this.img + "' alt=''></div>";
    var panes = this.getPanes();
    panes.overlayImage.appendChild(div);
}
    
HTMLMarker.prototype.draw = function(){
    var overlayProjection = this.getProjection();
    var position = overlayProjection.fromLatLngToDivPixel(this.pos);
    var panes = this.getPanes();
    panes.overlayImage.style.left = position.x + 30 + 'px';
    panes.overlayImage.style.top = position.y + 52 + 'px';
}