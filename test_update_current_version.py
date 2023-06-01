from argparse import Namespace
import json
import sys
import subprocess
import pathlib

import pytest

from update_current_version import VERSION_FILE_PATH, main

SCRIPT = "update_current_version.py"


@pytest.fixture 
def create_assets(tmp_path: pathlib.Path):
    def fn(asset_names):
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir(exist_ok=True)
        for asset in asset_names:
            (assets_dir / asset).touch()
        return assets_dir
    return fn


@pytest.fixture 
def current_version_file(tmp_path):
    f = tmp_path / "test_current_version.json"
    f.touch()
    return f


@pytest.mark.parametrize("asset_names", [
    ['windows.zip'],
    ['windows.zip', 'macos.zip'],
])
def test_version_file_udpated(asset_names, create_assets, current_version_file):
    assets_dir = create_assets(asset_names)
    args = Namespace(
        version="v1.1",
        assets_dir=assets_dir,
        repository="GOG-Nebula/plugin-test"
    )

    main(args, current_version_file)
    output = json.loads(current_version_file.read_text())
    assert output["tag_name"] == "v1.1"
    for name in asset_names:
        assert {"browser_download_url": f"https://github.com/GOG-Nebula/plugin-test/releases/download/v1.1/{name}", "name": name} in output["assets"]

def test_version_file_created(create_assets, current_version_file):
    current_version_file.unlink()
    assert not current_version_file.exists()

    assets_dir = create_assets(['windows.zip'])
    args = Namespace(
        version="v1.1",
        assets_dir=assets_dir,
        repository="GOG-Nebula/plugin-test"
    )

    main(args, current_version_file)
    assert current_version_file.exists()

def test_error_raised_on_wrong_asset_name(create_assets, current_version_file):
    assets_dir = create_assets(["wrong_name.7z"])
    args = Namespace(
        version="v1.1",
        assets_dir=assets_dir,
        repository="GOG-Nebula/plugin-test"
    )

    with pytest.raises(ValueError):
        main(args, current_version_file)


def test_version_file_updated_functional(create_assets):
    assets_dir = create_assets(['windows.zip'])
    interpreter = sys.executable
    subprocess.run([interpreter, SCRIPT, '--version', 'v3', '--assets_dir', str(assets_dir), '--repository', 'X/Y'])
    
    try:
        with open(VERSION_FILE_PATH) as f:
            content = json.load(f)
        assert content["tag_name"] == "v3"
        assert content["assets"] == [
            {"name": "windows.zip", "browser_download_url": "https://github.com/X/Y/releases/download/v3/windows.zip"}
        ]
    finally:
        pathlib.Path(VERSION_FILE_PATH).unlink()
    
