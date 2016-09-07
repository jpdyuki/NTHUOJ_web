/*
The MIT License (MIT)

Copyright (c) 2014 NTHUOJ team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/
var plot_piechart;
var confirm_change_userlevel;
$(function() {
  plot_piechart = function(data) {
    var statisticsTotal = 0;
    var datasets = data.datasets[0];
    datasets.backgroundColor = [];
    datasets.borderColor = [];
    var phase1 = Math.random() * 2.0 * Math.PI;
    var phase2 = phase1 + 2;
    var phase3 = phase2 + 2;
    for (var i = 0; i < datasets.data.length; i++) {
      statisticsTotal += datasets.data[i];
      // Generate random ranbow color to each data
      colR = Math.floor(Math.sin(0.5*i+phase1) * 127) + 128;
      colG = Math.floor(Math.sin(0.5*i+phase2) * 127) + 128;
      colB = Math.floor(Math.sin(0.5*i+phase3) * 127) + 128;
      datasets.backgroundColor.push('rgba(' + [colR, colG, colB, 0.2].join(',') + ')');
      datasets.borderColor.push('rgba(' + [colR, colG, colB, 1].join(',') + ')');
    }
    datasets.borderWidth = 1;
    data.datasets[0] = datasets;
    var ctx = $('#piechart');
    var pieChart = new Chart(ctx, {
      type: 'pie',
      data: data,
      options: {
        legend: {
            display: false
        },
        legendCallback: function(chart) {
          var text = [];
          text.push('<ul class="pie-legend">');
          for (var i = 0; i < chart.data.datasets[0].data.length; i++) {
            text.push('<li><span style="background-color:');
            text.push(chart.data.datasets[0].backgroundColor[i]);
            text.push('; border-color:');
            text.push(chart.data.datasets[0].borderColor[i]);
            text.push('"></span>');
            text.push(chart.data.labels[i]+': '+chart.data.datasets[0].data[i]);
            text.push('</li>');
          }
          text.push('</ul>');
          return text.join("");
        }
      }
    });
    var legend = pieChart.generateLegend();
    $('#piechart-legend').html(legend);
    if (statisticsTotal == 0) {
      // If no statistics available, appear this notification.
      $('#statistics').html('No statistics yet.');
    }
  };

  confirm_change_userlevel = function() {
    return confirm('Are you sure you want to change ' +
      $('#id_username').val() + ' to ' +
      $('#id_user_level option:selected').text() + '?');
  };
});
