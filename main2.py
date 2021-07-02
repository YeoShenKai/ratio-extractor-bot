import base64
from io import BytesIO

from flask import Flask
from flask import request
from flask.templating import render_template
from RatioAnalyserBot import output_website, web_plot
from matplotlib.figure import Figure

app = Flask(__name__)

#Activate venv: .\venv\Scripts\activate

@app.route("/")
def index():
    selection_industry_type = request.args.get("industry", "")
    print(selection_industry_type)

    try:
        total_revenue_growth = float(request.args.get("total_revenue_growth", ""))
        return_on_equity = float(request.args.get("return_on_equity", ""))
        total_asset_turnover = float(request.args.get("total_asset_turnover", ""))
        current_ratio = float(request.args.get("current_ratio", ""))
        ebitda_margin = float(request.args.get("ebitda_margin", ""))
        total_debt_capital = float(request.args.get("total_debt_capital", ""))
        user_inputs = [selection_industry_type, total_revenue_growth, return_on_equity, current_ratio,
                       ebitda_margin, total_asset_turnover, total_debt_capital]
        predictions = output_website("data/", user_inputs)
        #predictions = {'P/LTM Diluted EPS Before Extra [Latest] (x)': 'TEST1', 'P/BV [Latest] (x)': 'TEST2'}
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

    print(predictions[1])
    print(total_revenue_growth, return_on_equity, current_ratio, ebitda_margin, total_asset_turnover, total_debt_capital)

    '''
    user_inputs = [selection_industry_type, total_revenue_growth, return_on_equity, current_ratio, \
        ebitda_margin, total_asset_turnover, total_debt_capital]
    predictions = output_website("Chemicals Report.csv", user_inputs)
    predictions["P/LTM Diluted EPS Before Extra [Latest] (x)"] = str(round(predictions["P/LTM Diluted EPS Before Extra [Latest] (x)"], 2))
    predictions["P/BV [Latest] (x)"] = str(round(predictions["P/BV [Latest] (x)"], 1))
    
    '''
    return (
        render_template('webapp.html')
        + f' \
        <div class = "results">\
            <p> Selected Industry:  {selection_industry_type} </p> \
            <p> The estimated P/E ratio is: {predictions[0]["P/LTM Diluted EPS Before Extra [Latest] (x)"][1]} </p> \
            <p> The estimated P/B ratio is: {predictions[0]["P/BV [Latest] (x)"][1]} </p>\
        </div>'
    )

    '''
    '<p> Selected Industry: </p>'
    + selection_industry_type
    + '<p> The estimated P/E ratio is </p>'
    + predictions["P/LTM Diluted EPS Before Extra [Latest] (x)"]
    + '<br>'
    + '<p> The estimated P/B ratio is  </p>'
    + predictions["P/BV [Latest] (x)"]
    '''
    

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)