# #TODO: I have to finish these tests
# import unittest
# from unittest.mock import patch, MagicMock
# from typing import Dict, List
# from main import generate_fake_data_bulk_cached


# class TestGenerateFakeDataBulkCached(unittest.TestCase):

#     @patch("utils.fk_ids")
#     @patch("utils.fk_addresses")
#     def test_generate_fake_data_bulk_cached_structure(self, MockAddress, MockPerson):
#         # Arrange: set up mock return values
#         mock_person_instance = MagicMock()
#         mock_person_instance.dict_customers.return_value = {"id": "cust_1", "name": "John Doe"}
#         mock_person_instance.dict_card.return_value = {"card_id": "card_1", "number": "4111111111111111"}
#         MockPerson.return_value = mock_person_instance

#         mock_address_instance = MagicMock()
#         mock_address_instance.get_random_address.return_value = {"street": "123 Main St", "city": "Metropolis"}
#         MockAddress.return_value = mock_address_instance

#         num_records = 5

#         # Act
#         results = generate_fake_data_bulk_cached(num_records)

#         # Assert: correct length
#         self.assertIsInstance(results, List)
#         self.assertEqual(len(results), num_records)

#         # Assert: each item has expected structure
#         for item in results:
#             self.assertIsInstance(item, Dict)
#             self.assertIn("customers", item)
#             self.assertIn("cards", item)
#             self.assertIn("address", item)

#             self.assertIsInstance(item["customers"], dict)
#             self.assertIsInstance(item["cards"], dict)
#             self.assertIsInstance(item["address"], dict)

#         # Assert: methods are called expected number of times
#         self.assertEqual(mock_person_instance.dict_customers.call_count, num_records)
#         self.assertEqual(mock_person_instance.dict_card.call_count, num_records)
#         self.assertEqual(mock_address_instance.get_random_address.call_count, num_records)


#     @patch("utils.fk_ids")
#     @patch("utils.fk_addresses")
#     def test_generate_fake_data_bulk_cached_uses_cached_instances(self, MockAddress, MockPerson):
#         # Arrange
#         mock_person_instance = MagicMock()
#         mock_person_instance.dict_customers.return_value = {"id": "cust_x"}
#         mock_person_instance.dict_card.return_value = {"card_id": "card_x"}
#         MockPerson.return_value = mock_person_instance

#         mock_address_instance = MagicMock()
#         mock_address_instance.get_random_address.return_value = {"street": "Some St"}
#         MockAddress.return_value = mock_address_instance

#         num_records = 10

#         # Act
#         _ = generate_fake_data_bulk_cached(num_records)

#         # Assert: FakeDataPerson and FakeDataAddress are each instantiated only once
#         MockPerson.assert_called_once()
#         MockAddress.assert_called_once()

#         # And their methods used multiple times
#         self.assertEqual(mock_person_instance.dict_customers.call_count, num_records)
#         self.assertEqual(mock_person_instance.dict_card.call_count, num_records)
#         self.assertEqual(mock_address_instance.get_random_address.call_count, num_records)


# # if __name__ == "__main__":
# #     unittest.main()