


   

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

 

    return jsonify({
        "optimized_allocation": dict(zip(symbols_list, np.round(optimized_weights, 3).tolist())),
        "expected_return": round(port_return, 4),
        "expected_volatility": round(port_vol, 4)
    })

if __name__ == '__main__':
    app.run(debug=True)
