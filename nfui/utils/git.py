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
import requests
import sys

def run_command(command, directory):
  result = subprocess.run(
    command,
    cwd=directory,
    shell = True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
  )
  if result.returncode != 0:
    print(result.stderr, file=sys.stderr)
  return result

def fetch_repo_details(organization, project, base_target_path, force=False, base_url="https://api.github.com"):
  t = time.time()
  CACHE_VALID_TIME = 1

  cache_path = f'{base_target_path}/{organization}/{project}.json'
  current_epoch = time.time()

  # Check the cache and renew it only if not updated the last 300s
  if os.path.exists(cache_path) and not force:
    with open(cache_path, 'r') as f:
      data = json.load(f)
    epoch = int(data["time"])
    if (current_epoch - epoch) < CACHE_VALID_TIME:
      return data["results"]
    
  # current head is a dict with
  # ref: string
  # ref_type: type of reference tag, branch or sha
  # sha: sha matching the ref
  current_head = None
  if "head" in data.keys():
    current_head = data["head"]

  # Initialize results dictionary
  results = {'project': project, 'organization': organization}

  # Fetch branches
  branches_url = f'{base_url}/repos/{organization}/{project}/branches'
  branches_response = requests.get(branches_url)
  if branches_response.ok:
    branches_data = branches_response.json()
    results['branches'] = [branch['name'] for branch in branches_data]
  else:
    results['branches'] = []
    print(f"Error fetching branches: {branches_response.text}", file=sys.stderr)
    # TODO Raise Error

  # Fetch tags
  tags_url = f'{base_url}/repos/{organization}/{project}/tags'
  tags_response = requests.get(tags_url)
  if tags_response.ok:
    tags_data = tags_response.json()
    results['tags'] = [tag['name'] for tag in tags_data]
  else:
    results['tags'] = []
    print(f"Error fetching tags: {tags_response.text}", file=sys.stderr)
    # TODO Raise Error

  # You might also want to fetch additional information like the default branch
  repo_url = f'{base_url}/repos/{organization}/{project}'
  repo_response = requests.get(repo_url)
  if repo_response.ok:
    repo_data = repo_response.json()
    results['default_branch'] = repo_data.get('default_branch', 'main')
  else:
    raise

  if current_head == None:
    current_head = {
      "ref": results['default_branch'],
      "ref_type": "branch",
      "sha": [br["commit"]["sha"] for br in branches_data if br["name"] == results['default_branch']][0]
    }

  # Save results to cache
  with open(cache_path, 'w') as f:
    json.dump({"time": current_epoch, "info": results, "head": current_head}, f)

  elapsed = time.time() - t
  print(f'detail for {organization}/{project} in {int(elapsed*1000)} ms')

  return results

Rewrite the function above to perform the request in an async manner and exploit the results after (in the same order but waiting for the first)

def checkout_git(value, organization, project, base_target_path, base_url="https://raw.githubusercontent.com"):
  target_dir = os.path.join(base_target_path, organization, project, value)
  if os.path.exists(target_dir):
    shutil.rmtree(target_dir)

  os.makedirs(target_dir, exist_ok=True)

  # List of files to fetch
  files_to_fetch = ['nextflow.config', 'nextflow_schema.json', 'README.md']

  # Fetch each file
  for file_name in files_to_fetch:
    file_url = f'{base_url}/{organization}/{project}/{value}/{file_name}'
    response = requests.get(file_url)
    if response.status_code == 200:
      with open(os.path.join(target_dir, file_name), 'wb') as f:
        f.write(response.content)
    else:
      print(f"Could not fetch {file_name} from {file_url}: {response.status_code}", file=sys.stderr)
      # TODO Raise error

