def get_list_from_file(file_name):
    with open(file_name) as file:
        return file.read().splitlines()
