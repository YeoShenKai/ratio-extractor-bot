from flask import Flask
from flask import request
from RatioAnalyserBot import output_website

app = Flask(__name__)

print('hello')
@app.route("/")
def index():
    # Obtain the relevant inputs from the user
    print('hello')
    selection_industry_type = request.args.get("selection_industry_type", "")

    try:
        total_revenue_growth = float(request.args.get("total_revenue_growth", ""))
        return_on_equity = float(request.args.get("return_on_equity", ""))
        current_ratio = float(request.args.get("current_ratio", ""))
        ebitda_margin = float(request.args.get("ebitda_margin", ""))
        total_asset_turnover = float(request.args.get("total_asset_turnover", ""))
        total_debt_capital = float(request.args.get("total_debt_capital", ""))

        user_inputs = [selection_industry_type, total_revenue_growth, return_on_equity, current_ratio,
                       ebitda_margin, total_asset_turnover, total_debt_capital]

        predictions = output_website("Chemicals Report.csv", user_inputs)
        predictions["P/LTM Diluted EPS Before Extra [Latest] (x)"] = str(round(predictions["P/LTM Diluted EPS Before Extra [Latest] (x)"], 2))
        predictions["P/BV [Latest] (x)"] = str(round(predictions["P/BV [Latest] (x)"], 1))

    except ValueError:
        predictions = dict()
        predictions["P/LTM Diluted EPS Before Extra [Latest] (x)"] = "not available"
        predictions["P/BV [Latest] (x)"] = "not available"

    return (
            """
            <img src="/static/logo.png" alt="Savills Logo">
            <h1>Price Multiples Estimation</h1>
            
            <p>
            This web app is used as a reference to determine the possible price multiples (i.e. P/E and P/BV) to be utilized 
            for determining the valuation of a company in a similar industry. To utilize this model, indicate the industry and 
            input information on the latest financial ratios. Click the button and the price multiples will be generated accorindgly.
            </p>
            
            <p>
            The price multiples are generated based on regression analysis and with the financial ratio that has the highest
            correlation with the relevant price multiples.
            </p>
            
            <form action="" method="get">
                Industry Type:<br>
                <input type="radio" name="selection_industry_type" value="Commodity Chemicals (Primary)">
                <label for="Insurance">Commodity Chemicals (Primary)</label><br>
                <input type="radio" name="selection_industry_type" value="Manufacturing">
                <label for="Manufacturing">Manufacturing</label><br>
                
                <table>
                    <tr>
                        <td>Total Revenue Growth, 3 Year CAGR %:</td>
                        <td><input type="number" name="total_revenue_growth" placeholder=0.0 step=0.1 pattern="^\d*(\.\d{0,2})?$"/></td>
                    </tr>
                    <tr>
                        <td>Return on Equity %:</td>
                        <td><input type="number" name="return_on_equity" placeholder=0.0 step=0.1 pattern="^\d*(\.\d{0,2})?$"/></td>
                    </tr>
                    <tr>
                        <td>Current Ratio:</td>
                        <td><input type="number" name="current_ratio" placeholder=0.0 step=0.1 pattern="^\d*(\.\d{0,2})?$"/></td>
                    </tr>
                    <tr>
                        <td>EBITDA Margin %:</td>
                        <td><input type="number" name="ebitda_margin" placeholder=0.0 step=0.1 pattern="^\d*(\.\d{0,2})?$"/></td>
                    </tr>
                    <tr>
                        <td>Total Asset Turnover:</td>
                        <td><input type="number" name="total_asset_turnover" placeholder=0.0 step=0.1 pattern="^\d*(\.\d{0,2})?$"/></td>
                    <tr>
                    <tr>
                        <td>Total Debt / Capital %:</td>
                        <td><input type="number" name="total_debt_capital" placeholder=0.0 step=0.1 pattern="^\d*(\.\d{0,2})?$"/></td>
                    <tr>
                </table>
                <br>
                <input type="submit" value="Generate Price Multiples">
            </form>
            """
            + "Industry Selection: "
            + selection_industry_type
            + "<br>"
            + "The estimated P/E ratio is "
            + predictions["P/LTM Diluted EPS Before Extra [Latest] (x)"]
            + "<br>"
            + "The estimated P/B ratio is "
            + predictions["P/BV [Latest] (x)"]
            + "<br>"
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
