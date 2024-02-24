def fail(project_id, response):
    raise Exception(f'Project {project_id} failed to update. Reason: \n{response.status_code} - {response.text}')


def get_json_value(data, key):
    """Returns the value for the specified key in the JSON-object.
    :data      JSON-object to extract value by key.
    :key       Name of the key to search for within JSON-object.
    :return    Value of the specified key.
    """
    # TODO fix method
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                yield v
            else:
                yield from get_json_value(v, key)
    elif isinstance(data, list):
        for item in data:
            yield from get_json_value(item, key)
