from django.urls import path
from django.contrib.auth import views as auth_views
from blog import views


app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'), 
    path('posts/', views.post_list, name='post_list'),
    path('posts/category/<str:category>', views.post_list, name='post_list_category'),
    path('posts/<id>', views.post_detail, name='post_detail'),
    path('posts/<post_id>/comment', views.post_comment, name='post_comment'),
    path('ticket/', views.ticket, name='ticket'),
    path('search/', views.post_search, name='post_search'),
    path('profile/', views.profile, name='profile'),
    path('profile/create_post/', views.create_post, name='create_post'),
    path('delete-post/<int:post_id>', views.delete_post, name='delete_post'),
    path('edit-post/<int:post_id>', views.edit_post, name='edit_post'),
    path('delete-image/<int:image_id>', views.delete_image, name='delete_image'),
    path('delete-image/<int:image_id>', views.delete_image, name='delete_image'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('change-password/', auth_views.PasswordChangeView.as_view(success_url='done'), name='password_change'),
    path('change-password/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password-reset/', auth_views.PasswordResetView.as_view(success_url='done'), name='password-reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password-reset-done'),
    path('password-reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(success_url='/blog/password-reset/complete'), name='password-reset-confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password-reset-complete'),
    path('register/', views.user_register, name='user-register'),
    path('register/done', views.user_register_done, name='user-register-done'),
    path('account/edit/', views.account_edit, name='user-edit')




]