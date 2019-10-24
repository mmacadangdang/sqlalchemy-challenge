import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#weather app
app = Flask(__name__)


latest_date = (session.query(Measurement.date)
                .order_by(Measurement.date.desc())
                .first())
latest_date = list(np.ravel(latest_date))[0]

latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
latest_year = int(dt.datetime.strftime(latest_date, '%Y'))
latest_month = int(dt.datetime.strftime(latest_date, '%m'))
latest_day = int(dt.datetime.strftime(latest_date, '%d'))

year_ago = dt.date(latest_year, latest_month, latest_day) - dt.timedelta(days=365)
year_ago = dt.datetime.strftime(year_ago, '%Y-%m-%d')




@app.route("/")
def home():
    return (f"Hawai'i Climate<br/>"
            f"------------------------------<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/precipitaton<br/>"
            f"/api/v1.0/tobs<br/>"
            f"-------------------------------<br/>"
            f"datesearch/yyyy-mm-dd<br/>"
            f"/api/v1.0/datesearch/2016-08-23<br/>"
            f"-------------------------------<br/>"
            f"datesearch/start date(yyyy-mm-dd)/end date(yyyy-mm-dd)<br/>"
            f"/api/v1.0/datesearch/2016-08-23/2017-08-23"
           )
            

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > year_ago)
                      .order_by(Measurement.date)
                      .all())
    
    precipitation_data = []
    for result in results:
        precipitation_dict = {result.date: result.prcp, "Station": result.station}
        precipitation_data.append(precipitation_dict)

    return jsonify(precipitation_data)

@app.route("/api/v1.0/tobs")
def temperature():

    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > year_ago)
                      .order_by(Measurement.date)
                      .all())

    temp_data = []
    for result in results:
        temp_dict = {result.date: result.tobs, "Station": result.station}
        temp_data.append(temp_dict)

    return jsonify(temp_data)

@app.route("/api/v1.0/datesearch/<startDate>")
def start(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route("/api/v1.0/datesearch/<startDate>/<endDate>")
def startEnd(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)