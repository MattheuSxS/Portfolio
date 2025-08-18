import random
from faker import Faker


class FakeDataAddress:
    """
    FakeDataAddress generates random Brazilian address data, including coordinates near state capitals.

    Attributes:
        fake (Faker): An instance of the Faker library for generating fake address data.
        capitais_coords (dict): Dictionary mapping Brazilian state abbreviations to their capital city names and coordinates.

    Args:
        country (str, optional): Locale code for Faker. Defaults to 'pt_BR'.

    Methods:
        get_random_address():
            Generates a random address dictionary with the following fields:
                - 'Rua': address name and building number.
                - 'Bairro': Neighborhood name.
                - 'city': Capital city name.
                - 'Estado': State abbreviation.
                - 'CEP': Postal code.
                - 'Latitude': Latitude near the capital city.
                - 'Longitude': Longitude near the capital city.
            Returns:
                dict: Randomly generated address data.
    """
    def __init__(self, country:str = 'pt_BR'):
        self.fake = Faker(country)
        # self.fake.seed_instance(0)
        self.capitais_coords = \
            {
                'AC': {'city': 'Rio Branco',      'lat': -9.9749,     'lon': -67.8243, 'region': 'Norte'},
                'AL': {'city': 'Maceió',          'lat': -9.6658,     'lon': -35.7353, 'region': 'Nordeste'},
                'AP': {'city': 'Macapá',          'lat': 0.0349,      'lon': -51.0694, 'region': 'Norte'},
                'AM': {'city': 'Manaus',          'lat': -3.1189,     'lon': -60.0217, 'region': 'Norte'},
                'BA': {'city': 'Salvador',        'lat': -12.9777,    'lon': -38.5016, 'region': 'Nordeste'},
                'CE': {'city': 'Fortaleza',       'lat': -3.7327,     'lon': -38.5267, 'region': 'Nordeste'},
                'DF': {'city': 'Brasília',        'lat': -15.7942,    'lon': -47.8825, 'region': 'Centro-Oeste'},
                'ES': {'city': 'Vitória',         'lat': -20.3155,    'lon': -40.3378, 'region': 'Sudeste'},
                'GO': {'city': 'Goiânia',         'lat': -16.6869,    'lon': -49.2648, 'region': 'Centro-Oeste'},
                'MA': {'city': 'São Luís',        'lat': -2.5307,     'lon': -44.3068, 'region': 'Nordeste'},
                'MT': {'city': 'Cuiabá',          'lat': -15.6014,    'lon': -56.0977, 'region': 'Centro-Oeste'},
                'MS': {'city': 'Campo Grande',    'lat': -20.4697,    'lon': -54.6201, 'region': 'Centro-Oeste'},
                'MG': {'city': 'Belo Horizonte',  'lat': -19.9167,    'lon': -43.9345, 'region': 'Sudeste'},
                'PA': {'city': 'Belém',           'lat': -1.4558,     'lon': -48.5044, 'region': 'Norte'},
                'PB': {'city': 'João Pessoa',     'lat': -7.1219,     'lon': -34.8816, 'region': 'Nordeste'},
                'PR': {'city': 'Curitiba',        'lat': -25.4284,    'lon': -49.2733, 'region': 'Sul'},
                'PE': {'city': 'Recife',          'lat': -8.0476,     'lon': -34.8770, 'region': 'Nordeste'},
                'PI': {'city': 'Teresina',        'lat': -5.0919,     'lon': -42.8034, 'region': 'Nordeste'},
                'RJ': {'city': 'Rio de Janeiro',  'lat': -22.9068,    'lon': -43.1729, 'region': 'Sudeste'},
                'RN': {'city': 'Natal',           'lat': -5.7945,     'lon': -35.2110, 'region': 'Nordeste'},
                'RS': {'city': 'Porto Alegre',    'lat': -30.0346,    'lon': -51.2177, 'region': 'Sul'},
                'RO': {'city': 'Porto Velho',     'lat': -8.7619,     'lon': -63.9039, 'region': 'Norte'},
                'RR': {'city': 'Boa Vista',       'lat': 2.8235,      'lon': -60.6758, 'region': 'Norte'},
                'SC': {'city': 'Florianópolis',   'lat': -27.5954,    'lon': -48.5480, 'region': 'Sul'},
                'SP': {'city': 'São Paulo',       'lat': -23.5505,    'lon': -46.6333, 'region': 'Sudeste'},
                'SE': {'city': 'Aracaju',         'lat': -10.9472,    'lon': -37.0731, 'region': 'Nordeste'},
                'TO': {'city': 'Palmas',          'lat': -10.2128,    'lon': -48.3603, 'region': 'Norte'}
         }

    def get_random_address(self):

        select_uf = random.choice(list(self.capitais_coords.keys()))

        capital_info = self.capitais_coords[select_uf]
        city = capital_info['city']
        lat_base = capital_info['lat']
        lon_base = capital_info['lon']

        lat = lat_base + random.uniform(-0.05, 0.05)
        lon = lon_base + random.uniform(-0.05, 0.05)

        endereco = {
            'address_id':       f"ADDR##{self.fake.unique.uuid4()}",
            'address':          f'{self.fake.street_name()} {self.fake.building_number()}',
            'neighborhood':     self.fake.bairro(),
            'city':             city,
            'state':            select_uf,
            'postal_code':      self.fake.postcode(),
            'region':           capital_info['region'],
            'latitude':         f'{lat:.6f}',
            'longitude':        f'{lon:.6f}',
            'created_at':       None,
            'updated_at':       None,
            'deleted_at':       None,
            'fk_associate_id':  None
        }

        return endereco

if __name__ == "__main__":
    print("Gerando 5 endereços aleatórios e coerentes no Brasil:\n")

    for i in range(5):
        fk = FakeDataAddress()
        print(f"--- Endereço {i+1} ---")
        for chave, valor in fk.get_random_address().items():
            print(f"{chave}: {valor}")
        print("-" * 20 + "\n")
