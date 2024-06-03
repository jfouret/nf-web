import subprocess
import os
from git import Repo
import shutil
import tempfile
import json
import yaml
from pathlib import Path
import time
import re
# Replace the matched pattern with a colon

def parse_nf_manifest(file_path):
    manifest_detected = False
    open_brackets = 0
    closed_brackets = 0
    i=0
    description = ""
    nextflowVersion = ""
    with open(file_path, 'r') as f:
        for line in f.readlines():
            i += 1
            if line.startswith('manifest'):
                manifest_detected = True
            if manifest_detected:
                open_brackets += line.count('{')
                closed_brackets += line.count('}')
            else:
                continue
            if open_brackets == closed_brackets:
                break
            match = re.match(r"^\s*description\s*=\s*['\"]+([^'\"].*[^'\"])['\"]+\s*$", line)
            if match:
                description = match.group(1)
                continue
            match = re.match(r"^\s*nextflowVersion\s*=\s*['\"](.*)['\"]\s*$", line)
            if match:
                nextflowVersion = match.group(1)
                continue
            if open_brackets < closed_brackets:
                raise Exception(f'Invalid manifest file "{file_paht}", closing brackets without opening line {i}')
    results = {
        'description': description,
        'nextflowVersion': nextflowVersion
    }
    return results

def run_command(command, directory):
    # Use subprocess.run to execute the command
    result = subprocess.run(
        command,                      # command and arguments, split into a list
        cwd=directory,                # set the working directory for the command
        shell = True,                  # use shell to execute the command
        stdout=subprocess.PIPE,       # capture stdout
        stderr=subprocess.PIPE,       # capture stderr
        text=True                     # return outputs as string not bytes
    )
    # print if error
    if result.returncode != 0:
        print(result.stderr)
    return result

def build_url(organization, project, base_url = "https://github.com"):
    return f'{base_url}/{organization}/{project}.git'   

def fetch_repo_details(organization,project,base_target_path, force = False ,base_url = "https://github.com"):
    # Use a temporary directory to hold the bare clone

    cache_path = f'{base_target_path}/{organization}/{project}.json'
    current_epoch = int(time.time())
    # if file exists
    if os.path.exists(cache_path) and not force:
        with open(cache_path, 'r') as f:
            data = json.load(f)
        epoch = int(data["time"])
        if (current_epoch - epoch) < 300:
            return data["results"]

    repo_url = build_url(organization, project, base_url)
    nf_config_path = f'{base_target_path}/{organization}/{project}/nextflow.config'
    results = parse_nf_manifest(nf_config_path)
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Clone the repository as a bare repository
        repo = Repo.clone_from(repo_url, tmpdirname, bare=True)
        results['tags'] = [ x.name for x in repo.tags]
        results['branches'] = [ x.name for x in repo.branches]
    try:
        repo_obj = Repo(f'{base_target_path}/{organization}/{project}')
        try:
            branch = repo_obj.active_branch.name
        except:
            branch = "None" 
        tags_head = [tag.name for tag in repo_obj.tags if tag.commit == repo_obj.head.commit]
        results["head"] = repo_obj.head.commit.hexsha[:6]
        results["branch"] = branch
        results["tag"] = tags_head[0] if len(tags_head) > 0 else "None"
        results["changed"] = repo_obj.is_dirty()
        results['project'] = project
        results['organization'] = organization
    except:
        pass
    with open(cache_path, 'w') as f:
        json.dump({"time":current_epoch,"results":results}, f)
    return results

def checkout_git(value,organization,project,base_target_path,base_url = "https://github.com"):
    target_path = f'{base_target_path}/{organization}/{project}'
    shutil.rmtree(target_path, ignore_errors=True)
    repo_url = build_url(organization, project, base_url)
    target_org_path = f'{base_target_path}/{organization}'
    Path(target_org_path).mkdir(parents=True, exist_ok=True)
    run_command(f"git clone --depth 1 --branch {value} {repo_url}", target_org_path)
    run_command(f"git submodule update --init --recursive --depth 1", target_path)
    fetch_repo_details(organization, project, base_target_path, True)

