class ColorWheel {
    constructor (colors) {
        this.colors = colors;
        this.min_index = 0;
        this.max_index = this.colors.length;
        this.index = this.min_index;
    }

    getNext() {
        this.index = (this.index + 1) % this.max_index;
        return this.colors[this.index];
    }

    get(howmany) {
        let colors = [];

        for (let i=0; i<howmany; i++) {
            colors.push(this.getNext());
        }

        return colors;
    }
}

class ChartConfigDataset {
    constructor (title) {
        this.dataset = {
            label: title,
            backgroundColor: "#f00",
            borderColor: "#f00",
            borderWidth: 1,
            data: [],
            fill: true
        }
    }

    getDataset() {
        return this.dataset;
    }

    setTitle(title) {
        this.dataset.label = title;
    }

    setBackgroundColor(bg_color) {
        this.dataset.backgroundColor = bg_color;
    }

    setBorderColor(border_color) {
        this.dataset.borderColor = border_color;
    }

    setBorderWidth(border_width) {
        this.dataset.borderWidth = border_width;
    }

    setData(data) {
        this.dataset.data = data;
    }

    shouldFill(should_fill) {
        this.dataset.fill = should_fill;
    }
}

class ChartConfigGenerator {
    constructor(type, title) {
        this.title = title;

        this.config = {
            type: type,
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                title: {display: true, text: this.title},
                legend: {
                    position: 'top',
                    display: false
                },
                tooltips: {
                    mode: 'index',
                    intersect: false
                },
                animation: {
                    duration: 0, // general animation time
                },
                hover: {
                    mode: 'nearest',
                    intersect: true,
                    animationDuration: 0, // duration of animations when hovering an item
                },
                responsiveAnimationDuration: 0, // animation duration after a resize
                scales: {
                    xAxes: [{display: true, scaleLabel: {display: false, labelString: ""}, gridLines: {display: true,drawTicks: true} }],
                    yAxes: [{display: true, scaleLabel: {display: false, labelString: ""}, ticks: {suggestedMin: 0, suggestedMax: 100}, gridLines: {display: true,drawTicks: true}, ticks: {beginAtZero: true} }]
                }
            }
        };
    }

    setType(type) {
        this.config.type = type;
    }

    setTitle(title, should_show) {
        this.config.options.title = {display: should_show, text: title};
    }

    setLabels(labels) {
        this.config.data.labels = labels;
    }

    addDataset(dataset) {
        this.config.data.datasets.push(dataset);
    }

    setDataset(dataset) {
        this.config.data.datasets = dataset;
    }

    setData(data, dataset_index) {
        this.config.data.datasets[dataset_index].data = data;
    }

    setBackgroundColor(bg_color, dataset_index) {
        this.config.data.datasets[dataset_index].backgroundColor = bg_color;
    }

    setBorderColor(border_color, dataset_index) {
        this.config.data.datasets[dataset_index].borderColor = border_color;
    }

    setXAxisLabel(label, should_show) {
        this.config.options.scales.xAxes[0].scaleLabel.display = should_show;
        this.config.options.scales.xAxes[0].scaleLabel.labelString = label;
    }

    setYAxisLabel(label, should_show) {
        this.config.options.scales.yAxes[0].scaleLabel.display = should_show;
        this.config.options.scales.yAxes[0].scaleLabel.labelString = label;
    }

    getConfig() {
        return this.config;
    }
}

class ChartJSWrapper extends Chart {
    constructor (ctx, config) {
        return super(ctx, config);
    }

    updateConfig(config) {
        this.config = config;
    }
}

class BaseAnimatorObject
{
    constructor (data_url)
    {
        this.data_url = data_url;
    }

    update()
    {
        getJSON(
            this, this.data_url, function(ref, err, data)
            {
                if (err===null)
                {
                    ref.on_post_update(ref, data);
                }
                else
                {
                    ref.on_error(ref, err, data);
                }
            }
        );
    }

    on_post_update(ref, data)
    {
    }

    on_error(ref, err, data)
    {
    }
}

class UsageBarChartAnimator extends BaseAnimatorObject {
    constructor (ctx, config_generator, data_url) {
        super(data_url);

        this.ctx = ctx;
        this.config_generator = config_generator;
        this.chart = new ChartJSWrapper(this.ctx, this.config_generator.getConfig());
    }

    on_post_update(ref, data) {
        super.on_post_update(ref, data);

        let i = 0;
        let values = [];
        let labels = [];

        for (i=0; i<data.length; i++) {
            let item = data[i];
            labels.push(item.label);
            values.push(item.usage_metrics.total);
        }

        this.config_generator.setData(values, 0);
        this.config_generator.setLabels(labels);
        this.chart.updateConfig(this.config_generator.getConfig());
        this.chart.update();
    }
}

class UsageLineChartAnimator extends BaseAnimatorObject {
    constructor (ctx, config_generator, data_url) {
        super(data_url);

        this.ctx = ctx;
        this.dataset_color_wheel = new ColorWheel([
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)'
        ])
        this.config_generator = config_generator;
        this.chart = new ChartJSWrapper(this.ctx, this.config_generator.getConfig());
    }

    setDatasetParameters(color_wheel) {
        this.dataset_color_wheel = color_wheel;
    }

    on_post_update(ref, data) {
        super.on_post_update(ref, data);

        let i = 0;
        let datasets = [];

        for (i=0; i<data.length; i++) {
            let item = data[i];
            let color = this.dataset_color_wheel.getNext();

            let config_dataset = new ChartConfigDataset(item.label);
            config_dataset.shouldFill(false);
            config_dataset.setBackgroundColor(color);
            config_dataset.setBorderColor(color);
            config_dataset.setData(item.usage_metrics.usages);

            datasets.push(config_dataset.getDataset());
        }

        this.config_generator.setDataset(datasets);
        console.log(datasets);
        this.chart.updateConfig(this.config_generator.getConfig());
        this.chart.update();
    }
}