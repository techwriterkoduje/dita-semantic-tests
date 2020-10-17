#TODO: Add print messages for successful results
import json
from pathlib import Path
from xml.dom import minidom


def main():
    working_dir = Path(__file__).absolute()
    topic_path = working_dir.parent.parent / "resources" / "dita" / "reference.dita"
    app_folder = working_dir.parent.parent / "resources" / "app"
    config_path = app_folder / "config.json"

    doc = minidom.parse(topic_path.__str__())

    dl_entries = doc.getElementsByTagName("dlentry")
    config_properties = json.load(config_path.open()).keys()

    for dl_entry in dl_entries:
        filepaths = dl_entry.getElementsByTagName("filepath")
        if filepaths:
            filepath_to_check = filepaths[0].firstChild.nodeValue
            if "/" in filepath_to_check:
                full_path = app_folder / filepath_to_check
                if not full_path.exists():
                    print(f'Path does not exist: {filepath_to_check} (referenced in {topic_path.name})')
            else:
                all_files_and_folders = [f.name for f in app_folder.rglob("*")]
                if filepath_to_check not in all_files_and_folders:
                    print(f'File or folder not found: {filepath_to_check} (referenced in {topic_path.name}')
            param_lists = dl_entry.getElementsByTagName("parml")
            if param_lists:
                param_list_to_check = param_lists[0]
                params = param_list_to_check.getElementsByTagName("pt")
                param_names = [p.firstChild.nodeValue for p in params]
                for param_name in param_names:
                    if not param_name in config_properties:
                        print(f'Parameter "{param_name}" does not exist in the config file')
    print('Done')


if __name__ == "__main__":
    main()
