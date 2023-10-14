from django.contrib import admin
from django.urls import path, include
from agents import views as agent_views
from vault_manager import views as vault_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import messages
from django.shortcuts import redirect

urlpatterns = [
    path("", vault_views.index, name='index'),
    path("admin/", admin.site.urls, name='admin'),
    path("my_branches/", agent_views.my_branches, name="my_branches"),
    path("branches_under/<str:username>/", agent_views.branches_under, name="branches_under"),
    path("my_deposits/", agent_views.my_deposits, name="my_deposits"),
    path("profile/", agent_views.profile, name="profile"),
    path("zones/", agent_views.zones, name="zones"),
    path("all_agents/", agent_views.all_agents, name="all_agents"),
    path("branches/", agent_views.branches, name="branches"),
    path("vault/", include("vault_manager.urls")),

    path("login/", auth_views.LoginView.as_view(template_name="agents/login.html"), name="login"),
    path("logout/", lambda request: logout_with_message(request), name="logout"),
    path("password_reset/", 
        auth_views.PasswordResetView.as_view(template_name="agents/password_reset.html"), name="password_reset"),
    path("password_reset_complete/", 
        auth_views.PasswordResetCompleteView.as_view(template_name="agents/password_reset_complete.html"), name="password_reset_complete"),
    path("password_reset_confirm/<uidb64>/<token>", 
         auth_views.PasswordResetConfirmView.as_view(template_name="agents/password_reset_confirm.html"), name="password_reset_confirm"),
    path("password_reset/done", 
        auth_views.PasswordResetDoneView.as_view(template_name="agents/password_reset_done.html"), name="password_reset_done"),
    path("password_reset/done", 
        auth_views.PasswordResetDoneView.as_view(template_name="agents/password_reset_done.html"), name="password_reset_done"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

def logout_with_message(request):
    auth_views.LogoutView.as_view(next_page="login")(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("login")  # Redirect to the login page after logout

admin.site.site_header = "Yonna Forex Bureau - Vault Admin"
admin.site.site_title = "Yonna Vault Admin Portal"
admin.site.index_title = "Welcome To Yonna Vault Admin Portal"
