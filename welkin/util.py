from datetime import date, datetime, timezone

# NOTE: `clean_request_payload` and `clean_request_params` are intentionally DRY
# violations. The code may be the same, but they represent different knowledge.
# the same goes for `clean_request_payload` and `clean_json_list`


def clean_request_payload(payload: dict) -> dict:
    result = {}
    for k, v in payload.items():
        if isinstance(v, datetime):
            result[k] = clean_datetime(v)
        elif isinstance(v, date):
            result[k] = clean_date(v)
        elif isinstance(v, dict):
            result[k] = clean_request_payload(v)
        elif isinstance(v, list):
            result[k] = clean_json_list(v)
        else:
            result[k] = v

    return result


def clean_json_list(data: list) -> list:
    result = []
    for item in data:
        if isinstance(item, datetime):
            result.append(clean_datetime(item))
        elif isinstance(item, date):
            result.append(clean_date(item))
        elif isinstance(item, dict):
            result.append(clean_request_payload(item))
        elif isinstance(item, list):
            result.append(clean_json_list(item))
        else:
            result.append(item)

    return result


def clean_request_params(params: dict) -> dict:
    result = {}
    for k, v in params.items():
        if isinstance(v, datetime):
            result[k] = clean_datetime(v)
        elif isinstance(v, date):
            result[k] = clean_date(v)
        elif isinstance(v, list):
            result[k] = ",".join(v)
        else:
            result[k] = v

    return result


def clean_date(date: date) -> str:
    dt = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=timezone.utc)

    return clean_datetime(dt)


def clean_datetime(dt: datetime) -> str:
    return (
        dt.astimezone(tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
