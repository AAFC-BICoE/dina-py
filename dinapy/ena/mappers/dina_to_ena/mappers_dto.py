"""
Mappers for converting DINA Pydantic data objects to ENA XML models.

These mappers work with DINA Pydantic data objects (JsonApiData subclasses) deserialized
from JSON API responses using the schemas in dinapy.schemas.

DINA → ENA Entity Mapping Overview:
===================================

1. ENA PROJECT ← DINA Project
   - Direct mapping of name, description, and metadata
   - Unmapped DINA attributes → generic ENA attributes
   
2. ENA SAMPLE ← DINA MaterialSample + CollectingEvent
   - MaterialSample provides: alias, title, barcode, preparation info
   - CollectingEvent provides: collection date, geographic location
   - Taxon ID resolved from scientific name or provided by user
   - Unmapped attributes from both entities included with prefixes

3. ENA EXPERIMENT ← DINA MolecularAnalysisRun + USER CONFIGURATION
   - MolecularAnalysisRun provides: alias, title, description
   - USER MUST PROVIDE: library parameters and platform (cannot be mapped from DINA)
     * library_strategy (e.g., "AMPLICON", "WGS", "RNA-Seq")
     * library_source (e.g., "METAGENOMIC", "GENOMIC")
     * library_selection (e.g., "PCR", "RANDOM")
     * library_layout_type ("SINGLE" or "PAIRED")
     * instrument_model (e.g., "Illumina NovaSeq 6000")
   - These parameters should come from user forms, config files, or protocol docs

4. ENA RUN ← DINA Metadata (object store)
   - Metadata provides: filename, checksum, file metadata
   - File type derived from extension
   - Unmapped object store metadata included as attributes

Unmapped Attributes:
===================
All mappers support automatic inclusion of unmapped DINA attributes as generic
ENA Attribute(tag=key, value=value) objects. This preserves DINA metadata that
doesn't have explicit ENA equivalents.

- Regular attributes mapped directly
- managedAttributes prefixed with "managed_"
- preparationManagedAttributes prefixed with "prep_"
- CollectingEvent attributes prefixed with "ce_"

Example usage:
    ```python
    from dinapy.schemas.project_pydantic import ProjectDocument
    from dinapy.ena.mappers.dina_to_ena.mappers_dto import project_to_ena
    
    # Deserialize DINA API response
    project_data = ProjectDocument.deserialize(api_response).data
    
    # Convert to ENA model
    ena_project = project_to_ena(project_data, description_override="Study description")
    
    # Submit using ENASubmissionWorkflow
    from dinapy.ena.submission import ENASubmissionWorkflow
    workflow = ENASubmissionWorkflow(test=True)
    receipt = workflow.submit_project(ena_project)
    ```
"""
from __future__ import annotations
from typing import Optional, List

# Import DINA Pydantic data types (JsonApiData subclasses) for type hints
from dinapy.schemas.project_pydantic import ProjectData
from dinapy.schemas.material_sample_pydantic import MaterialSampleData
from dinapy.schemas.collecting_event_pydantic import CollectingEventData
from dinapy.schemas.molecular_analysis_run_pydantic import MolecularAnalysisRunData
from dinapy.schemas.metadata_pydantic import MetadataData

# Import ENA models
from dinapy.ena.models import (
    Project, Sample, Organism, Attribute,
    Experiment, Design, LibraryDescriptor, LibraryLayout, Platform, ObjectRef,
    Run, DataBlock, File
)

# For NCBI Taxonomy lookups
import requests
import time
from urllib.parse import quote


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def safe_get_attr(obj, attr: str, default=None):
    """Safely get an attribute, handling 'undefined' strings and None values.
    
    Works with both dictionaries and objects with attributes.
    """
    if obj is None:
        return default
    
    # Handle dict-like objects
    if isinstance(obj, dict):
        value = obj.get(attr, default)
    else:
        # Handle object attributes
        value = getattr(obj, attr, default)
    
    if value == 'undefined' or value is None:
        return default
    return value


def get_managed_attribute(attributes_obj, key: str, default=None):
    """Extract a value from managedAttributes or preparationManagedAttributes."""
    if attributes_obj is None:
        return default
    
    managed = safe_get_attr(attributes_obj, 'managedAttributes', {})
    prep_managed = safe_get_attr(attributes_obj, 'preparationManagedAttributes', {})
    
    if isinstance(managed, dict) and key in managed:
        value = managed[key]
        if value != 'undefined' and value is not None:
            return value
    
    if isinstance(prep_managed, dict) and key in prep_managed:
        value = prep_managed[key]
        if value != 'undefined' and value is not None:
            return value
    
    return default


def extract_filename_from_url(url: str) -> str:
    """Extract filename from a URL or path."""
    if not url or url == 'undefined':
        return ""
    return url.split("/")[-1].split("?")[0]


