import logging
from pydantic import BaseModel

from src.utils.logmod import log_level_atoi


class EnvConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int  = 7654
    cache_size: int = 8
    log_level: int = logging.INFO

    def assign_env_config(self, kv_line: str) -> None:
        """
        maps raw key-value pairs from config,
        should look like: XYZ=some_string
        """
        config_line = kv_line.strip().strip("\\n").strip(",")
        if config_line.startswith("#"):
            return

        print(f"reading conf\t\t{config_line}")
        [key, val] = kv_line.split("=", 1)
        conf_key = key.lower()
        conf_val = val.strip().strip("\"").strip()
        if conf_key.endswith(","):
            raise ValueError(f"Env config value should not end with a comma ',' {key}={val}")
        match conf_key:
            case "host":
                self.host = conf_val
            case "port":
                self.port = int(conf_val)
            case "cache_size":
                self.cache_size = int(conf_val)
            case "log_level":
                self.log_level = log_level_atoi(conf_val)
            case _:
                print(f"Unsupported env config key, {key}={val}")


def read_env() -> EnvConfig | None:
    conf = EnvConfig()
    file = open(".env", "r")
    try:
        for line in file:
            conf.assign_env_config(line)
    finally:
        file.close()
    # this should do the same without try,
    #   but does not work for some reason
    # with open(".env", "r") as file:
    #     for line in file:
    #         conf.assign_env_config(line)
    assert conf.cache_size > 0
    assert conf.host.strip() != ""
    assert conf.port > 0
    assert conf.log_level >= 0

    print(f"env conf:\t{conf}")

    return conf