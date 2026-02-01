from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .models import Case, ValidationResult, Party
from .serializers import CaseSerializer, ValidationResultSerializer
from .services.logic_engine import RuleValidator
from .services.gemini_service import GeminiService

class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

    @action(detail=False, methods=['post'])
    def submit_and_validate(self, request):
        """
        Main Endpoint: Receives case data -> Saves Draft -> Runs Logic Engine -> Runs Gemini -> Return Result
        """
        # 1. Validate Input Data
        import json
        
        # Check if 'data' field exists (Multipart) or use request.data directly (JSON)
        if 'data' in request.data:
             try:
                 data = json.loads(request.data['data'])
             except json.JSONDecodeError:
                 return Response({"error": "Invalid JSON in 'data' field"}, status=status.HTTP_400_BAD_REQUEST)
        else:
             data = request.data

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # 2. Save Case as Draft
                case = serializer.save()

                # 2.1 Handle File Uploads
                files = request.FILES.getlist('documents')
                if files:
                    from .models import Document
                    for f in files:
                        Document.objects.create(case=case, file=f)


                # 3. Serialize again to get full representation for Logic Engine (dates as strings/obj validation)
                case_data = serializer.data
                
                # 4. Run Logic Engine
                validator = RuleValidator()
                validation_output = validator.validate_case(case_data)
                
                # 5. Run Gemini AI (Simulated for Hackathon/ MVP)
                gemini = GeminiService()
                
                # Combine Logic Output + Case Text for Gemini
                # In real scenario: prompt = f"Case: {case.description}. Validation said: {validation_output}..."
                ai_analysis = gemini.analyze_text(case.description)
                reasoning = gemini.generate_reasoning(case_data, validation_output)
                
                # 6. Save Result
                result = ValidationResult.objects.create(
                    case=case,
                    is_accepted=validation_output['is_valid'],
                    rejection_reasons=validation_output['reasons'],
                    ai_analysis=ai_analysis,
                    generated_reasoning=reasoning,
                    confidence_score=0.95 # Mock high confidence
                )
                
                # 7. Update Case Status
                case.status = Case.CaseStatus.PENDING_JUDGE
                case.save()
                
                # 8. Return "Stunning" Response
                response_data = {
                    "case_id": case.id,
                    "status": "ACCEPTED" if result.is_accepted else "REJECTED",
                    "validation_details": validation_output['reasons'],
                    "ai_insight": {
                        "analysis": ai_analysis,
                        "generated_reasoning": reasoning
                    },
                    "ui_hints": {
                        "steps_completed": 3,
                        "steps_total": 5,
                        "next_action": "File Officially" if result.is_accepted else "Amend Complaint"
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def approve_case(self, request, pk=None):
        case = self.get_object()
        case.status = Case.CaseStatus.APPROVED
        case.save()
        return Response({'status': 'Approved', 'case_id': case.id})

    @action(detail=True, methods=['post'])
    def reject_case(self, request, pk=None):
        case = self.get_object()
        reason = request.data.get('reason', 'No reason provided')
        # Ideally store reason in a log or field
        case.status = Case.CaseStatus.REJECTED
        case.save()
        return Response({'status': 'Rejected', 'case_id': case.id})
