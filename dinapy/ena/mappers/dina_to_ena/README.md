# DINA to ENA Mappers

Mappers for converting DINA entities to ENA XML models for submission to the European Nucleotide Archive.

## Overview

These mappers convert DINA data entities (deserialized via Pydantic models) into ENA submission-ready models:

- **Project** → ENA Project/Study
- **MaterialSample** + **CollectingEvent** → ENA Sample (with auto-resolution)
- **MolecularAnalysisRun** + **User Config** → ENA Experiment
- **Metadata** (object store) → ENA Run

### Key Features

**Auto-resolution**: Taxon IDs automatically resolved from scientific names via NCBI Taxonomy API

**Reverse Geocoding**: Geographic locations derived from coordinates using Nominatim (OpenStreetMap)

**Unmapped Attributes**: DINA fields without ENA equivalents automatically preserved as generic attributes

**Relationship Handling**: Properly links related entities (CollectingEvent → Sample, Project+Sample → Experiment)

## Installation & Setup

The mappers work with DINA Pydantic data objects deserialized from JSON API responses using the `*Document` classes in `dinapy.schemas`.

```python
from dinapy.schemas.material_sample_pydantic import MaterialSampleDocument
from dinapy.ena.mappers.dina_to_ena.mappers_dto import material_sample_to_ena

# Deserialize DINA API response
material_sample_data = MaterialSampleDocument.deserialize(api_response).data

# Map to ENA Sample
ena_sample = material_sample_to_ena(material_sample_data, taxon_id=408172)
```

## Field Mappings

### Project → ENA Project

| ENA Field | DINA Mapping | Notes |
|-----------|--------------|-------|
| `Project.alias` | `data.id` | Unique identifier |
| `Project.title` | `data.attributes.name` | Project name |
| `Project.description` | `multilingualDescription` or managed attributes | Can be overridden via parameter |

### MaterialSample → ENA Sample

| ENA Field | DINA Mapping | Notes |
|-----------|--------------|-------|
| `Sample.alias` | `data.id` | Unique identifier (add timestamp to avoid conflicts) |
| `Sample.title` | `data.attributes.materialSampleName` | Sample name |
| `Sample.organism.taxon_id` | **Auto-resolved** or parameter | Automatically queries NCBI from scientific name |
| `Sample.attributes[collection date]` | `collectingEvent.endEventDateTime` | **Mandatory** - fallback to startEventDateTime |
| `Sample.attributes[geographic location]` | `collectingEvent.dwcCountry` | **Mandatory** - auto-derived from coordinates if missing |
| `Sample.attributes[sample_id]` | `data.attributes.barcode` | Optional barcode |
| `Sample.attributes[...]` | Unmapped DINA attributes | All other fields preserved with prefixes |

#### Auto-Resolution Features:

**Taxon ID Resolution**:
1. Extract scientific name from:
   - `effectiveScientificName` (highest priority)
   - `targetOrganismPrimaryScientificName`
   - `organism_data` parameter (if provided)
   - `managedAttributes.scientificName`
2. Query NCBI Taxonomy API to resolve taxon ID
3. Fall back to environmental sample (taxon ID 1284369) if not found
4. Results are cached to minimize API calls

**Geographic Location Resolution** (Mandatory for ENA):
1. Use `dwcCountry` from collecting event (highest priority)
2. If missing, reverse-geocode from `dwcVerbatimLatitude`/`dwcVerbatimLongitude` using Nominatim API
3. Also checks `geoReferenceAssertions` array for coordinates
4. Fall back to "not provided" (ENA controlled vocabulary term)
5. Format: "Country: State, Locality" or just "Country"

**Collection Date** (Mandatory for ENA):
1. Use `endEventDateTime` from collecting event (highest priority)
2. Fall back to `startEventDateTime`
3. Format: ISO 8601 date/datetime

