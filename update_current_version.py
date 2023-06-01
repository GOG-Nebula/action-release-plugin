import json
import pathlib
from argparse import ArgumentParser, Namespace
from typing import Dict, List

VERSION_FILE_PATH = "current_version.json"


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--assets_dir",
        type=pathlib.Path,
        help="Directory containing zipped plugin build for windows/macos",
        required=True,
    )
    parser.add_argument("--version", type=str, help="Tag name", required=True)
    parser.add_argument(
        "--repository", type=str, help="Repository name in the 'user/repository' format", required=True
    )
    args = parser.parse_args()
    return args


def main(args: Namespace, version_file_path: pathlib.Path):
    assets_paths: List[pathlib.Path] = list(args.assets_dir.iterdir())
    validate_assets(assets_paths)
    version_file = prepare_version_file_content(args.version, assets_paths, args.repository)
    with open(version_file_path, "w") as f:
        json.dump(version_file, f)


def validate_assets(assets_paths: List[pathlib.Path]):
    if not assets_paths:
        raise ValueError(f"No assets found in given directory")
    if not all([p.suffix == ".zip" for p in assets_paths]):
        raise ValueError("GOG Galaxy supports only 'zip' asserts")


def prepare_version_file_content(
    version: str, assets_paths: List[pathlib.Path], repository: str
) -> Dict[str, str]:
    version_file = {
        "tag_name": version,
        "assets": [],
    }
    for asset_path in assets_paths:
        version_file["assets"].append(
            {
                "browser_download_url": f"https://github.com/{repository}/releases/download/{version}/{asset_path.name}",
                "name": asset_path.name,
            }
        )
    return version_file


if __name__ == "__main__":
    args = parse_args()
    main(args, VERSION_FILE_PATH)
