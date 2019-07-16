import {Component, EventEmitter, Input, OnInit} from '@angular/core';
import 'leaflet/dist/leaflet.css';

declare let L;
import * as $ from 'jquery';
import HeatmapOverlay from 'leaflet-heatmap/leaflet-heatmap.js';
import {MapService} from '../../services/map-service/map.service';
import 'leaflet-maskcanvas';
import 'leaflet-velocity-ts';
import * as turf from '@turf/turf'

@Component({
    selector: 'app-heatmap',
    templateUrl: './heatmap.component.html',
    styleUrls: ['./heatmap.component.css']
})
export class HeatmapComponent implements OnInit {
    private mainControl;
    private tweetData;
    private tweetLayer;
    private liveTweetLayer;
    private liveTweetBird = [];
    private liveTweetMarkers;
    private liveTweetIdSet = new Set();
    private map;
    private switchStatus = 0;
    private tempLayers = [];
    private tempLayer1;
    private regionsMax = [];
    private Max = [0];
    private Min = [0];
    private temp_breaks = [-6, -3, 0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36];

    constructor(private mapService: MapService) {
    }

    ngOnInit() {
        // A hacky way to declare that
        const that = this;
        // Initialize map and 3 base layers
        const mapBoxUrl = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiY' +
            'SI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw';
        const satellite = L.tileLayer(mapBoxUrl, {id: 'mapbox.satellite'});
        const streets = L.tileLayer(mapBoxUrl, {id: 'mapbox.streets'});
        const dark = L.tileLayer(mapBoxUrl, {id: 'mapbox.dark'});
        this.map = L.map('map', {
            center: [33.64, -117.84],
            zoom: 5,
            maxzoom: 22,
            layers: [satellite, streets, dark]
        });

        // Initialize base layer group
        const baseLayers = {
            '<span style =\'color:blue\'>Satellite</span>': satellite,
            '<span style =\'color:red\'>Streets</span>': streets,
            '<span style =\'color:black\'>Dark</span>': dark
        };

        this.mainControl = L.control.layers(baseLayers).addTo(this.map);

        this.mapService.mapLoaded.emit(this.map);
        // Generate coordinate in siderbar
        this.map.addEventListener('mousemove', (ev) => {
            const lat = ev.latlng.lat;
            const lng = ev.latlng.lng;
            $('#mousePosition').html('Lat: ' + Math.round(lat * 100) / 100 + ' Lng: ' + Math.round(lng * 100) / 100);
        });

        // Get heatmap data from service
        //this.mapService.getHeatmapData();
        //this.mapService.heatmapDataLoaded.subscribe( this.heatmapDataHandler);

        // Get my heatmap data from service
        this.mapService.getmyTempData();
        this.mapService.contourDataLoaded.subscribe(this.contourDataHandler);
        this.mapService.contourDataLoaded.subscribe(this.polygonDataHandler);
        this.mapService.contourDataLoaded.subscribe(this.heatmapDataHandler);
        this.mapService.temperatureChangeEvent.subscribe(this.rangeSelectHandler);

        // Get tweets data from service
        this.mapService.getTweetsData();
        this.mapService.tweetDataLoaded.subscribe(this.tweetDataHandler);

        // Get rainfall data from service
        this.mapService.getWildfirePredictionData();
        this.mapService.fireEventDataLoaded.subscribe(this.fireEventHandler);

        // Get wind data from service
        this.mapService.getWindData();
        this.mapService.windDataLoaded.subscribe(this.windDataHandler);

        // Add event Listener to live tweet switch
        $('#liveTweetSwitch').on('click', this.liveTweetSwitchHandler);

        // Add event Listener when user specify a time range on time series
        $(window).on('timeRangeChange', this.timeRangeChangeHandler);
    }

    tweetDataHandler = (data) => {
        this.tweetLayer = L.TileLayer.maskCanvas({
            radius: 10,
            useAbsoluteRadius: true,
            color: '#000',
            opacity: 1,
            noMask: true,
            lineColor: '#e25822'
        });
        const tempData = [];
        this.tweetData = data.tweetData;
        data.tweetData.forEach(x => {
            tempData.push([x[0], x[1]]);
        });

        this.tweetLayer.setData(tempData);
        this.mainControl.addOverlay(this.tweetLayer, 'Fire tweet');

    }


    liveTweetSwitchHandler = (event) => {
        if (this.switchStatus === 1) {
            this.liveTweetLayer.clearLayers();
            this.mapService.stopliveTweet();
            this.switchStatus = 0;
            return;
        }
        this.mapService.getLiveTweetData();
        this.mapService.liveTweetLoaded.subscribe(this.liveTweetDataHandler);
        this.switchStatus = 1;
    }

