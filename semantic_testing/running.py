#TODO: Add print messages for successful results
import os
import shutil
from pathlib import Path
from xml.dom import minidom


def check_command_output(lines, command):
    if not lines:
        print(f"Problem executing command {command}")
        return

    for line in lines:
        if not line.startswith("Converting"):
            print(f"Problem executing command {command}: {line}")
            return
    print(f"Command OK: {command}")


def main():
    topic_path = (
            Path(__file__).absolute().parent.parent / "resources" / "dita" / "task.dita"
    )
    app_folder = Path(__file__).absolute().parent.parent / "resources" / "app"

    doc = minidom.parse(topic_path.__str__())

    path_to_check = None
    filepaths = doc.getElementsByTagName("filepath")
    if filepaths:
        path_in_topic = [
            filepath.firstChild.nodeValue
            for filepath in filepaths
            if filepath.getAttribute("outputclass") == "output_path"
        ][0]

        path_to_check = app_folder / path_in_topic

    if path_to_check and path_to_check.exists():
        shutil.rmtree(path_to_check)

    command_to_run = doc.getElementsByTagName("codeblock")[0].firstChild.nodeValue

    os.chdir(app_folder)
    stream = os.popen(command_to_run)
    output = stream.readlines()
    result = stream.close()
    if result:
        print(f"Problem running command {command_to_run}: {result}")
    else:
        check_command_output(output, command_to_run)

    if not path_to_check.exists():
        print(f"Specified output path does not exist: {path_to_check}")
    else:
        print(f"Path OK: {path_to_check}")


if __name__ == "__main__":
    main()
