from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/scrape', methods=['GET'])
def scrape_data():
    # URL of the website
    url = "https://aff.india-water.gov.in/table.php"

    # Get the location name from query parameters
    location_name = request.args.get('location', 'GUWAHATI(D.C.COURT)').upper()

    # Send a request to the website and get the HTML content
    response = requests.get(url)
    html_content = response.content

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table rows
    table_rows = soup.select('table#Flood1 tr')

    # Iterate over the rows
    forecast_data = []
    for row in table_rows[1:]:  # Skip the header row
        cells = row.find_all('td')
        if len(cells) < 2:
            continue
        site_name = cells[1].text.strip().upper()
        
        if site_name == location_name:
            # Extract forecast data for the desired location
            for i in range(6, len(cells), 3):
                if i+2 < len(cells):
                    date_time = cells[i].text.strip()
                    flood_condition = cells[i+1].text.strip()
                    max_wl = cells[i+2].text.strip()

                    # Separate date and time if possible
                    date, time = (date_time.split(" ") + [""])[:2]
                    
                    forecast_data.append({
                        'date': date,
                        'time': time,
                        'flood_condition': flood_condition,
                        'max_wl': max_wl
                    })
            
            # Return the forecast data
            return jsonify({
                'location_name': location_name,
                'forecast_data': forecast_data
            })

    # If location not found, return an empty response
    return jsonify({})

if __name__ == '__main__':
    app.run(debug=True)
