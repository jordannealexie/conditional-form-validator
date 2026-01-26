"""
Repository layer for field type system
Handles database operations for field types and enum definitions
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, text
from sqlalchemy.orm import joinedload
from app.models.field_types import (
    EnumDefinition,
    FieldTypeDefinition,
    FormFieldMapping,
    DataSourceType
)


class EnumDefinitionRepository:
    """Repository for EnumDefinition CRUD operations"""
    
    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> EnumDefinition:
        """Create a new enum definition"""
        enum_def = EnumDefinition(**kwargs)
        db.add(enum_def)
        await db.commit()
        await db.refresh(enum_def)
        return enum_def
    
    @staticmethod
    async def get_by_id(db: AsyncSession, enum_id: int) -> Optional[EnumDefinition]:
        """Get enum definition by ID"""
        result = await db.execute(
            select(EnumDefinition).where(EnumDefinition.id == enum_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[EnumDefinition]:
        """Get enum definition by name"""
        result = await db.execute(
            select(EnumDefinition).where(EnumDefinition.name == name)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        active_only: bool = False,
        source_type: Optional[DataSourceType] = None
    ) -> List[EnumDefinition]:
        """Get all enum definitions with optional filters"""
        query = select(EnumDefinition)
        
        filters = []
        if active_only:
            filters.append(EnumDefinition.active == True)
        if source_type:
            filters.append(EnumDefinition.source_type == source_type)
        
        if filters:
            query = query.where(and_(*filters))
        
        result = await db.execute(query.order_by(EnumDefinition.name))
        return list(result.scalars().all())
    
    @staticmethod
    async def update(db: AsyncSession, enum_def: EnumDefinition, **kwargs) -> EnumDefinition:
        """Update enum definition"""
        for key, value in kwargs.items():
            if value is not None and hasattr(enum_def, key):
                setattr(enum_def, key, value)
        await db.commit()
        await db.refresh(enum_def)
        return enum_def
    
    @staticmethod
    async def delete(db: AsyncSession, enum_def: EnumDefinition) -> None:
        """Delete enum definition"""
        await db.delete(enum_def)
        await db.commit()
    
    @staticmethod
    async def resolve_options(
        db: AsyncSession,
        enum_def: EnumDefinition
    ) -> List[Dict[str, Any]]:
        """
        Resolve enum options based on source type
        
        Returns list of {value, label} dicts
        """
        if enum_def.source_type == DataSourceType.STATIC:
            return enum_def.static_options or []
        
        elif enum_def.source_type == DataSourceType.DATABASE_TABLE:
            if not enum_def.table_name or not enum_def.value_column or not enum_def.label_column:
                raise ValueError("Database table configuration incomplete")
            
            # Build SQL query
            query_str = f"""
                SELECT {enum_def.value_column} as value, {enum_def.label_column} as label
                FROM {enum_def.table_name}
            """
            
            # Add filter conditions if present
            if enum_def.filter_conditions:
                where_clauses = []
                for field, value in enum_def.filter_conditions.items():
                    where_clauses.append(f"{field} = '{value}'")
                if where_clauses:
                    query_str += " WHERE " + " AND ".join(where_clauses)
            
            query_str += f" ORDER BY {enum_def.label_column}"
            
            result = await db.execute(text(query_str))
            rows = result.fetchall()
            
            return [{"value": row.value, "label": row.label} for row in rows]
        
        elif enum_def.source_type == DataSourceType.CUSTOM_QUERY:
            if not enum_def.custom_query:
                raise ValueError("Custom query not provided")
            
            result = await db.execute(text(enum_def.custom_query))
            rows = result.fetchall()
            
            # Assume query returns value and label columns
            return [{"value": row.value, "label": row.label} for row in rows]
        
        elif enum_def.source_type == DataSourceType.API_ENDPOINT:
            # API endpoint resolution would be handled by the service layer
            # as it requires HTTP client
            raise NotImplementedError("API endpoint resolution handled by service layer")
        
        return []


class FieldTypeDefinitionRepository:
    """Repository for FieldTypeDefinition CRUD operations"""
    
    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> FieldTypeDefinition:
        """Create a new field type definition"""
        field_type = FieldTypeDefinition(**kwargs)
        db.add(field_type)
        await db.commit()
        await db.refresh(field_type)
        return field_type
    
    @staticmethod
    async def get_by_id(db: AsyncSession, field_type_id: int) -> Optional[FieldTypeDefinition]:
        """Get field type definition by ID"""
        result = await db.execute(
            select(FieldTypeDefinition).where(FieldTypeDefinition.id == field_type_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[FieldTypeDefinition]:
        """Get field type definition by name"""
        result = await db.execute(
            select(FieldTypeDefinition).where(FieldTypeDefinition.name == name)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        active_only: bool = False,
        base_type: Optional[str] = None
    ) -> List[FieldTypeDefinition]:
        """Get all field type definitions with optional filters"""
        query = select(FieldTypeDefinition)
        
        filters = []
        if active_only:
            filters.append(FieldTypeDefinition.active == True)
        if base_type:
            filters.append(FieldTypeDefinition.base_type == base_type)
        
        if filters:
            query = query.where(and_(*filters))
        
        result = await db.execute(query.order_by(FieldTypeDefinition.name))
        return list(result.scalars().all())
    
    @staticmethod
    async def update(
        db: AsyncSession,
        field_type: FieldTypeDefinition,
        **kwargs
    ) -> FieldTypeDefinition:
        """Update field type definition"""
        for key, value in kwargs.items():
            if value is not None and hasattr(field_type, key):
                setattr(field_type, key, value)
        await db.commit()
        await db.refresh(field_type)
        return field_type
    
    @staticmethod
    async def delete(db: AsyncSession, field_type: FieldTypeDefinition) -> None:
        """Delete field type definition"""
        await db.delete(field_type)
        await db.commit()


class FormFieldMappingRepository:
    """Repository for FormFieldMapping CRUD operations"""
    
    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> FormFieldMapping:
        """Create a new field mapping"""
        mapping = FormFieldMapping(**kwargs)
        db.add(mapping)
        await db.commit()
        await db.refresh(mapping)
        return mapping
    
    @staticmethod
    async def get_by_template(
        db: AsyncSession,
        template_id: int
    ) -> List[FormFieldMapping]:
        """Get all field mappings for a template"""
        result = await db.execute(
            select(FormFieldMapping)
            .options(
                joinedload(FormFieldMapping.field_type),
                joinedload(FormFieldMapping.enum_definition)
            )
            .where(FormFieldMapping.template_id == template_id)
        )
        return list(result.unique().scalars().all())
    
    @staticmethod
    async def get_by_field(
        db: AsyncSession,
        template_id: int,
        field_name: str
    ) -> Optional[FormFieldMapping]:
        """Get field mapping for specific field"""
        result = await db.execute(
            select(FormFieldMapping)
            .options(
                joinedload(FormFieldMapping.field_type),
                joinedload(FormFieldMapping.enum_definition)
            )
            .where(
                and_(
                    FormFieldMapping.template_id == template_id,
                    FormFieldMapping.field_name == field_name
                )
            )
        )
        return result.unique().scalar_one_or_none()
    
    @staticmethod
    async def update(
        db: AsyncSession,
        mapping: FormFieldMapping,
        **kwargs
    ) -> FormFieldMapping:
        """Update field mapping"""
        for key, value in kwargs.items():
            if hasattr(mapping, key):
                setattr(mapping, key, value)
        await db.commit()
        await db.refresh(mapping)
        return mapping
    
    @staticmethod
    async def delete(db: AsyncSession, mapping: FormFieldMapping) -> None:
        """Delete field mapping"""
        await db.delete(mapping)
        await db.commit()
    
    @staticmethod
    async def delete_by_template(db: AsyncSession, template_id: int) -> None:
        """Delete all field mappings for a template"""
        result = await db.execute(
            select(FormFieldMapping).where(FormFieldMapping.template_id == template_id)
        )
        mappings = result.scalars().all()
        
        for mapping in mappings:
            await db.delete(mapping)
        
        await db.commit()
