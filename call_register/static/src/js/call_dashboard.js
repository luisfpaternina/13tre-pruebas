odoo.define('CallRegister.Dashboard', function(require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;
    var self = this;
    var currency;
    var ActionMenu = AbstractAction.extend({
        contentTemplate: 'CallRegisterdashboard',

        events: {
            // 'click .call_register_dashboard': 'onclick_call_register_dashboard'
        },
        init: function(parent, context) {
            this._super(parent, context);
            this.result = [];
        },
        renderElement: function(ev) {
            var self = this;
            $.when(this._super())
                .then(function(ev) {
                    // rpc.query({
                    //     model: "call_register.dashboard",
                    //     method: "get_calls_total_this_year"
                    // }).then(function (result) {
                    //     var total_calls_this_year = result;
                    //     $('#h1_total_calls_this_year').remove()
                    //     if (total_calls_this_year) {
                    //         $('#total_calls_this_year').append('<h2 style="color:#c767dc;" id="h1_total_calls_this_year">' + total_calls_this_year + '</h2>')
                    //     }
                    
                    rpc.query({
                        model: "call_register.dashboard",
                        method: "get_calls_by_numbers"
                    }).then(function (result) {
                        var ctx = document.getElementById("canvas-calls-month-top-ten").getContext('2d');
                        var labels = result.period; // Add labels to array
                        
                        if (window.donut != undefined) {
                            window.donut.destroy();
                        }

                        window.myCharts = new Chart(ctx, {
                            type: 'bar',
                            data: {
                                labels: labels,
                                datasets: [
                                    {
                                        label: "TOTAL LLAMADAS",
                                        backgroundColor: "#74ADFA",
                                        data: result['total']
                                    },

                                ]

                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                barValueSpacing: 5,
                                scales: {
                                    yAxes: [{
                                        ticks: {
                                            min: 0
                                        }
                                    }],
                                },
                            }

                    });
                    // });
                    // rpc.query({
                    //     model: "call_register.dashboard",
                    //     method: "get_calls_by_month"
                    //          })
                    //     .then(function (result) {
                    //         var ctx = document.getElementById("canvas-calls-month-top-ten").getContext('2d');
                    //         var labels = result.period; // Add labels to array
                    //         if (window.donut != undefined)
                    //                window.donut.destroy();
                    //         window.myCharts = new Chart(ctx, {
                    //             type: 'bar',
                    //             data: {
                    //                 labels: labels,
                    //                 datasets: [
                    //                 {
                    //                     label: "TOTAL",
                    //                     backgroundColor: "#74ADFA",
                    //                     data: result['total']
                    //                 },

                    //             ]

                    //             },
                    //             options: {
                    //             responsive: true,
                    //             maintainAspectRatio: false,
                    //             barValueSpacing: 20,
                    //             scales: {
                    //                 yAxes: [{
                    //                     ticks: {
                    //                         min: 0
                    //                     }
                    //                 }]
                    //             }
                    //         }

                    // });

                });
                // rpc.query({
                //     model: "call_register.dashboard",
                //     method: "get_duration_calls"
                //             })
                //     .then(function (result) {
                //         var ctx = document.getElementById("canvas-duration-call-answered").getContext('2d');
                //         var labels = result.period; // Add labels to array
                //         if (window.donut != undefined)
                //                 window.donut.destroy();
                //         window.myCharts = new Chart(ctx, {
                //             type: 'pie',
                //             data: {
                //                 labels: labels,
                //                 datasets: [{
                //                             backgroundColor: self.getListColors(labels),
                //                             data: result['time_answered']
                //                             }]


                //             },
                //             options: {
                //             responsive: true,
                //             plugins: {
                //                 legend: {
                //                 position: 'top',
                //                 },
                //             title: {
                //             display: true,
                //             }
                //             }
                //             },

                // });
                                // var ctx = document.getElementById("canvas-duration-call-not-answered").getContext('2d');
                                // var labels = result.period; // Add labels to array
                                // if (window.donut != undefined)
                                //        window.donut.destroy();
                    //         window.myCharts = new Chart(ctx, {
                    //             type: 'pie',
                    //             data: {
                    //                 labels: labels,
                    //                 datasets: [{
                    //                             backgroundColor: self.getListColors(labels),
                    //                             data: result['time_not_answered']
                    //                            }]
                    //             },
                    //             options: {
                    //             responsive: true,
                    //             plugins: {
                    //               legend: {
                    //                 position: 'top',
                    //               },
                    //           title: {
                    //             display: true,
                    //           }
                    //             }
                    //           },

                    // });

                    //         var ctx = document.getElementById("canvas-duration-call-total").getContext('2d');
                    //                 var labels = result.period; // Add labels to array
                    //                 if (window.donut != undefined)
                    //                        window.donut.destroy();
                    //         window.myCharts = new Chart(ctx, {
                    //             type: 'pie',
                    //             data: {
                    //                 labels: labels,
                    //                 datasets: [{
                    //                             backgroundColor: self.getListColors(labels),
                    //                             data: result['time_total']
                    //                            }]

                    //             },
                    //             options: {
                    //             responsive: true,
                    //             plugins: {
                    //               legend: {
                    //                 position: 'top',
                    //               },
                    //           title: {
                    //             display: true,
                    //           }
                    //             }
                    //           },

                    // });

                // })
                });
        },
        getListColors: function(period){
            var self = this;
            var coloR = []
            for (var month in period) {
                 coloR.push(self.getRandomColor());
            }
            return coloR;
        },

        getRandomColor: function() {
            var r = Math.floor(Math.random() * 255);
            var g = Math.floor(Math.random() * 255);
            var b = Math.floor(Math.random() * 255);
            return "rgb(" + r + "," + g + "," + b + ")";
                },

        willStart: function() {
            var self = this;
            return Promise.all([ajax.loadLibs(this), this._super()]);
        },
    });
    core.action_registry.add('call_register_dashboard', ActionMenu);

});