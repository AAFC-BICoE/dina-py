"""
ENA submission validation and data quality checking for DINA collections.

This module provides utilities to validate that material samples from DINA collections
are properly formatted and contain all required data for ENA submission, WITHOUT actually
submitting to ENA. Use this to identify and fix data quality issues before submission.

Example usage:
    >>> from dinapy.ena.batch_submission import validate_collection_for_ena
    >>> 
    >>> # Validate all samples in a collection
    >>> results = validate_collection_for_ena(
    ...     collection_id="019c9570-309b-7787-8e06-d3262486b4b5",
    ...     email="your.email@example.com"
    ... )
    >>> 
    >>> # Check validation results
    >>> summary = get_validation_summary(results)
    >>> print(f"Ready for submission: {summary['valid_samples']}/{summary['total_samples']}")
    >>> 
    >>> # Review issues
    >>> for result in results:
    ...     if result['status'] == 'invalid':
    ...         print(f"  ✗ {result['sample_name']}: {', '.join(result['issues'])}")
"""

from typing import List, Dict, Optional

from dinapy.apis.collectionapi.materialsampleapi import MaterialSampleAPI
from dinapy.apis.collectionapi.ena_helpers import prepare_sample_for_ena_mapping


def validate_collection_for_ena(
    collection_id: str,
    email: Optional[str] = None,
    verbose: bool = True
) -> List[Dict]:
    """
    Validate all samples from a DINA collection for ENA submission readiness.
    
    This function checks whether material samples have all required data for ENA
    submission WITHOUT actually submitting to ENA. It identifies missing required
    fields, invalid data, and other issues that would cause submission failures.
    
    Args:
        collection_id: UUID of the DINA collection to validate
        email: Email for NCBI taxon lookups (optional but recommended)
        verbose: Print detailed progress messages (default: True)
    
    Returns:
        List of dictionaries with validation results:
        [{
            'sample_id': str,
            'sample_name': str,
            'sample_alias': str,
            'status': 'valid' | 'invalid' | 'mapping_error',
            'issues': [str, ...],  # List of validation issues found
            'warnings': [str, ...],  # List of warnings (non-blocking)
            'ena_sample': Sample (if successfully mapped),
            'has_collecting_event': bool,
            'has_organism': bool,
            'taxon_id': int (if resolved)
        }, ...]
    
    Example:
        >>> from dinapy.ena.batch_submission import validate_collection_for_ena, get_validation_summary
        >>> 
        >>> # Validate all samples in a collection
        >>> results = validate_collection_for_ena(
        ...     collection_id="019c9570-309b-7787-8e06-d3262486b4b5",
        ...     email="your.email@example.com"
        ... )
        >>> 
        >>> # Get summary
        >>> summary = get_validation_summary(results)
        >>> print(f"Valid: {summary['valid_samples']}/{summary['total_samples']}")
        >>> 
        >>> # Find samples that need fixing
        >>> invalid = [r for r in results if r['status'] == 'invalid']
        >>> for result in invalid:
        ...     print(f"{result['sample_name']}:")
        ...     for issue in result['issues']:
        ...         print(f"  - {issue}")
    """
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"  ENA VALIDATION: Collection {collection_id}")
        print(f"{'='*70}\n")
        print("📋 PHASE 1: Fetching samples from DINA collection\n")
    
    material_sample_api = MaterialSampleAPI()
    
    if verbose:
        print(f"Fetching samples from collection {collection_id}...")
    
    response = material_sample_api.get_by_collection(
        collection_uuid=collection_id,
        include=['collectingEvent', 'organism', 'attachment', 'collection']
    )
    
    samples_data = response.json().get('data', [])
    included_data = response.json().get('included', [])
    
    if verbose:
        print(f"✓ Fetched {len(samples_data)} material samples")
        print(f"✓ Fetched {len(included_data)} related entities\n")
    
    if not samples_data:
        if verbose:
            print("⚠ No samples found in collection.")
        return []
    
    # Validate and map all samples
    if verbose:
        print(f"{'='*70}")
        print("🔍 PHASE 2: Validating samples for ENA submission\n")
    
    validation_results = []
    
    for idx, sample_data in enumerate(samples_data, 1):
        sample_name = sample_data.get('attributes', {}).get('materialSampleName', f'Sample_{idx}')
        sample_id = sample_data.get('id', 'unknown')
        
        result = {
            'sample_id': sample_id,
            'sample_name': sample_name,
            'status': 'valid',
            'issues': [],
            'warnings': [],
            'has_collecting_event': False,
            'has_organism': False
        }
        
        try:
            # Prepare sample DTOs
            ms_dto, ce_dto, org_data = prepare_sample_for_ena_mapping(sample_data, included_data)
            
            result['has_collecting_event'] = ce_dto is not None
            result['has_organism'] = org_data is not None
            
            # Map to ENA Sample
            from dinapy.ena.mappers.dina_to_ena.mappers_dto import material_sample_to_ena
            
            ena_sample = material_sample_to_ena(
                material_sample=ms_dto,
                collecting_event=ce_dto,
                organism_data=org_data,
                email=email,
                include_unmapped=True
            )
            
            result['sample_alias'] = ena_sample.alias
            result['ena_sample'] = ena_sample
            # Safely get taxon ID if it exists (use taxon_id, not taxonId - that's just the JSON alias)
            if ena_sample.organism and hasattr(ena_sample.organism, 'taxon_id'):
                result['taxon_id'] = ena_sample.organism.taxon_id
            else:
                result['taxon_id'] = None
            
            # Validate required ENA fields
            issues = _validate_ena_sample(ena_sample, ce_dto, org_data)
            result['issues'] = issues
            
            if issues:
                result['status'] = 'invalid'
                if verbose:
                    print(f"  ✗ [{idx}/{len(samples_data)}] {sample_name}: {len(issues)} issue(s)")
                    for issue in issues[:3]:  # Show first 3 issues
                        print(f"      - {issue}")
                    if len(issues) > 3:
                        print(f"      ...and {len(issues) - 3} more")
            else:
                if verbose:
                    print(f"  ✓ [{idx}/{len(samples_data)}] {sample_name}: Valid")
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            result['status'] = 'mapping_error'
            result['issues'] = [f"Failed to map to ENA format: {error_msg}"]
            if verbose:
                print(f"  ✗ [{idx}/{len(samples_data)}] {sample_name}: Mapping error")
                print(f"      - {error_msg}")
        
        validation_results.append(result)
    
    if verbose:
        valid_count = len([r for r in validation_results if r['status'] == 'valid'])
        invalid_count = len([r for r in validation_results if r['status'] == 'invalid'])
        error_count = len([r for r in validation_results if r['status'] == 'mapping_error'])
        
        print(f"\n{'='*70}")
        print(f"  VALIDATION SUMMARY")
        print(f"{'='*70}\n")
        print(f"Total samples: {len(samples_data)}")
        print(f"  ✓ Valid (ready for submission): {valid_count}")
        print(f"  ⚠ Invalid (has issues): {invalid_count}")
        print(f"  ✗ Mapping errors: {error_count}")
        
        if invalid_count > 0:
            print(f"\n⚠ {invalid_count} samples need fixes before submission")
            print("Use get_validation_summary() for detailed issue breakdown")
        
        print()
    
    return validation_results


