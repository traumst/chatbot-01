import logging
from pydantic import BaseModel, HttpUrl

from src.utils.logmod import log_level_atoi
from src.utils.lru_cache import LRUCache

env_cache: LRUCache = LRUCache(8, 1/4)
logger = logging.getLogger(__name__)

class EnvConfig(BaseModel):
    """Configuration defined by .env file"""

    host: str = "0.0.0.0"
    port: int  = 8080
    cache_size: int = 8
    log_level: int = logging.INFO
    db_conn_str: str = ""
    model_name: str = ""
    model_url: HttpUrl = None

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)

    def assign_env_value(self, kv_line: str) -> None:
        """
        maps raw key-value pairs from config,
        should look like: XYZ=some_string
        """
        config_line = kv_line.strip().strip("\\n").strip(",")
        if config_line.startswith("#"):
            return

        [key, val] = config_line.split("=", 1)
        conf_key = key.lower()
        conf_val = val.strip().strip("\"").strip()
        if conf_key.endswith(","):
            raise ValueError(f"Env config value should not end with a comma ',' {key}={val}")
        match conf_key:
            case "host":
                self.host = conf_val
                assert self.host is not None
                assert self.host != ""
            case "port":
                self.port = int(conf_val)
                assert self.port > 0
            case "cache_size":
                self.cache_size = int(conf_val)
                assert self.cache_size > 0
                assert self.cache_size <= 1024
            case "log_level":
                self.log_level = log_level_atoi(conf_val)
            case "db_str":
                self.db_conn_str = conf_val
                assert self.db_conn_str is not None
                assert self.db_conn_str != ""
            case "model_url":
                self.model_url = HttpUrl(conf_val)
                assert self.db_conn_str is not None
                assert self.db_conn_str != ""
            case "model_name":
                self.model_name = conf_val
                assert self.db_conn_str is not None
                assert self.db_conn_str != ""
            case _:
                print(f"Unsupported env config key, {key}={val}")

def read_env() -> EnvConfig | None:
    """serves env config from either cache or reads from .env"""

    conf: EnvConfig | None = env_cache.get("envConfig")
    if conf is not None and conf.cache_size > 0:
        logger.info("envConfig from cache:\t%s", conf)
        return conf

    conf = EnvConfig()
    with open(".env", "r", encoding="utf-8") as file:
        for line in file:
            conf.assign_env_value(line)
    assert conf.cache_size > 0
    assert conf.host.strip() != ""
    assert conf.port > 0
    assert conf.log_level >= 0
    logger.info("env conf loaded:\t%s", conf)
    env_cache.put("envConfig", conf)

    return conf
