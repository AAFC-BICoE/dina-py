# dina-py

## External Resource URL importer

Reads a .txt file to create External Resource URLs to be linked to Material Samples as Attachments

### Usage

Before using the script, make sure to go through the installation instructions in the repository's README

Once done, in the terminal, change current working directory:
```bash
cd external-resource-import-demo
```

Copy the .txt file containing the External URLs to be uploaded into the current folder.

Then run the **external_resource_importer.py** script.

An output file called **external_url_uuids.txt** should have been created containing the generated UUIDs for each External Resource.

Once seen, modify (as needed) and run **create_samples_from_dataset.py** to create Material Samples and connect them to the created External Resource URLs. They will be created and linked in the same order they are in from the .txt file from the user.
