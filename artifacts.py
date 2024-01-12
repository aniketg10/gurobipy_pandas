import io
import os
import pathlib
import sys
import zipfile

import requests


def download_executed_notebooks(runs_url, gh_token, head_sha):
    headers = {
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {gh_token}",
    }

    params = {
        "head_sha": head_sha,
        # "event": "push",
        # "branch": "main",
    }
    response = requests.get(runs_url, headers=headers, params=params)
    response.raise_for_status()
    runs_data = response.json()

    for run in runs_data["workflow_runs"]:
        print("Run id={id} event={event} status={status} path={path}".format(**run))

        if run["path"] != ".github/workflows/test.yml":
            continue
        if run["status"] != "completed":
            continue
        if run["conclusion"] != "success":
            continue

        artifacts_url = run["artifacts_url"]
        response = requests.get(artifacts_url, headers=headers)
        response.raise_for_status()
        artifacts_data = response.json()

        for artifact in artifacts_data["artifacts"]:
            print("Artifact id={id} name={name}".format(**artifact))

            if artifact["name"] != "ipynb-artifact":
                continue

            download_url = artifact["archive_download_url"]
            response = requests.get(download_url, headers=headers)
            response.raise_for_status()

            outpath = pathlib.Path("docs/source/examples")
            with io.BytesIO(response.content) as data, zipfile.ZipFile(data) as archive:
                for filename in archive.namelist():
                    target = outpath.joinpath(filename)
                    if target.exists():
                        target.unlink()
                    assert not target.exists()
                    archive.extract(filename, path="docs/source/examples")
                    assert target.exists()
                    print(f"Downloaded {target}")

                return True

    return False


# Run as pre-build step on RTD
# Local test: READTHEDOCS_GIT_COMMIT_HASH=95e93023a278bbf8e0471e0f48cf64c4413415ac READTHEDOCS=True GH_API_TOKEN=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 python artifacts.py

assert os.environ.get("READTHEDOCS") == "True"

success = download_executed_notebooks(
    runs_url="https://api.github.com/repos/Gurobi/gurobipy-pandas/actions/runs",
    # public repo scope is enough (for public repos)
    gh_token=os.environ["GH_API_TOKEN"],
    head_sha=os.environ["READTHEDOCS_GIT_COMMIT_HASH"],
)

if success:
    sys.exit(0)  # Success, RTD build can continue
else:
    sys.exit(183)  # Cancels the RTD build (rely on a later trigger to rebuild)

# Any error would be a build failure
