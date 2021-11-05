import argparse
from db_creator import DatabaseCreator


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_mode', type=str, choices=['webpage', 'csv', 'json'],
                        help='From what to extract players data.')
    parser.add_argument('output_mode', type=str, choices=['csv', 'excel', 'json'],
                        help='To which format to export data.')
    arguments = parser.parse_args()

    if arguments.input_mode == 'webpage':
        database_creator = DatabaseCreator.create_from_web()
    elif arguments.input_mode == 'csv':
        pass
    elif arguments.input_mode == 'json':
        pass

    if arguments.input_mode == 'csv':
        database_creator.to_csv()
    elif arguments.input_mode == 'excel':
        database_creator.to_excel()
    elif arguments.input_mode == 'json':
        pass



# Create csv from hive players data


# argparse

# based on argparse

# if csv mode:
#database_creator = DatabaseCreator.create_from_csv()












