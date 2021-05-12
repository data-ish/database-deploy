import sys
from deployer import Deployer
from pathlib import Path

def main():
    if (len(sys.argv)> 2):
        raise ValueError("db-deploy expects a single argument, for the config file only. Multiple Provided.")
    if  (len(sys.argv)==1):
        raise ValueError("db-deploy expects a single argument, for the config file only. None Provided.")

    config_file = sys.argv[1]
    print("Config file: {}".format(config_file))
    config_path = Path(config_file)

    if (config_path.is_file()):
        deployer = Deployer(config_file)
        deployer.deploy()
    else:
        raise ValueError("The config file specified does not exist.")



if __name__ == "__main__":
    main()