def derive_filetype_from_extension(extension: str) -> str:
    """
    Derive ENA-compatible filetype from file extension.
    
    Supported ENA filetypes: sra, srf, sff, fastq, fasta, tab, bam, cram,
                             CompleteGenomics_native, OxfordNanopore_native, PacBio_HDF5
    """
    if not extension or extension == 'undefined':
        return "fastq"
    
    ext_lower = extension.lower().lstrip(".")
    
    filetype_map = {
        "fastq": "fastq",
        "fq": "fastq",
        "fastq.gz": "fastq",
        "fq.gz": "fastq",
        "fasta": "fasta",
        "fa": "fasta",
        "fna": "fasta",
        "fasta.gz": "fasta",
        "fa.gz": "fasta",
        "bam": "bam",
        "cram": "cram",
        "sra": "sra",
        "srf": "srf",
        "sff": "sff",
        "tab": "tab",
        "tsv": "tab",
        "txt": "tab"
    }
    
    return filetype_map.get(ext_lower, "fastq")


def resolve_taxon_id_from_scientific_name(
    scientific_name: str,
    email: Optional[str] = None,
    cache: Optional[dict] = None
) -> Optional[int]:
    """
    Resolve NCBI taxon ID from scientific name using NCBI E-utilities.
    
    Uses NCBI's Entrez E-utilities API to search the taxonomy database.
    Ref: https://www.ncbi.nlm.nih.gov/books/NBK25499/
    
    Args:
        scientific_name: Scientific name (e.g., "Homo sapiens", "Escherichia coli")
        email: Email for NCBI API (recommended to identify your application)
        cache: Optional dict to cache lookups (key: scientific_name, value: taxon_id)
    
    Returns:
        NCBI taxon ID as integer, or None if not found
    
    Example:
        >>> resolve_taxon_id_from_scientific_name("Homo sapiens")
        9606
        >>> resolve_taxon_id_from_scientific_name("Escherichia coli")
        562
    
    Note:
        - Be respectful of NCBI's server resources
        - If making many requests, consider using a local cache
        - NCBI requests that you provide an email address
        - Rate limit: max 3 requests/second without API key
    """
    if not scientific_name or scientific_name == 'undefined':
        return None
    
    # Check cache first
    if cache is not None and scientific_name in cache:
        return cache[scientific_name]
    
    try:
        # Build the E-utilities esearch URL
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'taxonomy',
            'term': scientific_name,
            'retmode': 'json',
            'retmax': 1
        }
        
        if email:
            params['email'] = email
        
        # Make the request
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        # Extract taxon ID from search results
        id_list = data.get('esearchresult', {}).get('idlist', [])
        
        if id_list:
            taxon_id = int(id_list[0])
            
            # Cache the result
            if cache is not None:
                cache[scientific_name] = taxon_id
            
            # Be nice to NCBI servers - rate limit
            time.sleep(0.34)  # ~3 requests per second
            
            return taxon_id
        
        return None
    
    except (requests.RequestException, ValueError, KeyError) as e:
        # Log the error but don't crash
        print(f"Warning: Failed to resolve taxon ID for '{scientific_name}': {e}")
        return None


def resolve_country_from_coordinates(
    latitude: float,
    longitude: float,
    cache: Optional[dict] = None
) -> Optional[str]:
    """
    Reverse geocode coordinates to get country name using Nominatim (OpenStreetMap).
    
    Args:
        latitude: Decimal latitude
        longitude: Decimal longitude
        cache: Optional dict to cache results (key: "lat,lon" -> country)
    
    Returns:
        Country name string matching ENA's controlled vocabulary, or None if lookup fails
    
    Example:
        >>> resolve_country_from_coordinates(45.38, -75.71)
        'Canada'
    
    Note:
        - Uses Nominatim API (free, no API key required)
        - Results are cached to minimize API calls
        - Rate limited to be respectful to the service
        - Returns None on network errors or lookup failures
    """
    # Check cache first
    cache_key = f"{latitude},{longitude}"
    if cache is not None and cache_key in cache:
        return cache[cache_key]
    
    try:
        # Nominatim reverse geocoding API
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'zoom': 3,  # Country level
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'DINA-ENA-Mapper/1.0'  # Required by Nominatim usage policy
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract country from address
        country = data.get('address', {}).get('country')
        
        if country:
            # Cache the result
            if cache is not None:
                cache[cache_key] = country
            
            # Be respectful to Nominatim - rate limit to 1 request per second
            time.sleep(1.0)
            
            return country
        
        return None
    
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Warning: Failed to resolve country for coordinates ({latitude}, {longitude}): {e}")
        return None


