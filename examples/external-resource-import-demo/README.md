# dina-py

## External Resource URL importer

Reads a .txt file to create External Resource URLs to be linked to Material Samples as Attachments

### Usage

Before using the script, make sure to go through the installation instructions in the repository's README

Once done, in the terminal, change current working directory:
```bash
cd examples/external-resource-import-demo
```

Copy the .txt file containing the External URLs to be uploaded into the current folder.

Then modify (as needed) and run the **external_resource_importer.py** script.

An output file called **external_url_uuids.txt** should have been created containing the generated UUIDs for each External Resource.
A similar file called **material_sample_uuids.txt** should also appear for the created Material Samples.

Optionally, you can also link all creted Material Samples using **link_samples_to_project.py** which reads **material_sample_uuids.txt** and links them to a Project in DINA through a given Project UUID.
