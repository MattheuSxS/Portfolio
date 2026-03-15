import logging
from utils.helpers import Dashboard


# ******************************************************************************************************************** #
#                                              System Logging                                                          #
# ******************************************************************************************************************** #
logging.basicConfig(
    format=("%(asctime)s | %(levelname)s | File_name ~> %(module)s.py "
            "| Function ~> %(funcName)s | Line ~~> %(lineno)d  ~~>  %(message)s"),
    level=logging.INFO
)


# ******************************************************************************************************************** #
#                                              Main Execution Function                                                 #
# ******************************************************************************************************************** #
def main():
    dashboard = Dashboard("gcp-default-portfolio")
    dashboard.main_page()


if __name__ == "__main__":
    main()