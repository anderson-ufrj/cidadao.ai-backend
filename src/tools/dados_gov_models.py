"""
Data models for Dados.gov.br API responses.

This module contains Pydantic models for parsing and validating
responses from the Brazilian Open Data Portal API.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class Resource(BaseModel):
    """Model for a dataset resource (file)"""

    id: str = Field(..., description="Unique resource identifier")
    package_id: str = Field(..., description="Parent dataset identifier")
    name: str = Field(..., description="Resource name")
    description: Optional[str] = Field(None, description="Resource description")
    format: Optional[str] = Field(
        None, description="File format (CSV, JSON, XML, etc.)"
    )
    url: str = Field(..., description="URL to access the resource")
    size: Optional[int] = Field(None, description="File size in bytes")
    mimetype: Optional[str] = Field(None, description="MIME type")
    created: Optional[datetime] = Field(None, description="Creation date")
    last_modified: Optional[datetime] = Field(
        None, description="Last modification date"
    )

    @field_validator("format")
    @classmethod
    def uppercase_format(cls, v: Optional[str]) -> Optional[str]:
        """Normalize format to uppercase"""
        return v.upper() if v else None


class Tag(BaseModel):
    """Model for dataset tags"""

    name: str = Field(..., description="Tag name")
    display_name: Optional[str] = Field(None, description="Display name")
    vocabulary_id: Optional[str] = Field(None, description="Vocabulary identifier")

    class Config:
        populate_by_name = True


class Organization(BaseModel):
    """Model for data publishing organizations"""

    id: str = Field(..., description="Organization identifier")
    name: str = Field(..., description="Organization name")
    title: str = Field(..., description="Organization title")
    description: Optional[str] = Field(None, description="Organization description")
    image_url: Optional[str] = Field(None, description="Organization logo URL")
    created: Optional[datetime] = Field(None, description="Creation date")
    package_count: Optional[int] = Field(0, description="Number of datasets")

    class Config:
        populate_by_name = True


class Dataset(BaseModel):
    """Model for a complete dataset"""

    id: str = Field(..., description="Dataset identifier")
    name: str = Field(..., description="Dataset name (slug)")
    title: str = Field(..., description="Dataset title")
    author: Optional[str] = Field(None, description="Dataset author")
    author_email: Optional[str] = Field(None, description="Author email")
    maintainer: Optional[str] = Field(None, description="Dataset maintainer")
    maintainer_email: Optional[str] = Field(None, description="Maintainer email")
    license_id: Optional[str] = Field(None, description="License identifier")
    notes: Optional[str] = Field(None, description="Dataset description/notes")
    url: Optional[str] = Field(None, description="Dataset URL")
    version: Optional[str] = Field(None, description="Dataset version")
    state: Optional[str] = Field("active", description="Dataset state")
    type: Optional[str] = Field("dataset", description="Resource type")

    # Relationships
    organization: Optional[Organization] = Field(
        None, description="Publishing organization"
    )
    resources: list[Resource] = Field(
        default_factory=list, description="Dataset resources"
    )
    tags: list[Tag] = Field(default_factory=list, description="Dataset tags")

    # Metadata
    metadata_created: Optional[datetime] = Field(
        None, description="Metadata creation date"
    )
    metadata_modified: Optional[datetime] = Field(
        None, description="Metadata modification date"
    )

    # Additional fields
    extras: Optional[list[dict[str, Any]]] = Field(None, description="Extra metadata")

    class Config:
        populate_by_name = True


class DatasetSearchResult(BaseModel):
    """Model for dataset search results"""

    count: int = Field(..., description="Total number of results")
    results: list[Dataset] = Field(..., description="List of datasets")
    facets: Optional[dict[str, Any]] = Field(None, description="Search facets")
    search_facets: Optional[dict[str, Any]] = Field(
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

    packages: Optional[list[Dataset]] = Field(
        None, description="Organization's datasets"
    )

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
    user_id: Optional[str] = Field(None, description="User who performed the activity")
    object_id: str = Field(..., description="Dataset identifier")
    revision_id: Optional[str] = Field(None, description="Revision identifier")
    activity_type: str = Field(..., description="Type of activity")
    data: Optional[dict[str, Any]] = Field(None, description="Additional activity data")

    class Config:
        populate_by_name = True
