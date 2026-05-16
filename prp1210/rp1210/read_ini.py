"""Read RP121032.ini file."""

import configparser

INI_FILE_PATH = r'C:\Windows\RP121032.ini'


def read_ini() -> list[str]:
    """Call WIndows API, GetPrivateProfileString, to read RP121032.ini file.

    Returns:
        A list of vendor ID(s).
    """

    # if sys.platform != "win32":
    #     print("RP1210 is a Windows-only standard.")

    config = configparser.ConfigParser()
    try:
        config.read(INI_FILE_PATH)
        # Read the comma-separated string string
        raw_implementations = config.get(
            "RP1210Support", "APIImplementations", fallback="")

        # Parse into an array, cleaning up whitespace
        return [v.strip() for v in raw_implementations.split(",") if v.strip()]
    except (FileExistsError, FileNotFoundError):
        print(f"Error, file path '{INI_FILE_PATH}' does not exist.")
    except PermissionError:
        print("Access to RP121032.ini was blocked by system permissions.")
    except (configparser.Error, ValueError):
        print("Error occurred while parsing RP121032.ini file.")

    return []


# Example run:
if __name__ == "__main__":
    vendors = read_ini()
    print(f"Detected RP1210 Drivers: {vendors}")
