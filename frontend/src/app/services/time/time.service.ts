import {Injectable} from '@angular/core';
import {Observable, Subject, BehaviorSubject} from 'rxjs';
import {HttpClient, HttpParams} from '@angular/common/http';

@Injectable({
    providedIn: 'root'
})
export class TimeService {
    private subject = new BehaviorSubject('');
    private currentDateInISOString = null;

    constructor(private http: HttpClient) {
    }

    setCurrentDate(dateInISOString) {
        this.currentDateInISOString = dateInISOString;
    }

    getCurrentDate(): Observable<any> {
        if (this.currentDateInISOString !== null) {
            this.subject.next(this.currentDateInISOString);
        } else {
            const today = new Date();
            this.subject.next(today.toISOString());
        }
        return this.subject.asObservable();
    }
}

