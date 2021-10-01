from configparser import ConfigParser


def config(section, filename="config.ini"):
    parser = ConfigParser()
    parser.read(filename)

    if parser.has_section(section):
        params = dict(parser.items(section))
    else:
        raise Exception(f"Section {section} not found in the {filename} file.")

    return params


if __name__ == "__main__":
    config("postgresql")
