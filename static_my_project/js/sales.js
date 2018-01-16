$(document).ready(function(){

    function renderChart(id, data, labels){
        var ctx = $('#'+id);
        var myChart = new Chart(ctx, {
            type: 'line',
             data: {
                labels: labels,
                datasets: [{
                    label: 'Sales',
                    data: data,
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.2)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)'
                    ],
                     borderWidth: 1
                 }]
             },
             options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero:true
                        }
                    }]
                },
             }
        });
    }

    function getSalesData(id, type){

        var url = '/analytics/sales/data/';
        var method = 'GET';
        var data = {"type": type};

        $.ajax({
            url: url,
            method: method,
            data: data,
            success: function(data){
                renderChart(id, data.data, data.labels)
            },
            error: function(error){
                $.alert("An error occurred")
            }
        })
    }

    var chartsToRender = $('.my-render-chart');
    $.each(chartsToRender, function(index, html){
        var $this = $(this);
        if( $this.attr('id') && $this.attr('data-type') ){
            getSalesData($this.attr('id'), $this.attr('data-type'));
        }
    })
});