import os
from modules.fake_products import FakeCommerceData


def main(request: dict) -> dict:
    """
    Entry point function for the Cloud Function to generate fake product data.

    Args:
        request (dict): The request payload.

    Returns:
        dict: The response payload.
    """

    if type(request) != dict:
        dt_request = request.get_json()
    else:
        dt_request = request

    # Initialize the FakeProductData class
    fake_data_generator = FakeCommerceData()

    # Generate the complete dataset
    dataset = fake_data_generator.generate_complete_dataset()

    return {
        "status": "success",
        "message": "Fake product data generated successfully.",
        "data": dataset
    }

if __name__ == "__main__":
    print("Generating fake product data...")
    print(main({}))