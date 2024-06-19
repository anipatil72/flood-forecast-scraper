from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/scrape', methods=['GET'])
def scrape_data():
    url = "https://aff.india-water.gov.in/table.php"
    location_name = request.args.get('location', 'GUWAHATI(D.C.COURT)').upper()

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html_content = response.content
    except (requests.RequestException, requests.Timeout) as e:
        return jsonify({'error': 'Failed to fetch data', 'details': str(e)}), 500

    soup = BeautifulSoup(html_content, 'html.parser')
    table_rows = soup.select('table#Flood1 tr')

    forecast_data = []
    for row in table_rows[1:]:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue
        site_name = cells[1].text.strip().upper()
        
        if site_name == location_name:
            for i in range(6, len(cells), 3):
                if i+2 < len(cells):
                    date_time = cells[i].text.strip()
                    flood_condition = cells[i+1].text.strip()
                    max_wl = cells[i+2].text.strip()
                    date, time = (date_time.split(" ") + [""])[:2]
                    forecast_data.append({
                        'date': date,
                        'time': time,
                        'flood_condition': flood_condition,
                        'max_wl': max_wl
                    })

            return jsonify({
                'location_name': location_name,
                'forecast_data': forecast_data
            })

    return jsonify({'error': 'Location not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
