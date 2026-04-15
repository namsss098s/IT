from django.db import transaction
from .models import Edition


# 📦 Lấy edition (helper)
def get_edition(edition_id):
    return Edition.objects.get(id=edition_id)


# 🔻 Giảm số lượng (BORROW)
@transaction.atomic
def reduce_stock(edition_id):
    edition = Edition.objects.select_for_update().get(id=edition_id)

    if edition.available_quantity <= 0:
        raise ValueError("Book is out of stock")

    edition.available_quantity -= 1
    edition.save()

    return edition


# 🔺 Tăng số lượng (RETURN)
@transaction.atomic
def increase_stock(edition_id):
    edition = Edition.objects.select_for_update().get(id=edition_id)

    if edition.available_quantity >= edition.quantity:
        raise ValueError("Stock already full")

    edition.available_quantity += 1
    edition.save()

    return edition


# 🔁 Update quantity (admin chỉnh kho)
@transaction.atomic
def update_total_quantity(edition_id, new_quantity):
    edition = Edition.objects.select_for_update().get(id=edition_id)

    # giữ nguyên số sách đang mượn
    borrowed = edition.quantity - edition.available_quantity

    if new_quantity < borrowed:
        raise ValueError("New quantity less than borrowed books")

    edition.quantity = new_quantity
    edition.available_quantity = new_quantity - borrowed
    edition.save()

    return edition


# 🧹 Reset stock (hiếm dùng)
@transaction.atomic
def reset_stock(edition_id):
    edition = Edition.objects.select_for_update().get(id=edition_id)

    edition.available_quantity = edition.quantity
    edition.save()

    return edition