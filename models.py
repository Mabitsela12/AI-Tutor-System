from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Grade(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='uploads/grade/')

    def __str__(self):
        return self.name


class Subject(models.Model):  # Change to singular (Subject) for better practice
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.subject} - {self.grade.name}'

    class Meta:
        verbose_name_plural = 'subjects'

class SubjectContent(models.Model):
    grade = models.IntegerField()
    subject = models.CharField(max_length=100)
    content = models.TextField()
    
    def __str__(self):
        return self.subject

class Tutorial(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_pictures', default='default.jpg')
    grade_level = models.CharField(max_length=50)  # Make sure this is defined in the database
    completed_subjects = models.ManyToManyField(Subject, blank=True)
    quiz_count = models.IntegerField(default=0)
    last_subject_accessed = models.CharField(max_length=100, blank=True)

    AI_VOICE_CHOICES = [
        ('default', 'Default'),
        ('female', 'Female'),
        ('male', 'Male'),
    ]
    ai_voice = models.CharField(max_length=10, choices=AI_VOICE_CHOICES, default='default')

    bookmarked_tutorials = models.ManyToManyField(Tutorial, blank=True)

    def __str__(self):
        return self.user.username
    

class Quiz(models.Model):
    topic = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    grade = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.subject} - Grade {self.grade} on {self.topic}"
