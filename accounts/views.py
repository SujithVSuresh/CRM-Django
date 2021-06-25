from django.shortcuts import render, redirect
from django.http import HttpResponse

from . models import *
from . forms import OrderForm, CreateUserForm, CustomerForm
from . filters import OrderFilter

from django.contrib import messages #flash message import

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required #importing login decorators for restricting user before login
from . decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group


# Create your views here.

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid(): 
            form.save()
            #username = form.cleaned_data.get('username') #for getting that username
            #group = Group.objects.get(name='customer')
            #user.groups.add(group)
            #Customer.objects.create(
                #user=user,
            #)
            messages.success(request, 'Account was created')
            return redirect('login')
        
    context = {'form':form}
    return render(request, 'accounts/register.html', context)

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username OR Password was Incorrect')    

    context = {}
    return render(request, 'accounts/login.html', context)  

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer'])
def userPage(request):
    orders = request.user.customer.order_set.all() #querriying order details of that specific customer

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders':orders, 'total_orders':total_orders, 
              'delivered':delivered, 'pending':pending}
    return render(request, 'accounts/user.html', context)   

@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()


    context = {'form':form}
    return render(request, 'accounts/account_settings.html', context)     

@login_required(login_url='login') #login decorators
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders':orders, 'customers':customers,
    'total_orders':total_orders, 'delivered':delivered, 'pending':pending}

    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login') #login decorators
@allowed_users(allowed_roles=['Admin'])
def products(request):
    products = Product.objects.all()

    return render(request, 'accounts/products.html', {'products':products})

@login_required(login_url='login') #login decorators
@allowed_users(allowed_roles=['Admin'])
def customer(request, pk):
    customer = Customer.objects.get(id=pk)

    orders = customer.order_set.all()
    order_count = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders) #filtering for search
    orders = myFilter.qs

    context = {'customer':customer, 'orders':orders, 'order_count':order_count, 'myFilter':myFilter}
    return render(request, 'accounts/customer.html', context)  

@login_required(login_url='login') #login decorators
@allowed_users(allowed_roles=['Admin'])
def createOrder(request, pk):
    customer = Customer.objects.get(id=pk)
    form = OrderForm(initial={'customer':customer})  #it is from model form 'form.py' & initial is the instances
    if request.method == 'POST':
        #print('Printing POST:', request.POST)
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form':form}
    return render(request, 'accounts/order_form.html', context)  

@login_required(login_url='login') #login decorators
@allowed_users(allowed_roles=['Admin']) #user and admin permission
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form':form}

    return render(request, 'accounts/order_form.html', context)  

#for deleting
@login_required(login_url='login') #login decorators
@allowed_users(allowed_roles=['Admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
        return redirect('/')

    context = {'item':order}
    return render(request, 'accounts/delete.html', context)             
