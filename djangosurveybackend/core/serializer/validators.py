import logging
from typing import List


def remove_non_updatable(
    non_updatable_fields: List[str],
    kwargs_data_field="validated_data",
    args_data_index=2,
):
    def decorator(target_function):
        def wrapper(*args, **kwargs):
            if is_argument_exist(kwargs):
                validated_data = kwargs[kwargs_data_field]
            elif is_index_exist(args):
                validated_data = args[args_data_index]
            else:
                error = RuntimeError(
                    f"'{kwargs_data_field}' argument and index '{args_data_index}' are not exist"
                )
                logging.error(error)
                raise error
            for key in extract_non_updatable_keys(validated_data):
                validated_data.pop(key)
            return target_function(*args, **kwargs)

        def extract_non_updatable_keys(validated_data) -> List[str]:
            return list(
                filter(lambda k: k in non_updatable_fields, list(validated_data.keys()))
            )

        def is_index_exist(args):
            return args_data_index < len(args)

        def is_argument_exist(kwargs):
            return kwargs_data_field in kwargs.keys()

        return wrapper

    return decorator
