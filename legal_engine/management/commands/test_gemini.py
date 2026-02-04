from django.core.management.base import BaseCommand
from legal_engine.services.gemini_service import GeminiService

class Command(BaseCommand):
    help = 'Test Gemini Service Integration'

    def handle(self, *args, **kwargs):
        self.stdout.write("Testing Gemini Service Integration...")
        try:
            service = GeminiService()
            if service.is_active:
                self.stdout.write(self.style.SUCCESS('Gemini Service is ACTIVE'))
                self.stdout.write(f"Model: {service.model.model_name}")
                
                # Try generation
                response = service.analyze_text("Test case text")
                self.stdout.write("Response sample:")
                self.stdout.write(response[:100] + "...")
            else:
                self.stdout.write(self.style.ERROR('Gemini Service is INACTIVE'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
