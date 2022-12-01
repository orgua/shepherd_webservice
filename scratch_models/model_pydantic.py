from pathlib import Path

import yaml
from pydantic import BaseModel, Extra, conlist, constr, condecimal, root_validator, Field


def load_vsources() -> dict:
    def_file = "virtual_source_defs.yml"
    def_path = Path(__file__).parent.resolve() / def_file
    with open(def_path) as def_data:
        configs = yaml.safe_load(def_data)["virtsources"]
        configs = dict((k.lower(), v) for k, v in configs.items())
    return configs


configs_predef = load_vsources()


def acquire_def(name: str):
    name = name.lower()
    if name in configs_predef:
        config_base = configs_predef[name]
        return config_base
    else:
        ValueError(f"ConverterBase {name} not known!")


#class VirtualSourceBasePyd(BaseModel, extra=Extra.forbid):
class VirtualSourceBasePyd_old(BaseModel):

    name: constr(strip_whitespace=True, to_lower=True, min_length=4) = "neutral"
    converter_base: constr(strip_whitespace=True, to_lower=True, min_length=4) = "neutral"
    enable_boost: bool = False
    enable_buck: bool = False
    log_intermediate_voltage: bool = False

    interval_startup_delay_drain_ms: condecimal(ge=0, le=10e3) = 0

    harvester: constr(strip_whitespace=True, to_lower=True, min_length=4) = "mppt_opt"

    V_input_max_mV: condecimal(ge=0, le=10e3) = 10_000
    I_input_max_mA: condecimal(ge=0, le=4.29e3) = 4_200
    V_input_drop_mV: condecimal(ge=0, le=4.29e6) = 0.0

    C_intermediate_uF: condecimal(ge=0, le=100e3) = 0.0
    V_intermediate_init_mV: condecimal(ge=0, le=10e3) = 3000
    I_intermediate_leak_nA: condecimal(ge=0, le=4.29e9) = 0.0

    V_intermediate_enable_threshold: float = 1
    V_intermediate_disable_threshold_mV: float = 0
    interval_check_thresholds_ms: float = 0

    LUT_output_efficiency: conlist(item_type=condecimal(ge=0.0, le=1.0), min_items=12, max_items=12) = 12 * [1.00]

    @root_validator(pre=True)
    def recursive_fill(cls, values):
        if "converter_base" in values:
            config_name = values.get("converter_base")
            config_base = acquire_def(config_name)
            print(f"Will init VS from {config_name}")
            config_base["name"] = config_name
            base_dict = VirtualSourceBasePyd.recursive_fill(values=config_base)
            for key, value in values.items():
                base_dict[key] = value
            values = base_dict
        elif "name" in values and values.get("name").lower() in configs_predef:
            config_name = values.get("name")
            if config_name == "neutral":
                values = acquire_def(config_name)
                values["name"] = config_name
            else:
                config_base = acquire_def(config_name)
                print(f"Will init VS as {config_name}")
                config_base["name"] = config_name
                values = VirtualSourceBasePyd.recursive_fill(values=config_base)
        return values

    @root_validator(pre=False)
    def post_adjust(cls, values):
        # TODO
        return values

    def get_parameters(self):
        pass


class VirtualSourceBasePyd(BaseModel):

    name: str = Field(
        title="Name of Virtual Source",
        description="Slug to use this Name as later reference",
        default="neutral",
        strip_whitespace=True,
        to_lower=True,
        min_length=4,
    )
    converter_base: str = Field(default="neutral", strip_whitespace=True, to_lower=True, min_length=4)
    enable_boost: bool = Field(default=False, description="if false -> V_intermediate becomes V_input, output-switch-hysteresis is still usable")
    enable_buck: bool = Field(default=False, description="if false -> V_output becomes V_intermediate")
    log_intermediate_voltage: bool = False

    interval_startup_delay_drain_ms: condecimal(ge=0, le=10e3) = 0

    harvester: constr(strip_whitespace=True, to_lower=True, min_length=4) = "mppt_opt"

    V_input_max_mV: condecimal(ge=0, le=10e3) = 10_000
    I_input_max_mA: condecimal(ge=0, le=4.29e3) = 4_200
    V_input_drop_mV: condecimal(ge=0, le=4.29e6) = 0.0

    C_intermediate_uF: condecimal(ge=0, le=100e3) = 0.0
    V_intermediate_init_mV: condecimal(ge=0, le=10e3) = 3000
    I_intermediate_leak_nA: condecimal(ge=0, le=4.29e9) = 0.0

    V_intermediate_enable_threshold: float = 1
    V_intermediate_disable_threshold_mV: float = 0
    interval_check_thresholds_ms: float = 0

    LUT_output_efficiency: conlist(item_type=condecimal(ge=0.0, le=1.0), min_items=12, max_items=12) = 12 * [1.00]

    @root_validator(pre=True)
    def recursive_fill(cls, values):
        
        if "converter_base" in values:
            config_name = values.get("converter_base")
            config_base = acquire_def(config_name)
            print(f"Will init VS from {config_name}")
            config_base["name"] = config_name
            base_dict = VirtualSourceBasePyd.recursive_fill(values=config_base)
            for key, value in values.items():
                base_dict[key] = value
            values = base_dict
        elif "name" in values and values.get("name").lower() in configs_predef:
            config_name = values.get("name").lower()
            if config_name == "neutral":
                values = acquire_def(config_name)
                values["name"] = config_name
            else:
                config_base = acquire_def(config_name)
                print(f"Will init VS as {config_name}")
                config_base["name"] = config_name
                values = VirtualSourceBasePyd.recursive_fill(values=config_base)
        return values

    @root_validator(pre=False)
    def post_adjust(cls, values):
        # TODO
        return values

    def get_parameters(self):
        pass


class VirtualSourcePyd(VirtualSourceBasePyd):

    name: constr(strip_whitespace=True, to_lower=True, min_length=4)
    converter_base: constr(strip_whitespace=True, to_lower=True, min_length=4) = "neutral"

# TODO: what is missing
#   - documentation like name, description
#   - could be autogenerated from yaml-file: https://pydantic-docs.helpmanual.io/datamodel_code_generator/
#       - based on OpenAPI -> FastAPI