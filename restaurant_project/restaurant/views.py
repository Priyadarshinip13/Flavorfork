# restaurant/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.conf import settings


from .models import MenuItem, Order, OrderItem
from .forms import RegisterForm

import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

genai.configure(api_key="AIzaSyC6SlJq9twu2Sy4d9BaqCqsi9V-Z1oiREw")

@csrf_exempt
def gemini_chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        prompt = data.get("message")

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        return JsonResponse({"response": response.text})


def home(request):
    return render(request, 'restaurant/home.html')


def menu(request):
    items = MenuItem.objects.filter(is_available=True)  # filter only available items

    search = request.GET.get('search')
    category = request.GET.get('category')

    if search:
        items = items.filter(name__icontains=search)

    if category:
        items = items.filter(category__iexact=category)

    return render(request, 'restaurant/menu.html', {'items': items})



def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'restaurant/register.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('menu')
    else:
        form = AuthenticationForm()
    return render(request, 'restaurant/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    order, created = Order.objects.get_or_create(user=request.user, is_ordered=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, menu_item=item)

    if not created:
        order_item.quantity += 1
        order_item.save()

    return redirect('view_cart')


@login_required
def view_cart(request):
    order = Order.objects.filter(user=request.user, is_ordered=False).first()
    cart_items = order.items.all() if order else []
    total_price = sum(item.subtotal() for item in cart_items)

    return render(request, 'restaurant/order.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)

    if item.order.user == request.user:
        item.delete()

    return redirect('view_cart')


@login_required
def checkout(request):
    order = Order.objects.filter(user=request.user, is_ordered=False).first()
    if order:
        order.is_ordered = True
        order.save()
        # Optional: trigger PDF bill or thank you page
        return redirect('generate_bill_pdf')
    messages.error(request, "No items in cart to checkout.")
    return redirect('menu')


@login_required
def generate_bill_pdf(request):
    order = Order.objects.filter(user=request.user, is_ordered=True).last()

    if not order:
        messages.warning(request, "No completed order found.")
        return redirect('menu')

    context = {
        'user': request.user,
        'cart_items': order.items.all(),
        'total_price': sum(item.subtotal() for item in order.items.all()),
        'timestamp': timezone.now()
    }

    template_path = 'restaurant/pdf_bill.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="order_bill.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("PDF generation error <pre>" + html + "</pre>")

    return response
