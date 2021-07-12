import base64
from io import BytesIO

from flask import Flask
from flask import request
from flask.templating import render_template
from matplotlib.pyplot import plot
from RatioAnalyserBot import output_website, web_plot, web_plot_2
from matplotlib.figure import Figure

app = Flask(__name__)

#Activate venv: venv\Scripts\activate

@app.route("/")
def index(): #Fix url upon publish
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
        global besteqns_predictions
        besteqns_predictions = output_website("data/", user_inputs)
        besteqns = besteqns_predictions[0]
        predictions = besteqns_predictions[1]
        #predictions = {'P/LTM Diluted EPS Before Extra [Latest] (x)': 'TEST1', 'P/BV [Latest] (x)': 'TEST2'}
        print(besteqns_predictions)
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

    '''
    user_inputs = [selection_industry_type, total_revenue_growth, return_on_equity, current_ratio, \
        ebitda_margin, total_asset_turnover, total_debt_capital]
    predictions = output_website("Chemicals Report.csv", user_inputs)
    predictions["P/LTM Diluted EPS Before Extra [Latest] (x)"] = str(round(predictions["P/LTM Diluted EPS Before Extra [Latest] (x)"], 2))
    predictions["P/BV [Latest] (x)"] = str(round(predictions["P/BV [Latest] (x)"], 1))
    '''

    def output():
        return (f'\
            <div class = "results">\
            <p> Selected Industry:  {selection_industry_type} </p> \
            <p> The estimated P/E ratio is: {predictions[0]["P/LTM Diluted EPS Before Extra [Latest] (x)"][1]} </p> \
            <p> The estimated P/B ratio is: {predictions[0]["P/BV [Latest] (x)"][1]} </p>\
        </div>\
    ')

    outputs = output()
    return (
        render_template('webapp.html') + outputs
    )

#Graph: Seperate url?
@app.route("/graph")
def plots():
    plot_selection = request.args.get("plottype", "")
    if plot_selection:
        print('plot selection', plot_selection)
        plot_output = web_plot_2("data/", besteqns_predictions[0], besteqns_predictions[1], plot_selection)
    else:
        plot_selection = 'None'
        print('Plot selection none')
        plot_output = 'Please select a plot type'
    
    return render_template('plotpage.html') + plot_output + plot_selection

'''
def hello():
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"
'''

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)