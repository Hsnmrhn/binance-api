from flask import Flask, render_template_string
import pandas as pd
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Kripto Fiyat Takibi</title>
    <meta http-equiv="refresh" content="300">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .price-up { color: green; }
        .price-down { color: red; }
        table { border-collapse: collapse; width: 100%; }
        th, td { padding: 12px; text-align: left; border: 1px solid #ddd; }
        th { background-color: #f4f4f4; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:hover { background-color: #f5f5f5; }
    </style>
</head>
<body>
    <h1>BTC/USDT Fiyat Takibi</h1>
    <table>
        <tr><th>Zaman</th><th>Fiyat</th><th>Değişim</th></tr>
        {% for row in data %}
        <tr>
            <td>{{ row.timestamp }}</td>
            <td>{{ "%.2f"|format(row.price) }}</td>
            <td class="{{ row.change_class }}">
                {{ row.change_symbol }} {{ "%.2f"|format(row.pct_change) }}%
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route('/')
def home():
    if os.path.exists('/data/prices.csv'):
        df = pd.read_csv('/data/prices.csv')
        df['pct_change'] = df['price'].pct_change() * 100
        df['change_symbol'] = df['pct_change'].apply(
            lambda x: '↑' if x > 0 else '↓' if x < 0 else '-'
        )
        df['change_class'] = df['pct_change'].apply(
            lambda x: 'price-up' if x > 0 else 'price-down' if x < 0 else ''
        )
        
        data = df.tail(20).to_dict('records')
        return render_template_string(HTML_TEMPLATE, data=data)
    return "Henüz veri yok..."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)