import {EventEmitter, Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {HttpClient, HttpParams} from '@angular/common/http';
import {map} from 'rxjs/operators';
import {Tweet} from '../../models/tweet.model';
import {FirePrediction} from '../../models/firePrediction.model';
import {Wind} from '../../models/wind.model';
import {DropBoxItem} from '../../models/dropBox.model';
import {HeatMap} from '../../models/heatMap.model';
import {Boundary} from '../../models/boundary.model';


@Injectable({
    providedIn: 'root'
})
export class MapService {

    // Declare data events for components to action
    mapLoaded = new EventEmitter();
    temperatureChangeEvent = new EventEmitter();

    constructor(private http: HttpClient) {
    }


    getFireTweetData(): Observable<Tweet[]> {
        return this.http.get<Tweet[]>('http://127.0.0.1:5000/tweet/fire-tweet');
    }

    getWildfirePredictionData(): Observable<FirePrediction[]> {
        return this.http.get<FirePrediction[]>('http://127.0.0.1:5000/wildfire-prediction');
    }


    getWindData(): Observable<Wind[]> {
        return this.http.get<Wind[]>('http://127.0.0.1:5000/data/wind');
    }

    getBoundaryData(stateLevel, countyLevel, cityLevel, northEastBoundaries, southWestBoundaries): Observable<Boundary> {

        return this.http.post<object>('http://127.0.0.1:5000/search/boundaries', JSON.stringify({
            states: stateLevel,
            cities: cityLevel,
            counties: countyLevel,
            northEast: northEastBoundaries,
            southWest: southWestBoundaries,
        })).pipe(map(data => {
            return {type: 'FeatureCollection', features: data};
        }));
    }

    getFirePolygonData(northEastBoundaries, southWestBoundaries, setSize, start, end): Observable<any> {
        console.log('here in service');
        return this.http.post('http://127.0.0.1:5000/data/firePolygon', JSON.stringify({
            northEast: northEastBoundaries,
            southWest: southWestBoundaries,
            size: setSize,
            // date: '2019-08-04',
            startdate: start,
            enddate: end,
        })).pipe(map(data => {
            console.log('given data', data);
            return {type: 'FeatureCollection', features: data};
        }));
    }

    getDropBox(userInput): Observable<DropBoxItem[]> {
        // gets auto-completion suggestions

        return this.http.get<DropBoxItem[]>('http://127.0.0.1:5000/dropdownMenu', {params: new HttpParams().set('userInput', userInput)});
    }


    getTemperatureData(): Observable<HeatMap[]> {
        return this.http.get<HeatMap[]>('http://127.0.0.1:5000/data/recent-temp');
    }
}
