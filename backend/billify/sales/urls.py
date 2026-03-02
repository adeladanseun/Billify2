from django.urls import path
from .user_views import *
from .views import DashboardView

#when the user logs in again, the previous tokens are invalidated or not depending on the settings attribute ALLOW_MULTIPLE_DEVICE_LOGIN
#.views only contains inherited classes for now

urlpatterns = [
    path('api/login/', LoginView.as_view()),
    path('api/register/', RegisterView.as_view()), #requires username and password in body
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', TokenBlacklistView.as_view(), name='logout_view'), #requires refresh token in post body

    path('api/test/', TestReturnAuth.as_view()),


    path('dashboard/', DashboardView.as_view()),
    
    
]
#path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),