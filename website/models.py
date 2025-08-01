from django.db import models
from django.contrib.auth.models import User

class Professor(models.Model):
    id = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id} - {self.name}"

class Module(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.code} - {self.name}"

class ModuleInstance(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    year = models.IntegerField()
    semester = models.IntegerField()

    def __str__(self):
        return f"{self.module.code} (year={self.year}, sem={self.semester})"

class TeachingAssignment(models.Model):
    module_instance = models.ForeignKey(ModuleInstance, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('module_instance', 'professor')

    def __str__(self):
        return f"{self.professor.id} teaches {self.module_instance}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    teaching_assignment = models.ForeignKey(TeachingAssignment, on_delete=models.CASCADE)
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'teaching_assignment')

    def __str__(self):
        return f"Rating({self.rating}) by {self.user.username} for {self.teaching_assignment}"
