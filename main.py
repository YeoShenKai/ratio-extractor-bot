from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/")
def index():

    # Obtain the relevant inputs from the user
    selection_industry_type = request.args.get("selection_industry_type", "")

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
            <input type="radio" name="selection_industry_type" value="Insurance">
            <label for="Insurance">Insurance</label><br>
            <input type="radio" name="selection_industry_type" value="Manufacturing">
            <label for="Manufacturing">Manufacturing</label><br>
            
            <table>
                <tr>
                    <td>Total Revenue Growth, 3 Year CAGR %:</td>
                    <td><input type="number" name="total_revenue growth" pattern="^\d*(\.\d{0,2})?$"/></td>
                </tr>
                <tr>
                    <td>Return on Equity %:</td>
                    <td><input type="number" name="return_on_equity" pattern="^\d*(\.\d{0,2})?$"/></td>
                </tr>
                <tr>
                    <td>Current Ratio:</td>
                    <td><input type="number" name="current_ratio" pattern="^\d*(\.\d{0,2})?$"/></td>
                </tr>
                <tr>
                    <td>EBITDA Margin %:</td>
                    <td><input type="number" name="ebitda_margin" pattern="^\d*(\.\d{0,2})?$"/></td>
                </tr>
                <tr>
                    <td>Total Asset Turnover:</td>
                    <td><input type="number" name="total_asset_turnover" pattern="^\d*(\.\d{0,2})?$"/></td>
                <tr>
                <tr>
                    <td>Total Debt / Capital %:</td>
                    <td><input type="number" name="total_debt_capital" pattern="^\d*(\.\d{0,2})?$"/></td>
                <tr>
            </table>
            <br>
            <input type="submit" value="Generate Price Multiples">
        </form>
        """
            + "Industry Selection: "
            + selection_industry_type
            + "<br>"
            + "The estimated P/E ratio is <br>"
            + "The estimated P/BV ratio is <br>"
    )


@app.route("/<int:celsius>")
def fahrenheit_from(celsius):
    """Convert Celsius to Fahrenheit degrees."""
    try:
        fahrenheit = float(celsius) * 9 / 5 + 32
        fahrenheit = round(fahrenheit, 3)
        return str(fahrenheit)
    except ValueError:
        return "Invalid input"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
