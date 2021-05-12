from collections import OrderedDict
import json
import os
import psycopg2

class Deployer:
    
    def __init__(self, config_file: str):
        self.sql_directory = os.path.dirname(config_file) 
        with open(config_file, "r") as f:
            self.config = json.loads(f.read(), object_pairs_hook=OrderedDict)   
        return
        
    def deploy(self):
        self.conn = self.get_connection()
        self.ensure_log_tables_exist()
        for section in self.get_sections():
            print("Start Deploying Section:     {}".format(section))
            is_repeatable = self.is_repeatable_section(section)
            for file_name in self.get_files(section):
                file_path_name = self.get_file_path(file_name)
                if (is_repeatable):
                    self.deploy_repeatable_file(file_path_name)
                else:
                    self.deploy_file(file_path_name)
            print("Finish Deploying Section:     {}".format(section))
        return

    def deploy_file(self, file_name: str):
        if self.is_already_deployed(file_name):
            print("Skipping already deployed file:  {}".format(file_name))
        else:
            self.log_activity(file_name, "start")
            with open(file_name, "r") as sql:
                cur = self.conn.cursor()
                try:
                    cur.execute(sql.read())
                    self.log_deployed(file_name)
                    self.log_activity(file_name, "success")
                    print("Deployed:    {}".format(file_name))
                except Exception as exception:
                    self.log_activity(file_name, "failure")
                    self.print_exception(exception, file_name)
                    raise exception
        return

    def deploy_repeatable_file(self, file_name: str):
        with open(file_name, "r") as sql:
            cur = self.conn.cursor()
            try:
                cur.execute(sql.read())
                print("Deployed:    {}".format(file_name))
            except Exception as exception:
                self.print_exception(exception, file_name)
                raise exception
        return

    def is_already_deployed(self, file_name: str):
        cur = self.conn.cursor()
        cur.execute("select count(1) from dbdeploy.deployed as d where d.filename = %s", (file_name,))
        return cur.fetchone()[0] > 0

    def log_deployed(self, file_name: str):
        cur = self.conn.cursor()
        cur.execute("insert into dbdeploy.deployed(filename) values (%s)",(file_name, ))

    def log_activity(self, file_name: str, type: str):
        activity = {"start" : 1, "success" : 2, "failure" : 3}
        activity_type_id = activity[type]
        cur = self.conn.cursor()
        cur.execute("insert into dbdeploy.activity(filename, activitytypeid) values (%s, %s)",(file_name, activity_type_id))
        return

    def get_connection(self):
        connection_config = self.config["connection"]
        secret = os.getenv(connection_config["password_env_variable"])
        conn = psycopg2.connect(host = connection_config["server"], user = connection_config["user"], password = secret, dbname = connection_config["database"])
        conn.set_session(autocommit = True)
        return conn

    def ensure_log_tables_exist(self):
        with open("database-deploy-logging.sql", "r") as sql:
            cur = self.conn.cursor()
            cur.execute(sql.read())
        return

    def print_exception(self, exception: Exception, file_name: str):
        print("---------------------------\n")
        print ("DEPLOYMENT FAILED\n")
        print("Failure in file:   {}".format(file_name))
        print(exception)
        print("---------------------------")

    def get_sections(self):
        return self.config["sections"].keys()

    def is_repeatable_section(self, section: str):
        return self.config["sections"][section]["isRepeatable"]

    def get_files(self, section: str):
        return self.config["sections"][section]["files"]

    def get_file_path(self, file_name):
        return os.path.join(self.sql_directory, file_name)

    def __str__(self):
        return str(self.config)

