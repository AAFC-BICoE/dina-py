# Query and create a new CSV with a different field

This Python script is designed to:

1. Read a CSV file: Takes an input CSV file containing a list of original directory names.
2. Query Dina API: For each directory name, queries the Dina API to retrieve a specific attribute (barcode).
3. Write to CSV: Writes the original directory name and the retrieved barcode to a new CSV file.

# Instructions

### 1. Configure the keycloak-config.sample.yml

Create a copy and rename the `keycloak-config.sample.yml` to be `keycloak-config.yml`. Change the configuration to use the environment you wish to run this script on.

This script is read only and does not create/update records.

### 2. Update the `base_url` variable inside `main.py`.

Update the variable to match your keycloak config settings.

It will need to end with `/api/objectstore-api/metadata`, for example:

```
https://dina.local/api/objectstore-api/metadata
```

### 3. Provide an import.csv file

This file should contain a original filename value to search for, for example:

```csv
objectName_1
objectName_2
objectName_3
```

Each original filename needs to be on it's own line.

### 4. Run the script

Run the script:

```shell
python3 main.py 
```

This can take a while to run. An output.csv file will be created.
