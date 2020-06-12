/*  THIS JS SHEET BELONGS TO TING.COM
    Author: Ir Christian Scott -> Code Pipes Solutions
    Date : 09 June 2020
*/

$(document).ready(function(){

	var charts = $(".ting-data-charts-canvas");
	var charts_types = ['for the last 7 days', 'for the last 6 months', 'for the last 5 years'];

	Highcharts.setOptions({
		colors: ['#a3a1fb', '#54d8ff', '#ff9f54', '#DDDF00', '#24CBE5', '#64E572', '#FF9655', '#FFF263', '#6AF9C4']
	});

	if(charts.length > 0) {
		
		for (var i = 0; i < charts.length; i++) {
			
			var canvas = $(charts[i]);
			var data = canvas.attr("data-chart-data");

			if(data != null && data !== undefined && data != "") {

				var json_data = JSON.parse(data);
				var chart_data = json_data.map(data =>  parseInt(data.data) );
				var chart_labels = json_data.map(data => data.date);

				setupHighcharts(canvas, chart_data, chart_labels, json_data);
			}
		}
	}

	setTimeout(() => reflowCharts() , 500);

	$("#ting-charts-select-type").dropdown({
		onChange: function(value) {
			var url = $(this).attr("data-url");
			$.ajax({
				url: url,
				data: {type: value},
				success: function(response) {
					var placement_data = response[0].map(data =>  parseInt(data.data) );
					var placement_labels = response[0].map(data => data.date);

					var placement = $("#ting-data-charts-canvas-1");
					setupHighcharts(placement, placement_data, placement_labels, response[0]);

					var incomes_data = response[1].map(data =>  parseInt(data.data) );
					var incomes_labels = response[1].map(data => data.date);

					var incomes = $("#ting-data-charts-canvas-2");
					setupHighcharts(incomes, incomes_data, incomes_labels, response[1]);

					var waiters_data = response[2].map(data =>  parseInt(data.data) );
					var waiters_labels = response[2].map(data => data.date);

					var waiters = $("#ting-data-charts-canvas-3");
					if(waiters != null && waiters != undefined && waiters.length > 0) {
						setupHighcharts(waiters, waiters_data, waiters_labels, response[2]);
					}

					$("#ting-data-charts-label-placements").text('Placements ' + charts_types[parseInt(value) - 1]);
					$("#ting-data-charts-label-incomes").text('Incomes ' + charts_types[parseInt(value) - 1]);
					$("#ting-data-charts-label-waiters").text('Waiter Placements ' + charts_types[parseInt(value) - 1]);
					$("#ting-data-charts-label-ordered").text('Most Ordered Menus ' + charts_types[parseInt(value) - 1]);
				},
				error: function(_, t, e) { }
			});

			var menus_container = $("#ting-data-ordered-menus");

			if(menus_container != null && menus_container != undefined && menus_container.length > 0) {
				var load_url = menus_container.attr("data-url");
				$.ajax({
					url: load_url,
					data: {type: value},
					success: function(response) { menus_container.html(response) },
					error: function(_, t, e) { }
				});
			}
		}
	});

	var menus_items = $(".ting-menus-item");
	if(menus_items.length > 0) { 
		$("#ting-admin-reports-content-panel").loadAjax($(menus_items[0]).attr("data-url"));
	}

	$(".ting-menus-item").click(function(e) {
		e.preventDefault();
		var url = $(this).attr("data-url");
		if(url != null && url != undefined && url != "") {
			$(this).addClass("active").siblings().removeClass("active");
			$("#ting-admin-reports-content-panel").loadAjax(url);
		}
	});
});

var reflowCharts = function () {
	for (var i = 0; i < Highcharts.charts.length; i++) { Highcharts.charts[i].reflow() }
}

function setupHighcharts(canvas, data, labels, raw_data) {
	
	var prefix = canvas.attr("data-chart-prefix");
	var suffix = canvas.attr("data-chart-suffix");
	var series = canvas.attr("data-chart-series");

	var type = canvas.attr("data-chart-type");
	var chart_data = type != "pie" ? data : raw_data.map(data => { return {name: data.date, y: parseFloat(data.data)} })

	var options = {
		chart: {
			type: type,
			style: { fontFamily: 'Poppins, Avenir' },
			width: null
		},
		title: { text: null },
		xAxis: { categories: labels },
		yAxis: { title: { text: null } },
		tooltip: {
			shared: true,
			valueSuffix: ' ' + suffix,
			valuePrefix: prefix + ' '
		},
		credits: { enabled: false },
		plotOptions: {
			areaspline: { fillOpacity: 0.5 },  
			marker: { symbol: 'circle' },
			column: {
				pointPadding: 0.2,
				borderWidth: 0
			},
			pie: {
	            allowPointSelect: true,
	            cursor: 'pointer',
	            dataLabels: { enabled: false },
	            showInLegend: true
	        }
		},
		series: [{
			name: series,
			data: chart_data,
			fillColor: {
				linearGradient: [0, 0, 0, 300],
				stops: [
				    [0, Highcharts.getOptions().colors[0]],
				    [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
				]
			},
			marker: { symbol: 'circle' }
		}]
	};
	Highcharts.chart(canvas.attr('id'), options);
}

String.prototype.addComma = function () {
    return this.replace(/(.)(?=(.{3})+$)/g, '$1,')
}

function addCommas(nStr) {
    nStr += '';
    var comma = /,/g;
    nStr = nStr.replace(comma, '');
    x = nStr.split('.');
    x1 = x[0];
    x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    return x1 + x2;
}

jQuery.fn.loadAjax = function(url) {
	var container = $(this);
	container.find(".ting-loader").show();
	container.find(".ting-data-content").empty();
	$.ajax({
        type: 'GET',
        url: url,
        success: function(response){
            if(typeof response === 'object' && response != null){
                if(response.type == 'error'){
                    container.find(".ting-loader").hide();
                    container.find(".ting-data-content").html('<div class="ui red message"><b>Error '+ response.status +' : </b>' + response.message + '</div>');
                }
            } else {
                container.find(".ting-loader").hide();                  
                container.find(".ting-data-content").html(response);
            }
        },
    	error: function(_, t, e){
            container.find(".ting-loader").hide();
            container.find(".ting-data-content").html('<div class="ui red message">' + e + '</div>');
        }
   	});
}