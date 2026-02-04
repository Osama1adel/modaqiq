from django.core.management.base import BaseCommand
from legal_engine.models import Case, ValidationResult, Party
from legal_engine.services.logic_engine import RuleValidator
from legal_engine.services.gemini_service import GeminiService
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Clears old cases and creates a fresh test case with Gemini analysis'

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning up old data...")
        ValidationResult.objects.all().delete()
        Case.objects.all().delete()
        Party.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Old data deleted."))

        self.stdout.write("Creating new test case...")
        
        # Create Parties
        plaintiff = Party.objects.create(
            name="Ahmed Al-Muwadhaf",
            party_type=Party.PartyType.INDIVIDUAL,
            role=Party.Role.PLAINTIFF,
            national_id="1010101010"
        )
        
        defendant = Party.objects.create(
            name="Ministry of Justice",
            party_type=Party.PartyType.GOVERNMENT,
            role=Party.Role.DEFENDANT
        )

        # Define multiple test cases
        test_cases = [
            {
                "title": "فصل تعسفي (مقبولة)",
                "description": "تظلم من قرار فصل تعسفي صادر من جهة حكومية دون سابق إنذار أو تحقيق، حيث صدر القرار بتاريخ 1445/01/01 وتم العلم به في 1445/01/05، وقدمت تظلم للجهة في 1445/01/10 ولم يتم الرد.",
                "court_type": "Administrative Court",
                "incident_date": datetime.date.today() - datetime.timedelta(days=30),
                "grievance_date": datetime.date.today() - datetime.timedelta(days=20),
                "party_role": Party.Role.PLAINTIFF
            },
            {
                "title": "تقادم الزمن (مرفوضة)",
                "description": "اعتراض على قرار إداري صدر قبل 10 سنوات، ولم أقدم أي تظلم طوال هذه الفترة. أطالب بإلغاء القرار الآن.",
                "court_type": "Administrative Court",
                "incident_date": datetime.date.today() - datetime.timedelta(days=4000), # Very old
                "grievance_date": None,
                "party_role": Party.Role.PLAINTIFF
            },
            {
                "title": "طلب تعويض (مقبولة)",
                "description": "أطالب بتعويض مادي قدره 50000 ريال عن الأضرار التي لحقت سيارتي بسبب حفرة في الطريق التابع للبلدية. لدي تقرير مرور وصور للأضرار.",
                "court_type": "General Court",
                "incident_date": datetime.date.today() - datetime.timedelta(days=15),
                "grievance_date": datetime.date.today() - datetime.timedelta(days=5),
                "party_role": Party.Role.PLAINTIFF
            },
            {
                 "title": "عدم تقديم تظلم (مرفوضة)",
                 "description": "صدر قرار بنقلي تعسفياً قبل شهر. لم أتظلم للجهة الإدارية وأريد رفع دعوى مباشرة للمحكمة.",
                 "court_type": "Administrative Court",
                 "incident_date": datetime.date.today() - datetime.timedelta(days=30),
                 "grievance_date": None, # Missing Grievance
                 "party_role": Party.Role.PLAINTIFF
            }
        ]

        for i, data in enumerate(test_cases, 1):
            self.stdout.write(f"Processing Case {i}: {data['title']}...")
            
            case = Case.objects.create(
                title=data['title'],
                description=data['description'],
                court_type=data['court_type'],
                incident_date=data['incident_date'],
                grievance_date=data['grievance_date'],
                status=Case.CaseStatus.DRAFT,
                plaintiff=plaintiff,
                defendant=defendant
            )
            
            # Logic Engine
            validator = RuleValidator()
            logic_input = {
                "incident_date": data['incident_date'],
                "grievance_date": data['grievance_date'],
                "case_type": "ADMINISTRATIVE",
                "court_type": data['court_type']
            }
            validation_output = validator.validate_case(logic_input)
            
            # Gemini Service
            gemini = GeminiService()
            # Only run AI if simple logic allows, or run anyway to see what it says
            # We'll run it for all to demonstrate
            try:
                ai_analysis = gemini.analyze_text(case.description)
                reasoning = gemini.generate_reasoning(data, validation_output)
            except Exception as e:
                ai_analysis = f"Error: {e}"
                reasoning = "Error"

            # Save Result
            ValidationResult.objects.create(
                case=case,
                is_accepted=validation_output.get('is_valid', True),
                rejection_reasons=validation_output.get('reasons', []),
                ai_analysis=ai_analysis,
                generated_reasoning=reasoning,
                confidence_score=0.95
            )
            
            case.status = Case.CaseStatus.PENDING_JUDGE
            case.save()
            self.stdout.write(self.style.SUCCESS(f"Finished Case {i}."))
