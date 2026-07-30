import sqlite3

from tqdm import tqdm

from database import create_table, insert_functions
from input_processing import find_files, parse_arguments
from extraction import process_file


def main() -> None:
    target_path, database_file = parse_arguments()
    con = sqlite3.connect(database_file)
    create_table(con)

    if target_path.is_dir():
        files = list(find_files(target_path))
        for file_path in tqdm(files, total=len(files), desc="Processing files"):
            insert_functions(con, process_file(file_path))
    elif target_path.is_file():
        insert_functions(con, process_file(target_path))

    con.commit()
    con.close()
    tqdm.write("Program completed.")


if __name__ == "__main__":
    main()
