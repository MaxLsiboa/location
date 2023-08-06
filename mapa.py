from flask import Flask, jsonify, render_template
import os
import requests
import socket

app = Flask(__name__)
azure_maps_key = 'ogO3LN0D67EJ9Xf783lDZ82GcPQDgA4NXWM3MUBHI18'

# Função para obter o endereço IP do usuário
def get_user_ip():
    try:
        # Cria um socket e conecta a um serviço externo para obter o endereço IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        user_ip = s.getsockname()[0]
        s.close()
        return user_ip
    except:
        return None

# Função para obter a localização do usuário com base no endereço IP
def get_user_location():
    user_ip = get_user_ip()
    if user_ip:
        url = f'https://atlas.microsoft.com/geolocation/ip/json?api-version=1.0&ip={user_ip}&subscription-key={azure_maps_key}'
        response = requests.get(url)
        data = response.json()
        if 'lat' in data and 'lon' in data:
            return data
    return None

# Função para obter dados de tráfego em tempo real do Azure Maps
def get_traffic_data(latitude, longitude):
    url = f'https://atlas.microsoft.com/traffic/flow/segment/json?api-version=1.0&subscription-key={azure_maps_key}&format=json&query={latitude},{longitude}'
    response = requests.get(url)
    data = response.json()
    # Processar a resposta e extrair os dados relevantes
    # Retornar os dados de tráfego em tempo real como um dicionário
    return {
        "congestion_percent": data['congestionPercentage'],
        "accidents": data['accidents'],
        "construction": data['construction'],
        "travel_time_minutes": data['travelTimeMinutes']
    }

# Rota para renderizar o template "mapa.html"
@app.route('/')
def index():
    user_location = get_user_location()
    if user_location:
        latitude = user_location['lat']
        longitude = user_location['lon']
        traffic_data = get_traffic_data(latitude, longitude)
        return render_template('mapa.html', latitude=latitude, longitude=longitude, traffic_data=traffic_data)
    else:
        return render_template('mapa.html', latitude=None, longitude=None, traffic_data=None)

# Rota para obter os dados de tráfego em tempo real em JSON
@app.route('/get_traffic_data/<latitude>/<longitude>')
def get_traffic_data_route(latitude, longitude):
    data = get_traffic_data(latitude, longitude)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
