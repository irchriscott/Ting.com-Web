$(document).ready(function() {

    var admin = window.__TING__Administrator

    var uuid = PubNub.generateUUID();
    var pubnub = new PubNub({
        publishKey: "pub-c-62f722d6-c307-4dd9-89dc-e598a9164424",
        subscribeKey: "sub-c-6597d23e-1b1d-11ea-b79a-866798696d74",
        uuid: uuid
    });

    // button.addEventListener('click', () => {
    //     pubnub.publish({
    //         channel : "pubnub_onboarding_channel",
    //         message : {"sender": uuid, "content": "Hello From JavaScript SDK"}
    // }, function(status, response) {
    //       //Handle error here
    //     });
    // });

    pubnub.subscribe({ channels: [admin.channel, admin.branch.channel], withPresence: true });

    pubnub.addListener({
        message: function(event) {
            var message = typeof event.message === 'object' ? event.message : JSON.parse(event.message)
            switch(message.type) {
                case 'request_resto_table':
                    if(admin.permissions.includes('can_assign_table')) {
                        iziToast.show({
                            id: message.uuid,
                            title: 'New Client Placed',
                            titleSize: '16px',
                            message: '<p style="color:#FFFFFF; margin-top:5px;">A new client has been placed on table <b>' + message.data.table + '</b></p>',
                            messageSize: '13px',
                            theme: 'dark',
                            image: message.sender.image,
                            imageWidth: 120,
                            maxWidth: 450,
                            position: 'topRight',
                            timeout: 30000,
                            progressBar: false,
                            buttons: [
                                ['<button>VIEW PLACEMENTS</button>', function (instance, toast) {
                                    window.location = window.__TING__URL__Get__Placements
                                }, true] 
                            ],
                            onOpening: function () {},
                            onOpened: function () {},
                            onClosing: function () {},
                            onClosed: function () {}
                        });
                        loadAjaxURL("ting-data-placements-container", window.__TING__URL__Load__Placements);
                        loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements)
                    }
                    break;
                case 'response_w_resto_table':
                    iziToast.show({
                        id: message.uuid, 
                        title: 'New Table For You',
                        titleSize: '16px',
                        message: '<p style="color:#FFFFFF; margin-top:5px;">You have been assigned to the client on table <b>' + message.data.table + '</b></p>',
                        messageSize: '13px',
                        theme: 'dark',
                        image: message.data.user.image,
                        imageWidth: 120,
                        maxWidth: 450,
                        position: 'topRight',
                        timeout: 30000,
                        progressBar: false,
                        onOpening: function () {},
                        onOpened: function () {},
                        onClosing: function () {},
                        onClosed: function () {}
                    });
                    loadAjaxURL("ting-data-placements-container", window.__TING__URL__Load__Placements);
                    loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements)
                    break;
                default:
                    break;
            }
        },
        presence: function(event) {}
    });
})

function loadAjaxURL(container, url){
    setTimeout(function(){
        $("#" + container).load(url, function(){$(this).children(".ting-loader").hide();
        }, function(error){showErrorMessage("error", error);});
    });
}