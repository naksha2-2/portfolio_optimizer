from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

# Get your free API key from https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY = "MSBAQE9P30PPZE6Y"  # Replace with your actual key

def get_stock_price_alpha_vantage(symbol):
    """Get stock price using Alpha Vantage API"""
    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # Check if we got valid data
        if "Global Quote" in data and data["Global Quote"]:
            price = float(data["Global Quote"]["05. price"])
            return price
        else:
            print(f"Invalid data for {symbol}: {data}")
            return None
            
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    portfolio = None
    error = None

    if request.method == "POST":
        try:
            # 1. Get user inputs
            stocks_input = request.form.get("stocks", "").strip()
            capital_input = request.form.get("capital", "").strip()
            risk_input = request.form.get("risk", "").strip()

            if not stocks_input:
                raise ValueError("Please enter stock tickers")
            if not capital_input:
                raise ValueError("Please enter investment capital")

            stocks = [s.strip().upper() for s in stocks_input.split(",") if s.strip()]
            capital = float(capital_input)
            risk = risk_input or "medium"

            if capital <= 0:
                raise ValueError("Capital must be greater than 0")
            if not stocks:
                raise ValueError("No valid stock tickers provided")

            # 2. Get stock prices using Alpha Vantage
            prices = {}
            failed_stocks = []
            
            for stock in stocks:
                price = get_stock_price_alpha_vantage(stock)
                if price is not None:
                    prices[stock] = price
                    print(f"{stock}: ${price}")
                else:
                    failed_stocks.append(stock)

            # Remove any stocks without prices
            valid_stocks = [s for s in stocks if s in prices]
            if not valid_stocks:
                error_msg = "No valid stock prices found. Check tickers!"
                if failed_stocks:
                    error_msg += f" Failed: {', '.join(failed_stocks)}"
                raise ValueError(error_msg)

            # 3. Decide allocation weights based on risk
            n = len(valid_stocks)

            if risk == "low":
                if n == 1:
                    weights = [1.0]
                else:
                    weights = [0.6] + [0.4/(n-1)]*(n-1)
            elif risk == "medium":
                weights = [1/n] * n
            elif risk == "high":
                if n == 1:
                    weights = [1.0]
                else:
                    weights = [0.4/(n-1)]*(n-1) + [0.6]
            else:
                weights = [1/n] * n  # Default to equal weighting

            # 4. Calculate shares + leftover
            portfolio = {}
            total_invested = 0
            
            for i, stock in enumerate(valid_stocks):
                allocation = capital * weights[i]
                shares = int(allocation // prices[stock])
                invested = shares * prices[stock]
                portfolio[stock] = {
                    "shares": shares,
                    "price": round(prices[stock], 2),
                    "value": round(invested, 2)  # Using 'value' to match your HTML
                }
                total_invested += invested

            leftover = capital - total_invested
            portfolio["leftover_cash"] = round(leftover, 2)

        except ValueError as e:
            error = str(e)
        except Exception as e:
            error = f"An unexpected error occurred: {str(e)}"

    return render_template("index.html", portfolio=portfolio, error=error)

if __name__ == "__main__":
    app.run(debug=True)