from base64 import urlsafe_b64encode
from email import message
from lib2to3.pgen2.tokenize import generate_tokens
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect,render
from django.contrib.auth import authenticate, login, logout
from loginsystem import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from . tokens import generate_tokens
from django.core.mail import EmailMessage, send_mail

# Create your views here.
def home(request):
    return render(request, 'authentication/index.html')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request,"Username already exist! Please try some other username")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request,"Email already exist! Please try some other username")
            return redirect('home')

        if len(username)>10:
            messages.error(request,"Username must be under 10 characters")
            return redirect('home')

        if pass1 != pass2:
            messages.error(request,"Passwords did not match!")
            return redirect('home')

        if not username.isalnum():
            messages.error(request,"Username must be alphanumeric")
            return redirect('home')

        myUser = User.objects.create_user(username,email,pass1)
        myUser.first_name= fname
        myUser.last_name= lname
        myUser.is_active = False
        myUser.save()

        messages.success(request, "Your account has been succesfully created.")

        #welcome mail
        subject = "Welcome to my loginsystem"
        message = "Hello "+ myUser.first_name +"!\n"+"Thankyou for vivting our website. We have sent confirmation for your mail. Please confirm. \n\nPratima yadav"
        from_email = settings.EMAIL_HOST_USER
        to_list=[myUser.email]
        send_mail(subject, message, from_email,to_list,fail_silently=True)

        #Email Address confirmation
        current_site= get_current_site(request)
        email_subject="Confirm your mail"
        message2= render_to_string('email_confirmation.html',{'name':myUser.first_name,'domain':current_site.domain,'uid':urlsafe_base64_encode(force_bytes(myUser.pk)),'token':generate_tokens.make_token(myUser)})

        email= EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myUser.email],
        )
        email.fail_silently= True
        email.senfd()
        return redirect('signin')


    return render(request, 'authentication/signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1=request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname= user.first_name

            return render(request, 'authentication/index.html', {'fname':fname})
        else:
            messages.error(request, "Bad Credentials")
            return redirect('home')
    return render(request, 'authentication/signin.html')

def signout(request):
    logout(request)
    messages.success(request,"succesfully log out")
    return redirect('home')
