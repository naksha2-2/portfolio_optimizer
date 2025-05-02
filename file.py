from flask import Flask, jsonify, request
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Financial Portfolio Optimizer API!"

@app.route('/optimize', methods=['GET'])
def optimize_portfolio():
    symbols = request.args.get('symbols')
    if not symbols:
        return jsonify({"error": "Please provide stock symbols!"}), 400

    symbols_list = symbols.split(',')

    try:
        raw_data = yf.download(symbols_list, period="1y", group_by='ticker', auto_adjust=True)

        # Handle single vs multiple symbol case
        if len(symbols_list) > 1:
            close_prices = pd.DataFrame({
                symbol: raw_data[symbol]['Close']
                for symbol in symbols_list if 'Close' in raw_data[symbol]
            })
        else:
            close_prices = raw_data[['Close']]
            close_prices.columns = [symbols_list[0]]
    except Exception as e:
        return jsonify({"error": f"Data retrieval failed: {str(e)}"}), 500

    df = close_prices.dropna()
    if df.empty:
        return jsonify({"error": "No valid stock data found!"}), 400

    # Calculate returns
    returns = df.pct_change().dropna()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    num_assets = len(symbols_list)

    def portfolio_performance(weights):
        port_return = np.dot(weights, mean_returns)
        port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return port_return, port_vol

    # Get optimization type and weight bounds
    objective = request.args.get('objective', 'max_sharpe')
    min_weight = float(request.args.get('min_weight', 0))
    max_weight = float(request.args.get('max_weight', 1))
    print(f"min_weight: {min_weight}, max_weight: {max_weight}")
    bounds = tuple((min_weight, max_weight) for _ in range(num_assets))
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    init_guess = num_assets * [1. / num_assets]

    # Define objective function
    def objective_fn(weights):
        port_return, port_vol = portfolio_performance(weights)
        if objective == 'min_volatility':
            return port_vol
        elif objective == 'max_return':
            return -port_return
        else:  # max_sharpe
            return - (port_return - 0.01) / port_vol  # Sharpe Ratio

    try:
        result = minimize(objective_fn, init_guess, bounds=bounds, constraints=constraints)
        if not result.success:
            raise Exception("Optimization did not converge")
    except Exception as e:
        return jsonify({"error": f"Optimization failed: {str(e)}"}), 500

    optimized_weights = result.x
    port_return, port_vol = portfolio_performance(optimized_weights)

    return jsonify({
        "optimized_allocation": dict(zip(symbols_list, np.round(optimized_weights, 3).tolist())),
        "expected_return": round(port_return, 4),
        "expected_volatility": round(port_vol, 4)
    })



@app.route('/summary', methods=['GET'])
def portfolio_summary():
    symbols = request.args.get('symbols')
    if not symbols:
        return jsonify({"error": "Please provide stock symbols!"}), 400

    symbols_list = symbols.split(',')

    try:
        data = yf.download(symbols_list, period="1y")['Close']
        data = data.dropna()
    except Exception as e:
        return jsonify({"error": f"Data fetch failed: {str(e)}"}), 500

    if data.empty:
        return jsonify({"error": "No data found for given symbols"}), 400

    returns = data.pct_change().dropna()
    cumulative = (1 + returns).prod() - 1
    std_devs = returns.std()

    return jsonify({
        "cumulative_return": cumulative.round(4).to_dict(),
        "standard_deviation": std_devs.round(4).to_dict()
    })


if __name__ == '__main__':
    app.run(debug=True)

