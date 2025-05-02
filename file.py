


    if not symbols:
        return jsonify({"error": "Please provide stock symbols!"}), 400

    symbols_list = symbols.split(',')
    data = {}

    for symbol in symbols_list:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1y")
        data[symbol] = hist['Close'].tolist()

    return jsonify(data)

@app.route('/optimize', methods=['GET'])
def optimize_portfolio():
    symbols = request.args.get('symbols')  # e.g., ?symbols=AAPL,MSFT,GOOGL
    if not symbols:
        return jsonify({"error": "Please provide stock symbols!"}), 400

    symbols_list = symbols.split(',')

    # Download data and handle single vs multiple symbol structures
    raw_data = yf.download(symbols_list, period="1y", group_by='ticker', auto_adjust=True)

    if len(symbols_list) > 1:
        try:
            close_prices = pd.DataFrame({
                symbol: raw_data[symbol]['Close']
                for symbol in symbols_list
                if 'Close' in raw_data[symbol]
            })
        except KeyError:
            return jsonify({"error": "Adjusted Close data not found!"}), 500
    else:
        try:
            close_prices = raw_data[['Close']]
            close_prices.columns = [symbols_list[0]]
        except KeyError:
            return jsonify({"error": "Adjusted Close data not found!"}), 500

    df = close_prices.dropna()

    # Calculate daily returns
    returns = df.pct_change().dropna()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    num_assets = len(symbols_list)

    def portfolio_performance(weights):
        port_return = np.dot(weights, mean_returns)
        port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return port_return, port_vol

    def neg_sharpe_ratio(weights):
        p_return, p_vol = portfolio_performance(weights)
        return - (p_return - 0.01) / p_vol  # Assuming 1% risk-free rate

    # Constraints: weights must sum to 1
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    init_guess = num_assets * [1. / num_assets]

    result = minimize(neg_sharpe_ratio, init_guess, bounds=bounds, constraints=constraints)

    if not result.success:
        return jsonify({"error": "Optimization failed!"}), 500

    optimized_weights = result.x
    port_return, port_vol = portfolio_performance(optimized_weights)

    return jsonify({
        "optimized_allocation": dict(zip(symbols_list, np.round(optimized_weights, 3).tolist())),
        "expected_return": round(port_return, 4),
        "expected_volatility": round(port_vol, 4)
    })

if __name__ == '__main__':
    app.run(debug=True)
