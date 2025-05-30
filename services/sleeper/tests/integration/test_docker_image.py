# pylint:disable=unused-variable
# pylint:disable=unused-argument
# pylint:disable=redefined-outer-name

import json
import shutil
import urllib.request
from pathlib import Path
from typing import Dict

import pytest

import docker
import jsonschema
import yaml


# HELPERS
def _download_url(url: str, file: Path):
    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(url) as response, file.open("wb") as out_file:
        shutil.copyfileobj(response, out_file)
    assert file.exists()


def _convert_to_simcore_labels(image_labels: Dict) -> Dict:
    io_simcore_labels = {}
    for key, value in image_labels.items():
        if str(key).startswith("io.simcore."):
            simcore_label = json.loads(value)
            simcore_keys = list(simcore_label.keys())
            assert len(simcore_keys) == 1
            simcore_key = simcore_keys[0]
            simcore_value = simcore_label[simcore_key]
            io_simcore_labels[simcore_key] = simcore_value
    assert len(io_simcore_labels) > 0
    return io_simcore_labels


# FIXTURES


@pytest.fixture(scope="session")
def metadata_labels(metadata_file: Path) -> Dict:
    with metadata_file.open() as fp:
        metadata = yaml.safe_load(fp)
        return metadata


# TESTS


def test_docker_io_simcore_labels_against_files(
    docker_image: docker.models.images.Image, metadata_labels: Dict
):
    image_labels = docker_image.labels
    io_simcore_labels = _convert_to_simcore_labels(image_labels)
    # check files are identical
    SKIPPED_KEYS = ["key", "name"]
    for key, value in io_simcore_labels.items():
        if key in SKIPPED_KEYS:
            continue
        assert key in metadata_labels
        assert value == metadata_labels[key]
