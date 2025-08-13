import configparser

def read_config(file_path: str, verbose: bool) -> configparser.ConfigParser:
    """
    Read the configuration file and return a ConfigParser object.
    @param file_path: The path to the configuration file.
    @param verbose: Whether to print verbose output.
    @return: A ConfigParser object containing the configuration.
    """
    config = configparser.ConfigParser()
    try:
        config.read(file_path)
    except Exception as e:
        print(f"Error reading configuration file '{file_path}': {e}")
    if verbose:
        print(f"Configuration file '{file_path}' read successfully.")
    return config

def get_overleaf_projects(config: configparser.ConfigParser, verbose: bool) -> dict[str, str]:
    """
    Get Overleaf project IDs and their corresponding GitLab repository paths from the configuration.
    @param config: The ConfigParser object containing the configuration.
    @param verbose: Whether to print verbose output.
    @return: A dictionary mapping Overleaf project IDs to GitLab repository paths.
    """
    projects: dict[str, str] = dict()
    
    for section in config.sections():
        if section.startswith("repos"):
            for overleaf_id, gitlab_path in config.items(section):
                projects[overleaf_id] = gitlab_path

    if verbose:
        print(f"Found Overleaf projects: {list(projects.keys())}")
    return projects
