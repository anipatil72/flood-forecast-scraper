# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import requests
# from bs4 import BeautifulSoup

# app = Flask(__name__)
# CORS(app)

# @app.route('/scrape', methods=['GET'])
# def scrape_data():
#     url = "https://aff.india-water.gov.in/table.php"
#     location_name = request.args.get('location', 'GUWAHATI(D.C.COURT)').upper()

#     try:
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()
#         html_content = response.content
#     except (requests.RequestException, requests.Timeout) as e:
#         return jsonify({'error': 'Failed to fetch data', 'details': str(e)}), 500

#     soup = BeautifulSoup(html_content, 'html.parser')
#     table_rows = soup.select('table#Flood1 tr')

#     forecast_data = []
#     for row in table_rows[1:]:
#         cells = row.find_all('td')
#         if len(cells) < 2:
#             continue
#         site_name = cells[1].text.strip().upper()
        
#         if site_name == location_name:
#             for i in range(6, len(cells), 3):
#                 if i+2 < len(cells):
#                     date_time = cells[i].text.strip()
#                     flood_condition = cells[i+1].text.strip()
#                     max_wl = cells[i+2].text.strip()
#                     date, time = (date_time.split(" ") + [""])[:2]
#                     forecast_data.append({
#                         'date': date,
#                         'time': time,
#                         'flood_condition': flood_condition,
#                         'max_wl': max_wl
#                     })

#             return jsonify({
#                 'location_name': location_name,
#                 'forecast_data': forecast_data
#             })

#     return jsonify({'error': 'Location not found'}), 404

# if __name__ == '__main__':
#     app.run(debug=True)

# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import requests
# from bs4 import BeautifulSoup

# app = Flask(__name__)
# CORS(app)

# @app.route('/scrape', methods=['GET'])
# def scrape_data():
#     url = "https://aff.india-water.gov.in/table.php"
#     location_name = request.args.get('location', 'GUWAHATI(D.C.COURT)').upper()

#     try:
#         response = requests.get(url, timeout=10)
#         response.raise_for_status()
#         html_content = response.content
#     except (requests.RequestException, requests.Timeout) as e:
#         return jsonify({'error': 'Failed to fetch data', 'details': str(e)}), 500

#     soup = BeautifulSoup(html_content, 'html.parser')
#     table_rows = soup.select('table#Flood1 tr')

#     forecast_data = []
#     district = None
#     for row in table_rows[1:]:
#         cells = row.find_all('td')
#         if len(cells) < 2:
#             continue
#         site_name = cells[1].text.strip().upper()
#         district_name = cells[3].text.strip().upper()

#         if site_name == location_name:
#             district = district_name
#             for i in range(6, len(cells), 3):
#                 if i+2 < len(cells):
#                     date_time = cells[i].text.strip()
#                     flood_condition = cells[i+1].text.strip()
#                     max_wl = cells[i+2].text.strip()
#                     date, time = (date_time.split(" ") + [""])[:2]
#                     forecast_data.append({
#                         'date': date,
#                         'time': time,
#                         'flood_condition': flood_condition,
#                         'max_wl': max_wl
#                     })

#             return jsonify({
#                 'location_name': location_name,
#                 'district': district,
#                 'forecast_data': forecast_data
#             })

#     return jsonify({'error': 'Location not found'}), 404

# if __name__ == '__main__':
#     app.run(debug=True)



from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

LOGIN_URL = "https://aff.india-water.gov.in/index.php"
DATA_URL = "https://aff.india-water.gov.in/table.php"
USERNAME = "your_username"
PASSWORD = "your_password"

@app.route('/scrape', methods=['GET'])
def scrape_data():
    location_name = request.args.get('location', 'GUWAHATI(D.C.COURT)').upper()

    session = requests.Session()
    
    try:
        login_payload = {
            'username': USERNAME,
            'password': PASSWORD,
            'login_user': 'Login'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
            'Referer': LOGIN_URL,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://aff.india-water.gov.in',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        login_response = session.post(LOGIN_URL, data=login_payload, headers=headers, timeout=10, allow_redirects=True)
        login_response.raise_for_status()
        
        # Check if login was successful by checking if we're on the home page
        if "/home.php" not in login_response.url:
            return jsonify({'error': 'Login failed'}), 500
    except (requests.RequestException, requests.Timeout) as e:
        return jsonify({'error': 'Failed to log in', 'details': str(e)}), 500

    try:
        table_response = session.get(DATA_URL, headers=headers, timeout=10)
        table_response.raise_for_status()
        
        # Check if we successfully loaded the table page
        if "Flood Forecast" not in table_response.text:
            return jsonify({'error': 'Failed to access data page'}), 500
        
        html_content = table_response.content
    except (requests.RequestException, requests.Timeout) as e:
        return jsonify({'error': 'Failed to fetch data', 'details': str(e)}), 500

    soup = BeautifulSoup(html_content, 'html.parser')
    table_rows = soup.select('table#Flood1 tr')

    forecast_data = []
    district = None
    for row in table_rows[1:]:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue
        site_name = cells[1].text.strip().upper()
        district_name = cells[3].text.strip().upper()

        if site_name == location_name:
            district = district_name
            for i in range(6, len(cells), 3):
                if i + 2 < len(cells):
                    date_time = cells[i].text.strip()
                    flood_condition = cells[i + 1].text.strip()
                    max_wl = cells[i + 2].text.strip()
                    date, time = (date_time.split(" ") + [""])[:2]
                    forecast_data.append({
                        'date': date,
                        'time': time,
                        'flood_condition': flood_condition,
                        'max_wl': max_wl
                    })

            return jsonify({
                'location_name': location_name,
                'district': district,
                'forecast_data': forecast_data
            })

    return jsonify({'error': 'Location not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)