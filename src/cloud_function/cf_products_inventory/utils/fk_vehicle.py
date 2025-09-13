import random
from faker import Faker
from typing import List, Dict
from datetime import timedelta
from faker_vehicle import VehicleProvider

try:
    from utils.fk_dates import GeneratorDate
except ImportError:
    from fk_dates import GeneratorDate


class GeneratorDeliveryVehicle(GeneratorDate):
    """
        GeneratorDeliveryVehicle is a class for generating realistic, randomized delivery vehicle data
        for use in inventory systems, testing, or simulations.

        Attributes:
            VEHICLE_TYPES (dict): Dictionary defining supported vehicle types and their specifications,
            including brands, models, capacity, and fuel efficiency.
            STATUS (list): List of possible vehicle statuses (e.g., 'available', 'in_route', etc.).
            faker (Faker): Instance of the Faker library for generating fake data.

        Methods:
            __init__(country: str = 'pt_BR'):
                Initializes the generator with a specified locale for data generation.

            generate_board(type: str) -> str:
                Generates a license plate string based on the vehicle type.

            generate_vehicle() -> Dict:
                Generates a dictionary representing a single vehicle with randomized attributes, including insurance
                and optional driver information.

            generate_fleet(quantity: int) -> List[Dict]:
                Generates a list of vehicle dictionaries representing a fleet of the specified size.
    """

    def __init__(self, country: str = 'pt_BR'):
        super().__init__(country)
        self.faker = Faker(country)
        self.faker.add_provider(VehicleProvider)

        self.VEHICLE_TYPES = {
            'motorcycle': {
                'brand': ['Honda', 'Yamaha', 'Suzuki', 'Kawasaki'],
                'model': ['CG 160', 'Factor 125', 'Biz 125', 'Ninja 300'],
                'capacity_kg': (5, 30),
                'fuel_efficiency_km_l': (30, 40),
                'average_speed_km_h': (80, 110)
            },
            'van': {
                'brand': ['Fiat', 'Volkswagen', 'Renault', 'Mercedes-Benz'],
                'model': ['Fiorino', 'Saveiro', 'Kangoo', 'Sprinter'],
                'capacity_kg': (200, 800),
                'fuel_efficiency_km_l': (15, 25),
                'average_speed_km_h': (80, 100)
            },
            'truck': {
                'brand': ['Volvo', 'Scania', 'MAN', 'Mercedes-Benz'],
                'model': ['FH 540', 'R 450', 'TGX 440', 'Actros 2651'],
                'capacity_kg': (5000, 15000),
                'fuel_efficiency_km_l': (10, 20),
                'average_speed_km_h': (70, 80)
            }
        }

        self.STATUS = ['available', 'in_route', 'under_maintenance', 'deactivated']
        self.STATUS_PROBABILITIES = [0.80, 0.10, 0.07, 0.03]


    def generate_board(self, type: str) -> str:
        """
            Generates a vehicle board (license plate) string based on the specified type.

            Args:
                type (str): The type of vehicle. If 'motorcycle', generates a custom plate format.
                            For other types, generates a standard license plate.

            Returns:
                str: The generated license plate string.
        """
        match type:
            case 'motorcycle':
                return f"{random.choice(['JKL', 'MNO', 'PQR'])}{random.randint(1000, 9999)}"
            case _:
                return self.faker.license_plate()

    def generate_vehicle(self) -> Dict:
        """
            Generates a dictionary representing a vehicle with randomized attributes.

            Returns:
                Dict: A dictionary containing vehicle information, including:
                    - vehicle_id (str): Unique identifier for the vehicle.
                    - location (str): Warehouse location code.
                    - type (str): Type of the vehicle.
                    - brand (str): Vehicle brand.
                    - model (str): Vehicle model.
                    - year (int): Year of manufacture.
                    - license_plate (str): Generated license plate.
                    - capacity_kg (int): Vehicle load capacity in kilograms.
                    - average_speed_km_h (float): Average speed in km/h.
                    - fuel_efficiency_km_l (float): Fuel efficiency in km/l.
                    - status (str): Current status of the vehicle.
                    - manufacture_date (str): Manufacture date in 'YYYY-MM-DD' format.
                    - last_maintenance (str): Last maintenance date in 'YYYY-MM-DD' format.
                    - next_maintenance (str): Next scheduled maintenance date in 'YYYY-MM-DD' format.
                    - tracker (bool): Whether the vehicle has a tracker installed.
                    - insurance (dict): Insurance details with keys:
                        - insurer (str): Name of the insurance company.
                        - policy_number (str): Insurance policy number.
                        - validity (str): Insurance validity date in 'YYYY-MM-DD' format.
                    - driver (dict or None): Driver details if assigned, with keys:
                        - name (str): Driver's name.
                        - cnh (int): Driver's license number.
                        - cnh_validity (str): License validity date in 'YYYY-MM-DD' format.
                    If no driver is assigned, this field is None.
        """
        _type = random.choice(list(self.VEHICLE_TYPES.keys()))
        specs = self.VEHICLE_TYPES[_type]

        #TODO: I must implement the date generation for the last maintenance
        manufacturing_data = self.faker.date_between(start_date='-5y', end_date='today')
        last_maintenance = self.faker.date_between(
            start_date=manufacturing_data,
            end_date='today'
        )

        LOCATION = [
            "WH_Lambertstad_SP",
            "WH_Lambertstad_SC",
            "WH_Lake_Michelle_DF",
            "WH_New_Kristen_BA",
            "WH_North_Allison_AM"
        ]

        return {
            'vehicle_id': f"VE##{self.faker.uuid4()}",
            'location': random.choice(LOCATION),
            'type': _type,
            'brand': random.choice(specs['brand']),
            'model': random.choice(specs['model']),
            'year': manufacturing_data.year,
            'license_plate': self.generate_board(_type),
            'capacity_kg': random.randint(*specs['capacity_kg']),
            'average_speed_km_h': round(random.uniform(*specs['average_speed_km_h']), 2),
            'fuel_efficiency_km_l': round(random.uniform(*specs['fuel_efficiency_km_l']), 2),
            'status': random.choices(self.STATUS, weights=self.STATUS_PROBABILITIES, k=1)[0],
            'manufacture_date': manufacturing_data.strftime('%Y-%m-%d'),
            'last_maintenance': last_maintenance.strftime('%Y-%m-%d'),
            'next_maintenance': (last_maintenance + timedelta(days=180)).strftime('%Y-%m-%d'),
            'tracker': self.faker.boolean(chance_of_getting_true=80),
            'insurance': {
                'insurer': self.faker.company(),
                'policy_number': self.faker.ean(length=13),
                'validity': self.generate_date(start_date='now', end_date='+2y')
            },
            'driver': {
                'name': self.faker.name(),
                'cnh': self.faker.random_number(digits=11, fix_len=True),
                'cnh_validity': self.generate_date(start_date='now', end_date='+5y')
            } if random.random() > 0.15 else None,  # 15% de chance de não ter motorista atribuído
            'created_at': self.generate_date(start_date='-120d', end_date='now', option='datetime'),
            'updated_at': None,

        }


    def generate_fleet(self, quantity: int) -> List[Dict]:
        """
            Generates a list of vehicle dictionaries representing a fleet.

            Args:
                quantity (int): The number of vehicles to generate.

            Returns:
                List[Dict]: A list of dictionaries, each representing a generated vehicle.
        """
        return [self.generate_vehicle() for _ in range(quantity)]



if __name__ == "__main__":
    generator = GeneratorDeliveryVehicle()

    # Gerar 10 veículos de entrega
    frota = generator.generate_fleet(10)

    # Exibir os dados gerados
    for i, veiculo in enumerate(frota, 1):
        print(f"\n🚚 Veículo #{i}:")
        for key, value in veiculo.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for subkey, subvalue in value.items():
                    print(f"    {subkey}: {subvalue}")
            else:
                print(f"  {key}: {value}")