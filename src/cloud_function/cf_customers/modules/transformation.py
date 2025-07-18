import re
import logging
from datetime import datetime, timedelta



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
        Obfuscates sensitive customer data in a list of dictionaries.

        This function iterates over a list of dictionaries containing customer and card information,
        hiding the 'cpf' field in the 'customers' dictionary and the 'card_number' field in the 'cards' dictionary
        using the respective helper functions.

        Args:
            data_list (list): A list of dictionaries, each containing 'customers' and 'cards' sub-dictionaries.

        Returns:
            list[dict[str, dict]]: The input list with sensitive fields obfuscated.
    """
    for _ in range(len(data_list)):
        data_list[_]['customers']['cpf'] = _hide_cpf(data_list[_]['customers']['cpf'])
        data_list[_]['cards']['card_number'] = _hide_card(data_list[_]['cards']['card_number'])

    logging.info("Sensitive data hidden successfully.")
    return data_list


def add_columns(data_list: list) -> list[dict[str, dict]]:
    """
        Adds additional columns to each dictionary in the provided data list.

        For each entry in the data_list, this function:
        - Sets 'created_at' to the current timestamp and 'updated_at' to None for 'customers', 'cards', and 'address' sub-dictionaries.
        - Sets 'fk_associate_id' in 'cards' and 'address' sub-dictionaries to the value of 'associate_id' from the 'customers' sub-dictionary.

        Args:
            data_list (list): A list of dictionaries, each containing 'customers', 'cards', and 'address' sub-dictionaries.

        Returns:
            list[dict[str, dict]]: The updated list with additional columns added to each sub-dictionary.
    """

    for _ in range(len(data_list)):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        data_list[_]['customers']['created_at'] = current_time
        data_list[_]['customers']['updated_at'] = None

        data_list[_]['cards']['card_holder_name']   = f"{data_list[_]['customers']['name']} {data_list[_]['customers']['last_name']}"
        data_list[_]['cards']['created_at']         = current_time
        data_list[_]['cards']['updated_at']         = None
        data_list[_]['cards']['fk_associate_id']    = data_list[_]['customers']['associate_id']

        data_list[_]['address']['created_at']       = current_time
        data_list[_]['address']['updated_at']       = None
        data_list[_]['address']['fk_associate_id']  = data_list[_]['customers']['associate_id']

    logging.info("Columns added successfully.")
    return data_list


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