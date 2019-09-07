
// var bg_color_wheel = new ColorWheel([
//     'rgba(255, 99, 132, 0.2)',
//     'rgba(54, 162, 235, 0.2)',
//     'rgba(255, 206, 86, 0.2)',
//     'rgba(75, 192, 192, 0.2)',
//     'rgba(153, 102, 255, 0.2)',
//     'rgba(255, 159, 64, 0.2)'
// ]);

var bg_color_wheel = new ColorWheel([
    'rgba(255, 159, 64, 0.2)'
]);

// var border_color_wheel = new ColorWheel([
//     'rgba(255, 99, 132, 1)',
//     'rgba(54, 162, 235, 1)',
//     'rgba(255, 206, 86, 1)',
//     'rgba(75, 192, 192, 1)',
//     'rgba(153, 102, 255, 1)',
//     'rgba(255, 159, 64, 1)'
// ]);

var border_color_wheel = new ColorWheel([
    'rgba(255, 159, 64, 1)'
]);

var device_usage_bar_chart_config = new ChartConfigGenerator('bar', 'Hours used by Device');
var device_usage_bar_chart_config_dataset = new ChartConfigDataset(
    device_usage_bar_chart_config.title
);
device_usage_bar_chart_config.addDataset(device_usage_bar_chart_config_dataset.getDataset());
device_usage_bar_chart_config.setBackgroundColor(bg_color_wheel.get(6), 0);
device_usage_bar_chart_config.setBorderColor(border_color_wheel.get(6), 0);
device_usage_bar_chart_config.setYAxisLabel("# hours used", true);

var device_usage_bar_chart_ctx = document.getElementById('device-usage-bar-canvas');
var device_usage_bar_chart_animator = new UsageBarChartAnimator(
    device_usage_bar_chart_ctx,
    device_usage_bar_chart_config,
    'get_device_usage_metrics'
)
device_usage_bar_chart_animator.update();





var device_usage_line_chart_config = new ChartConfigGenerator('line', 'Duration Plot');
device_usage_line_chart_config.setXAxisLabel("Time Axis", true);

var device_usage_line_chart_ctx = document.getElementById('device-usage-line-canvas');
var device_usage_line_chart_animator = new UsageLineChartAnimator(
    device_usage_line_chart_ctx,
    device_usage_line_chart_config,
    'get_device_usage_metrics'
)
device_usage_line_chart_animator.update();






var user_usage_bar_chart_config = new ChartConfigGenerator('bar', 'Hours used by Users');
var user_usage_bar_chart_config_dataset = new ChartConfigDataset(
    user_usage_bar_chart_config.title
);
user_usage_bar_chart_config.addDataset(user_usage_bar_chart_config_dataset.getDataset());
user_usage_bar_chart_config.setBackgroundColor(bg_color_wheel.get(6), 0);
user_usage_bar_chart_config.setBorderColor(border_color_wheel.get(6), 0);
user_usage_bar_chart_config.setYAxisLabel("# hours used", true);

var user_usage_bar_chart_ctx = document.getElementById('user-usage-bar-canvas');
var user_usage_bar_chart_animator = new UsageBarChartAnimator(
    user_usage_bar_chart_ctx,
    user_usage_bar_chart_config,
    'get_user_usage_metrics'
)
user_usage_bar_chart_animator.update();






var user_usage_line_chart_config = new ChartConfigGenerator('line', 'Duration Plot');
user_usage_line_chart_config.setXAxisLabel("Time Axis", true);

var user_usage_line_chart_ctx = document.getElementById('user-usage-line-canvas');
var user_usage_line_chart_animator = new UsageLineChartAnimator(
    user_usage_line_chart_ctx,
    user_usage_line_chart_config,
    'get_user_usage_metrics'
)
user_usage_line_chart_animator.update();