**Unmapped Attributes**:
- Regular attributes → direct mapping
- `managedAttributes` → prefixed with `managed_`
- `preparationManagedAttributes` → prefixed with `prep_`
- `extensionValues` → flattened with dot notation, prefixed with `ext_`
- CollectingEvent attributes → prefixed with `ce_`

### MolecularAnalysisRun → ENA Experiment

| ENA Field | DINA Mapping | Notes |
|-----------|--------------|-------|
| `Experiment.alias` | `data.id` | Workflow/run ID |
| `Experiment.title` | `data.attributes.name` | Run name |
| `Experiment.study_ref.accession` | External parameter | Must link to existing ENA study |
| `Experiment.design.design_description` | `managedAttributes.objective` | Can be overridden |
| `Experiment.design.sample_descriptor.accession` | External parameter | Must link to ENA sample accession |
| `Experiment.design.library_strategy` | External parameter | From dropdown/config (e.g., "WGS", "RNA-Seq") |
| `Experiment.design.library_source` | External parameter | From dropdown/config (e.g., "GENOMIC") |
| `Experiment.design.library_selection` | External parameter | From dropdown/config (e.g., "RANDOM") |
| `Experiment.design.library_layout` | External parameter | "SINGLE" or "PAIRED" |
| `Experiment.platform.instrument_model` | External parameter | From dropdown/config |

**Required Parameters from Dropdown/Config:**
- `library_strategy`: WGS, RNA-Seq, AMPLICON, METAGENOMIC, etc.
- `library_source`: GENOMIC, TRANSCRIPTOMIC, METAGENOMIC, etc.
- `library_selection`: RANDOM, PCR, unspecified, etc.
- `library_layout_type`: SINGLE or PAIRED
- `instrument_model`: e.g., "Illumina NovaSeq 6000", "MinION"
- `nominal_length` (optional): Fragment length for paired-end
- `nominal_sdev` (optional): Fragment length std dev for paired-end

### Metadata → ENA Run

| ENA Field | DINA Mapping | Notes |
|-----------|--------------|-------|
| `Run.alias` | `data.id` | Object store metadata ID |
| `Run.title` | `data.attributes.acCaption` or `filename` | File caption or name |
| `Run.experiment_ref.accession` | External parameter | Must link to ENA experiment |
| `Run.files[].filename` | `originalFilename` or from `resourceExternalURL` | Derived filename |
| `Run.files[].filetype` | Derived from `fileExtension` | Auto-detected or from dropdown |
| `Run.files[].checksum` | `acHashValue` | MD5 or SHA-256 hash |
| `Run.files[].checksum_method` | Derived from `acHashFunction` | "MD5" or "SHA-256" |

**Supported File Types:**
- fastq, fasta, bam, cram, sra, srf, sff, tab

## Usage Examples

### Single Entity Mapping

```python
from dinapy.schemas.project_pydantic import ProjectDocument
from dinapy.ena.mappers.dina_to_ena.mappers_dto import project_to_ena

# Deserialize DINA API response
project_data = ProjectDocument.deserialize(dina_api_response).data

# Map to ENA Project
ena_project = project_to_ena(
    project=project_data,
    description_override="Study of marine microbial communities"
)
```

### Mapping with Auto-Resolution

```python
from dinapy.schemas.material_sample_pydantic import MaterialSampleDocument
from dinapy.schemas.collecting_event_pydantic import CollectingEventDocument
from dinapy.ena.mappers.dina_to_ena.mappers_dto import material_sample_to_ena
import time

# Deserialize both entities
material_sample_data = MaterialSampleDocument.deserialize(sample_response).data
collecting_event_data = CollectingEventDocument.deserialize(event_response).data

# Map to ENA Sample with auto-resolution
ena_sample = material_sample_to_ena(
    material_sample=material_sample_data,
    collecting_event=collecting_event_data,
    # taxon_id is optional - will auto-resolve from scientific name if not provided
    email="researcher@example.com",  # Recommended for NCBI API
    checklist="ERC000050",  # Optional: GSC MIxS water checklist
    include_unmapped=True  # Include DINA-specific attributes
)

# Add unique timestamp to avoid alias conflicts
timestamp = str(int(time.time()))
ena_sample.alias = f"{ena_sample.alias}_{timestamp}"

print(f"Taxon ID: {ena_sample.organism.taxon_id}")  # Auto-resolved
print(f"Attributes: {len(ena_sample.attributes)}")  # Includes unmapped DINA fields

# Geographic location was automatically derived from coordinates if needed
geo_attr = next(a for a in ena_sample.attributes if "geographic location" in a.tag)
print(f"Location: {geo_attr.value}")  # e.g., "Canada" or "not provided"
```

