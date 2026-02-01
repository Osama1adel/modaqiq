from django.db import models
from django.utils.translation import gettext_lazy as _

class Party(models.Model):
    class PartyType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', _('Individual')
        GOVERNMENT = 'GOVERNMENT', _('Government Entity')
        COMPANY = 'COMPANY', _('Company')

    class Role(models.TextChoices):
        PLAINTIFF = 'PLAINTIFF', _('Plaintiff')
        DEFENDANT = 'DEFENDANT', _('Defendant')

    name = models.CharField(max_length=255)
    party_type = models.CharField(max_length=20, choices=PartyType.choices)
    role = models.CharField(max_length=20, choices=Role.choices)
    national_id = models.CharField(max_length=20, blank=True, null=True) # For individuals
    license_number = models.CharField(max_length=50, blank=True, null=True) # For companies

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

class ProceduralRule(models.Model):
    """
    Stores dynamic rules for validation.
    Example: 
    - code: "STATUTE_OF_LIMITATIONS_TOURISM"
    - description: "Article 16 - Tourism cases must be filed within 60 days"
    - parameter_value: "60" (days)
    - active: True
    """
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    parameter_value = models.JSONField(help_text="Dynamic parameters for the rule (e.g., {'days': 60})")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Case(models.Model):
    class CaseStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        SUBMITTED = 'SUBMITTED', _('Submitted')
        VALIDATED = 'VALIDATED', _('Validated')
        REJECTED = 'REJECTED', _('Rejected')

    class RequestType(models.TextChoices):
        ADMINISTRATIVE_DECISION = 'ADMINISTRATIVE_DECISION', _('Challenging an administrative decision')
        COMPENSATION = 'COMPENSATION', _('Claim for compensation') 

    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Dates for procedural calculation
    incident_date = models.DateField(help_text="Date when the incident happened or right was denied")
    grievance_date = models.DateField(null=True, blank=True, help_text="Date of complaint to the entity")
    submission_date = models.DateField(auto_now_add=True)
    
    # Parties
    plaintiff = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='cases_as_plaintiff')
    defendant = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='cases_as_defendant')
    
    # Validation Logic
    court_type = models.CharField(max_length=100, help_text="e.g., General, Administrative, Commercial")
    request_type = models.CharField(
        max_length=50, 
        choices=RequestType.choices, 
        default=RequestType.ADMINISTRATIVE_DECISION,
        help_text="Type of request: Decision Challenge or Compensation"
    )
    claim_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=CaseStatus.choices, default=CaseStatus.DRAFT)
    
    documents = models.JSONField(default=list, help_text="List of attached document metadata")

    def __str__(self):
        return self.title

class ValidationResult(models.Model):
    """
    Stores the output of the Logic Engine & Gemini
    """
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name='validation_result')
    is_accepted = models.BooleanField()
    
    # Structured reasons for the 'Smart Dashboard'
    rejection_reasons = models.JSONField(default=list, help_text="List of procedural errors if any")
    
    # Gemini Output
    ai_analysis = models.TextField(help_text="Gemini's analysis of the legal text")
    generated_reasoning = models.TextField(help_text="The eloquent reasoning generated for the judge")
    
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.case.title}: {'Accepted' if self.is_accepted else 'Rejected'}"

class Document(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='case_documents')
    file = models.FileField(upload_to='case_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.case.title}"
