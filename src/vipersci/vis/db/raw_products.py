#!/usr/bin/env python
# coding: utf-8

"""Defines the VIS Raw_Product table using the SQLAlchemy ORM."""

# Copyright 2022, United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
#
# Reuse is permitted under the terms of the license.
# The AUTHORS file and the LICENSE file are at the
# top level of this library.

from datetime import datetime, timedelta, timezone
from warnings import warn

from sqlalchemy import orm
from sqlalchemy.orm import synonym, validates
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Identity,
    Integer,
    String,
)
from sqlalchemy.ext.hybrid import hybrid_property

from vipersci.pds.pid import VISID, vis_instruments, vis_compression
from vipersci.pds.datetime import isozformat
from vipersci.vis.header import pga_gain as header_pga_gain


Base = orm.declarative_base()


class RawProduct(Base):
    """An object to represent rows in the Raw_Products table for VIS.
    """

    # This class is derived from SQLAlchemy's orm.declarative_base()
    # which means that it has a variety of class properties that are
    # then swept up into properties on the instantiated object via
    # super().__init__().

    # The table represents many of these objects, so the __tablename__ is
    # plural while the class name is singular.
    __tablename__ = "raw_products"

    # The Column() names below should use "snake_case" for the names that are
    # committed to the database as column names.  Furthermore, those names
    # should be similar, if not identical, to the PDS4 Class and Attribute
    # names that they represent.  Other names (like Yamcs parameter camelCase
    # names) are implemented as synonyms. Aside from the leading "id" column,
    # the remainder are in alphabetical order, since there are so many.

    id = Column(Integer, Identity(start=1), primary_key=True)
    adc_gain = Column(
        Integer, nullable=False, doc="ADC_GAIN from the MCSE Image Header."
    )
    adcGain = synonym("adc_gain")
    auto_exposure = Column(
        Boolean,
        nullable=False,
        doc="AUTO_EXPOSURE from the MCSE Image Header.",
    )
    autoExposure = synonym("auto_exposure")
    bad_pixel_table_id = Column(
        Integer,
        nullable=False,
        # There is a Defective Pixel Map (really a list of 128 coordinates) for
        # each MCAM.  The "state" of this is managed by the ground and not
        # reflected in any Image Header information attached to an individual
        # image.  It is not clear how to obtain this information from Yamcs,
        # or even what might be recorded, so this column's value is TBD.
    )
    cameraId = synonym(
        "mcam_id"
    )  # This value maybe isn't the mcam_id since it is 0-7 from Yamcs?
    capture_id = Column(
        Integer,
        nullable=False,
        doc="The captureId from the command sequence."
        # TODO: learn more about captureIds to provide better doc here.
    )
    captureId = synonym("capture_id")
    _exposure_duration = Column(
        "exposure_duration",
        Integer,
        nullable=False,
        doc="The exposure time in microseconds, the result of decoding the "
        "EXP_STEP and EXP paramaters from the MCSE Image Header.",
    )
    exposureTime = synonym("exposure_duration")  # Yamcs parameter name.
    file_creation_datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        doc="The time at which file_name was created.",
    )
    file_path = Column(
        String,
        nullable=False,
        doc="The absolute path (POSIX style) that contains the Array_2D_Image "
        "that this metadata refers to.",
    )
    # Not sure where we're getting info for these light booleans yet.
    hazlight_aft_port_on = Column(Boolean, nullable=False)
    hazlight_aft_starboard_on = Column(Boolean, nullable=False)
    hazlight_center_port_on = Column(Boolean, nullable=False)
    hazlight_center_starboard_on = Column(Boolean, nullable=False)
    hazlight_fore_port_on = Column(Boolean, nullable=False)
    hazlight_fore_starboard_on = Column(Boolean, nullable=False)
    image_id = Column(
        Integer,
        nullable=False,
        doc="The IMG_ID from the MCSE Image Header used for CCU storage and "
        "retrieval.",
    )
    imageHeight = synonym("lines")
    imageId = synonym("image_id")
    imageWidth = synonym("samples")
    instrument_name = Column(
        String, nullable=False, doc="The full name of the instrument."
    )
    instrument_temperature = Column(
        Float,
        nullable=False,
        doc="The TEMPERATURE from the MCSE Image Header.  TBD how to convert "
        "this 16-bit integer into degrees C.",
    )
    # There is a sensor in the camera body (PT1000) which is apparently not
    # connected (sigh).  And there is also a sensor external to each camera
    # body (AD590), need to track down its Yamcs feed.
    lines = Column(
        Integer,
        nullable=False,
        doc="The imageHeight parameter from the Yamcs imageHeader.",
    )
    _lobt = Column(
        "lobt",
        Integer,
        nullable=False,
        doc="The TIME_TAG from the MCSE Image Header.",
    )
    mcam_id = Column(
        Integer, nullable=False, doc="The MCAM_ID from the MCSE Image Header."
    )
    md5_checksum = Column(
        String,
        nullable=False,
        doc="The md5 checksum of the file described by file_path.",
    )
    mission_phase = Column(
        String,
        nullable=False,
        # Not sure what form this will take, nor where it can be looked up.
    )
    navlight_left_on = Column(Boolean, nullable=False)
    navlight_right_on = Column(Boolean, nullable=False)
    offset = Column(
        Integer,
        nullable=False,
        doc="The OFFSET parameter from the MCSE Image Header describing the dark "
        "level offset.",
    )
    onboard_compression_ratio = Column(
        Float,
        nullable=False,
        # This is a PDS img:Onboard_Compression parameter which is the ratio
        # of the size, in bytes, of the original uncompressed data object
        # to its compressed size.  This operation is done by RFSW, but not
        # sure where to get this parameter from ...?
    )
    onboard_compression_type = Column(
        String,
        nullable=False,
        # This is the PDS img:Onboard_Compression parameter.  For us this
        # is going to be ICER, Lossless, or rarely None.
    )
    output_image_mask = Column(
        Integer,
        nullable=False,
        doc="The outputImageMask from the Yamcs imageHeader."
        # TODO: learn more about outputImageMask to provide better doc here.
    )
    output_image_type = Column(
        String,
        nullable=False,
        doc="The outputImageType from the Yamcs imageHeader."
        # TODO: learn more about outputImageType to provide better doc here.
    )
    outputImageMask = synonym("output_image_mask")
    outputImageType = synonym("output_image_type")
    _pid = Column(
        "product_id", String, nullable=False, doc="The PDS Product ID."
    )
    padding = Column(
        Integer,
        nullable=False,
        doc="The padding parameter from the Yamcs imageHeader.",
        # Not sure what this value means or where it comes from.
    )
    pga_gain = Column(
        Float,
        nullable=False,
        doc="The translated floating point multiplier derived from PGA_GAIN "
        "from the MCSE Image Header.",
    )
    ppaGain = synonym(
        "pga_gain"
    )  # Surely, this is a Yamcs typo, should be pgaGain
    processing_info = Column(
        Integer,
        nullable=False,
        doc="The processingInfo parameter from the Yamcs imageHeader."
        # TODO: learn more about processingInfo to provide better doc here.
    )
    processingInfo = synonym("processing_info")
    purpose = Column(
        String,
        nullable=False,
        doc="This is the value for the PDS "
        "Observation_Area/Primary_Result_Summary/purpose parameter, it "
        "has a restricted set of allowable values.",
    )
    samples = Column(
        Integer,
        nullable=False,
        doc="The imageWidth parameter from the Yamcs imageHeader.",
    )
    software_name = Column(String, nullable=False)
    software_version = Column(String, nullable=False)
    software_type = Column(String, nullable=False)
    software_program_name = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    stereo = Column(
        Boolean,
        nullable=False,
        doc="The stereo parameter from the Yamcs imageHeader."
        # TODO: learn more about stereo to provide better doc here.
    )
    stop_time = Column(DateTime(timezone=True), nullable=False)
    temperature = synonym("instrument_temperature")
    voltage_ramp = Column(
        Integer,
        nullable=False,
        doc="The VOLTAGE_RAMP parameter from the MCSE Image Header.",
    )
    voltageRamp = synonym("voltage_ramp")
    yamcs_generation_time = Column(
        DateTime(timezone=True),
        nullable=False,
        doc="The generation time of the source record from Yamcs.",
    )
    yamcs_name = Column(
        String,
        nullable=False,
        doc="The full parameter name from Yamcs that this product data came from, "
        "formatted like a / separated string."
    )

    def __init__(self, **kwargs):

        if kwargs.keys() >= {"start_time", "lobt"}:
            if (
                datetime.fromtimestamp(kwargs["lobt"], tz=timezone.utc)
                != kwargs["start_time"]
            ):
                raise ValueError(
                    f"The start_time {kwargs['start_time']} does not equal "
                    f"the lobt {kwargs['lobt']}"
                )

        # Exposure duration is a hybrid_property that also sets the stop_time,
        # if super().__init() processes exposure duration while self.start_time
        # is still None, then object initiation will fail.  Removing it from
        # the parameters we pass to super().__init() and then setting it
        # after avoids this error condition.
        exp_dur = None
        for k in ("exposureTime", "exposure_duration"):
            if k in kwargs:
                exp_dur = kwargs[k]
                del kwargs[k]

        # If present, product_id needs some special handling:
        if "product_id" in kwargs:
            pid = VISID(kwargs["product_id"])
            del kwargs["product_id"]
        else:
            pid = False

        rpargs = dict()
        otherargs = dict()
        for k, v in kwargs.items():
            if k in self.__table__.columns or k in self.__mapper__.synonyms:
                rpargs[k] = v
            else:
                otherargs[k] = v

        # Instantiate early, so that the parent orm_declarative Base can
        # resolve all of the synonyms.
        super().__init__(**rpargs)

        # Ensure stop_time consistency by setting this *after* start_time is set in
        # super().__init__()
        self.exposure_duration = exp_dur

        # Ensure instrument_name consistency and existence.
        if "instrument_name" in kwargs:
            self.instrument_name = VISID.instrument_name(self.instrument_name)
        elif "yamcs_name" in kwargs:
            maybe_name = self.yamcs_name.split("/")[-1].replace("_", " ")
            if maybe_name.endswith((" icer", " jpeg", " slog")):
                maybe_name = maybe_name[:-5]

            self.instrument_name = VISID.instrument_name(maybe_name)

        # Ensure product_id consistency
        if pid:

            if "lobt" in kwargs:
                if pid.datetime() != self.lobt:
                    raise ValueError(
                        f"The product_id datetime ({pid.datetime()}) and the "
                        f"provided lobt ({kwargs['lobt']}) disagree."
                    )

            if "start_time" in kwargs and pid.datetime() != self.start_time:
                raise ValueError(
                    f"The product_id datetime ({pid.datetime()}) and the "
                    f"provided start_time ({kwargs['start_time']}) disagree."
                )

            if (
                self.instrument_name is not None
                and vis_instruments[pid.instrument] != self.instrument_name
            ):
                raise ValueError(
                    f"The product_id instrument code ({pid.instrument}) and "
                    f"the provided instrument_name "
                    f"({self.instrument_name}) disagree."
                )

            if (
                self.onboard_compression_ratio is not None
                and vis_compression[pid.compression]
                != self.onboard_compression_ratio
            ):
                raise ValueError(
                    f"The product_id compression code ({pid.compression}) and "
                    f"the provided onboard_compression_ratio "
                    f"({self.onboard_compression_ratio}) disagree."
                )

        elif (
            self.start_time is not None
            and self.instrument_name is not None
            and self.onboard_compression_ratio is not None
        ):
            pid = VISID(
                self.start_time.date(),
                self.start_time.time(),
                self.instrument_name,
                self.onboard_compression_ratio,
            )
        else:
            got = dict()
            for k in (
                "product_id",
                "start_time",
                "instrument_name",
                "onboard_compression_ratio",
            ):
                v = getattr(self, k)
                if v is not None:
                    got[k] = v

            raise ValueError(
                "Either product_id must be given, or each of start_time, "
                f"instrument_name, and onboard_compression_ratio. Got: {got}"
            )

        self._pid = str(pid)

        # Is this really a good idea?  Not sure.  This instance variable plus
        # label_dict() and update() allow other key/value pairs to be carried around
        # in this object, which is handy.  If these are well enough known, perhaps
        # they should just be pre-defined properties and not left to chance?
        self.labelmeta = otherargs

        return

    @hybrid_property
    def exposure_duration(self):
        return self._exposure_duration

    @exposure_duration.setter
    def exposure_duration(self, value: int):
        """Takes an exposure time in microseconds."""
        self._exposure_duration = value
        self.stop_time = self.start_time + timedelta(microseconds=value)

    @hybrid_property
    def lobt(self):
        return self._lobt

    @lobt.setter
    def lobt(self, lobt):
        self._lobt = lobt
        self.start_time = datetime.fromtimestamp(lobt, tz=timezone.utc)

    @hybrid_property
    def product_id(self):
        # Really am going back and forth about whether this should be returned as
        # a full VISID object or just as the string as it is now.
        return self._pid

    @product_id.setter
    def product_id(self, pid):
        # In this class, the source of product_id information really is what
        # comes from Yamcs, and so this should not be monkeyed with.  Theoretically
        # changing this would imply changes to start time, lobt, stop time,
        # intrument name and onboard_compression_ratio directly, but those changes then
        # also divorce this object from the Yamcs parameters that it came from and
        # has all manner of other implications.  So at this time, this can only be
        # set when this object is instantiated.
        raise NotImplementedError(
            "product_id cannot be set directly after instantiation."
        )

    @validates("pga_gain")
    def validate_pga_gain(self, key, value):
        return header_pga_gain(value)

    @validates("mcam_id")
    def validate_mcam_id(self, key, value: int):
        s = {0, 1, 2, 3, 4}
        if value not in s:
            # raise ValueError(f"mcam_id must be one of {s}, but is {value}")
            warn(f"mcam_id must be one of {s}, but is {value}")
        return value

    @validates(
        "file_creation_datetime",
        "start_time",
        "stop_time",
        "yamcs_generation_time",
    )
    def validate_datetime_asutc(self, key, value):
        if isinstance(value, datetime):
            if value.utcoffset() is None:
                raise ValueError(f"{key} must be tz aware.")
            dt = value
        elif isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value)
            except ValueError:
                dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        else:
            raise ValueError(f"{key} must be a datetime or an ISO 8601 formatted string.")

        return dt.astimezone(timezone.utc)

    @validates("onboard_compression_type")
    def validate_onboard_compression_type(self, key, value: str):
        s = {"ICER", "Lossless", "None"}
        if value not in s:
            raise ValueError(
                f"onboard_compression_type must be one of {s}, but was {value}."
            )
        return value

    @validates("purpose")
    def validate_purpose(self, key, value: str):
        s = {
            "Calibration",
            "Checkout",
            "Engineering",
            "Navigation",
            "Observation Geometry",
            "Science",
            "Supporting Observation",
        }
        if value not in s:
            raise ValueError(f"purpose must be one of {s}")
        return value

    def label_dict(self):
        """Returns a dictionary suitable for label generation."""
        _inst = self.instrument_name.lower().replace(" ", "_")
        _sclid = "urn:nasa:pds:context:instrument_host:spacecraft.viper"
        onoff = {True: "On", False: "Off", None: "Unknown"}
        pid = VISID(self.product_id)
        d = dict(
            lid=f"urn:nasa:pds:viper_vis:raw:{self.product_id}",
            mission_lid="urn:nasa:pds:viper",
            sc_lid=_sclid,
            inst_lid=f"{_sclid}.{_inst}",
            gain_number=(self.adc_gain * self.pga_gain),
            exposure_type="Auto" if self.auto_exposure else "Manual",
            led_wavelength=453,  # nm
            luminaires={
                "NavLight Left": onoff[self.navlight_left_on],
                "NavLight Right": onoff[self.navlight_right_on],
                "HazLight Aft Port": onoff[self.hazlight_aft_port_on],
                "HazLight Aft Starboard": onoff[
                    self.hazlight_aft_starboard_on
                ],
                "HazLight Center Port": onoff[self.hazlight_center_port_on],
                "HazLight Center Starboard": onoff[
                    self.hazlight_center_starboard_on
                ],
                "HazLight Fore Port": onoff[self.hazlight_fore_port_on],
                "HazLight Fore Starboard": onoff[
                    self.hazlight_fore_starboard_on
                ],
            },
            compression_class="Lossless"
            if pid.compression == "a"
            else "Lossy",
        )
        for c in self.__table__.columns:
            if isinstance(getattr(self, c.name), datetime):
                d[c.name] = isozformat(getattr(self, c.name))
            else:
                d[c.name] = getattr(self, c.name)

        d.update(self.labelmeta)

        return d

    def update(self, other):
        for k, v in other.items():
            if k in self.__table__.columns or k in self.__mapper__.synonyms:
                setattr(self, k, v)
            else:
                self.labelmeta[k] = v
