# portfolio_optimizer
Designed and developed a web-based portfolio optimization tool using Python and Flask. The application retrieves historical stock data using the Yahoo Finance API, calculates key financial metrics (expected return, volatility, Sharpe ratio), and optimizes portfolio allocation based on Modern Portfolio Theory. 



🚀 Features

Fetches stock historical prices using Yahoo Finance API (yfinance)

Computes:

Expected Returns

Portfolio Volatility

Covariance Matrix

Sharpe Ratio

Optimizes portfolio allocation based on Modern Portfolio Theory (MPT)

Flask-based UI – enter tickers + capital + risk preference

Result table + recommended weights

🛠️ Tech Stack
Component	Technology
Backend	Python, Flask
Data Source	Yahoo Finance API (yfinance)
Optimization	Numpy / Pandas / MPT
Frontend	HTML + CSS
📂 Project Structure
project_folder/
│
├── app.py
├── templates/
│   └── index.html
└── static/
    └── styles.css

🧰 Installation & Setup
git clone https://github.com/yourusername/portfolio-optimizer.git
cd portfolio-optimizer

pip install -r requirements.txt

python app.py


Open your browser → http://127.0.0.1:5000/

📊 Example Input
Stocks: AAPL, GOOGL, AMZN
Capital: $10000
Risk Level: Medium

📥 Dependencies
Flask
pandas
numpy
yfinance

📡 Data Flow

User inputs stock tickers and capital

App downloads OHLC data (Yahoo Finance)

Compute metrics (mean return, variance, Sharpe ratio)

Run optimization (maximize Sharpe / Minimize variance)

Return final weights & performance summary

🚧 Future Improvements

Add Efficient Frontier Plot

Support Crypto Assets

Add correlation heatmap

Add multiple optimization modes (Min Variance / Max Sharpe / Risk-parity)

📜 License

MIT License

⭐ Contribute

Pull Requests welcome!
If you like this project, give it a star ⭐ on GitHub!
