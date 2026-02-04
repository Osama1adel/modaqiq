from datetime import date, timedelta
from typing import Dict, Any, List

class RuleValidator:
    """
    Core Logic Engine for Mudadeq.
    Validates cases against procedural rules.
    """

    def validate_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for validation.
        """
        reasons = []
        
        # 1. Article 8: Mandatory Grievance for Civil Service/Military
        # Assumes 'court_type' or plaintiff details imply this. 
        # For this hackathon, we check if implied by input/description or explicit type.
        if not self._check_article_8_grievance(case_data):
             reasons.append({
                "code": "ARTICLE_8_GRIEVANCE_MISSING",
                "message": "عدم قبول الدعوى لانتفاء شرط التظلم الوجوبي (المادة 8 من نظام المرافعات).",
                "severity": "BLOCKER"
            })

        # 2. Article 16: Statute of Limitations (60 Days)
        if not self._check_statute_of_limitations(case_data):
            reasons.append({
                "code": "ARTICLE_16_TIMEOUT",
                "message": "عدم قبول الدعوى لرفعها بعد الميعاد المقرر نظاماً (60 يوماً - المادة 16).",
                "severity": "BLOCKER"
            })

        return {
            "is_valid": len(reasons) == 0,
            "reasons": reasons
        }

    def _check_article_8_grievance(self, case_data: Dict[str, Any]) -> bool:
        """
        Article 8: Certain cases (Civil Service, Military) require a grievance before suing.
        """
        # Heuristic: If it's an administrative case involving government, assume it might need grievance.
        # Strict check: If user said "No Grievance" (grievance_date is missing) but it is required.
        
        # In our form, we have 'grievance_date'. If it's valid, they did grievance.
        has_grievance = bool(case_data.get('grievance_date'))
        
        # If user explicitly selected "No Grievance" in UI, we might flag it.
        # But for simplification, if it's an Administrative case, we encourage grievance.
        # Let's say if it's a "Compensation" or "Contract" case, maybe not needed? 
        # For Safety/Demo: If Validation logic sees 'Civil Service' keywords, require it.
        
        description = case_data.get('description', '').lower()
        requires_grievance = any(k in description for k in ['ترقية', 'تاديب', 'فصل', 'خدمة مدنية', 'عسكرية', 'راتب'])
        
        if requires_grievance and not has_grievance:
            return False
        
        return True

    def _check_statute_of_limitations(self, case_data: Dict[str, Any]) -> bool:
        """
        Article 16: 60 days from Knowledge or Grievance Outcome.
        """
        submission_date = case_data.get('submission_date')
        if not submission_date:
            submission_date = date.today()
        elif isinstance(submission_date, str):
            from datetime import datetime
            try:
                submission_date = datetime.strptime(submission_date, "%Y-%m-%d").date()
            except ValueError:
                 submission_date = date.today() # Fallback
        
        # The start date for calculation:
        # If there was a grievance, use the grievance outcome date (or date of grievance + 60 days if silent).
        # If no grievance, use incident/knowledge date.
        
        grievance_date = case_data.get('grievance_date')
        incident_date = case_data.get('incident_date')
        
        start_date = None
        
        if grievance_date:
            # If they grieved, valid period starts after grievance response or 60 days silence
            # For simplicity, if grievance_date is provided, we calculate from it (assuming immediate response or silence start)
            # A better field would be 'grievance_outcome_date' if we had it mapped in logic.
            # Let's assume grievance_date represents the END of the grievance process for now or use incident_date as fallback.
             if isinstance(grievance_date, str):
                from datetime import datetime
                grievance_date = datetime.strptime(grievance_date, "%Y-%m-%d").date()
             start_date = grievance_date # Simplifying: 60 days from grievance date
        elif incident_date:
            if isinstance(incident_date, str):
                from datetime import datetime
                incident_date = datetime.strptime(incident_date, "%Y-%m-%d").date()
            start_date = incident_date
        else:
            return True # Can't validate without dates
            
        limit_days = 60
        delta = (submission_date - start_date).days
        
        return delta <= limit_days
