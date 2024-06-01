import subprocess

def get_command_output(command):
    try:
        result = subprocess.run(command, shell=True, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_software_versions():
    versions = {}
    commands = {
        'AWS CLI': "aws --version",
        'Nextflow': "nextflow -v",
        'Java': "java --version | head -n 1",
        'Docker': "docker info | grep '^ Version'",
        'Apptainer': "apptainer version",
        'Singularity': "singularity version"
    }

    for software, command in commands.items():
        output = get_command_output(command)
        if output:
            # Parse the output to extract the version
            if software == 'Docker':
                version = output.split(' ')[-1].strip()
            elif software == 'AWS CLI':
                version = output.split(' ')[0].split("/")[1].strip()
            elif software == 'Java':
                version = output.split(' ')[1].strip()
            elif software == 'Nextflow':
                version = output.split(' ')[-1].strip()
            else:
                version = output.strip()
            versions[software] = {'Status': 'Available', 'Version': version}
        else:
            versions[software] = {'Status': 'Not Available', 'Version': 'N/A'}

    return versions
