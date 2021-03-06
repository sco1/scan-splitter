import itertools
from textwrap import dedent

import click
import pytest
from src import parser


LINE_CLEANER_TEST_CASES = [
    (  # Short-circuit on comment
        "1  *****  Body Fat / Fitness: *****",
        "*****  Body Fat / Fitness: *****",
    ),
    (  # Swap tabs for spaces
        "1  AbdomenBack	5.6	7.8	-9.10",
        "AbdomenBack 5.6 7.8 -9.10",
    ),
    (  # Remove colon
        "1  Actual Weight: 1.2",
        "Actual Weight 1.2",
    ),
    (
        "1  Body Fat (men): 1.2",
        "Body Fat (men) 1.2",
    ),
    (
        "1  Waist at 50%: 1.2",
        "Waist at 50% 1.2",
    ),
    (
        "1  Chest / Bust Circum Tape Measure: 1.2",
        "Chest / Bust Circum Tape Measure 1.2",
    ),
    (
        "1  Bust60DegreesLeft	1.2	1.2	1.2",
        "Bust60DegreesLeft 1.2 1.2 1.2",
    ),
]


@pytest.mark.parametrize(("raw_line", "truth_line"), LINE_CLEANER_TEST_CASES)
def test_line_cleaning(raw_line: str, truth_line: str) -> None:  # noqa: D103
    assert parser._clean_line(raw_line) == truth_line


LINE2CSV_TEST_CASES = [
    (
        "Halter 1.2",
        "Halter,1.2",
    ),
    (
        "halter 1.2",
        "halter,1.2",
    ),
    (
        "Actual Weight 1.2",
        "Actual Weight,1.2",
    ),
    (
        "Chest/Bust Circum Back Left 1.2",
        "Chest/Bust Circum Back Left,1.2",
    ),
    (
        "ActualWeight 1.2",
        "ActualWeight,1.2",
    ),
    (
        "Chest / Bust Circum Tape Measure 1.2",
        "Chest / Bust Circum Tape Measure,1.2",
    ),
    (
        "Body Fat (men) 1.2",
        "Body Fat (men),1.2",
    ),
    (
        "Waist at 50% 1.2",
        "Waist at 50%,1.2",
    ),
    (
        "Bust60DegreesLeft 1.2 1.2 1.2",
        "Bust60DegreesLeft,1.2,1.2,1.2",
    ),
    (
        "AbdomenBack 5.6 7.8 -9.10",
        "AbdomenBack,5.6,7.8,-9.10",
    ),
    (
        "Bust With Drop Back 5.6 7.8 -9.10",
        "Bust With Drop Back,5.6,7.8,-9.10",
    ),
    (
        "Right heel 5.6 7.8 -9.10",
        "Right heel,5.6,7.8,-9.10",
    ),
]


@pytest.mark.parametrize(("raw_line", "truth_csv"), LINE2CSV_TEST_CASES)
def test_line2csv(raw_line: str, truth_csv: str) -> None:  # noqa: D103
    assert parser._line2csv(raw_line) == truth_csv


COMPOSITE_TEST_CASES = [
    (
        dedent(  # Check that headers are discarded; anthro is joined
            """\
            #SizeStream Measurements
            #Stored on Tue May 18 06:49:24 2021
            #SizeStream Core Measurements
            #format - Measurement Valid (1 = valid), Measurement Name, Measurement
            #
            1  Actual Weight: 1.2
            #SizeStream Custom Measurements
            #format - Measurement Valid (1 = valid), Measurement Name, Measurement
            #
            1  Chest: 3.4
            #SizeStream Landmarks
            #format - Landmarks Valid (1 = valid), Landmark Name, Landmark x y z
            #
            1  AbdomenBack	5.6	7.8	-9.10
            """
        ),
        ["Actual Weight,1.2", "Chest,3.4"],
        ["AbdomenBack,5.6,7.8,-9.10"],
    ),
    (
        dedent(  # Check that comments are discarded
            """\
            #SizeStream Measurements
            #Stored on Tue May 18 06:49:24 2021
            #SizeStream Core Measurements
            #format - Measurement Valid (1 = valid), Measurement Name, Measurement
            #
            1  Actual Weight: 1.2
            #SizeStream Custom Measurements
            #format - Measurement Valid (1 = valid), Measurement Name, Measurement
            #
            1  *****  Body Fat / Fitness: *****
            1  Chest: 3.4
            #SizeStream Landmarks
            #format - Landmarks Valid (1 = valid), Landmark Name, Landmark x y z
            #
            1  AbdomenBack	5.6	7.8	-9.10
            """
        ),
        ["Actual Weight,1.2", "Chest,3.4"],
        ["AbdomenBack,5.6,7.8,-9.10"],
    ),
]


