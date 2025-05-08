from colorama import init
from test_generator import (
    collect_modules_from_root,
    get_unit_test_url,
    download_test_file,
)
import os

init(autoreset=True)


def main():
    result = collect_modules_from_root()
    test_folder = os.path.join(os.getcwd(), "tests")
    os.makedirs(test_folder, exist_ok=True)

    for module in result["modules"]:
        for file in module["files"]:
            response_data = get_unit_test_url(file, result)
            if response_data:
                module_path = os.path.join(test_folder, module["module"])
                os.makedirs(module_path, exist_ok=True)

                init_file_path = os.path.join(module_path, "__init__.py")
                if not os.path.exists(init_file_path):
                    open(init_file_path, "a").close()

                file_name = os.path.basename(file)
                test_file_name = f"test_{file_name}"
                dest_file_path = os.path.join(module_path, test_file_name)
                download_test_file(response_data["url"], dest_file_path)

    init_file_path = os.path.join(test_folder, "__init__.py")
    if not os.path.exists(init_file_path):
        open(init_file_path, "a").close()


if __name__ == "__main__":
    from setup import check_packages

    check_packages()
    main()
