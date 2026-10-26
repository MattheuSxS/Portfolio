import requests

class MapOfBrazil:
    def __init__(self):
        self.state_names = {
            'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
            'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
            'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
            'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
            'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
            'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
            'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
        }

    def _get_fallback_geojson(self):
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "SP",
                    "properties": {"name": "São Paulo"},
                    "geometry": {"type": "Polygon", "coordinates": [[[]]]}
                },
                # Adicione outros estados conforme necessário
            ]
        }

    def get_brazil_geojson(self):
        geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        try:
            response = requests.get(geojson_url)
            return response.json()
        except:
            return self._get_fallback_geojson()