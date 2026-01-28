import asyncio
import sys
from pathlib import Path

# Add project root to path
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

from app.db.session import AsyncSessionLocal
from app.repositories.forms import FormTemplateRepository
from app.schemas.forms import FormTemplateResponse

async def test_templates():
    async with AsyncSessionLocal() as session:
        try:
            print("Fetching templates...")
            templates = await FormTemplateRepository.get_all(session, active_only=True)
            print(f"Found {len(templates)} templates")
            
            for template in templates:
                print(f"Template: {template.name}, Bank: {template.bank.name if template.bank else 'No bank'}")
                
            # Test serialization
            print("\nTesting serialization...")
            for template in templates:
                try:
                    response = FormTemplateResponse.model_validate(template)
                    print(f"✅ Template '{template.name}' serialized successfully")
                except Exception as e:
                    print(f"❌ Error serializing template '{template.name}': {str(e)}")
                    print(f"   Template fields: {list(template.__dict__.keys())}")
                    
        except Exception as e:
            print(f"❌ Repository error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_templates())