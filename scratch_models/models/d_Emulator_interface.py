from datetime import datetime
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import confloat
from pydantic import root_validator

from .d_Features_interface import GpioLogging
from .d_Features_interface import PowerLogging
from .d_Features_interface import SystemLogging
from .d_VirtualSource_model import VirtualSource


class TargetPort(str, Enum):
    A = "A"
    B = "B"


class Compression(str, Enum):
    lzf = "lzf"
    gzip1 = 1  # TODO: will not work


compressions_allowed: list = [None, "lzf", 1]


class EmulatorIF(BaseModel):

    # General config
    input_path: Path
    output_path: Optional[Path]
    # ⤷ output_path:
    #   - providing a directory -> file is named emu_timestamp.h5
    #   - for a complete path the filename is not changed except it exists and overwrite is disabled -> emu#num.h5
    force_overwrite: bool = False
    output_compression: Union[None, str, int] = None
    # ⤷ should be 1 (level 1 gzip), lzf, or None (order of recommendation)

    start_time: datetime  # = Field(default_factory=datetime.utcnow)
    duration: timedelta

    # emulation-specific
    use_cal_default: bool = False
    # ⤷ do not load calibration from EEPROM

    enable_io: bool = False
    # ⤷ pre-req for sampling gpio
    io_port: TargetPort = "A"
    # ⤷ either Port A or B
    pwr_port: TargetPort = "A"
    # ⤷ that one will be current monitored (main), the other is aux
    voltage_aux: confloat(ge=0, le=5) = 0
    # ⤷ aux_voltage options:
    #   - None to disable (0 V),
    #   - 0-4.5 for specific const Voltage,
    #   - "mid" will output intermediate voltage (vsource storage cap),
    #   - true or "main" to mirror main target voltage

    # TODO: verbosity

    # sub-elements
    virtual_source: VirtualSource = {"name": "neutral"}
    power_logging: PowerLogging = PowerLogging()
    gpio_logging: GpioLogging = GpioLogging()
    sys_logging: SystemLogging = SystemLogging()

    class Config:
        # title = "Virtual Source MinDef"
        allow_mutation = False  # const after creation?
        extra = "forbid"  # no unnamed attributes allowed
        validate_all = True  # also check defaults
        min_anystr_length = 4
        anystr_lower = True
        anystr_strip_whitespace = True  # strip leading & trailing whitespaces
        # fields["start_time"].description =

    @root_validator()
    def validate(cls, values: dict):
        comp = values.get("output_compression")
        if comp not in compressions_allowed:
            raise ValueError(
                f"value is not allowed ({comp} not in {compressions_allowed}",
            )
        # TODO: limit paths
        # TODO: date older than now?
        # TODO:
        return values

    @root_validator(pre=False)
    def post_adjust(cls, values: dict):
        # TODO
        return values

    def get_parameters(self):
        # TODO
        print("you got it")
        return self.dict()
        # pass