### Batch Mapping

```python
from dinapy.schemas.material_sample_pydantic import MaterialSampleDocument
from dinapy.ena.mappers.dina_to_ena.mappers_dto import batch_material_samples_to_ena

# Deserialize multiple samples
material_sample_dtos = [MaterialSampleDocument.deserialize(r).data for r in responses]

# Prepare taxon IDs (resolve externally)
taxon_ids = {
    "sample-1": 408172,
    "sample-2": 408172,
    # ...
}

# Batch map
ena_samples = batch_material_samples_to_ena(
    material_samples=material_sample_dtos,
    taxon_ids=taxon_ids,
    checklist="ERC000050"
)
```

### Complete Experiment Mapping

```python
from dinapy.schemas.molecular_analysis_run_pydantic import MolecularAnalysisRunDocument
from dinapy.ena.mappers.dina_to_ena.mappers_dto import molecular_analysis_run_to_ena

# Deserialize
molecular_run_data = MolecularAnalysisRunDocument.deserialize(run_response).data

# Map with library configuration
ena_experiment = molecular_analysis_run_to_ena(
    molecular_run=molecular_run_data,
    study_accession="PRJEB12345",       # From previous ENA submission
    sample_accession="ERS567890",        # From previous ENA submission
    library_strategy="AMPLICON",         # User selection/config
    library_source="METAGENOMIC",        # User selection/config
    library_selection="PCR",             # User selection/config
    library_layout_type="PAIRED",        # User selection/config
    instrument_model="Illumina NovaSeq 6000",  # User selection/config
    design_description="16S rRNA amplicon sequencing",
    nominal_length=300,
    nominal_sdev=50.0
)
```

## Required External Data

### Taxonomy Resolution (Auto-Resolved)
✅ **Automatically handled** by `material_sample_to_ena()` if scientific name is present in DINA
- Queries NCBI Taxonomy API using E-utilities
- Falls back to environmental sample taxon ID (1284369)
- Uses caching to minimize API calls
- Rate-limited to respect NCBI's usage policy (3 requests/second)
- **Manual override**: Provide `taxon_id` parameter if you have pre-resolved IDs

### Geographic Locations (Auto-Resolved)
✅ **Automatically handled** by `material_sample_to_ena()` if coordinates are present
- Extracts from `dwcCountry` field (highest priority)
- Reverse-geocodes from coordinates using Nominatim API (OpenStreetMap)
- Checks both direct fields and `geoReferenceAssertions` array
- Falls back to "not provided" (valid ENA controlled vocabulary term)
- Format matches ENA requirements: "Country: Region, Locality" or "Country"
- **Manual override**: Provide `geographic_location` parameter to bypass auto-resolution

### ENA Accessions (Required for Linking)
⚠️ **Must be obtained from previous submissions**:
- **Study/Project Accessions**: Submit project first → get accession (e.g., PRJEB12345)
- **Sample Accessions**: Submit samples → get accessions (e.g., ERS567890 or SAMEA123456)
- **Experiment Accessions**: Submit experiments → get accessions (e.g., ERX123456)
- These accessions are required for linking: Experiment needs Project+Sample, Run needs Experiment
- Use `receipt.get_accession('PROJECT')` to extract from submission receipts

