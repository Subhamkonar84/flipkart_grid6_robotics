from django.shortcuts import render, redirect
from .models import Item
from .forms import ItemForm
from django.contrib import messages  # To display feedback messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from .models import Notification
from django.shortcuts import render

incorrect_quantities=[]
missing_items=[]
extra_items=[]

@csrf_exempt
def external_update_item(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request
            data = json.loads(request.body)
            name = data.get('name')
            quantity = int(data.get('quantity', 0))
            expiry_date = data.get('expiry_date')

            # Validate inputs
            if not all([name, quantity, expiry_date]):
                return JsonResponse({'error': 'All fields (name, quantity, expiry_date) are required.'}, status=400)

            # Parse expiry_date
            try:
                expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
            
            today = datetime.today().date()
            if expiry_date < today:
                Notification.objects.create(message=f'The item "{name[4:] if name.startswith('bad_') else name}" is expired and has an expired date: {expiry_date}.')
                return JsonResponse({'error': f'The item "{name[4:] if name.startswith('bad_') else name}" is expired and has an expired date: {expiry_date}.'}, status=400)
            
            if name.startswith("bad_"):
                    Notification.objects.create(message=f'The item "{name[4:]}" is an defective piece and should no be shipped')
                    return JsonResponse({'error': f'he item "{name}" has an defective piece and should no be shipped'}, status=400)

            # Check if the item is expired
            

            # Check if the item already exists
            item = Item.objects.filter(name=name).first()

            if item:
                # Update the quantity and expiry date
                item.quantity += quantity
                item.expiry_date = max(item.expiry_date, expiry_date)  # Keep the later expiry date
                item.save()
                message = f'Item "{name}" updated successfully. Quantity incremented by {quantity}.'
            else:
                # Create a new item
                Item.objects.create(name=name, quantity=quantity, expiry_date=expiry_date)
                message = f'Item "{name}" added successfully.'

            return JsonResponse({'message': message}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

    return JsonResponse({'error': 'Invalid HTTP method. Use POST.'}, status=405)

def check_notifications(request):
    # Get all unread notifications
    notifications = Notification.objects.filter(is_read=False)

    if notifications.exists():
        # Format notifications as a list of dictionaries
        data = [{'id': n.id, 'message': n.message} for n in notifications]
        
        # Delete the notifications after fetching them
        notifications.delete()
        
        return JsonResponse({'notifications': data}, status=200)

    return JsonResponse({'notifications': []}, status=200)

def fetch_items(request):
    items = Item.objects.all().values('id', 'name', 'quantity', 'expiry_date')
    return JsonResponse(list(items), safe=False)

def compare_items(needed_items, actual_items):
    # Initialize results
    missing_items = {}
    incorrect_items = {}
    extra_items = {}

    # Compare needed_items with actual_items
    for item, needed_quantity in needed_items.items():
        actual_quantity = actual_items.get(item, 0)
        
        if actual_quantity == 0:
            # Item is completely missing
            missing_items[item] = needed_quantity
        elif actual_quantity < needed_quantity:
            # Item is partially missing
            missing_items[item] = needed_quantity - actual_quantity
        elif actual_quantity > needed_quantity:
            # Item has extra quantity
            incorrect_items[item] = actual_quantity - needed_quantity

    # Check for extra items in actual_items not present in needed_items
    for item, actual_quantity in actual_items.items():
        if item not in needed_items:
            extra_items[item] = actual_quantity

    return {
        "missing_items": missing_items,
        "incorrect_items": incorrect_items,
        "extra_items": extra_items
    }

def item_list(request):
    items = Item.objects.all()
    incorrect_items = []
    extra_items = []
    missing_items = []

    if request.method == 'POST':
        if 'clear_table' in request.POST:
            Item.objects.all().delete()
            return redirect('item_list')

        if 'add_item' in request.POST:
            form = ItemForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('item_list')

        if 'check_bill' in request.POST:
            print(Item.objects)
            raw_input = request.POST.get('items', '').strip()  # Get input and strip whitespace

            if not raw_input:  # Check if the input is empty
                messages.warning(request, 'Please Check Your Input and try again')
            else:
                missing_items = []  # To track missing items
                incorrect_items = []  # To track items with incorrect quantities
                extra_items = []  # To track extra items
                all_match = True  # Assume all items match initially

                try:
                    # Parse the input string into a dictionary
                    needed_items = {}
                    entries = [entry.strip() for entry in raw_input.split(',') if entry.strip()]
                    for entry in entries:
                        name, quantity = entry.split(':')
                        needed_items[name] = int(quantity)

                    # Pre-fetch all items from the database into a dictionary for efficiency
                    actual_items = {item.name: item.quantity for item in items}


                    result = compare_items(needed_items, actual_items)


                    for name, quantity in result['missing_items'].items():
                        missing_items.append(f"{quantity} ({name}), is missing ")
                        all_match = False

                    for name, quantity in result['incorrect_items'].items():
                        incorrect_items.append(f"{name}: needed {needed_items[name]}, got {actual_items[name]} (extra: {quantity})")
                        all_match = False

                    for name, quantity in result['extra_items'].items():
                        extra_items.append(f"{quantity} ({name}) is extra ")
                        all_match = False
 
                    print("missing item=",missing_items)
                    print("incorrect item=",incorrect_items)
                    print("extra item=",extra_items)       
                    

                except ValueError:
                    messages.error(request, 'Invalid input format. Use "name:quantity,name:quantity".')

    form = ItemForm()
    return render(request, 'billing/item_list.html', {
        'items': items,
        'form': form,
        'missing_items': missing_items,
        'extra_items': extra_items,
        'incorrect_quantities': incorrect_items,
    })


