from django.shortcuts import render
from django.http import HttpResponse
#from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import StockData
from django.shortcuts import HttpResponse
 
#new imports
import databento as db
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv() 

 
# Code of your application, which uses environment variables (e.g. from `os.environ` or
# `os.getenv`) as if they came from the actual environment.
import requests
import json

APIKEY = os.getenv("APIKEY")
 
client = db.Historical(key=os.getenv("APIKEY"))
 
# Next, we will request the tbbo data
 
# Finally, we will calculate the mid-price for each row
#gLBX["mid_px"] = gLBX[["ask_px_00", "bid_px_00"]].mean(axis=1)
 
DATABASE_ACCESS = True
#if False, the app will always query the Alpha Vantage APIs regardless of whether the stock data for a given ticker is already in the local database
 
#view function for rendering home.html
def home(request):
    return render(request, 'home.html', {})
 
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
 
#print("testesttaoifidoahifoaof dsaiofashioaiosfh")
 
@csrf_exempt
def get_stock_data(request):
    #if request.is_ajax(): #request.headers.get('x-requested-with') == 'XMLHttpRequest':
   
    if is_ajax(request=request):
        #get ticker from the AJAX POST request
        ticker = request.POST.get('ticker', 'null')
        ticker = ticker.upper()
       
     #   if DATABASE_ACCESS == True:
            #checking if the database already has data stored for this ticker before querying the Alpha Vantage API
     #       if StockData.objects.filter(symbol=ticker).exists():
                #We have the data in our database! Get the data from the database directly and send it back to the frontend AJAX call
       #         entry = StockData.objects.filter(symbol=ticker)[0]
 
                #reset the data
                #StockData.objects.filter(symbol=ticker).delete()
       #         return HttpResponse(entry.data, content_type='application/json')
 
        #obtain stock data from DataBento APIs
        #get adjusted close data
        #price_series = requests.get(f'https://hist.databento.com/v0/METHOD_FAMILY.METHOD').json()
       
        #package up the data in an output dictionary
        #output_dictionary = {}
       # output_dictionary['prices'] = data_var
        data = client.timeseries.get_range(
        dataset="DBEQ.BASIC",
        start="2024-11-04T00:00:00",
        end="2024-11-05T00:00:00",
        symbols=[ticker],
        stype_in="raw_symbol",
#   stype_out="instrument_id",
    #schema="trades",
        schema="ohlcv-1s",
)
 
        gLBX = data.to_df()
#tutorial stuff
        resampled_df = (
            gLBX.groupby([gLBX.index.to_period("5 min"), "symbol"])
            .agg({"open": "first", "high": "max", "low":"min", "close":"last", "volume":"sum"})
            .reset_index("symbol")
        )
        resampled_df.index = resampled_df.index.to_timestamp().tz_localize("UTC")
        resampled_df.index.names = ["ts_event"]
        resampled_df.columns = ["symbol", "open", "high", "low", "close", "volume"]
 
        json_data = resampled_df.reset_index().to_json(orient="records", date_format="iso")
       
        #load attempt
        #output_dictionary = {}
       # output_dictionary['prices'] = json_data
 
        #data_var = json.loads(json_data)
     
 
        #save the dictionary to database
       # temp = StockData(symbol=ticker, data=json.dumps(resampled_df))
      # temp.save()
 #
        #return the data back to the frontend AJAX call
        return HttpResponse(json_data, content_type='application/json')
       # return JsonResponse({"success": True, "data": "Stock data here"})
 
    else:
        message = "Not Ajax"
        return HttpResponse(message)
        #return JsonResponse({"error": "Invalid request type"}, status=400)

        
