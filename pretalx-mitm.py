"""
Mirror all web pages.

Useful if you are living down under.
"""

from mitmproxy import http
import logging
from urllib.parse import parse_qs
import json


def request(flow: http.HTTPFlow) -> None:
    if "schedule/widgets/schedule.json" in flow.request.pretty_url:
        logging.info(flow.request.path)

        parsed = parse_path(flow.request.path)

        logging.info(json.dumps(parsed))

        flow.metadata["parsed"] = parsed
        flow.metadata["to_be_modified"] = True

        if "If-None-Match" in flow.request.headers:
            del flow.request.headers["If-None-Match"]
        flow.request.path = f"/{parsed['real_path']}"


def response(flow: http.HTTPFlow) -> None:
    if flow.metadata.get("to_be_modified", False):
        logging.info("to be modified")
        data = json.loads(flow.response.content)
        tracks = parse_tracks(flow.metadata["parsed"])
        if len(tracks) == 0:
            return
        logging.info(f"Filtering by tracks {tracks}")

        talks = data.get("talks", [])
        for talk in talks:
            if "track" not in talk:
                logging.warn(f"Found talk without track: {talk}")
        talks = [talk for talk in talks if "track" in talk and talk["track"] in tracks]

        track_data = data.get("tracks")
        track_data = [track for track in track_data if track["id"] in tracks]

        data = {
            **data,
            "talks": talks,
            "tracks": track_data,
        }

        flow.response.text = json.dumps(data)


def parse_path(path: str) -> dict:
    split = path.split("/")
    event = split[1]
    params = split[2]
    real_path = "/".join([event, *split[3:]])

    return {
        "event": event,
        "params": params,
        "rest": split[3:],
        "real_path": real_path,
    }


def parse_tracks(parsed: dict) -> list[int]:
    try:
        params = parsed["params"]

        parsed = parse_qs(params)
        logging.info(f"params: {params}, parsed: {parsed}")

        tracks = parsed.get("track", [])[0].split(",")

        return [int(x) for x in tracks]
    except Exception as e:
        logging.exception(e)
        return []
