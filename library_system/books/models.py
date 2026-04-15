from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200, db_index=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    description = models.TextField(blank=True)
    publisher = models.CharField(max_length=150, blank=True)

    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )

    authors = models.ManyToManyField(
        Author,
        blank=True,
        related_name='books'
    )

    def __str__(self):
        return self.title


class Edition(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='editions'   # 🔥 thêm để query đẹp hơn
    )

    edition_number = models.PositiveIntegerField()

    quantity = models.PositiveIntegerField(default=0)

    available_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('book', 'edition_number')

    def save(self, *args, **kwargs):
        # 🔥 lần đầu tạo → available = quantity
        if not self.pk:
            self.available_quantity = self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - Edition {self.edition_number}"
    
