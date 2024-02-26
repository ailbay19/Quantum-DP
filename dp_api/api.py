from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from main import country_year_query, get_errors_between, country_all_queries
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pandas as pd

# To run the api, run the following command in the terminal: uvicorn main:app --reload
# and open your browser at http://127.0.0.1:8000/${endpoint_url}
# For interactive API documentation, visit http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc

# example dataformat to return
#     const dataset = [
#   {
#     real: 59,
#     pseudo: 57,
#     quantum: 86,
#     month: 'Jan',
#   },
# ];

app = FastAPI()


class Tempetures(BaseModel):
    real: list[float] = []
    pseudo: list[float] = []
    quantum: list[float] = []

class BudgetManager:
    budget = 1000

    @staticmethod
    def spend(amount):
        BudgetManager.budget = BudgetManager.budget - amount

        # TODO: REMOVE?
        # RESET IF OUT OF BUDGET
        if(BudgetManager.budget < 0):
            BudgetManager.budget = 1000
        
        return amount
    
    @staticmethod
    def get_budget():
        return BudgetManager.budget

origins = [
    "http://localhost:3001",
    "http://localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TempeturesResponse(BaseModel):
    histogramData: list[dict[str, float]]
    errorPercentages: dict[str, float]

class TRUpd(BaseModel):
    data : List[TempeturesResponse]
    labels : list[str]

@app.post("/", response_model=List[TempeturesResponse]) # endpoint url can be anything
def func_name(country: str, year:str, budget_percent:int = 1):
    avg_tempetures = country_year_query(country, year, BudgetManager.spend(budget_percent))

    print(f"\n\nREMAINING BUDGET: {BudgetManager.budget}\n")

    avg_tempetures_real = avg_tempetures[0]
    avg_tempetures_dp = avg_tempetures[1]
    avg_tempetures_quantum_dp = avg_tempetures[2]
    histogramData: list[dict[str, float]] = [{"avg_real": avg_tempetures_real[i], "avg_dp": avg_tempetures_dp[i], "avg_quantum_dp": avg_tempetures_quantum_dp[i]} for i in range(len(avg_tempetures_real))]

    pseudo_error, real_error, pseudo_vs_real = get_errors_between(*avg_tempetures)
    errorPercentages: dict[str, float] = {"dp_error": pseudo_error, "quantum_dp_error": real_error}

    return [{ "histogramData": histogramData, 'errorPercentages': errorPercentages}]

@app.post("/yearly", response_model=TRUpd) # endpoint url can be anything
def yearly(country: str, budget_percent:int = 1):
    queries = country_all_queries(country, BudgetManager.spend(budget_percent))

    response = []
    for query in queries:
        histogramData: list[dict[str, float]] = [{"avg_real": query[0][i], "avg_dp": query[1][i], "avg_quantum_dp": query[2][i]} for i in range(len(query[0]))]

        pseudo_error, real_error, pseudo_vs_real = get_errors_between( *query )
        errorPercentages: dict[str, float] = {"dp_error": pseudo_error, "quantum_dp_error": real_error}

        response.append( {"histogramData":histogramData, "errorPercentages": errorPercentages} )

    return {"data": response, "labels": queries[0][0].reset_index()['year'].tolist()}