import csv
from dinapy.dinaapi import DinaAPI

# Configure path to keycloak configuration
dina = DinaAPI("./keycloak-config.yml")
base_url = "https://dina.local/api/objectstore-api/metadata"
skip = 0

with open('import.csv', 'r') as csvfile, open('output.csv', 'w', newline='') as output_file:
  reader = csv.reader(csvfile)
  writer = csv.writer(output_file)

  # Write header row to output file
  writer.writerow(['original_directory_name', 'barcode'])

  # Skip through already processed records using the skip variable above.
  for _ in range(skip):
    next(reader)

  # Loop through each row
  for row in reader:
    # Filter to be used:
    params = {
      "filter[managedAttributes.original_directory_name][EQ]": row[0],
      "page[limit]": 1000,
      # "include": "derivatives"
    }

    request = dina.get_req_dina(base_url, params=params)
    if request.status_code == 200:
      if request.json()["meta"]["totalResourceCount"] == 1:
        # Generate the output CSV.
        barcode = request.json()["data"][0]["attributes"]["managedAttributes"]["barcode"]
        writer.writerow([row[0], barcode])
        print(row[0] + " found barcode: " + barcode, flush=True)
      else:
        print("Only one record expected, found more or less for: " + row[0], flush=True)
    else:
      print("Status Code:", flush=True)
      print(request.status_code, flush=True)
      print(params, flush=True)
      exit()