### Sequencing Parameters (Required for Experiments)
⚠️ **Must be provided by user** - cannot be mapped from DINA:
- `library_strategy`: e.g., "WGS", "RNA-Seq", "AMPLICON", "METAGENOMIC"
- `library_source`: e.g., "GENOMIC", "TRANSCRIPTOMIC", "METAGENOMIC"
- `library_selection`: e.g., "RANDOM", "PCR", "unspecified"
- `library_layout_type`: "SINGLE" or "PAIRED"
- `instrument_model`: e.g., "Illumina NovaSeq 6000", "MinION"
- These should come from user forms, configuration files, or protocol documentation

## API Reference

### Core Mappers

#### `project_to_ena(project, description_override)`
Maps DINA `ProjectData` to ENA Project.

**Parameters:**
- `project` (`ProjectData`): Deserialized DINA project
- `description_override` (str, optional): Override project description

**Returns:** `Project` - ENA Project model

#### `material_sample_to_ena(material_sample, collecting_event, taxon_id, checklist, geographic_location, organism_data, email, taxon_cache, include_unmapped)`
Maps DINA `MaterialSampleData` to ENA Sample with auto-resolution.

**Parameters:**
- `material_sample` (`MaterialSampleData`): Deserialized DINA material sample (**required**)
- `collecting_event` (`CollectingEventData`, optional): Related collecting event (provides collection date and location)
- `taxon_id` (int, optional): NCBI Taxonomy ID - if not provided, auto-resolved from scientific name
- `checklist` (str, optional): ENA checklist ID (e.g., "ERC000011")
- `geographic_location` (str, optional): Override auto-resolved location
- `organism_data` (dict, optional): Organism data from DINA relationship (alternative source for scientific name)
- `email` (str, optional): Email for NCBI API requests (recommended)
- `taxon_cache` (dict, optional): Cache dict for taxon lookups and geocoding (improves performance)
- `include_unmapped` (bool, optional): Include unmapped DINA attributes (default: True)

**Returns:** `Sample` - ENA Sample model

**Auto-Resolution:**
- If `taxon_id` not provided: Queries NCBI Taxonomy API using scientific name from DINA
- If `geographic_location` not provided: Reverse-geocodes from coordinates or uses dwcCountry
- Collection date automatically extracted from collecting event
- All unmapped DINA fields preserved as generic ENA attributes

#### `molecular_analysis_run_to_ena(molecular_run, study_accession, sample_accession, ...)`
Maps DINA `MolecularAnalysisRunData` to ENA Experiment.

**Required Parameters:**
- `molecular_run` (`MolecularAnalysisRunData`): Deserialized run
- `study_accession` (str): ENA study accession
- `sample_accession` (str): ENA sample accession
- `library_strategy` (str): Library strategy
- `library_source` (str): Library source
- `library_selection` (str): Library selection method
- `library_layout_type` (str): "SINGLE" or "PAIRED"
- `instrument_model` (str): Sequencing instrument

**Returns:** `Experiment` - ENA Experiment model

#### `metadata_to_ena_run(metadata, experiment_accession, filetype, checksum, checksum_method)`
Maps DINA `MetadataData` to ENA Run.

**Parameters:**
- `metadata` (`MetadataData`): Deserialized metadata
- `experiment_accession` (str): ENA experiment accession
- `filetype` (str, optional): Override file type
- `checksum` (str, optional): Override checksum
- `checksum_method` (str): "MD5" or "SHA-256" (default: "MD5")

**Returns:** `Run` - ENA Run model

### Batch Mappers

See docstrings in `mappers_dto.py` for batch mapper signatures and usage.

## See Also

- [ENA Submission Documentation](https://ena-docs.readthedocs.io/)
- [ENA XML Schema Documentation](https://github.com/enasequence/schema)
- [NCBI Taxonomy](https://www.ncbi.nlm.nih.gov/taxonomy)
- Example: `examples/ena/dina_to_ena_mapping_example.py`