def extract_scientific_name_from_material_sample(
    material_sample: MaterialSampleData,
    organism_data: Optional[dict] = None
) -> Optional[str]:
    """
    Extract scientific name from MaterialSample data.
    
    Looks in multiple places (in priority order):
    1. Direct attributes: effectiveScientificName, targetOrganismPrimaryScientificName
    2. organism_data parameter (if organism was fetched separately)
    3. managedAttributes (common custom field location)
    4. extensionValues
    
    Args:
        material_sample: MaterialSampleData
        organism_data: Optional dict with organism information from DINA organism relationship.
                       Can be in two formats:
                       1. From included array: {"id": "...", "type": "organism", "attributes": {...}}
                       2. From separate API call: {"data": {"id": "...", "type": "organism", "attributes": {...}}}
    
    Returns:
        Scientific name string, or None if not found
    
    Note:
        The organism data structure from DINA typically looks like:
        {
            "id": "...",
            "type": "organism",
            "attributes": {
                "determination": [{
                    "verbatimScientificName": "Species name",
                    "scientificName": "Species name",
                    "isPrimary": true
                }]
            }
        }
    """
    attrs = material_sample.attributes
    
    # First, try direct attributes (most reliable)
    effective_name = safe_get_attr(attrs, 'effectiveScientificName')
    if effective_name and effective_name != 'undefined':
        return effective_name
    
    target_name = safe_get_attr(attrs, 'targetOrganismPrimaryScientificName')
    if target_name and target_name != 'undefined':
        return target_name
    
    # Try organism data if provided
    if organism_data:
        try:
            # Handle both formats:
            # 1. With "data" wrapper: {"data": {"id": "...", "type": "organism", "attributes": {...}}}
            # 2. Without "data" wrapper (from included array): {"id": "...", "type": "organism", "attributes": {...}}
            if 'data' in organism_data:
                # Format with "data" wrapper (separate API call)
                organism_attrs = organism_data.get('data', {}).get('attributes', {})
            else:
                # Format without "data" wrapper (from included array)
                organism_attrs = organism_data.get('attributes', {})
            
            determinations = organism_attrs.get('determination', [])
            for det in determinations:
                # Check if this is the primary determination
                if det.get('isPrimary'):
                    # Try scientificName first, then verbatimScientificName
                    sci_name = det.get('scientificName') or det.get('verbatimScientificName')
                    if sci_name and sci_name != 'undefined':
                        return sci_name
            # If no primary, take the first one
            if determinations:
                sci_name = determinations[0].get('scientificName') or determinations[0].get('verbatimScientificName')
                if sci_name and sci_name != 'undefined':
                    return sci_name
        except (AttributeError, KeyError):
            pass
    
    # Try managedAttributes
    sci_name = get_managed_attribute(attrs, 'scientificName')
    if sci_name:
        return sci_name
    
    return None


def is_valid_attribute_value(value) -> bool:
    """Check if a value is valid for ENA attribute (not None, undefined, empty, or complex object)."""
    if value is None or value == 'undefined':
        return False
    if isinstance(value, (dict, list)):
        return False
    str_val = str(value).strip().lower()
    return str_val not in ('', 'none', 'undefined')


