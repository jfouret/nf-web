import re

def parse_nf_manifest(file_path):
  within_manifest_scope = False
  open_brackets = 0
  closed_brackets = 0
  i = 0
  description = ""
  nextflowVersion = ""
  with open(file_path, 'r') as f:
    for line in f.readlines():
      i += 1
      match = re.match(r"^\s*manifest\.description\s*=\s*['\"](.*)['\"]\s*$", line)
      if match:
        description = match.group(1)
        continue
      match = re.match(r"^\s*manifest\.nextflowVersion\s*=\s*['\"](.*)['\"]\s*$", line)
      if match:
        nextflowVersion = match.group(1)
        continue
      match = re.match(r"^\s*manifest\s*\{\s*$")
      if match:
        within_manifest_scope = True
        open_brackets = 1
        continue
      if within_manifest_scope and open_brackets ==1:
        open_brackets += line.count('{')
        open_brackets -= line.count('}')
        match = re.match(r"^\s*description\s*=\s*['\"](.*)['\"]\s*$", line)
        if match:
          description = match.group(1)
          continue
        match = re.match(r"^\s*nextflowVersion\s*=\s*['\"](.*)['\"]\s*$", line)
        if match:
          nextflowVersion = match.group(1)
          continue
      if within_manifest_scope and open_brackets==0:
        within_manifest_scope= False
      if description != "" and nextflowVersion != "":
        break
  results = {
    'description': description,
    'nextflowVersion': nextflowVersion
  }
  return results