def _validate_ena_sample(ena_sample, collecting_event, organism_data) -> List[str]:
    """
    Validate an ENA Sample model for required fields and data quality.
    
    Returns list of validation issues (empty list if valid).
    """
    issues = []
    
    # Required fields check
    if not ena_sample.title:
        issues.append("Missing sample title")
    
    if not ena_sample.alias:
        issues.append("Missing sample alias")
    
    # Organism/taxonomy validation
    if not organism_data:
        issues.append("Missing organism information")
    else:
        # organism_data structure: {'id': '...', 'type': 'organism', 'attributes': {'determination': [...]}}
        attrs = organism_data.get('attributes', {})
        determination = attrs.get('determination', [])
        
        if not determination:
            issues.append("Missing organism determination")
        else:
            # Check for scientific name which will be resolved to taxon ID
            has_scientific_name = False
            for det in determination:
                if det.get('scientificName'):
                    has_scientific_name = True
                    break
            
            if not has_scientific_name:
                issues.append("Missing scientific name in organism determination - cannot resolve taxonomy")
    
    # Check for required ENA attributes
    required_attrs = {
        'collection date': 'Collection date is required by ENA',
        'geographic location (country and/or sea)': 'Geographic location is required by ENA'
    }
    
    if ena_sample.attributes:
        found_attrs = {attr.tag.lower() for attr in ena_sample.attributes}
        
        for req_tag, error_msg in required_attrs.items():
            if req_tag.lower() not in found_attrs:
                issues.append(error_msg)
            else:
                # Check if the attribute has a truly invalid/empty value
                # Note: ENA accepts fallback values like "not collected" and "not provided"
                attr = next((a for a in ena_sample.attributes if a.tag.lower() == req_tag.lower()), None)
                if attr and (not attr.value or attr.value.strip() == ''):
                    issues.append(f"{error_msg} (value is empty)")
    else:
        issues.append("No sample attributes found")
        for error_msg in required_attrs.values():
            issues.append(error_msg)
    
    # Source data validation (warnings about missing source data)
    if not collecting_event:
        issues.append("No collecting event - ENA fallback values will be used (may not be appropriate)")
    
    # This check should happen earlier, but keep as backstop
    if not organism_data:
        issues.append("No organism data - taxon resolution may fail")
    
    return issues