    liveTweetDataHandler = (data) => {
        this.liveTweetMarkers = L.TileLayer.maskCanvas({
            radius: 10,
            useAbsoluteRadius: true,
            color: '#000',
            opacity: 1,
            noMask: true,
            lineColor: '#e25822'
        });

        // Mockup Data for liveTweetLayer
        const birdIcon = L.icon({
            iconUrl: 'assets/image/perfectBird.gif',
            iconSize: [20, 20]
        });

        const birdCoordinates = [];

        data.data.forEach((tweet) => {
            if (!this.liveTweetIdSet.has(tweet.id)) {
                const point = [tweet.lat, tweet.long];
                birdCoordinates.push([tweet.lat, tweet.long]);
                const marker = L.marker(point, {icon: birdIcon}).bindPopup('I am a live tweet');
                this.liveTweetBird.push(marker);
                this.liveTweetIdSet.add(tweet.id);
            }
        });

        this.liveTweetLayer = L.layerGroup(this.liveTweetBird);
        this.liveTweetLayer.addTo(this.map);


        this.liveTweetMarkers.setData(birdCoordinates);
        const birds = $('.leaflet-marker-icon');
        window.setTimeout(() => {
            this.liveTweetBird = [];
            this.liveTweetLayer.clearLayers();
            this.liveTweetLayer.addLayer(this.liveTweetMarkers);
        }, 3200);
        let bird: any = 0;
        for (bird of birds) {
            if (bird.src.indexOf('perfectBird') !== -1) {
                $(bird).css('animation', 'fly 3s linear');
            }
        }
    }

    timeRangeChangeHandler = (event, data) => {
        const tempData = [];
        this.tweetData.forEach(entry => {
            if (entry[2] > data.timebarStart && entry[2] < data.timebarEnd) {
                tempData.push([entry[0], entry[1]]);
            }
        });
        this.tweetLayer.setData(tempData);
    }

    fireEventHandler = (data) => {

        const fireEventList = [];

        for (const ev of  data.fireEvents) {
            const point = [ev.lat, ev.long];
            const size = 40;
            const fireIcon = L.icon({
                iconUrl: 'assets/image/pixelfire.gif',
                iconSize: [size, size],
            });
            const marker = L.marker(point, {icon: fireIcon}).bindPopup('I am on fire(image>40%)');
            fireEventList.push(marker);

        }
        const fireEvents = L.layerGroup(fireEventList);
        this.mainControl.addOverlay(fireEvents, 'Fire event');
    }

    windDataHandler = (wind) => {
        // there's not much document about leaflet-velocity.
        // all we got is an example usage from
        // github.com/0nza1101/leaflet-velocity-ts
        const velocityLayer = L.velocityLayer({
            displayValues: true,
            displayOptions: {
                position: 'bottomleft', // REQUIRED !
                emptyString: 'No velocity data', // REQUIRED !
                angleConvention: 'bearingCW', // REQUIRED !
                velocityType: 'Global Wind',
                displayPosition: 'bottomleft',
                displayEmptyString: 'No wind data',
                speedUnit: 'm/s'
            },
            data: wind.data,
            maxVelocity: 12 // affect color and animation speed of wind
        });
        this.mainControl.addOverlay(velocityLayer, 'Global wind');
    }


    heatmapDataHandler = (data) => {
        // use heatmapOverlay from leaflet-heatmap
        // Documentation for details in change of custom parameter
        // https://www.patrick-wied.at/static/heatmapjs/docs.html#heatmap-setData
        const heatmapConfig = {
            radius: 1,
            maxOpacity: 0.63,
            minOpacity: 0.2,
            scaleRadius: true,
            useLocalExtrema: false,
            blur: 1,
            latField: 'lat',
            lngField: 'long',
            valueField: 'temp',
            // gradient is customized to match the color scales of temp plotting layers exactly the same
            gradient: {
                '.1': '#393fb8',
                '.2': '#45afd6',
                '.3': '#49ebd8',
                '.4': '#49eb8f',
                '.5': '#a6e34b',
                '.55': '#f2de5a',
                '.6': '#edbf18',
                '.65': '#e89c20',
                '.7': '#f27f02',
                '.75': '#f25a02',
                '.8': '#f23a02',
                '.85': '#f0077f',
                '.9': '#f205c3',
                '.99': '#9306ba',
            }
        };
        const heatmapLayer = new HeatmapOverlay(heatmapConfig);
        heatmapLayer.setData({max: 680, data: data.contourData});
        this.mainControl.addOverlay(heatmapLayer, 'Temp heatmap');
    }


