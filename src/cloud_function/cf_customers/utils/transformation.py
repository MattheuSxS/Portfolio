import re
import logging
from zoneinfo import ZoneInfo
from datetime import datetime


def _hide_cpf(cpf_number: str) -> str:
    """
        Obfuscates a Brazilian CPF number by hiding the middle digits.

        Args:
            cpf_number (str): The CPF number to be obfuscated. Can contain formatting characters.

        Returns:
            str: The obfuscated CPF in the format 'XXX.***.***-XX'. If the input is invalid, returns '000.000.000-00'.

        Raises:
            None

        Notes:
            - Only the first three and last two digits of the CPF are shown.
            - If the input does not contain exactly 11 digits, a warning is logged and a default value is returned.
    """

    clean_cpf = re.sub(r'\D', '', cpf_number)
    if len(clean_cpf) != 11:
        logging.warning("Invalid CPF format")
        return "000.000.000-00"

    return f'{clean_cpf[:3]}.***.***-{clean_cpf[-2:]}'


def _hide_card(card_number: str) -> str:
    """
        Obfuscates a card number by replacing its middle digits with asterisks.

        The function removes all non-digit characters from the input card number,
        validates its length, and returns a masked version showing only the first
        three and last three digits. If the card number length is invalid, a default
        masked value is returned.

        Args:
            card_number (str): The card number to be obfuscated.

        Returns:
            str: The obfuscated card number with middle digits replaced by asterisks,
                or a default masked value if the input is invalid.
    """

    clean_card = re.sub(r'\D', '', card_number)
    if not 13 <= len(card_number) <= 19:
        logging.warning("Invalid card number length")
        return "0000 0000 0000 0000"

    first_six = clean_card[:3]
    last_four = clean_card[-3:]
    num_asteriscos = len(clean_card) - len(first_six) - len(last_four)

    return f'{first_six}{"*" * num_asteriscos}{last_four}'


def hide_data(data_list: list) -> list[dict[str, dict]]:
    """
        Hides sensitive customer data such as CPF and card number in a list of data dictionaries.

        Args:
            data_list (list): A list of dictionaries, each containing 'customers' and 'cards' keys with sensitive information.

        Returns:
            list[dict[str, dict]]: The modified list with sensitive data (CPF and card number) masked or hidden.

        Note:
            This function modifies the input list in place by masking the 'cpf' field in 'customers' and the 'card_number' field in 'cards'.
    """
    for data in data_list:
        data['customers']['cpf'] = _hide_cpf(data['customers']['cpf'])
        data['cards']['card_number'] = _hide_card(data['cards']['card_number'])

    logging.info("Sensitive data hidden successfully.")
    return data_list


def add_columns(data_list: list) -> list[dict[str, dict]]:
    """
        Adds and updates specific columns in each dictionary of the input data list for customers, cards, and addresses.

        For each item in the input list, this function:
        - Adds 'created_at' (current timestamp) and 'updated_at' (None) to 'customers', 'cards', and 'address' sub-dictionaries.
        - Adds 'fk_associate_id' (from 'customers.associate_id') to 'cards' and 'address'.
        - Adds 'card_holder_name' (concatenation of 'customers.name' and 'customers.last_name') to 'cards'.

        Args:
            data_list (list): A list of dictionaries, each containing 'customers', 'cards', and 'address' sub-dictionaries.

        Returns:
            list[dict[str, dict]]: The modified list with updated and additional columns for each item.
    """

    current_time = datetime.now(ZoneInfo('Europe/Dublin')).strftime('%Y-%m-%d %H:%M:%S')

    def process_item(item):
        customer = item['customers']
        associate_id = customer['associate_id']
        full_name = f"{customer['name']} {customer['last_name']}"

        item['customers'].update({
            'created_at': current_time,
            'updated_at': None
        })

        item['cards'].update({
            'card_holder_name': full_name,
            'created_at': current_time,
            'updated_at': None,
            'fk_associate_id': associate_id
        })

        item['address'].update({
            'created_at': current_time,
            'updated_at': None,
            'fk_associate_id': associate_id
        })

        return item

    logging.info("Columns added successfully.")
    return [process_item(item) for item in data_list]


def split_data(data_list: list) -> dict[str, list]:
    """
        Splits the input data list into three separate lists: customers, cards, and address.

        Args:
            data_list (list): A list of dictionaries containing 'customers', 'cards', and 'address' sub-dictionaries.

        Returns:
            dict: A dict containing three lists:
                - List of customer dictionaries.
                - List of card dictionaries.
                - List of address dictionaries.
    """


    return \
        {
            "tb_customers": [data['customers'] for data in data_list],
            "tb_cards":     [data['cards'] for data in data_list],
            "tb_address":   [data['address'] for data in data_list]
        }