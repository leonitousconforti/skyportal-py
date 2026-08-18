"""Client construction."""

from __future__ import annotations

import httpx

from skyportal_py import (
    acls,
    allocations,
    analysis,
    annotations,
    assignments,
    candidates,
    catalog_queries,
    classifications,
    comments,
    filters,
    followup_requests,
    galaxies,
    groups,
    instruments,
    localizations,
    mmadetectors,
    objs,
    observation_plans,
    observations,
    observing_runs,
    photometry,
    profile,
    roles,
    shifts,
    sources,
    spatial_catalogs,
    spectra,
    streams,
    tags,
    taxonomies,
    telescopes,
    users,
)


class SkyPortal(httpx.Client):
    """An ``httpx.Client`` with the typed endpoint functions bound as methods.

    Endpoint functions take the client as their first argument, so assigning
    them here turns them into methods (``self`` is the client). Both spellings
    work: ``client.fetch_source("ZTF...")`` and
    ``sources.fetch_source(client, "ZTF...")``.
    """

    fetch_acls = acls.fetch_acls
    post_user_acl = acls.post_user_acl
    delete_user_acl = acls.delete_user_acl
    fetch_allocations = allocations.fetch_allocations
    fetch_allocation = allocations.fetch_allocation
    fetch_analysis_service = analysis.fetch_analysis_service
    fetch_analysis_services = analysis.fetch_analysis_services
    post_analysis_service = analysis.post_analysis_service
    update_analysis_service = analysis.update_analysis_service
    delete_analysis_service = analysis.delete_analysis_service
    fetch_default_analysis = analysis.fetch_default_analysis
    fetch_default_analyses = analysis.fetch_default_analyses
    post_default_analysis = analysis.post_default_analysis
    update_default_analysis = analysis.update_default_analysis
    delete_default_analysis = analysis.delete_default_analysis
    post_analysis = analysis.post_analysis
    fetch_analysis = analysis.fetch_analysis
    fetch_analyses = analysis.fetch_analyses
    delete_analysis = analysis.delete_analysis
    post_analysis_upload = analysis.post_analysis_upload
    fetch_analysis_results = analysis.fetch_analysis_results
    fetch_analysis_plot = analysis.fetch_analysis_plot
    fetch_annotations = annotations.fetch_annotations
    post_annotation = annotations.post_annotation
    update_annotation = annotations.update_annotation
    delete_annotation = annotations.delete_annotation
    fetch_assignment = assignments.fetch_assignment
    fetch_assignments = assignments.fetch_assignments
    post_assignment = assignments.post_assignment
    update_assignment = assignments.update_assignment
    delete_assignment = assignments.delete_assignment
    fetch_candidate = candidates.fetch_candidate
    fetch_candidates = candidates.fetch_candidates
    post_candidate = candidates.post_candidate
    post_catalog_query = catalog_queries.post_catalog_query
    post_swift_lsxps_query = catalog_queries.post_swift_lsxps_query
    post_gaia_alerts_query = catalog_queries.post_gaia_alerts_query
    fetch_classifications = classifications.fetch_classifications
    post_classification = classifications.post_classification
    delete_classification = classifications.delete_classification
    fetch_classification = classifications.fetch_classification
    fetch_classifications_query = classifications.fetch_classifications_query
    update_classification = classifications.update_classification
    delete_source_classifications = classifications.delete_source_classifications
    post_classification_vote = classifications.post_classification_vote
    delete_classification_vote = classifications.delete_classification_vote
    fetch_sources_by_classification = classifications.fetch_sources_by_classification
    fetch_comments = comments.fetch_comments
    post_comment = comments.post_comment
    update_comment = comments.update_comment
    delete_comment = comments.delete_comment
    fetch_filters = filters.fetch_filters
    fetch_filter = filters.fetch_filter
    fetch_followup_request = followup_requests.fetch_followup_request
    fetch_followup_requests = followup_requests.fetch_followup_requests
    post_followup_request = followup_requests.post_followup_request
    delete_followup_request = followup_requests.delete_followup_request
    update_followup_request = followup_requests.update_followup_request
    post_followup_request_comment = followup_requests.post_followup_request_comment
    post_followup_request_watcher = followup_requests.post_followup_request_watcher
    delete_followup_request_watcher = followup_requests.delete_followup_request_watcher
    fetch_followup_request_schedule = followup_requests.fetch_followup_request_schedule
    update_followup_request_prioritization = (
        followup_requests.update_followup_request_prioritization
    )
    fetch_default_followup_request = followup_requests.fetch_default_followup_request
    fetch_default_followup_requests = followup_requests.fetch_default_followup_requests
    post_default_followup_request = followup_requests.post_default_followup_request
    delete_default_followup_request = followup_requests.delete_default_followup_request
    request_followup_photometry = followup_requests.request_followup_photometry
    post_facility_message = followup_requests.post_facility_message
    fetch_galaxies = galaxies.fetch_galaxies
    fetch_galaxy_catalogs = galaxies.fetch_galaxy_catalogs
    post_galaxy_catalog = galaxies.post_galaxy_catalog
    delete_galaxy_catalog = galaxies.delete_galaxy_catalog
    post_galaxy_catalog_ascii = galaxies.post_galaxy_catalog_ascii
    post_galaxy_catalog_regalade = galaxies.post_galaxy_catalog_regalade
    post_galaxy_catalog_ned = galaxies.post_galaxy_catalog_ned
    fetch_groups = groups.fetch_groups
    fetch_group = groups.fetch_group
    post_group = groups.post_group
    update_group = groups.update_group
    delete_group = groups.delete_group
    fetch_public_group = groups.fetch_public_group
    post_group_stream = groups.post_group_stream
    delete_group_stream = groups.delete_group_stream
    post_group_user = groups.post_group_user
    update_group_user = groups.update_group_user
    delete_group_user = groups.delete_group_user
    post_group_users_from_groups = groups.post_group_users_from_groups
    fetch_instruments = instruments.fetch_instruments
    fetch_instrument = instruments.fetch_instrument
    fetch_localization = localizations.fetch_localization
    delete_localization = localizations.delete_localization
    post_localization_from_notice = localizations.post_localization_from_notice
    fetch_localization_skymap = localizations.fetch_localization_skymap
    fetch_localization_tags = localizations.fetch_localization_tags
    fetch_localization_properties = localizations.fetch_localization_properties
    fetch_localization_crossmatch = localizations.fetch_localization_crossmatch
    fetch_localization_observability_plot = (
        localizations.fetch_localization_observability_plot
    )
    fetch_localization_airmass_chart = localizations.fetch_localization_airmass_chart
    fetch_localization_worldmap_plot = localizations.fetch_localization_worldmap_plot
    fetch_mmadetector = mmadetectors.fetch_mmadetector
    fetch_mmadetectors = mmadetectors.fetch_mmadetectors
    post_mmadetector = mmadetectors.post_mmadetector
    update_mmadetector = mmadetectors.update_mmadetector
    delete_mmadetector = mmadetectors.delete_mmadetector
    fetch_mmadetector_spectrum = mmadetectors.fetch_mmadetector_spectrum
    fetch_mmadetector_spectra = mmadetectors.fetch_mmadetector_spectra
    post_mmadetector_spectrum = mmadetectors.post_mmadetector_spectrum
    update_mmadetector_spectrum = mmadetectors.update_mmadetector_spectrum
    delete_mmadetector_spectrum = mmadetectors.delete_mmadetector_spectrum
    fetch_mmadetector_time_interval = mmadetectors.fetch_mmadetector_time_interval
    fetch_mmadetector_time_intervals = mmadetectors.fetch_mmadetector_time_intervals
    post_mmadetector_time_intervals = mmadetectors.post_mmadetector_time_intervals
    update_mmadetector_time_interval = mmadetectors.update_mmadetector_time_interval
    delete_mmadetector_time_interval = mmadetectors.delete_mmadetector_time_interval
    delete_obj = objs.delete_obj
    fetch_obj_position = objs.fetch_obj_position
    post_super_obj = objs.post_super_obj
    fetch_super_obj = objs.fetch_super_obj
    fetch_super_objs = objs.fetch_super_objs
    update_super_obj = objs.update_super_obj
    delete_super_obj = objs.delete_super_obj
    fetch_unsourced_finding_chart = objs.fetch_unsourced_finding_chart
    post_observation_plan = observation_plans.post_observation_plan
    post_observation_plans = observation_plans.post_observation_plans
    fetch_observation_plan = observation_plans.fetch_observation_plan
    fetch_observation_plans = observation_plans.fetch_observation_plans
    delete_observation_plan = observation_plans.delete_observation_plan
    post_observation_plan_manual = observation_plans.post_observation_plan_manual
    fetch_observation_plan_names = observation_plans.fetch_observation_plan_names
    fetch_observation_plan_name_exists = (
        observation_plans.fetch_observation_plan_name_exists
    )
    post_observation_plan_treasuremap = (
        observation_plans.post_observation_plan_treasuremap
    )
    delete_observation_plan_treasuremap = (
        observation_plans.delete_observation_plan_treasuremap
    )
    fetch_observation_plan_gcn = observation_plans.fetch_observation_plan_gcn
    post_observation_plan_queue = observation_plans.post_observation_plan_queue
    delete_observation_plan_queue = observation_plans.delete_observation_plan_queue
    fetch_observation_plan_movie = observation_plans.fetch_observation_plan_movie
    fetch_observation_plan_simsurvey = (
        observation_plans.fetch_observation_plan_simsurvey
    )
    delete_observation_plan_simsurvey = (
        observation_plans.delete_observation_plan_simsurvey
    )
    fetch_observation_plan_simsurvey_plot = (
        observation_plans.fetch_observation_plan_simsurvey_plot
    )
    fetch_observation_plan_geojson = observation_plans.fetch_observation_plan_geojson
    fetch_observation_plan_survey_efficiency = (
        observation_plans.fetch_observation_plan_survey_efficiency
    )
    post_observation_plan_observing_run = (
        observation_plans.post_observation_plan_observing_run
    )
    delete_observation_plan_fields = observation_plans.delete_observation_plan_fields
    post_default_observation_plan = observation_plans.post_default_observation_plan
    fetch_default_observation_plan = observation_plans.fetch_default_observation_plan
    fetch_default_observation_plans = observation_plans.fetch_default_observation_plans
    delete_default_observation_plan = observation_plans.delete_default_observation_plan
    fetch_allocation_observation_plans = (
        observation_plans.fetch_allocation_observation_plans
    )
    fetch_observations = observations.fetch_observations
    post_observation = observations.post_observation
    delete_observation = observations.delete_observation
    post_observation_ascii = observations.post_observation_ascii
    fetch_observation_simsurvey = observations.fetch_observation_simsurvey
    delete_observation_simsurvey = observations.delete_observation_simsurvey
    fetch_observation_simsurvey_plot = observations.fetch_observation_simsurvey_plot
    post_observation_treasuremap = observations.post_observation_treasuremap
    delete_observation_treasuremap = observations.delete_observation_treasuremap
    post_observation_external_api = observations.post_observation_external_api
    fetch_observation_external_api = observations.fetch_observation_external_api
    delete_observation_external_api = observations.delete_observation_external_api
    fetch_observing_runs = observing_runs.fetch_observing_runs
    fetch_observing_run = observing_runs.fetch_observing_run
    post_observing_run = observing_runs.post_observing_run
    delete_observing_run = observing_runs.delete_observing_run
    fetch_photometry = photometry.fetch_photometry
    post_photometry = photometry.post_photometry
    fetch_photometry_point = photometry.fetch_photometry_point
    delete_photometry = photometry.delete_photometry
    fetch_profile = profile.fetch_profile
    fetch_roles = roles.fetch_roles
    post_user_role = roles.post_user_role
    delete_user_role = roles.delete_user_role
    fetch_shift = shifts.fetch_shift
    fetch_shifts = shifts.fetch_shifts
    post_shift = shifts.post_shift
    update_shift = shifts.update_shift
    delete_shift = shifts.delete_shift
    post_shift_user = shifts.post_shift_user
    update_shift_user = shifts.update_shift_user
    delete_shift_user = shifts.delete_shift_user
    fetch_shift_summary = shifts.fetch_shift_summary
    fetch_source = sources.fetch_source
    fetch_sources = sources.fetch_sources
    post_source = sources.post_source
    update_source = sources.update_source
    fetch_spatial_catalog = spatial_catalogs.fetch_spatial_catalog
    fetch_spatial_catalogs = spatial_catalogs.fetch_spatial_catalogs
    post_spatial_catalog = spatial_catalogs.post_spatial_catalog
    delete_spatial_catalog = spatial_catalogs.delete_spatial_catalog
    post_spatial_catalog_ascii = spatial_catalogs.post_spatial_catalog_ascii
    fetch_spectrum = spectra.fetch_spectrum
    fetch_spectra = spectra.fetch_spectra
    post_spectrum = spectra.post_spectrum
    delete_spectrum = spectra.delete_spectrum
    fetch_streams = streams.fetch_streams
    fetch_stream = streams.fetch_stream
    post_stream = streams.post_stream
    update_stream = streams.update_stream
    delete_stream = streams.delete_stream
    post_stream_user = streams.post_stream_user
    delete_stream_user = streams.delete_stream_user
    fetch_obj_tag_options = tags.fetch_obj_tag_options
    post_obj_tag_option = tags.post_obj_tag_option
    update_obj_tag_option = tags.update_obj_tag_option
    delete_obj_tag_option = tags.delete_obj_tag_option
    fetch_obj_tags = tags.fetch_obj_tags
    post_obj_tag = tags.post_obj_tag
    delete_obj_tag = tags.delete_obj_tag
    fetch_taxonomies = taxonomies.fetch_taxonomies
    fetch_taxonomy = taxonomies.fetch_taxonomy
    fetch_telescopes = telescopes.fetch_telescopes
    fetch_telescope = telescopes.fetch_telescope
    post_telescope = telescopes.post_telescope
    update_telescope = telescopes.update_telescope
    delete_telescope = telescopes.delete_telescope
    fetch_users = users.fetch_users
    fetch_user = users.fetch_user
    post_user = users.post_user
    update_user = users.update_user
    delete_user = users.delete_user


def create_client(
    base_url: str,
    token: str | None = None,
    *,
    timeout: float = 30.0,
) -> SkyPortal:
    """Create a client configured for a SkyPortal instance.

    Reuse one client per instance: it pools connections, so repeated
    requests skip the TCP/TLS handshake.

    Parameters
    ----------
    base_url : str
        Root URL of the SkyPortal instance, e.g. ``https://fritz.science``.
    token : str, optional
        API token from your SkyPortal profile page. Omit for anonymous
        access to instances that allow it.
    timeout : float, optional
        Timeout in seconds applied to every request.
    """
    headers = {} if token is None else {"Authorization": f"token {token}"}
    return SkyPortal(base_url=base_url, headers=headers, timeout=timeout)
