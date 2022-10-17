from marchov.marchov import Marchov
from marchov.secrets import *


if __name__ == "__main__":
    client = Marchov(
        nickname=USERNAME,
        sasl_username=USERNAME,
        sasl_password=PASSWORD,
    )
    client.run(SERVER, tls=True, tls_verify=False)
