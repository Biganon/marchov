from marchov.marchov import Marchov
from marchov.secrets import *

if __name__ == "__main__":
    client = Marchov(
        nickname="M`arch`ov",
        sasl_username="M`arch`ov",
        sasl_password=PASSWORD,
    )
    client.run("irc.libera.chat", tls=True, tls_verify=False)
