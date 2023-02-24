from models.d_VirtualSource_model import VirtualSource
from pydantic import constr


class VirtualSourcePyd(VirtualSource):
    name: constr(strip_whitespace=True, to_lower=True, min_length=4)
    converter_base: constr(
        strip_whitespace=True,
        to_lower=True,
        min_length=4,
    ) = "neutral"


# TODO: what is missing
#   - documentation like name, description
#   - could be autogenerated from yaml-file: https://pydantic-docs.helpmanual.io/datamodel_code_generator/
#       - based on OpenAPI -> FastAPI
#   - immutability of fields: https://pydantic-docs.helpmanual.io/usage/models/#faux-immutability
#   - pydantic can check inputs of method with decorator: @validate_arguments