    contourDataHandler = (data) => {
        // used turf built in features to add contour lines,
        // but contour lines can only built on ractangled data size boundary
        let tempPointsList = [];
        for (let points of data.contourData) {
            const tempPoint = turf.point([points.long, points.lat], {'temperature': points.temp});
            tempPointsList.push(tempPoint);
        }
        // Establish features and break points for contour lines
        const tempFeatures = turf.featureCollection(tempPointsList);
        const pointGrid = turf.explode(tempFeatures);
        const lines = turf.isolines(pointGrid, this.temp_breaks, {zProperty: 'temperature'});
        // Make contour lines smooth
        const _lFeatures = lines.features;
        for (let i = 0; i < _lFeatures.length; i++) {
            const _coords = _lFeatures[i].geometry.coordinates;
            const _lCoords = [];
            for (let j = 0; j < _coords.length; j++) {
                const _coord = _coords[j];
                const line = turf.lineString(_coord);
                const curved = turf.bezierSpline(line);
                _lCoords.push(curved.geometry.coordinates);
            }
            _lFeatures[i].geometry.coordinates = _lCoords;
        }
        // Give colors from light to dark for different temperature
        const tempEvents = [];
        for (let index = 0; index < lines.features.length; index++) {
            const colorCode = Math.floor(200 * (index + 1) / this.temp_breaks.length + 55);
            tempEvents.push(L.geoJSON(lines.features[index], {
                style: {
                    color: 'rgb(0, ' + colorCode + ', ' + colorCode + ')',
                    weight: 1,
                    opacity: 0.4
                }
            }));
        }
        // Add the contour layer to the map
        const region = L.layerGroup(tempEvents);
        this.mainControl.addOverlay(region, 'temp-contour');

    }

    polygonDataHandler = (data) => {
        let my = data.contourData;
        let all_latlng = []
        // Classify points for different temp into different list
        for (let t = 0; t < this.temp_breaks.length - 1; t++) {
            let latlng_list = [];
            for (let i = 0; i < my.length; i++) {
                if (my[i].temp >= this.temp_breaks[t] && my[i].temp <= this.temp_breaks[t + 1]) {
                    latlng_list.push([Number(my[i].lat), Number(my[i].long)]);
                }
            }
            all_latlng.push(latlng_list)

        }
        console.log(all_latlng);
        // Assign a different color and a layer for each small temperature interval
        const colorlist = ['#393fb8', '#45afd6', '#49ebd8', '#49eb8f', '#a6e34b', '#f2de5a', '#edbf18', '#e89c20', '#f27f02', '#f25a02', '#f23a02', '#f0077f', '#f205c3', '#9306ba'];
        const boxlist = ['blue- -6C', 'lightblue- -3C', 'greenblue- 0C', 'green- 3C', 'lightgreen- 6C', 'yellow- 9C', 'darkyellow- 12C', 'lightorange- 15C', 'orange-18C', 'richorange- 21C', 'red- 24C', 'purplered- 27C', 'lightpurple- 30C', 'purple- 33C']
        for (let i = 0; i < colorlist.length; i++) {
            this.tempLayer1 = L.TileLayer.maskCanvas({
                radius: 25,
                useAbsoluteRadius: true,
                color: '#000',
                opacity: 0.85,
                noMask: true,
                lineColor: colorlist[i]
            });
            this.tempLayer1.setData(all_latlng[i]);
            this.mainControl.addOverlay(this.tempLayer1, boxlist[i]);
            this.tempLayers.push(this.tempLayer1);
        }
        console.log(this.tempLayers);
    }

    rangeSelectHandler = (event) => {
        // Respond to the input range of temperature from the range selector in side bar

        // var int: always keep the lastest input Max/Min temperature
        if (event.newTemperature !== undefined) {
            this.Max = [];
            this.Max.push(event.newTemperature);
        }
        if (event.newTemperature2 !== undefined) {
            this.Min = [];
            this.Min.push(event.newTemperature2);
        }

        // for each valid input range, given list of layers of temp plotting satisfy the range and add to map
        if (this.Min[0] <= this.Max[0]) {
            for (let i = 0; i < this.temp_breaks.length; i++) {

                if (this.Max[0] >= this.temp_breaks[i] && this.Max[0] < this.temp_breaks[i + 1]) {
                    this.regionsMax = [];
                    for (let k = 0; k <= i; k++) {
                        const region = this.tempLayers[k];
                        this.regionsMax.push(region);
                    }
                }
            }
            for (let i = 0; i < this.temp_breaks.length; i++) {
                if (this.Min[0] >= this.temp_breaks[i] && this.Min[0] < this.temp_breaks[i + 1]) {
                    this.regionsMax.splice(0, i);
                }
            }

            console.log(this.regionsMax);
            for (const layer of this.tempLayers) {
                this.map.removeLayer(layer);
            }
            for (const region of this.regionsMax) {
                region.addTo(this.map);
            }
        }
    }


}