@pytest.mark.parametrize(
    ("raw_src", "truth_anthro", "truth_landmark"), COMPOSITE_TEST_CASES, ids=itertools.count()
)
def test_composite_file_parsing(  # noqa: D103
    raw_src: str, truth_anthro: list[str], truth_landmark: list[str]
) -> None:
    anthro, landmark = parser.split_composite_file(raw_src.splitlines())

    assert anthro == truth_anthro
    assert landmark == truth_landmark


SUBJ_ID_TEST_CASES = [
    (
        "1 2021-04-20_18-00-00_composite",
        ("1", ""),
    ),
    (
        "001 2021-04-20_18-00-00_composite",
        ("001", ""),
    ),
    (
        "CPEN1 2021-04-20_18-00-00_composite",
        ("1", "CPEN"),
    ),
    (
        "CPEN001 2021-04-20_18-00-00_composite",
        ("001", "CPEN"),
    ),
    (
        "cpen001 2021-04-20_18-00-00_composite",
        ("001", "cpen"),
    ),
    (
        "A001 2021-04-20_18-00-00_composite",
        ("001", "A"),
    ),
    (
        "A1 2021-04-20_18-00-00_composite",
        ("1", "A"),
    ),
    (
        "a1 2021-04-20_18-00-00_composite",
        ("1", "a"),
    ),
    (
        "1234 (2) 2021-04-20_18-00-00_composite",
        ("1234 (2)", ""),
    ),
    (
        "CPEN1234 (2) 2021-04-20_18-00-00_composite",
        ("1234 (2)", "CPEN"),
    ),
    (
        "1234-2 2021-04-20_18-00-00_composite",
        ("1234-2", ""),
    ),
    (
        "CPEN1234-2 2021-04-20_18-00-00_composite",
        ("1234-2", "CPEN"),
    ),
]


@pytest.mark.parametrize(("raw_line", "truth_id"), SUBJ_ID_TEST_CASES)
def test_subject_id_extraction(raw_line: str, truth_id: tuple[str, str]) -> None:  # noqa: D103
    assert parser.extract_subj_id(raw_line) == truth_id


def test_no_subject_id_raises() -> None:  # noqa: D103
    with pytest.raises(click.ClickException):
        parser.extract_subj_id("2021-04-20_18-00-00_composite")


SAMPLE_DEFAULT_LOCATION = "FOO"
LOCATION_INSERTION_TEST_CASES = [
    (
        "001 2021-04-20_18-00-00_composite",
        ("001", SAMPLE_DEFAULT_LOCATION),
    ),
    (
        "CPEN001 2021-04-20_18-00-00_composite",
        ("001", "CPEN"),
    ),
]


@pytest.mark.parametrize(("raw_line", "truth_id"), LOCATION_INSERTION_TEST_CASES)
def test_default_location_insertion(raw_line: str, truth_id: tuple[str, str]) -> None:  # noqa: D103
    assert parser.extract_subj_id(raw_line, default_location=SAMPLE_DEFAULT_LOCATION) == truth_id


ROW_EXTRACTION_TEST_CASES = [
    (
        dedent(
            """\
            Measurement Name,Measurement
            Actual Weight,123.45
            Abdomen Circum Tape Measure,3.14
            """
        ),
        [
            "Measurement Name",
            "Actual Weight",
            "Abdomen Circum Tape Measure",
        ],
    ),
    (
        dedent(
            """\
            SS_Vars
            Actual_Weight
            Abdomen_Circum_Tape_Measure
            """
        ),
        [
            "SS_Vars",
            "Actual_Weight",
            "Abdomen_Circum_Tape_Measure",
        ],
    ),
]


@pytest.mark.parametrize(("raw_src", "truth_rownames"), ROW_EXTRACTION_TEST_CASES)
def test_row_name_extraction(raw_src: str, truth_rownames: list[str]) -> None:  # noqa: D103
    assert parser.extract_measurement_names(raw_src) == truth_rownames
