from django.shortcuts import render, redirect
from .models import Item
from .forms import ItemForm
from django.contrib import messages  # To display feedback messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from .models import Notification

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
            
            if name.startswith("bad_"):
                    Notification.objects.create(message=f'The item "{name[4:]}" is an defective piece and should no be shipped')
                    return JsonResponse({'error': f'he item "{name}" has an defective piece and should no be shipped'}, status=400)

            # Check if the item is expired
            today = datetime.today().date()
            if expiry_date < today:
                Notification.objects.create(message=f'The item "{name}" has an expired date: {expiry_date}.')
                return JsonResponse({'error': f'The item "{name}" has an expired date: {expiry_date}.'}, status=400)

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

def item_list(request):
    items = Item.objects.all()
    unmatched_items = []
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
            raw_input = request.POST.get('items', '').strip()  # Get input and strip whitespace

            if not raw_input:  # Check if the input is empty
                messages.error(request, 'Input cannot be empty. Use the format "name:quantity,name:quantity".')
            else:
                missing_items = []  # To track missing items
                incorrect_quantities = []  # To track items with incorrect quantities
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

                    # Check for missing items or incorrect quantities
                    for name, quantity in needed_items.items():  # From "things needed"
                        if name not in actual_items:
                            missing_items.append(f"{name}: needed {quantity}, got 0")
                            all_match = False
                        elif actual_items[name] != quantity:
                            actual_quantity = actual_items[name]
                            difference = actual_quantity - quantity
                            incorrect_quantities.append(
                                f"{name}: needed {quantity}, got {actual_quantity} (difference: {difference})"
                            )
                            all_match = False

                    # Check for extra items in the database
                    needed_item_names = set(needed_items.keys())
                    for name, quantity in actual_items.items():  # From "things we got"
                        if name not in needed_item_names:
                            extra_items.append(f"{name}: extra with quantity {quantity}")
                            all_match = False

                    # Handle the results of the check
                    if all_match:
                        messages.success(request, 'All items match correctly with the table.')
                    else:
                        if missing_items:
                            messages.error(
                                request,
                                f"Missing items:\n" + "\n".join(missing_items)
                            )
                        if incorrect_quantities:
                            messages.error(
                                request,
                                f"Items with incorrect quantities:\n" + "\n".join(incorrect_quantities)
                            )
                        if extra_items:
                            messages.error(
                                request,
                                f"Extra items in the table:\n" + "\n".join(extra_items)
                            )
                        if missing_items or incorrect_quantities or extra_items:
                            messages.error(
                                request,
                                f"Summary:\n" +
                                (f"Missing items:\n" + "\n".join(missing_items) + "\n" if missing_items else "") +
                                (f"Items with incorrect quantities:\n" + "\n".join(incorrect_quantities) + "\n" if incorrect_quantities else "") +
                                (f"Extra items in the table:\n" + "\n".join(extra_items) if extra_items else "")
                            )

                except ValueError:
                    messages.error(request, 'Invalid input format. Use "name:quantity,name:quantity".')







    form = ItemForm()
    return render(request, 'billing/item_list.html', {
        'items': items,
        'form': form,
        'unmatched_items': unmatched_items,
        'missing_items': missing_items,
        'extra_items': extra_items,
    })