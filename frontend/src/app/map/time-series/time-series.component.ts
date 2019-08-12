import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import * as $ from 'jquery';
import {MapService} from '../../services/map-service/map.service';
import {TimeService} from '../../services/time/time.service';
import {Tweet} from '../../models/tweet.model';

declare var require: any;
const Highcharts = require('highcharts');

@Component({
    selector: 'app-time-series',
    templateUrl: './time-series.component.html',
    styleUrls: ['./time-series.component.css']
})
export class TimeSeriesComponent implements OnInit {

    @Output() timeRangeChange = new EventEmitter();
    private hasPlotBand = false;
    private currentDateInISO = null;

    constructor(private mapService: MapService, private timeService: TimeService) {
    }

    ngOnInit() {
        this.timeService.getCurrentDate().subscribe(date => {
            this.setCurrentDate(date)});
        this.mapService.getFireTweetData().subscribe(this.drawTimeSeries);

    }

    setCurrentDate(dateString) {
        console.log(dateString);
        this.currentDateInISO = dateString;
    }

    // Draw time series
    drawTimeSeries = (tweets: Tweet[]) => {
        console.log(this.currentDateInISO)
        const chartData = [];
        const dailyCount = {};

        for (const tweet of tweets) {
            const createAt = tweet.create_at.split('T')[0];
            if (dailyCount.hasOwnProperty(createAt)) {
                dailyCount[createAt]++;
            } else {
                dailyCount[createAt] = 1;
            }
        }
        // time bar
        Object.keys(dailyCount).sort().forEach(key => {
            chartData.push([new Date(key).getTime(), dailyCount[key]]);
        });

        const timeseries = Highcharts.chart('timebar-container', {
            chart: {
                type: 'line',
                zoomType: 'x',
                height: 200,
                backgroundColor: null,
                events: {
                    selection(event) {
                        let timebarStart = 1;
                        let timebarEnd = 0;
                        if (event.hasOwnProperty('xAxis')) {
                            timebarStart = event.xAxis[0].min;
                            timebarEnd = event.xAxis[0].max;
                        } else {
                            timebarStart = event.target.axes[0].dataMin;
                            timebarEnd = event.target.axes[0].dataMax;
                        }
                        $(window).trigger('timeRangeChange', {timebarStart, timebarEnd});
                    },
                    click: (event) => {
                        const halfUnit = 86400000 / 2;
                        let dateInMs = event.xAxis[0].value - event.xAxis[0].value % halfUnit;
                        dateInMs += dateInMs % (halfUnit * 2);
                        const dateInISO = new Date(dateInMs).toISOString();
                        if (!this.hasPlotBand) {
                            timeseries.xAxis[0].addPlotBand({
                                from: dateInMs - halfUnit,
                                to: dateInMs + halfUnit,
                                color: '#d88040',
                                id: 'plotBand'
                            });
                            this.currentDateInISO = dateInISO;
                            this.hasPlotBand = true;
                        } else if (dateInISO !== this.currentDateInISO) {
                            timeseries.xAxis[0].removePlotBand('plotBand');
                            timeseries.xAxis[0].addPlotBand({
                                from: dateInMs - halfUnit,
                                to: dateInMs + halfUnit,
                                color: '#d88040',
                                id: 'plotBand'
                            });
                            this.currentDateInISO = dateInISO;
                            this.hasPlotBand = true;
                        } else {
                            timeseries.xAxis[0].removePlotBand('plotBand');
                            this.currentDateInISO = null;
                            this.hasPlotBand = false;
                        }

                    },
                }
            },
            title: {
                text: 'Wildfire',
                style: {
                    color: '#e25822'
                }
            },
            xAxis: {
                type: 'datetime',
                crosshair: true,
            },
            series: [{
                data: chartData,
                color: '#e25822',
                name: '<span style=\'color:#e25822\'>Wildfire Tweet</span>'
            }]

        });
    }


}
