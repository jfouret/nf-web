## Project Brief: Nextflow Web GUI

### Overview
Develop a Flask web application to manage local Nextflow pipelines and runs. The application will feature a web-based GUI utilizing Bootstrap and Vue.js for specific elements. For security, the server will generate a random password at startup, which will be displayed to the user and required to start a session. The application will support configuration and management of Nextflow pipelines, configuration files, run configurations, and the execution of runs.

### Application Configuration Variables
- **root_dir**: The default root directory will be the directory from which the server is started. This directory will be divided per user.
  - **root_dir/pipelines**: This directory will host Nextflow workflows.
  - **root_dir/runs**: This directory will store the runs.
  - **root_dir/configs**: This directory will store Nextflow configuration files.
  - **root_dir/run_configs**: This directory will store run configuration files, each containing `params.json` and `run.json`.

### Pages

#### 1. **Login Page** [TODO]
- **Purpose**: To prompt for authentication.
- **Behavior**: If no session is open, this is the default redirect page.

#### 2. **Home Page** [DONE]
- **Purpose**: To display user and host information.
- **Requirements**:
  - Must have an active session.
  - Display host information including:
    - Size of `/` (used and available)
    - Memory and CPU details (including CPU brand name)
    - Software availability and versions for Java, Nextflow, Docker, Apptainer, and Singularity
  - Provide navigation buttons to the "Pipelines," "Runs," "Configs," and "Run Configs" pages.

#### 3. **Pipelines Page** [DONE]
- **Purpose**: To list available pipelines.
- **Requirements**:
  - Display a table with the following columns:
    - **Pipeline Name**: e.g., viral-recon for nf-core/viral-recon
    - **Organization**: e.g., nf-core
    - **Commit**: SHA of the commit
    - **Tags**: List of tags (from the origin)
    - **Branch**: Name of the current branch
    - **Changed**: Boolean indicating if there are changes in the local directory compared to the commit
  - Information should be gathered on the backend as a list of dictionaries and rendered using Vue.js and Bootstrap.

#### 4. **Import Pipeline Page** [DONE]
- **Purpose**: To import new pipelines.
- **Requirements**:
  - User enters a pipeline name in the format `{{organization}}/{{pipeline_name}}`.
  - Server fetches available branches or tags for the specified pipeline.
  - Define the repository as `https://github.com/{{organization}}/{{pipeline_name}}.git` and clone it into `{{root_dir}}/pipelines/{{organization}}/{{pipeline_name}}`.

#### 5. **Pipeline Page** [TODO]
- **Purpose**: To summarize and manage a specific pipeline.
- **Requirements**:
  - Display a summary of the selected pipeline.
  - Eventually show the README page of the pipeline.
  - Allow users to select a different tag, resulting in a git checkout on the backend and page update.
  - Provide a form based on the JSON schema specified in the `nextflow_schema.json` located in the pipeline directory, using a Vue.js module that can generate forms from this file.

#### 6. **Configs Page** [TODO]
- **Purpose**: Allow users to upload, view, and manage configuration files in `{{root_dir}}/configs`.
- **Requirements**:
  - config files are stored in `{{root_dir}}/configs`
  - For each file, we store the metadata in `{{root_dir}}/configs/{{filename}}.meta.yml`
  - Metadata are:
    - filename
    - name
  - Display a table with the following columns:
    - **Config File Name**: Name of the configuration file (must be unique)
    - **Filename**: Filename given to the configuration file (must be unique), style adapted to filename (eg using monospace font)
    - **Delete**: Button to Delete the config file (asking confirmation in a popup)
    - **Edit**: Button to redirects to the edition 
  - The table is built by reading all file matching `{{root_dir}}/configs/(.*).meta.yml` where the captured filname exists.
  - **Create form**: A form before the table, on the single line with the field for the name of the config, the file name and a button create. upon creation it redirects to the edit page with an empty file.

#### 6 bis **Config Edit** [TODO]
- **Purpose**: To edit one Nextflow configuration files.
- **Requirements**:
  - filename of config file is given in url as field option
  - file editor (ace) to edit file in `{{root_dir}}/configs/{{filename}}`

#### 7. **Run Configs Page** [TODO]
- **Purpose**: To list and manage run configurations.
- **Requirements**:
  - Display a table with the following columns:
    - **Pipeline Name**: Name of the pipeline
    - **Release Tag**: Release tag of the pipeline
    - **Nextflow Config**: Optional Nextflow configuration file
    - **Parameters File**: JSON file with its content shown
  - Allow users to create and manage run configurations, specifying the pipeline name, release tag, optional Nextflow config, and required parameters file.
  - Store run configurations in `{{root_dir}}/run_configs` as:
    - `params.json`: Contains parameters for the run.
    - `run.json`: Contains a link to the Nextflow config file (used with `-c`) in `{{root_dir}}/configs`, the pipeline, and the release tag.

#### 8. **Runs Page** [TODO]
- **Purpose**: To list and manage runs based on run configurations.
- **Requirements**:
  - Display a table with the following columns:
    - **Run ID**: Unique identifier for the run
    - **Pipeline Name**: Name of the pipeline
    - **Release Tag**: Release tag of the pipeline
    - **Status**: Current status of the run
  - Provide a button to start a new run based on a selected run configuration.
  - Store runs in `{{root_dir}}/runs`, linking the `params.json` and `run.json` files and including a `.nextflow.log` file.
  - Display the updated content of the `.nextflow.log` file for each run.

### Interaction Overview
1. **Login**: User logs in using the generated password displayed at server startup.
2. **Navigation**: User navigates through the application using the header bar to access Home, Pipelines, Configs, Run Configs, and Runs pages.
3. **Pipelines Management**: Users can view, import, and manage pipelines, including checking out different tags and editing pipeline details based on the JSON schema.
4. **Configuration Management**: Users can upload and manage Nextflow configuration files.
5. **Run Configurations**: Users can create and manage configurations for runs, specifying necessary details for each run. Run configurations are stored in `{{root_dir}}/run_configs` as `params.json` and `run.json` files.
6. **Run Execution**: Users can start runs based on configurations, with the backend handling the execution of Nextflow commands. Runs are stored in `{{root_dir}}/runs` and link the `params.json` and `run.json` files, including a `.nextflow.log` file to track the execution progress.

By ensuring each page has a clear purpose and detailed requirements, developers can implement the application effectively and efficiently.


