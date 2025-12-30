FROM mitmproxy/mitmproxy

COPY pretalx-mitm.py /pretalx-mitm.py

ENTRYPOINT ["mitmdump", "--mode", "reverse:https://pretalx.dlrgjugendnds.de", "-s", "/pretalx-mitm.py"]
