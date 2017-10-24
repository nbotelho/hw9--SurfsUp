import datetime as dt
import numpy as np
import pandas as pd

from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func

#Calculating a date exactly one year from today
prev_year = dt.date.today() - dt.timedelta(days=365) 

#Create an engine to connect to the hawaii.sqlite database
engine = create_engine("sqlite:///hawaii.sqlite", echo=False)

# Using SQLAlchemy automap_base() to reflect tables from hawaii.sqlite above into classes 
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

#Creating a db session
session = Session(engine)

#Saving a reference to classes Station and Station_Measurement
station = Base.classes.hawaii_station
measurement = Base.classes.hawaii_station_measurement

#Create an app
app = Flask(__name__)

###############################################################################################
#Define what to do when a user hits the home page
###############################################################################################
@app.route('/')
def index():
    print("Server received request for 'Home' page...")
    return "Welcome to the Climate API Home page!"

###############################################################################################
# Define what to do when a user hits the following endpoint -> /api/v1.0/precipitation
###############################################################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Query for the dates and precipitation observations from the last year.
    prcp_12_month_data = session.query( measurement.measurement_date, measurement.precipitation).\
        filter(measurement.measurement_date >= prev_year).\
       order_by(measurement.measurement_date.asc()).all()

    # Convert list of tuples to a Dictionary using date as the key and precipitation as the value.
    prcp_list = []
    for prcp in  prcp_12_month_data:
        prcp_dict = {}
        prcp_dict = {prcp[0]: prcp[1]}
        prcp_list.append(prcp_dict)

    # Return the json representation of your dictionary.
    return jsonify(prcp_list)  

###############################################################################################
# endpoint -> /api/v1.0/stations
###############################################################################################

@app.route("/api/v1.0/stations")

def stations():
    # Query to return the stations, ordered by the station abbr.
    stations = session.query( station.station_abbr).\
               order_by(station.station_abbr.asc()).all()
        
    #Unpack tuples using list comprehension 
    station_list = [row[0] for row in stations]        
        
    # Return the json representation of the stations.
    return jsonify(station_list)   

###############################################################################################
# endpoint -> /api/v1.0/tobs
###############################################################################################

@app.route("/api/v1.0/tobs")
def obs_temp():
	

	#Return a  list of Temperature Observations (tobs) for the previous year
	tobs = session.query(measurement.observed_temperature_F).\
	    	filter(measurement.measurement_date >= prev_year).\
	   		order_by(measurement.measurement_date.asc()).all()
	   
	tobs_list = [row[0] for row in tobs]         
	    
	#Return the json representation of the observed temperatures. Convert the api data into a valid json response object.
	return jsonify(tobs_list)   
################################################################################################  
# endpoint -> /api/v1.0/<start_dt>
################################################################################################
@app.route("/api/v1.0/<start_dt>")
def agg_temp(start_dt):

	#Return a json list of the minimum temperature, the average temperature, and the max 
	#temperature for all dates greater than and equal to the start date.
	min_temp = session.query(func.min(measurement.observed_temperature_F)).\
                filter(measurement.measurement_date >= start_dt ).first()      
	
	max_temp = session.query(func.max(measurement.observed_temperature_F)).\
				filter(measurement.measurement_date >= start_dt ).first() 

	avg_temp = session.query(func.min(measurement.observed_temperature_F)).\
				filter(measurement.measurement_date >= start_dt ).first() 
                                
	#Return the json representation of the observed temperatures. Convert the api data into a valid json response object.
	return jsonify(min_temp[0], max_temp[0], avg_temp[0])              
################################################################################################
# endpoint -> /api/v1.0/<start_dt>/<end_dt>
################################################################################################   

@app.route("/api/v1.0/<start_dt>/<end_dt>")
def agg_temp_start_end(start_dt, end_dt):

	#Return a json list of the minimum temperature, the average temperature, and the max 
	#temperature for all dates greater than and equal to the start date.
	min_temp = session.query(func.min(measurement.observed_temperature_F)).\
                filter(measurement.measurement_date.between(start_dt, end_dt)).first()      
	
	max_temp = session.query(func.max(measurement.observed_temperature_F)).\
				filter(measurement.measurement_date.between(start_dt, end_dt)).first() 

	avg_temp = session.query(func.min(measurement.observed_temperature_F)).\
				filter(measurement.measurement_date.between(start_dt, end_dt)).first() 
                                
	#Return the json representation of the observed temperatures. Convert the api data into a valid json response object.
	return jsonify(min_temp[0], max_temp[0], avg_temp[0])  
#################################################################################################

if __name__ == '__main__':
   app.run(debug=True)   