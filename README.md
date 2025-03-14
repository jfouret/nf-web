# liteflow

A liteweigth workflow web manager.

## Project Description

**liteflow** is a lightweight, open-source web application designed to manage local workflows and runs, primarily compatible with Nextflow. It is built using Flask and offers a simple, user-friendly interface for single-user environments. The application is designed to be easily deployable, with minimal configuration required, making it an ideal choice for users who need a straightforward solution for managing workflows without the overhead of complex systems.

## Key Features
- **Lightweight and Simple**: Designed to be minimalistic and efficient, ensuring quick deployment and ease of use.
- **Single-User Focus**: Currently supports single-user environments, with potential for multi-user support in future updates.
- **Easy Deployment**: Can be deployed effortlessly on local systems, with no need for extensive setup.
- **Configuration-Based Security**: No secrets are stored within the application; all configurations are managed at the system level.
- **Simple Web Server**: Operates without SSL, intended to be used behind a reverse proxy for secure connections.
- **Nextflow Compatibility**: Primarily supports Nextflow workflows, with plans to extend compatibility to Toil and CWL in the future.
A Flask web application to manage local workflow and runs.
- **Open Source**: Fully open-source, encouraging community contributions and transparency.
- **Future Compatibility**: Designed with extensibility in mind, allowing for future support of additional workflow engines like Toil and CWL.
**Configuration Simplicity**: All configurations are handled through system-level settings, ensuring security and simplicity.
**Workflow Management**: Easily manage and execute local workflows.
**Run Tracking**: Monitor the status and progress of workflow runs.

In-developement

Check the [brief](./brief.md)

## Testing

### Setup

The project uses Playwright for end-to-end testing. To set up the testing environment:

```bash
pip install -r requirements-test.txt
```

### Running Tests

To run the login tests:
```bash
python -m pytest tests/test_login.py -v
```

To run all tests:
```bash
python -m pytest tests/ -v
```
