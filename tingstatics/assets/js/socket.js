$(document).ready(function() {

    var admin = window.__TING__Administrator

    var uuid = PubNub.generateUUID();
    var pubnub = new PubNub({
        publishKey: "pub-c-62f722d6-c307-4dd9-89dc-e598a9164424",
        subscribeKey: "sub-c-6597d23e-1b1d-11ea-b79a-866798696d74",
        uuid: uuid
    });

    loadAdminMessagesCount();
    loadAdminMessages();

    $("#ting-show-admin-messages").click(function(event){ 
        $("#ting-admin-messages-container").slideDown(150);
        event.stopPropagation();
        loadAdminMessages();
    });

    $("#ting-admin-messages-container, .modals, .dimmer").click(function(event) { event.stopPropagation(); });
    $(window).click(function() { $("#ting-admin-messages-container").slideUp(150); });

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
                        loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements);
                    }
                    break;
                case 'request_assign_waiter':
                    if(admin.permissions.includes('can_assign_table')) {
                        iziToast.show({
                            id: message.uuid,
                            title: 'Waiter Needed',
                            titleSize: '16px',
                            message: '<p style="color:#FFFFFF; margin-top:5px;">A waiter is needed on table <b>' + message.data.table + '</b>. Please assign !</p>',
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
                        loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements);
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
                    loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements);
                    break;
                case 'request_table_order':
                    if(admin.permissions.includes('can_receive_orders')) {
                        iziToast.show({
                            id: message.uuid, 
                            title: 'New Order On Table ' + message.data.table,
                            titleSize: '16px',
                            message: '<p style="color:#FFFFFF; margin-top:5px;"> ' + message.data.user.name + ' has placed an order on table <b>' + message.data.table + '</b></p>',
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
                        loadAjaxURL("ting-sides-pannel-content-orders", window.__TING__URL__Load__Dash__Orders);
                        loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements);
                    }
                    break;
                case 'request_w_table_order':
                    if (!admin.permissions.includes('can_receive_orders')){
                        iziToast.show({
                            id: message.uuid, 
                            title: 'New Order On Table ' + message.data.table,
                            titleSize: '16px',
                            message: '<p style="color:#FFFFFF; margin-top:5px;"> ' + message.data.user.name + ' has placed an order on table <b>' + message.data.table + '</b></p>',
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
                        loadAjaxURL("ting-sides-pannel-content-orders", window.__TING__URL__Load__Dash__Orders);
                        loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements);
                    }
                    break;
                case 'request_notify_order':
                    iziToast.show({
                        id: message.uuid, 
                        title: 'Order Delayed On Table ' + message.data.table,
                        titleSize: '16px',
                        message: '<p style="color:#FFFFFF; margin-top:5px;"> ' + message.sender.name + ' has placed an order on table <b>' + message.data.table + '</b> but it seems it is delaying. Please, Accept or Decline the order.</p>',
                        messageSize: '13px',
                        theme: 'dark',
                        image: message.sender.image,
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
                    loadAjaxURL("ting-sides-pannel-content-orders", window.__TING__URL__Load__Dash__Orders);
                    loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements);
                    break;
                case 'request_w_notify_order':
                    if (!admin.permissions.includes('can_receive_orders')){
                        iziToast.show({
                            id: message.uuid, 
                            title: 'Order Delayed On Table ' + message.data.table,
                            titleSize: '16px',
                            message: '<p style="color:#FFFFFF; margin-top:5px;"> ' + message.sender.name + ' has placed an order on table <b>' + message.data.table + '</b> but it seems it is delaying. Please, Accept or Decline the order</p>',
                            messageSize: '13px',
                            theme: 'dark',
                            image: message.sender.image,
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
                        loadAjaxURL("ting-sides-pannel-content-orders", window.__TING__URL__Load__Dash__Orders);
                        loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements);
                    }
                    break;
                case 'response_w_orders_updated':
                    loadAjaxURL("ting-sides-pannel-content-orders", window.__TING__URL__Load__Dash__Orders);
                    loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements);
                    loadAjaxURL("ting-data-placements-container", window.__TING__URL__Load__Placements);
                    break;
                case 'request_bill_request':
                    iziToast.show({
                        id: message.uuid, 
                        title: 'Bill Requested On Table ' + message.data.table,
                        titleSize: '16px',
                        message: '<p style="color:#FFFFFF; margin-top:5px;"> ' + message.sender.name + ' has requested his bill for him to further finalize his placement.</p>',
                        messageSize: '13px',
                        theme: 'dark',
                        image: message.sender.image,
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
                    loadAjaxURL("ting-sides-pannel-content-orders", window.__TING__URL__Load__Dash__Orders);
                    loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements);
                    break;
                case 'request_w_bill_request':
                    if (!admin.permissions.includes('can_complete_bill')){
                        iziToast.show({
                            id: message.uuid, 
                            title: 'Bill Requested On Table ' + message.data.table,
                            titleSize: '16px',
                            message: '<p style="color:#FFFFFF; margin-top:5px;"> ' + message.sender.name + ' has requested his bill for him to further finalize his placement.</p>',
                            messageSize: '13px',
                            theme: 'dark',
                            image: message.sender.image,
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
                        loadAjaxURL("ting-sides-pannel-content-orders", window.__TING__URL__Load__Dash__Orders);
                        loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements);
                    }
                    break;
                case 'response_w_request_message':
                    if(admin.permissions.includes('can_get_requests') || admin.id == message.receiver.id) {
                        iziToast.show({
                            id: message.uuid, 
                            title: 'Request From ' + message.sender.name + ', Table ' + message.data.table,
                            titleSize: '16px',
                            message: '<p style="color:#FFFFFF; margin-top:5px;"> ' + message.message + '</p>',
                            messageSize: '13px',
                            theme: 'dark',
                            image: message.sender.image,
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
                        loadAdminMessages();
                        loadAdminMessagesCount();
                    }
                    break;
                case 'request_placement_terminated':
                    iziToast.show({
                        id: message.uuid, 
                        title: 'Placement Terminated On Table ' + message.data.table,
                        titleSize: '16px',
                        message: '<p style="color:#FFFFFF; margin-top:5px;"> ' + message.sender.name + ' has terminated his placement and freed the space.</p>',
                        messageSize: '13px',
                        theme: 'dark',
                        image: message.sender.image,
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
                    loadAjaxURL("ting-sides-pannel-content-orders", window.__TING__URL__Load__Dash__Orders);
                    loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements);
                    break;
                case 'request_w_placement_terminated':
                    if (!admin.permissions.includes('can_complete_bill')){
                        iziToast.show({
                            id: message.uuid, 
                            title: 'Placement Terminated On Table ' + message.data.table,
                            titleSize: '16px',
                            message: '<p style="color:#FFFFFF; margin-top:5px;"> ' + message.sender.name + ' has terminated his placement and freed the space.</p>',
                            messageSize: '13px',
                            theme: 'dark',
                            image: message.sender.image,
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
                        loadAjaxURL("ting-sides-pannel-content-orders", window.__TING__URL__Load__Dash__Orders);
                        loadAjaxURL("ting-sides-pannel-content-placements", window.__TING__URL__Load__Dash__Placements);
                    }
                    break;
                default:
                    break;
            }
        },
        presence: function(event) {}
    });
});

function loadAjaxURL(container, url){
    setTimeout(function(){
        $("#" + container).load(url, 
            function(){$(this).children(".ting-loader").hide();}, 
            function(error){showErrorMessage("error", error);
        });
    });
}

function loadAdminMessages() {
    setTimeout(function(){
        $("#ting-admin-messages-container").load(
            window.__TING__URL__Load__Admin__Messages, function(){}, 
            function(error){showErrorMessage("error", error);
        });
    });
}

function loadAdminMessagesCount() {
    setTimeout(function(){
        $.ajax({
            type:"GET", url: window.__TING__URL__Load__Admin__Messages__Count, data: {},
            success: function(r){
                if(parseInt(r) !== NaN && parseInt(r) !== undefined && parseInt(r) > 0) {
                    $("#ting-admin-messages-count").text(r).show();
                } else { $("#ting-admin-messages-count").hide(); }
            },
            error: function(_, t, e){showErrorMessage("error", e)}
        });
    });
}