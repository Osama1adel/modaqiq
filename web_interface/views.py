from django.shortcuts import render
from legal_engine.models import Case

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def judge_dashboard(request):
    cases = Case.objects.select_related('plaintiff', 'validation_result').order_by('-submission_date')
    return render(request, 'judge_dashboard.html', {'cases': cases})

def success_page(request):
    return render(request, 'success.html')
