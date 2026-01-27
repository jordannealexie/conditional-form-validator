"""
Common query parameter dependencies for pagination
Provides backward-compatible pagination support
"""
from typing import Optional
from fastapi import Query


class PaginationParams:
    """
    Pagination parameters for list endpoints
    
    Backward compatible:
    - If page and page_size are not provided, returns all results (legacy behavior)
    - If provided, applies pagination
    """
    
    def __init__(
        self,
        page: Optional[int] = Query(None, ge=1, description="Page number (1-indexed)"),
        page_size: Optional[int] = Query(None, ge=1, le=1000, description="Items per page (max 1000)"),
        skip: Optional[int] = Query(None, ge=0, description="Number of items to skip (alternative to page)"),
        limit: Optional[int] = Query(None, ge=1, le=1000, description="Number of items to return (alternative to page_size)")
    ):
        """
        Initialize pagination parameters
        
        Supports two pagination styles:
        1. Page-based: page + page_size
        2. Offset-based: skip + limit
        
        Args:
            page: Page number (1-indexed)
            page_size: Items per page
            skip: Number of items to skip
            limit: Number of items to return
        """
        # Use skip/limit if provided, otherwise calculate from page/page_size
        if skip is not None and limit is not None:
            self.skip = skip
            self.limit = limit
        elif page is not None and page_size is not None:
            self.skip = (page - 1) * page_size
            self.limit = page_size
        else:
            # Default to no pagination (backward compatible)
            self.skip = 0
            self.limit = 10000  # Large default to return all
        
        # Store original page/page_size for response metadata
        self.page = page
        self.page_size = page_size
    
    @property
    def is_paginated(self) -> bool:
        """Check if pagination parameters were provided"""
        return self.page is not None and self.page_size is not None
    
    def get_page_metadata(self, total: int) -> dict:
        """
        Get pagination metadata for response
        
        Args:
            total: Total number of items
            
        Returns:
            Pagination metadata dict
        """
        if not self.is_paginated:
            return {
                "total": total,
                "returned": min(total, self.limit)
            }
        
        total_pages = (total + self.page_size - 1) // self.page_size if self.page_size > 0 else 1
        
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": self.page < total_pages if self.page else False,
            "has_prev": self.page > 1 if self.page else False
        }
