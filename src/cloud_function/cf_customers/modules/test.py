import requests
import random
import time

def obter_endereco_com_cep():
    # Coordenadas aproximadas do território brasileiro
    lat = random.uniform(-33.7, 5.3)  # Latitude Brasil
    lon = random.uniform(-73.9, -34.8)  # Longitude Brasil

    # Construir URL da API Nominatim
    url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}&addressdetails=1"

    try:
        # Fazer requisição com headers adequados (Nominatim requer User-Agent)
        headers = {
            "User-Agent": "MyAddressGenerator/1.0 (seu@email.com)"
        }
        response = requests.get(url, headers=headers)

        # Verificar resposta
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})

            # Construir endereço completo
            endereco = {
                "rua": address.get("road", ""),
                "numero": address.get("house_number", ""),
                "bairro": address.get("suburb") or address.get("neighbourhood", ""),
                "cidade": address.get("city") or address.get("town") or address.get("village", ""),
                "estado": address.get("state", ""),
                "cep": address.get("postcode", ""),
                "pais": address.get("country", ""),
                "geolocalizacao": (lat, lon),
                "endereco_completo": data.get("display_name", "")
            }

            # Verificar se temos dados mínimos válidos
            if endereco["cidade"] and endereco["estado"]:
                return endereco
            return None

        # Tratar limite de requisições
        elif response.status_code == 429:
            print("Muitas requisições. Esperando 1 segundo...")
            time.sleep(1)
            return obter_endereco_com_cep()

    except Exception as e:
        print(f"Erro na requisição: {e}")
        return None

# Exemplo de uso
if __name__ == "__main__":
    endereco = obter_endereco_com_cep()
    while not endereco:  # Tentar até conseguir um endereço válido
        endereco = obter_endereco_com_cep()

    print("Endereço completo com CEP:")
    for chave, valor in endereco.items():
        print(f"{chave}: {valor}")