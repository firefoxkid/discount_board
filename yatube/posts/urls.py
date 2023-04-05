from django.urls import path

from . import views

urlpatterns = [
    path('new/', views.new_post, name='new_post'),
    # Работа с подписками
    path("follow/", views.follow_index, name="follow_index"),
    path("<str:username>/follow/",
         views.profile_follow,
         name="profile_follow"),
    path("<str:username>/unfollow/",
         views.profile_unfollow,
         name="profile_unfollow"),
    path('<str:username>/', views.profile, name='profile'),
    path('<username>/<post_id>/edit/', views.post_edit, name='post_edit'),
    path('<username>/<post_id>/post_del/', views.post_del, name='post_del'),
    path("group/<slug:slug>/", views.group_posts, name="group_posts"),
    # Главная страница
    path('', views.index, name='index'),
    # Просмотр записи
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    # Работа со страницами ошибок
    path('404/', views.page_not_found, name='page_not_found'),
    path('500/', views.server_error, name='server_error'),
    # Работа с комментариями
    path("<username>/<int:post_id>/comment",
         views.add_comment,
         name="add_comment"),
    path("<username>/<int:post_id>/comment_del/<int:comment_id>",
         views.comment_del,
         name="comment_del"),

]
