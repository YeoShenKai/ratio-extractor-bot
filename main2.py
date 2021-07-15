import base64
from io import BytesIO

from flask import Flask
from flask import request
from flask.templating import render_template
from flask.typing import ResponseReturnValue
from matplotlib.pyplot import plot
from RatioAnalyserBot import output_website, web_plot, web_plot_2
from matplotlib.figure import Figure

app = Flask(__name__)

#Activate venv: venv\Scripts\activate

@app.route("/")
def index(): #Fix url upon publish
    global selection_industry_type
    selection_industry_type = request.args.get("industry", "")

    try:
        total_revenue_growth = float(request.args.get("total_revenue_growth", ""))
        return_on_equity = float(request.args.get("return_on_equity", ""))
        total_asset_turnover = float(request.args.get("total_asset_turnover", ""))
        current_ratio = float(request.args.get("current_ratio", ""))
        ebitda_margin = float(request.args.get("ebitda_margin", ""))
        total_debt_capital = float(request.args.get("total_debt_capital", ""))
        user_inputs = [selection_industry_type, total_revenue_growth, return_on_equity, current_ratio,
                       ebitda_margin, total_asset_turnover, total_debt_capital]
        user_inputs_indexing = [None, 'Total Revenues, 3 Yr CAGR % [LTM] (%)', 'Return on Equity % [LTM]', 'Current Ratio [LTM]',\
             'EBITDA Margin % [LTM]', 'Total Asset Turnover [Latest Annual]', 'Total Debt/Capital % [Latest Annual]']
        global besteqns_predictions
        besteqns_predictions = output_website("data/", user_inputs)
        besteqns = besteqns_predictions[0]
        predictions = besteqns_predictions[1]
        #predictions = {'P/LTM Diluted EPS Before Extra [Latest] (x)': 'TEST1', 'P/BV [Latest] (x)': 'TEST2'}
        print(besteqns_predictions)

        global user_input_values
        user_input_values = {}
        for dependent, indeps_eqn_corr in besteqns.items():
            input_index = user_inputs_indexing.index(indeps_eqn_corr[0])
            input_value = user_inputs[input_index]
            if indeps_eqn_corr[0] not in user_input_values:
                user_input_values[indeps_eqn_corr[0]] = input_value
        
    except:
        total_revenue_growth = None
        return_on_equity = None
        total_asset_turnover = None
        current_ratio = None
        ebitda_margin = None
        total_debt_capital = None
        
        predictions = [dict(),[0,0]]
        predictions[0]["P/LTM Diluted EPS Before Extra [Latest] (x)"] = ['not available', 'not available']
        predictions[0]["P/BV [Latest] (x)"] = ['not available', 'not available']

    #print(predictions[1])
    #print(total_revenue_growth, return_on_equity, current_ratio, ebitda_margin, total_asset_turnover, total_debt_capital)

    def output():
        return (f'\
            <div class = "results">\
            <p> Selected Industry:  {selection_industry_type} </p> \
            <p> The estimated P/E ratio is: {predictions[0]["P/LTM Diluted EPS Before Extra [Latest] (x)"][1]} </p> \
            <p> The estimated P/B ratio is: {predictions[0]["P/BV [Latest] (x)"][1]} </p>\
        </div>\
        <div class = "plots">\
            <h2> Visualise the data! </h2>\
            <button onclick="window.location.href = \'/graph\'" style="font-size: 100%;"> Plots </button>\
        </div>\
    ')

    outputs = output()
    return (
        render_template('webapp.html') + outputs
    )

@app.route("/graph")
def plots():
    try: 
        besteqns_predictions
        plot_selection = request.args.get("plottype", "")
        if plot_selection:
            plot_output = web_plot_2("data/", besteqns_predictions[0], besteqns_predictions[1], plot_selection, selection_industry_type, user_input_values)
        else:
            plot_selection = 'None'
            plot_output = 'Please select a plot type'    
        return render_template('plotpage.html') + plot_output
    except:
        return render_template('plotpage-error.html')

@app.route("/test")
def test():
    return('hello world')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)