def flatten_dict(d: dict, parent_key: str = '', sep: str = '.') -> dict:
    """
    Flatten a nested dictionary using dot notation.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator between keys (default: '.')
    
    Returns:
        Flattened dictionary with dot-notation keys
    
    Example:
        >>> flatten_dict({'a': {'b': 1, 'c': 2}})
        {'a.b': 1, 'a.c': 2}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def extract_unmapped_attributes(
    attributes_obj,
    exclude_keys: set,
) -> List[Attribute]:
    """
    Extract unmapped attributes from a DINA attributes object as generic ENA Attribute objects.
    
    Always extracts:
        - managedAttributes (prefixed with 'managed_')
        - preparationManagedAttributes (prefixed with 'prep_')
        - extensionValues (flattened with dot notation, prefixed with 'ext_')
    
    Args:
        attributes_obj: The attributes object from a DINA data object (e.g., material_sample.attributes)
        exclude_keys: Set of attribute keys that were already explicitly mapped
    
    Returns:
        List of ENA Attribute objects for unmapped fields
    
    Example:
        extensionValues = {
            "mixs_soil_v4": {
                "store_cond": "6months/-80oC",
                "env_package": "Soil"
            }
        }
        
        Produces:
        - Attribute(tag="ext_mixs_soil_v4.store_cond", value="6months/-80oC")
        - Attribute(tag="ext_mixs_soil_v4.env_package", value="Soil")
    """
    if attributes_obj is None:
        return []
    
    # Convert to dict if needed
    if isinstance(attributes_obj, dict):
        attrs_dict = attributes_obj
    else:
        attrs_dict = {k: v for k, v in vars(attributes_obj).items() if not k.startswith('_')} if hasattr(attributes_obj, '__dict__') else {}
    
    # Fields to always skip (metadata, relationships, complex structures)
    # Note: managedAttributes, preparationManagedAttributes, and extensionValues are processed separately
    skip_fields = {
        'managedAttributes', 'preparationManagedAttributes', 'extensionValues',
        'type', 'version', 'createdOn', 'createdBy', 'group', 'relationships', 
        'id', 'sourceSet', 'isRestricted', 'restrictionRemarks', 'restrictionFieldsExtension',
        'allowDuplicateName', 'publiclyReleasable', 'notPubliclyReleasableReason',
        'tags', 'stateChangedOn', 'stateChangeRemarks', 'hierarchy',
        'targetOrganismPrimaryClassification', 'associations', 'identifiers'
    }
    
    attributes = []
    
    # Process regular attributes
    for key, value in attrs_dict.items():
        if key in exclude_keys or key in skip_fields:
            continue
        if is_valid_attribute_value(value):
            attributes.append(Attribute(tag=key, value=str(value)))
    
    # Always process managedAttributes, preparationManagedAttributes, and extensionValues
    for managed_field, prefix in [
        ('managedAttributes', 'managed_'),
        ('preparationManagedAttributes', 'prep_')
    ]:
        managed = safe_get_attr(attributes_obj, managed_field, {})
        if isinstance(managed, dict):
            for key, value in managed.items():
                if key not in exclude_keys and is_valid_attribute_value(value):
                    attributes.append(Attribute(tag=f"{prefix}{key}", value=str(value)))
    
    # Process extensionValues with flattening
    extension_values = safe_get_attr(attributes_obj, 'extensionValues', {})
    if isinstance(extension_values, dict):
        # Flatten the nested structure
        flattened = flatten_dict(extension_values)
        for key, value in flattened.items():
            if key not in exclude_keys and is_valid_attribute_value(value):
                attributes.append(Attribute(tag=f"ext_{key}", value=str(value)))
    
    return attributes


# =============================================================================
# SINGLE ENTITY MAPPERS
# =============================================================================

def project_to_ena(
    project: ProjectData,
    description_override: Optional[str] = None,
    include_unmapped: bool = True
) -> Project:
    """
    Map DINA Project data to ENA Project.
    
    Mapping:
        - Project.alias <- project.id
        - Project.title <- project.attributes.name
        - Project.description <- description_override or multilingualDescription
        - Unmapped attributes <- generic Attribute objects (if include_unmapped=True)
    
    Args:
        project: DINA ProjectData
        description_override: Optional description override (e.g., from dropdown on export)
        include_unmapped: If True, include unmapped DINA attributes as generic ENA attributes
    
    Returns:
        ENA Project model
    """
    alias = project.id or ""
    attrs = project.attributes
    
    # Get title
    title = safe_get_attr(attrs, 'name', 'Untitled Project')
    if title == 'undefined':
        title = 'Untitled Project'
    
    # Get description (priority: override > multilingualDescription > managed attributes)
    description = description_override
    if not description:
        multilingual_desc = safe_get_attr(attrs, 'multilingualDescription')
        if isinstance(multilingual_desc, dict):
            descs = multilingual_desc.get('descriptions', [])
            if descs:
                description = " ".join(d.get('desc', '') for d in descs if d.get('desc'))
    if not description:
        description = get_managed_attribute(attrs, 'description') or "No description"
    
    # Extract unmapped attributes
    mapped_keys = {'name', 'multilingualDescription', 'description'}
    attributes = extract_unmapped_attributes(attrs, mapped_keys) if include_unmapped else []
    
    return Project(
        alias=alias,
        title=title,
        description=description,
        sequencingProject={},
        project_links=[],
        attributes=attributes
    )


def material_sample_to_ena(
    material_sample: MaterialSampleData,
    collecting_event: Optional[CollectingEventData] = None,
    taxon_id: Optional[int] = None,
    checklist: Optional[str] = None,
    geographic_location: Optional[str] = None,
    organism_data: Optional[dict] = None,
    email: Optional[str] = None,
    taxon_cache: Optional[dict] = None,
    include_unmapped: bool = True
) -> Sample:
    """
    Map DINA MaterialSample data to ENA Sample.
    
    Mapping:
        - Sample.alias <- material_sample.id
        - Sample.title <- material_sample.attributes.materialSampleName
        - Sample.organism.taxon_id <- taxon_id parameter OR auto-resolved from scientific name
        - Sample.geographic_location <- collecting_event (dwcCountry > reverse geocode from coords > "not provided")
        - Sample.collection_date <- collecting_event (endEventDateTime > startEventDateTime)
        - Unmapped attributes <- generic Attribute objects (if include_unmapped=True)
    
    Args:
        material_sample: DINA MaterialSampleData
        collecting_event: Optional related CollectingEventData
        taxon_id: NCBI taxon ID (if not provided, will attempt to auto-resolve)
        checklist: Optional ENA checklist identifier (e.g., "ERC000011")
        geographic_location: Optional geographic location override
        organism_data: Optional organism data from DINA (contains scientific name)
        email: Email for NCBI API requests (recommended)
        taxon_cache: Optional dict to cache taxon ID AND coordinate lookups (keys: scientific_name, 'geo_cache')
        include_unmapped: If True, include unmapped DINA attributes as generic ENA attributes
    
    Returns:
        ENA Sample model
    
    Note:
        If taxon_id is not provided, the function will attempt to:
        1. Extract scientific name from organism_data or material_sample
        2. Query NCBI Taxonomy database to resolve taxon ID
        3. Fall back to environmental sample taxon ID (1284369) if resolution fails
        
        Collection date and geographic location are MANDATORY for ENA. The mapper will:
        - Collection date: Use endEventDateTime > startEventDateTime from collecting event
        - Geographic location: Use dwcCountry > reverse geocode from coordinates > "not provided"
        - Reverse geocoding uses Nominatim (OpenStreetMap) API - free, no API key required
    """
    alias = material_sample.id or ""
    attrs = material_sample.attributes
    
    # Get title
    title = safe_get_attr(attrs, 'materialSampleName') or safe_get_attr(attrs, 'dwcCatalogNumber') or alias
    
    # Resolve taxon ID if not provided
    if not taxon_id:
        scientific_name = extract_scientific_name_from_material_sample(material_sample, organism_data)
        if scientific_name:
            taxon_id = resolve_taxon_id_from_scientific_name(scientific_name, email=email, cache=taxon_cache)
    taxon_id = taxon_id or 1284369  # Fall back to environmental sample
    
    # Build explicitly mapped attributes
    attributes = []
    if checklist:
        attributes.append(Attribute(tag="ENA-CHECKLIST", value=checklist))
    
    # Collection date and geographic location from collecting event (MANDATORY for ENA)
    if collecting_event:
        ce_attrs = collecting_event.attributes
        
        # Collection date: try endEventDateTime first, fall back to startEventDateTime
        collection_date = safe_get_attr(ce_attrs, 'endEventDateTime') or safe_get_attr(ce_attrs, 'startEventDateTime')
        if collection_date and collection_date != 'undefined':
            attributes.append(Attribute(tag="collection date", value=str(collection_date)))
        
        # Geographic location: try dwcCountry, fall back to reverse geocoding from coordinates
        if not geographic_location:
            country = safe_get_attr(ce_attrs, 'dwcCountry')
            state = safe_get_attr(ce_attrs, 'dwcStateProvince')
            
            if country:
                geographic_location = country if not state else f"{country}: {state}"
            else:
                # Try to derive country from coordinates using reverse geocoding
                lat = safe_get_attr(ce_attrs, 'dwcVerbatimLatitude')
                lon = safe_get_attr(ce_attrs, 'dwcVerbatimLongitude')
                
                # Also check geoReferenceAssertions if direct fields are empty
                if not lat or not lon:
                    geo_refs = safe_get_attr(ce_attrs, 'geoReferenceAssertions', [])
                    if geo_refs and len(geo_refs) > 0:
                        # Get the primary assertion or first one
                        primary = next((g for g in geo_refs if g.get('isPrimary')), geo_refs[0])
                        lat = primary.get('dwcDecimalLatitude')
                        lon = primary.get('dwcDecimalLongitude')
                
                if lat and lon:
                    try:
                        lat_float = float(lat)
                        lon_float = float(lon)
                        # Initialize cache if not provided
                        if taxon_cache is not None and 'geo_cache' not in taxon_cache:
                            taxon_cache['geo_cache'] = {}
                        geo_cache = taxon_cache.get('geo_cache', {}) if taxon_cache else None
                        
                        country = resolve_country_from_coordinates(lat_float, lon_float, cache=geo_cache)
                        if country:
                            geographic_location = country if not state else f"{country}: {state}"
                    except (ValueError, TypeError):
                        pass
                
                # Fall back to "not provided" if still no location
                if not geographic_location:
                    geographic_location = "not provided"
    
    # Ensure geographic location is always present (MANDATORY for ENA)
    if geographic_location:
        attributes.append(Attribute(tag="geographic location (country and/or sea)", value=geographic_location))
    
    # Additional material sample attributes
    if prep_date := safe_get_attr(attrs, 'preparationDate'):
        attributes.append(Attribute(tag="collection date", value=str(prep_date)))
    if barcode := safe_get_attr(attrs, 'barcode'):
        attributes.append(Attribute(tag="sample_id", value=str(barcode)))
    
    # Add unmapped attributes
    if include_unmapped:
        mapped_keys = {'materialSampleName', 'dwcCatalogNumber', 'preparationDate', 'barcode',
                      'effectiveScientificName', 'targetOrganismPrimaryScientificName'}
        attributes.extend(extract_unmapped_attributes(attrs, mapped_keys))
        
        # Add unmapped collecting event attributes with prefix
        if collecting_event:
            ce_mapped = {'endEventDateTime', 'startEventDateTime', 'dwcCountry', 'dwcStateProvince',
                        'dwcVerbatimLatitude', 'dwcVerbatimLongitude', 'geoReferenceAssertions'}
            ce_unmapped = extract_unmapped_attributes(collecting_event.attributes, ce_mapped)
            for attr in ce_unmapped:
                attr.tag = f"ce_{attr.tag}"
            attributes.extend(ce_unmapped)
    
    return Sample(
        alias=alias,
        title=title,
        organism=Organism(taxonId=taxon_id),
        attributes=attributes
    )


def molecular_analysis_run_to_ena(
    molecular_run: MolecularAnalysisRunData,
    study_accession: str,
    sample_accession: str,
    library_strategy: str,
    library_source: str,
    library_selection: str,
    library_layout_type: str,
    instrument_model: str,
    design_description: Optional[str] = None,
    nominal_length: Optional[int] = None,
    nominal_sdev: Optional[float] = None,
    include_unmapped: bool = True
) -> Experiment:
    """
    Map DINA MolecularAnalysisRun data to ENA Experiment.
    
    IMPORTANT: Library and platform parameters CANNOT be directly mapped from DINA and must
    be provided by the user. These represent sequencing methodology choices that are not
    typically stored in DINA's MolecularAnalysisRun entity.
    
    Mapping:
        - Experiment.alias <- molecular_run.id
        - Experiment.title <- molecular_run.attributes.name
        - Experiment.study_ref <- study_accession parameter (USER PROVIDED)
        - Experiment.design.sample_descriptor <- sample_accession parameter (USER PROVIDED)
        - Experiment.design.library_descriptor.* <- USER PROVIDED PARAMETERS
        - Experiment.platform.instrument_model <- USER PROVIDED PARAMETER
        - Unmapped attributes <- generic Attribute objects (if include_unmapped=True)
    
    Args:
        molecular_run: DINA MolecularAnalysisRunData (provides alias, title, description)
        study_accession: ENA study accession - USER MUST PROVIDE (e.g., "PRJEB12345")
        sample_accession: ENA sample accession - USER MUST PROVIDE (e.g., "ERS123456")
        library_strategy: USER MUST PROVIDE - e.g., "WGS", "RNA-Seq", "AMPLICON", "METAGENOMIC"
        library_source: USER MUST PROVIDE - e.g., "GENOMIC", "TRANSCRIPTOMIC", "METAGENOMIC"
        library_selection: USER MUST PROVIDE - e.g., "RANDOM", "PCR", "unspecified"
        library_layout_type: USER MUST PROVIDE - "SINGLE" or "PAIRED"
        instrument_model: USER MUST PROVIDE - e.g., "Illumina NovaSeq 6000", "MinION"
        design_description: Optional experiment design description
        nominal_length: Fragment length for paired-end (required if PAIRED layout)
        nominal_sdev: Fragment length standard deviation for paired-end
        include_unmapped: If True, include unmapped DINA attributes as generic ENA attributes
    
    Returns:
        ENA Experiment model
    
    Example:
        ```python
        # After submitting project and sample, get their accessions
        project_accession = project_receipt.get_accession('PROJECT')  # e.g., 'PRJEB12345'
        sample_accession = sample_receipt.get_accession('SAMPLE')    # e.g., 'ERS567890'
        
        # User must provide sequencing parameters that aren't in DINA
        experiment = molecular_analysis_run_to_ena(
            molecular_run=molecular_analysis_run_data,
            study_accession=project_accession,
            sample_accession=sample_accession,
            library_strategy="AMPLICON",        # User config
            library_source="METAGENOMIC",       # User config
            library_selection="PCR",            # User config
            library_layout_type="PAIRED",       # User config
            instrument_model="Illumina NovaSeq 6000"  # User config
        )
        ```
    """
    alias = molecular_run.id or ""
    attrs = molecular_run.attributes
    
    # Get title
    title = safe_get_attr(attrs, 'name') or f"Molecular Analysis Run {alias}"
    
    # Get design description
    if not design_description:
        design_description = (get_managed_attribute(attrs, 'objective') or 
                            get_managed_attribute(attrs, 'description') or
                            f"Sequencing experiment for {title}")
    
    # Build experiment components
    design = Design(
        designDescription=design_description,
        sampleDescriptor=ObjectRef(accession=sample_accession),
        libraryDescriptor=LibraryDescriptor(
            libraryStrategy=library_strategy,
            librarySource=library_source,
            librarySelection=library_selection,
            libraryLayout=LibraryLayout(
                layoutType=library_layout_type,
                nominalLength=nominal_length,
                nominalSdev=nominal_sdev
            )
        )
    )
    
    experiment = Experiment(
        alias=alias,
        title=title,
        studyRef=ObjectRef(accession=study_accession),
        design=design,
        platform=Platform(instrumentModel=instrument_model)
    )
    
    # Add unmapped attributes if experiment model supports it
    if include_unmapped and hasattr(experiment, 'attributes'):
        mapped_keys = {'name', 'objective', 'description'}
        experiment.attributes = extract_unmapped_attributes(attrs, mapped_keys)
    
    return experiment


def metadata_to_ena_run(
    metadata: MetadataData,
    experiment_accession: str,
    filetype: Optional[str] = None,
    checksum: Optional[str] = None,
    checksum_method: str = "MD5",
    include_unmapped: bool = True
) -> Run:
    """
    Map DINA Metadata data (object store) to ENA Run.
    
    Mapping:
        - Run.alias <- metadata.id
        - Run.title <- metadata.attributes.acCaption or filename
        - Run.experiment_ref <- experiment_accession parameter
        - Run.files[].filename <- originalFilename or derived from resourceExternalURL
        - Run.files[].filetype <- derived from fileExtension or override
        - Run.files[].checksum <- acHashValue or override
        - Unmapped attributes <- generic Attribute objects (if include_unmapped=True)
    
    Args:
        metadata: DINA MetadataData (object store)
        experiment_accession: ENA experiment accession (e.g., "ERX123456")
        filetype: Optional filetype override (e.g., "fastq", "bam")
        checksum: Optional checksum override
        checksum_method: "MD5" or "SHA-256"
        include_unmapped: If True, include unmapped DINA attributes as generic ENA attributes
    
    Returns:
        ENA Run model
    """
    alias = metadata.id or ""
    attrs = metadata.attributes
    
    # Get title (priority: acCaption > originalFilename > filename > alias)
    title = (safe_get_attr(attrs, 'acCaption') or 
             safe_get_attr(attrs, 'originalFilename') or 
             safe_get_attr(attrs, 'filename') or 
             alias)
    
    # Get filename
    filename = safe_get_attr(attrs, 'originalFilename') or safe_get_attr(attrs, 'filename')
    if not filename:
        if external_url := safe_get_attr(attrs, 'resourceExternalURL'):
            filename = extract_filename_from_url(external_url)
    filename = filename or title
    
    # Derive filetype
    if not filetype:
        if file_ext := safe_get_attr(attrs, 'fileExtension'):
            filetype = derive_filetype_from_extension(file_ext)
        elif "." in filename:
            filetype = derive_filetype_from_extension(filename.split(".")[-1])
        else:
            filetype = "fastq"
    
    # Get checksum
    if not checksum:
        checksum = safe_get_attr(attrs, 'acHashValue')
        if checksum:
            # Infer checksum method from hash function
            hash_function = safe_get_attr(attrs, 'acHashFunction', '').upper()
            if 'SHA' in hash_function or '256' in hash_function:
                checksum_method = "SHA-256"
            else:
                checksum_method = "MD5"
    
    if not checksum:
        # Placeholder - in production, compute from file
        checksum = "0" * 32
    
    # Create run
    run = Run(
        alias=alias,
        title=title,
        experimentRef=ObjectRef(accession=experiment_accession),
        dataBlocks=[DataBlock(files=[File(
            filename=filename,
            filetype=filetype,
            checksumMethod=checksum_method,
            checksum=checksum
        )])]
    )
    
    # Add unmapped attributes if run model supports it
    if include_unmapped and hasattr(run, 'attributes'):
        mapped_keys = {'acCaption', 'originalFilename', 'filename', 'resourceExternalURL',
                      'fileExtension', 'acHashValue', 'acHashFunction'}
        run.attributes = extract_unmapped_attributes(attrs, mapped_keys)
    
    return run


# =============================================================================
# BATCH MAPPERS
# =============================================================================

def batch_material_samples_to_ena(
    material_samples: List[MaterialSampleData],
    collecting_events: Optional[dict[str, CollectingEventData]] = None,
    taxon_ids: Optional[dict[str, int]] = None,
    organism_data: Optional[dict[str, dict]] = None,
    checklist: Optional[str] = None,
    email: Optional[str] = None,
    auto_resolve_taxa: bool = True
) -> List[Sample]:
    """
    Batch map DINA MaterialSample data objects to ENA Samples.
    
    Args:
        material_samples: List of DINA MaterialSampleData objects
        collecting_events: Dict mapping material sample IDs to CollectingEventData objects
        taxon_ids: Dict mapping material sample IDs to NCBI taxon IDs (pre-resolved)
        organism_data: Dict mapping material sample IDs to organism data from DINA
        checklist: Optional ENA checklist identifier
        email: Email for NCBI API requests (recommended if auto_resolve_taxa=True)
        auto_resolve_taxa: If True, will query NCBI to resolve taxon IDs (default: True)
    
    Returns:
        List of ENA Sample models
    
    Example:
        ```python
        samples = batch_material_samples_to_ena(
            material_samples=material_sample_data_list,
            collecting_events={ms.id: ce for ms, ce in zip(material_sample_data_list, ce_data_list)},
            email="your.email@institution.edu",
            auto_resolve_taxa=True
        )
        ```
    """
    samples = []
    collecting_events = collecting_events or {}
    taxon_ids = taxon_ids or {}
    organism_data = organism_data or {}
    
    # Shared cache for taxon lookups to avoid duplicate API calls
    taxon_cache = {} if auto_resolve_taxa else None
    
    for ms in material_samples:
        ms_id = ms.id
        ce = collecting_events.get(ms_id)
        taxon_id = taxon_ids.get(ms_id)
        org_data = organism_data.get(ms_id)
        
        sample = material_sample_to_ena(
            material_sample=ms,
            collecting_event=ce,
            taxon_id=taxon_id,
            checklist=checklist,
            organism_data=org_data,
            email=email if auto_resolve_taxa else None,
            taxon_cache=taxon_cache,
            include_unmapped=True
        )
        samples.append(sample)
    
    return samples


def batch_molecular_runs_to_ena(
    molecular_runs: List[MolecularAnalysisRunData],
    study_accession: str,
    experiment_configs: dict[str, dict]
) -> List[Experiment]:
    """
    Batch map DINA MolecularAnalysisRun data objects to ENA Experiments.
    
    Args:
        molecular_runs: List of DINA MolecularAnalysisRunData objects
        study_accession: ENA study accession
        experiment_configs: Dict mapping run IDs to config dicts with keys:
            - sample_accession: ENA sample accession
            - library_strategy: e.g., "WGS"
            - library_source: e.g., "GENOMIC"
            - library_selection: e.g., "RANDOM"
            - library_layout_type: "SINGLE" or "PAIRED"
            - instrument_model: e.g., "Illumina NovaSeq 6000"
            - nominal_length (optional): for paired-end
            - nominal_sdev (optional): for paired-end
    
    Returns:
        List of ENA Experiment models
    """
    experiments = []
    
    for run in molecular_runs:
        run_id = run.id
        config = experiment_configs.get(run_id, {})
        
        sample_accession = config.get('sample_accession')
        if not sample_accession:
            continue
        
        experiment = molecular_analysis_run_to_ena(
            molecular_run=run,
            study_accession=study_accession,
            sample_accession=sample_accession,
            library_strategy=config.get('library_strategy', 'WGS'),
            library_source=config.get('library_source', 'GENOMIC'),
            library_selection=config.get('library_selection', 'RANDOM'),
            library_layout_type=config.get('library_layout_type', 'PAIRED'),
            instrument_model=config.get('instrument_model', 'Illumina NovaSeq 6000'),
            design_description=config.get('design_description'),
            nominal_length=config.get('nominal_length'),
            nominal_sdev=config.get('nominal_sdev')
        )
        experiments.append(experiment)
    
    return experiments


def batch_metadata_to_ena_runs(
    metadata_objects: List[MetadataData],
    experiment_accessions: dict[str, str],
    run_configs: Optional[dict[str, dict]] = None
) -> List[Run]:
    """
    Batch map DINA Metadata data objects to ENA Runs.
    
    Args:
        metadata_objects: List of DINA MetadataData objects
        experiment_accessions: Dict mapping metadata IDs to ENA experiment accessions
        run_configs: Optional dict mapping metadata IDs to config dicts with keys:
            - filetype: e.g., "fastq"
            - checksum: MD5 or SHA-256 checksum
            - checksum_method: "MD5" or "SHA-256"
    
    Returns:
        List of ENA Run models
    """
    runs = []
    run_configs = run_configs or {}
    
    for metadata in metadata_objects:
        metadata_id = metadata.id
        experiment_accession = experiment_accessions.get(metadata_id)
        
        if not experiment_accession:
            continue
        
        config = run_configs.get(metadata_id, {})
        
        run = metadata_to_ena_run(
            metadata=metadata,
            experiment_accession=experiment_accession,
            filetype=config.get('filetype'),
            checksum=config.get('checksum'),
            checksum_method=config.get('checksum_method', 'MD5')
        )
        runs.append(run)
    
    return runs
