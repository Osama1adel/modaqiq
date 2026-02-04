
class Document(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='case_documents')
    file = models.FileField(upload_to='case_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.case.title}"
