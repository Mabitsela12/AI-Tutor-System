from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # Correct import for auth_views
from .views import quiz_view, search_view, grade_content_view, subject_detail_view
from .views import CustomPasswordChangeView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('grade/<int:grade>/', views.grade_page, name='grade_page'),
    path('grade/<int:grade>/', views.grade_detail_view, name='grade_detail'),
    path('subjects/<int:grade>/', views.subjects_view, name='subjects_view'),
    path('subject-content/<int:grade>/<str:subject>/', views.subject_content_view, name='subject_content_view'),
    path('quiz/<int:grade>/<str:subject>/', views.subject_quiz_view, name='subject_quiz'),
    path('quizzes/', quiz_view, name="quizzes"),
    path('search/', search_view, name='search'),
    path('grade_content/<int:grade>/', grade_content_view, name='grade_content'),
    path('grades/<int:grade>/subjects/<str:subject>/', subject_detail_view, name='subject_detail'),  # URL for subject details
    path('index/', views.assistant, name='assistant'),
    path('essay_form/', views.check_essay, name='check_essay'),
    path('topic-content/<int:grade>/<str:subject>/<str:topic>/', views.topic_content_view, name='topic_content'),
    path('new/', views.new, name='new'),
    path('extract_text/', views.extract_text, name='extract_text'),
    path('ask_question/', views.ask_question, name='ask_question'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('user-guide/', views.user_guide, name='user_guide'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('update_preferences/', views.update_preferences, name='update_preferences'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('chat/', views.chat_view, name='chat_view'),  # URL to access the chat form
    path('chat_step/', views.chat_step, name='chat_step'),  # URL to process the chat message
    path('quiz_combined/', views.quiz_combined, name='quiz_combined'),
    path('submit_quiz/', views.submit_quiz, name='submit_quiz'),
    path('quiz_results/', views.quiz_results, name='quiz_results'),
    path('about/', views.about, name='about'),
    path('help_center/', views.help_center, name='help_center'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)