import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class EnvConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int  = 7654
    cache_size: int = 8

    def assign_env_config(self, kv_line: str) -> None:
        """
        maps raw key-value pairs from config,
        should look like: XYZ=some_string
        """
        kv_line = kv_line.strip()
        if kv_line.startswith("#"):
            return None
        [key, val] = kv_line.split("=", 1)
        conf_key = key.lower()
        if conf_key.endswith(","):
            logger.warning(f"Env config value maybe broken, {key}={val}")
        match conf_key:
            case "host":
                self.host = val
            case "port":
                self.port = int(val)
            case "cache_size":
                self.cache_size = int(val)
            case _:
                logger.warning(f"Unsupported env config key, {key}={val}")

def read_env() -> EnvConfig | None:
    conf = EnvConfig()
    file = open(".env", "r")
    try:
        for line in file:
            conf.assign_env_config(line)
    finally:
        file.close()
    return conf