def get_validation_summary(results: List[Dict]) -> Dict:
    """
    Generate a summary report from validation results.
    
    Args:
        results: List of result dictionaries from validate_collection_for_ena()
    
    Returns:
        Dictionary with detailed validation statistics:
        {
            'total_samples': int,
            'valid_samples': int,
            'invalid_samples': int,
            'mapping_errors': int,
            'samples_without_collecting_event': int,
            'samples_without_organism': int,
            'common_issues': {issue: count, ...},  # Most frequent issues
            'invalid_samples_details': [
                {
                    'sample_name': str,
                    'sample_id': str,
                    'issues': [str, ...],
                    'warnings': [str, ...]
                }, ...
            ]
        }
    
    Example:
        >>> summary = get_validation_summary(results)
        >>> print(f"Ready: {summary['valid_samples']}/{summary['total_samples']}")
        >>> print(f"\nMost common issues:")
        >>> for issue, count in sorted(summary['common_issues'].items(), key=lambda x: x[1], reverse=True)[:5]:
        ...     print(f"  - {issue}: {count} samples")
    """
    summary = {
        'total_samples': len(results),
        'valid_samples': 0,
        'invalid_samples': 0,
        'mapping_errors': 0,
        'samples_without_collecting_event': 0,
        'samples_without_organism': 0,
        'common_issues': {},
        'invalid_samples_details': []
    }
    
    for result in results:
        status = result['status']
        
        if status == 'valid':
            summary['valid_samples'] += 1
        elif status == 'invalid':
            summary['invalid_samples'] += 1
            summary['invalid_samples_details'].append({
                'sample_name': result['sample_name'],
                'sample_id': result['sample_id'],
                'issues': result.get('issues', []),
                'warnings': result.get('warnings', [])
            })
        elif status == 'mapping_error':
            summary['mapping_errors'] += 1
            summary['invalid_samples_details'].append({
                'sample_name': result['sample_name'],
                'sample_id': result['sample_id'],
                'issues': result.get('issues', []),
                'warnings': []
            })
        
        # Count samples without key relationships
        if not result.get('has_collecting_event'):
            summary['samples_without_collecting_event'] += 1
        if not result.get('has_organism'):
            summary['samples_without_organism'] += 1
        
        # Track common issues
        for issue in result.get('issues', []):
            summary['common_issues'][issue] = summary['common_issues'].get(issue, 0) + 1
    
    return summary


def print_validation_report(results: List[Dict], max_samples: int = 10):
    """
    Print a detailed validation report to console.
    
    Args:
        results: List of result dictionaries from validate_collection_for_ena()
        max_samples: Maximum number of invalid samples to show in detail (default: 10)
    
    Example:
        >>> results = validate_collection_for_ena(collection_id)
        >>> print_validation_report(results)
    """
    summary = get_validation_summary(results)
    
    print(f"\n{'='*70}")
    print(f"  VALIDATION REPORT")
    print(f"{'='*70}\n")
    
    # Overall statistics
    print(f"📊 Overall Statistics:")
    print(f"  Total samples: {summary['total_samples']}")
    print(f"  ✓ Valid (ready for submission): {summary['valid_samples']}")
    print(f"  ⚠ Invalid (needs fixes): {summary['invalid_samples']}")
    print(f"  ✗ Mapping errors: {summary['mapping_errors']}")
    
    if summary['total_samples'] > 0:
        valid_pct = (summary['valid_samples'] / summary['total_samples']) * 100
        print(f"\n  Readiness: {valid_pct:.1f}%")
    
    # Data quality metrics
    print(f"\n📋 Data Quality:")
    print(f"  Samples without collecting event: {summary['samples_without_collecting_event']}")
    print(f"  Samples without organism: {summary['samples_without_organism']}")
    
    # Common issues
    if summary['common_issues']:
        print(f"\n⚠ Most Common Issues:")
        sorted_issues = sorted(summary['common_issues'].items(), key=lambda x: x[1], reverse=True)
        for issue, count in sorted_issues[:5]:
            print(f"  - {issue}: {count} samples")
    
    # Invalid samples details
    if summary['invalid_samples_details']:
        print(f"\n❌ Samples Needing Fixes (showing first {max_samples}):")
        for detail in summary['invalid_samples_details'][:max_samples]:
            print(f"\n  Sample: {detail['sample_name']} (ID: {detail['sample_id'][:8]}...)")
            if detail['issues']:
                print(f"    Issues:")
                for issue in detail['issues']:
                    print(f"      - {issue}")
            if detail.get('warnings'):
                print(f"    Warnings:")
                for warning in detail['warnings']:
                    print(f"      - {warning}")
        
        if len(summary['invalid_samples_details']) > max_samples:
            remaining = len(summary['invalid_samples_details']) - max_samples
            print(f"\n  ...and {remaining} more samples with issues")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if summary['samples_without_collecting_event'] > 0:
        print(f"  - Add collecting event data to {summary['samples_without_collecting_event']} samples")
    if summary['samples_without_organism'] > 0:
        print(f"  - Add organism data to {summary['samples_without_organism']} samples")
    if summary['valid_samples'] == summary['total_samples']:
        print(f"  ✓ All samples are valid - ready for ENA submission!")
    elif summary['valid_samples'] > 0:
        print(f"  - Fix issues in {summary['invalid_samples'] + summary['mapping_errors']} samples")
        print(f"  - Then proceed with submission for all samples")
    
    print(f"\n{'='*70}\n")
