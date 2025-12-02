"""
Data models for Dados.gov.br API responses.

This module contains Pydantic models for parsing and validating
responses from the Brazilian Open Data Portal API.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Resource(BaseModel):
    """Model for a dataset resource (file)"""

    id: str = Field(..., description="Unique resource identifier")
    package_id: str = Field(..., description="Parent dataset identifier")
    name: str = Field(..., description="Resource name")
    description: str | None = Field(None, description="Resource description")
    format: str | None = Field(None, description="File format (CSV, JSON, XML, etc.)")
    url: str = Field(..., description="URL to access the resource")
    size: int | None = Field(None, description="File size in bytes")
    mimetype: str | None = Field(None, description="MIME type")
    created: datetime | None = Field(None, description="Creation date")
    last_modified: datetime | None = Field(None, description="Last modification date")

    @field_validator("format")
    @classmethod
    def uppercase_format(cls, v: str | None) -> str | None:
        """Normalize format to uppercase"""
        return v.upper() if v else None


class Tag(BaseModel):
    """Model for dataset tags"""

    name: str = Field(..., description="Tag name")
    display_name: str | None = Field(None, description="Display name")
    vocabulary_id: str | None = Field(None, description="Vocabulary identifier")

    class Config:
        populate_by_name = True


class Organization(BaseModel):
    """Model for data publishing organizations"""

    id: str = Field(..., description="Organization identifier")
    name: str = Field(..., description="Organization name")
    title: str = Field(..., description="Organization title")
    description: str | None = Field(None, description="Organization description")
    image_url: str | None = Field(None, description="Organization logo URL")
    created: datetime | None = Field(None, description="Creation date")
    package_count: int | None = Field(0, description="Number of datasets")

    class Config:
        populate_by_name = True


class Dataset(BaseModel):
    """Model for a complete dataset"""

    id: str = Field(..., description="Dataset identifier")
    name: str = Field(..., description="Dataset name (slug)")
    title: str = Field(..., description="Dataset title")
    author: str | None = Field(None, description="Dataset author")
    author_email: str | None = Field(None, description="Author email")
    maintainer: str | None = Field(None, description="Dataset maintainer")
    maintainer_email: str | None = Field(None, description="Maintainer email")
    license_id: str | None = Field(None, description="License identifier")
    notes: str | None = Field(None, description="Dataset description/notes")
    url: str | None = Field(None, description="Dataset URL")
    version: str | None = Field(None, description="Dataset version")
    state: str | None = Field("active", description="Dataset state")
    type: str | None = Field("dataset", description="Resource type")

    # Relationships
    organization: Organization | None = Field(
        None, description="Publishing organization"
    )
    resources: list[Resource] = Field(
        default_factory=list, description="Dataset resources"
    )
    tags: list[Tag] = Field(default_factory=list, description="Dataset tags")

    # Metadata
    metadata_created: datetime | None = Field(
        None, description="Metadata creation date"
    )
    metadata_modified: datetime | None = Field(
        None, description="Metadata modification date"
    )

    # Additional fields
    extras: list[dict[str, Any]] | None = Field(None, description="Extra metadata")

    class Config:
        populate_by_name = True


class DatasetSearchResult(BaseModel):
    """Model for dataset search results"""

    count: int = Field(..., description="Total number of results")
    results: list[Dataset] = Field(..., description="List of datasets")
    facets: dict[str, Any] | None = Field(None, description="Search facets")
    search_facets: dict[str, Any] | None = Field(
        None, description="Active search facets"
    )

    class Config:
        populate_by_name = True


class ResourceSearchResult(BaseModel):
    """Model for resource search results"""

    count: int = Field(..., description="Total number of results")
    results: list[Resource] = Field(..., description="List of resources")

    class Config:
        populate_by_name = True


class TagWithCount(BaseModel):
    """Model for tags with usage count"""

    name: str = Field(..., description="Tag name")
    count: int = Field(..., description="Number of datasets using this tag")

    class Config:
        populate_by_name = True


class OrganizationWithDatasets(Organization):
    """Extended organization model including datasets"""

    packages: list[Dataset] | None = Field(None, description="Organization's datasets")

    class Config:
        populate_by_name = True


class DataPortalStats(BaseModel):
    """Model for general portal statistics"""

    dataset_count: int = Field(..., description="Total number of datasets")
    organization_count: int = Field(..., description="Total number of organizations")
    resource_count: int = Field(..., description="Total number of resources")
    tag_count: int = Field(..., description="Total number of unique tags")

    class Config:
        populate_by_name = True


class DatasetActivity(BaseModel):
    """Model for dataset activity/history"""

    id: str = Field(..., description="Activity identifier")
    timestamp: datetime = Field(..., description="Activity timestamp")
    user_id: str | None = Field(None, description="User who performed the activity")
    object_id: str = Field(..., description="Dataset identifier")
    revision_id: str | None = Field(None, description="Revision identifier")
    activity_type: str = Field(..., description="Type of activity")
    data: dict[str, Any] | None = Field(None, description="Additional activity data")

    class Config:
        populate_by_name = True
