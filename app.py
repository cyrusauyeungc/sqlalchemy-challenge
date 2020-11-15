#################################################
# Import dependencies
#################################################
import pandas as pd
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# Create connection to the sqllite
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available routes."""
    return (
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/Station<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/(YYYY-MM-DD)<br>"
        f"/api/v1.0(start=YYYY-MM-DD)/(end=YYYY-MM-DD)<br>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all measurements"""
    # Query all passengers
    results = session.query(Measurement).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all measurement
    # Convert the query results to a dictionary using date as the key and prcp as the value.
    measurement_list = []
    for result in results:
        measurement_list_dict = {}
        measurement_list_dict["date"] = result.date
        measurement_list_dict["prcp"] = result.prcp
        measurement_list.append(measurement_list_dict)

    return jsonify(measurement_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
	# Query all stations
    results = session.query(Station.station).all()
    session.close()
    
    # Convert list of tuples into normal list
    all_station = list(np.ravel(results))

    # Jsonify summary
    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def tempartureobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all temparture observation"""
    # Calculate the date 1 year ago from the last data point in the database
    results_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    str_date=list(np.ravel(results_date))[0]
    latest_date=dt.datetime.strptime(str_date,"%Y-%m-%d")
    year_back=latest_date-dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
    results=session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date.desc()).\
            filter(Measurement.date>=year_back).all()
    session.close()
    all_temperature=[]
    for tobs,date in results:
        tobs_dict={}
        tobs_dict['date']=date
        tobs_dict['tobs']=tobs
        all_temperature.append(tobs_dict)
    return jsonify(all_temperature)

@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()
    temp_obs={}
    temp_obs["Min_Temp"]=results[0][0]
    temp_obs["avg_Temp"]=results[0][1]
    temp_obs["max_Temp"]=results[0][2]
    return jsonify(temp_obs)

@app.route("/api/v1.0/<start>/<end>")
def calc_temps_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format YYYY-mm-dd
        end_date (string): A date string in the format YYYY-mm-dd
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()    
    session.close()
    temp_range={}
    temp_range["Min_Temp"]=results[0][0]
    temp_range["avg_Temp"]=results[0][1]
    temp_range["max_Temp"]=results[0][2]
    return jsonify(temp_range)

if __name__ == '__main__':
    app.run(debug=True)